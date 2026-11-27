"""
app.py — Streamlit display/config layer for TradeForge.

Display and configuration ONLY — no scanner/indicators/ranking/market_context
logic lives here. Every scan/rank/rule/market-context computation is done by
the existing modules, imported and called as-is:

  - run_daily.py's own top-level calls (get_global_latest_date,
    update_all_symbols, update_all_indices, get_active_symbols, build_rs_map,
    scan_all_symbols, summarize_results) and its _classify() outcome
    classifier, reused directly rather than reimplemented.
  - src.scanner.report / src.market_context.report / src.reporting.volume_chart
    for detail-view content (rule breakdown data, market context text, the
    volume chart image).

Two things in this file are deliberately display-layer RE-FILTERS of already-
scanned data, not re-invocations of the scan itself:

  1. The RS cutoff slider and per-rule toggles recompute pass/fail against
     each already-scanned result's raw rs_rank / rule.passed values, entirely
     in this file. scan_symbol() (scanner/scanner.py) bakes RS_RANK_CUTOFF in
     at scan time and is never touched — moving the slider doesn't trigger a
     750-symbol rescan, it just re-evaluates the numbers already in memory.
     The slider ALSO writes its value back to src/config/settings.py (so a
     future CLI run of run_daily.py/main.py picks up the new default) but
     that persisted value has no effect on the current session's already-
     loaded table — same reason.
  2. Per-rule toggle labels are read from the first scan result's own
     rules[i].name at runtime, not hardcoded — avoids the sidebar silently
     drifting out of sync with trend_template.py.

The "Run Scanner" progress indicator is a coarse 4-stage spinner (freshness
check / data update / index update / scan), calling update_all_symbols() and
scan_all_symbols() completely unchanged as single blocking calls — a true
per-symbol 0-750 progress bar would require looping over update_history()/
scan_symbol() directly in this file instead of the batch wrappers, which was
deliberately not chosen (see conversation) to keep zero lines touched in
data/update_all.py and scanner/scanner.py.

Run from the tradeforge root (same CWD requirement as run_daily.py/main.py,
for the relative data/reports/logs paths to resolve): streamlit run app.py
"""

import re
from pathlib import Path

import pandas as pd
import streamlit as st

from run_daily import _classify
from src.config import settings
from src.data.price_repository import get_global_latest_date
from src.data.symbol_repository import get_active_symbols
from src.data.symbol_universe_repository import (
    get_all_symbol_universes,
    get_all_universes,
)
from src.data.symbol_industry_repository import get_all_symbol_industries
from src.data.update_all import update_all_symbols
from src.data.index_updater import update_all_indices
from src.market_context.report import format_market_context, get_market_context_for_stock
from src.patterns.vcp import format_pivot_status
from src.ranking.relative_strength import build_rs_map
from src.ranking.sector_relative_strength import calculate_sector_relative_strength
from src.reporting.volume_chart import plot_volume_trend
from src.scanner.scanner import scan_all_symbols, summarize_results

SETTINGS_PATH = Path("src/config/settings.py")


def _tradingview_url(symbol: str) -> str:
    ticker = symbol.split(":")[-1].split("-")[0]
    return f"https://www.tradingview.com/chart/?symbol=NSE:{ticker}"

st.set_page_config(page_title="TradeForge", layout="wide")


# ============================================================
# SETTINGS.PY READ/WRITE — RS_RANK_CUTOFF only. Atomic write (tmp file +
# replace) so a crash mid-write can't corrupt the file the rest of the
# codebase imports from.
# ============================================================
def _write_rs_cutoff(new_value: int) -> None:
    text = SETTINGS_PATH.read_text()
    new_text, n = re.subn(
        r"^RS_RANK_CUTOFF\s*=\s*\d+",
        f"RS_RANK_CUTOFF = {new_value}",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if n == 0:
        st.warning("Could not find RS_RANK_CUTOFF in settings.py — value not persisted to disk.")
        return

    tmp_path = SETTINGS_PATH.with_suffix(".py.tmp")
    tmp_path.write_text(new_text)
    tmp_path.replace(SETTINGS_PATH)
    settings.RS_RANK_CUTOFF = new_value  # keep this process's module state in sync too


# ============================================================
# RUN SCANNER — same sequence as run_daily.main(), coarse per-phase status.
# ============================================================
def run_scanner():
    with st.status("Running scanner...", expanded=True) as status:
        st.write("Checking data freshness...")
        prior_date = get_global_latest_date()
        st.write(
            f"Data last updated: {prior_date}" if prior_date
            else "Data last updated: never (no data in database)"
        )

        st.write("Updating symbol data (750 symbols — this can take a minute)...")
        update_results = update_all_symbols()
        new_date = get_global_latest_date()
        outcome, updated, no_data, up_to_date, errors = _classify(update_results)
        st.session_state["outcome_info"] = {
            "outcome": outcome,
            "new_date": new_date,
            "updated": updated,
            "no_data": no_data,
            "errors": errors,
        }
        st.write(f"Data update outcome: {outcome} (latest date: {new_date})")

        st.write("Updating index data...")
        index_results = update_all_indices()
        index_errors = [r for r in index_results if r["status"] == "error"]
        if index_errors:
            st.write(
                f"Note: {len(index_errors)} index update(s) failed — "
                f"market context may use slightly stale index data."
            )

        st.write("Scanning symbols against Trend Template + RS...")
        symbols = get_active_symbols()
        rs_map = build_rs_map()
        scan_results = scan_all_symbols(symbols, rs_map)
        summary = summarize_results(scan_results)

        st.session_state["scan_results"] = scan_results
        st.session_state["scan_summary"] = summary
        st.session_state["symbol_universes"] = get_all_symbol_universes()
        st.session_state["symbol_industries"] = get_all_symbol_industries()

        # Derived HERE, synchronously, before this function returns — not
        # lazily inside build_results_dataframe(). render_sidebar() runs
        # before build_results_dataframe() in the script's top-to-bottom
        # order on every rerun, including this SAME rerun (this button
        # handler runs inline, then the script continues to render_sidebar()
        # right after). Deriving it later meant the very first render after
        # a scan saw rule_names=None, so render_sidebar() returned an EMPTY
        # enabled_rules set — every rule silently unenforced, Overall
        # collapsing to "RS cutoff only" until the next unrelated rerun.
        first_with_rules = next((r for r in scan_results if "rules" in r), None)
        st.session_state["rule_names"] = (
            [rule.name for rule in first_with_rules["rules"]] if first_with_rules else None
        )

        status.update(
            label=f"Scan complete — {summary['passed_count']}/{summary['total']} passed",
            state="complete",
        )


# ============================================================
# OUTCOME BANNER — and the shared stale-symbol set the results table/
# detail view also use.
#
# "no_data" is only unambiguous when EVERY symbol lands there (or in
# up_to_date) with zero updates — that's what "unchanged_holiday" means,
# a real holiday hits the whole universe. Any other outcome where
# no_data appears alongside genuine "updated" symbols is a mixed
# result: something (an expired token, a transient API failure) kept
# a subset of symbols from refreshing, and update_history()'s
# if-df.empty path currently reports that identically to "no candles
# exist for this date range" — the SAME ambiguity update_history()
# already has for errors vs. genuinely-absent data, just one level up.
# Not fixed at the source (data/downloader.py) here — that's shared by
# run_daily.py/main.py too and deserves its own confirmed root cause
# before changing, not a guess. This only broadens what THIS app
# flags as "don't fully trust this row's freshness."
# ============================================================
def _get_possibly_stale_symbols() -> set[str]:
    info = st.session_state.get("outcome_info")
    if info is None:
        return set()

    stale = {r["symbol"] for r in info["errors"]}
    if info["outcome"] != "unchanged_holiday":
        stale |= {r["symbol"] for r in info["no_data"]}
    return stale


def render_outcome_banner():
    info = st.session_state.get("outcome_info")
    if info is None:
        return

    outcome = info["outcome"]
    stale = _get_possibly_stale_symbols()

    def _sample(symbols, n=8):
        symbols = sorted(symbols)
        shown = ", ".join(symbols[:n])
        return shown + (f", and {len(symbols) - n} more" if len(symbols) > n else "")

    if outcome == "advanced":
        if stale:
            st.warning(
                f"Data updated, but {len(stale)} symbol(s) got no fresh data this run "
                f"(status other than 'updated') — their scan results may be using stale "
                f"cached prices: {_sample(stale)}"
            )
        else:
            st.success(f"Data updated successfully. Latest date: {info['new_date']}")
    elif outcome == "unchanged_holiday":
        st.info(
            f"No new data — Fyers confirms no data available for the missing date(s) "
            f"(consistent with a weekend/holiday). Data current as of {info['new_date']}."
        )
    elif outcome == "partial":
        st.warning(
            f"Data update partially failed — {len(stale)} symbol(s) may be stale "
            f"(errored or got no fresh data this run): {_sample(stale)}"
        )
    else:  # failed
        st.error(
            f"Data update failed — {len(stale)} symbol(s) errored, no successful updates. "
            f"Results may not reflect current market conditions."
        )


# ============================================================
# SIDEBAR
# ============================================================
def render_sidebar():
    st.sidebar.header("Filters")

    all_universes = get_all_universes()
    selected_universes = st.sidebar.multiselect(
        "Universe", options=all_universes, default=all_universes
    )

    rs_cutoff = st.sidebar.slider(
        "RS cutoff",
        min_value=1,
        max_value=99,
        value=st.session_state.get("rs_cutoff", settings.RS_RANK_CUTOFF),
        key="rs_cutoff",
    )
    if rs_cutoff != st.session_state.get("_last_written_rs_cutoff", settings.RS_RANK_CUTOFF):
        _write_rs_cutoff(rs_cutoff)
        st.session_state["_last_written_rs_cutoff"] = rs_cutoff

    st.sidebar.header("Trend Template rules")
    rule_names = st.session_state.get("rule_names")
    enabled_rules = set(rule_names) if rule_names else set()
    if rule_names is None:
        st.sidebar.caption("Run the scanner to see per-rule toggles.")
    else:
        for name in rule_names:
            key = f"rule_toggle::{name}"
            checked = st.sidebar.checkbox(name, value=st.session_state.get(key, True), key=key)
            if not checked:
                enabled_rules.discard(name)

    return selected_universes, rs_cutoff, enabled_rules


# ============================================================
# RESULTS TABLE — recomputes rs_passed/rule pass/overall against the
# CURRENT sidebar state, not the frozen scan-time values. See module
# docstring point 1.
# ============================================================
def build_results_dataframe(
    scan_results, symbol_universes, symbol_industries, selected_universes, rs_cutoff, enabled_rules, stale_symbols
):
    # rs_map rebuilt from scan_results (each result already carries its own
    # RelativeStrengthResult as result["rs"], baked in at scan time) rather
    # than threading build_rs_map()'s output through session_state as a
    # second copy of the same data -- same "don't duplicate what's already
    # in scan_results" reasoning the rest of this function already follows.
    rs_map = {
        result["symbol"]: result["rs"]
        for result in scan_results
        if "error" not in result and result.get("rs") is not None
    }
    sector_rs_map = calculate_sector_relative_strength(rs_map)

    rows = []
    for result in scan_results:
        if "error" in result:
            continue

        symbol = result["symbol"]
        universes = symbol_universes.get(symbol, [])
        if selected_universes and not (set(universes) & set(selected_universes)):
            continue

        rs = result["rs"]
        rs_rank = rs.rs_rank if rs else None
        rs_passed_live = rs_rank is not None and rs_rank >= rs_cutoff

        industry = symbol_industries.get(symbol)

        row = {
            "symbol": symbol,
            "universe": ", ".join(universes),
            "rs_rank": rs_rank,
            "Industry": industry,
            "Sector RS": sector_rs_map.get(industry),
        }

        all_enabled_passed = True
        for rule in result["rules"]:
            row[rule.name] = rule.passed
            if rule.name in enabled_rules and not rule.passed:
                all_enabled_passed = False

        row["RS >= cutoff"] = rs_passed_live
        row["Overall"] = all_enabled_passed and rs_passed_live
        row["Possibly stale"] = symbol in stale_symbols
        row["Chart"] = _tradingview_url(symbol)
        rows.append(row)

    return pd.DataFrame(rows)


def render_detail(result, symbol_universes, stale_symbols):
    symbol = result["symbol"]
    st.subheader(symbol)
    st.link_button("View Chart", _tradingview_url(symbol))

    if symbol in stale_symbols:
        st.warning(
            "This symbol got no fresh data on the last scan run — these results "
            "may be based on stale cached prices."
        )

    rs = result["rs"]
    st.metric("RS Rank", rs.rs_rank if rs else "N/A")

    st.write("**Trend Template rule breakdown**")
    for rule in result["rules"]:
        with st.expander(f"{'✅ PASS' if rule.passed else '❌ FAIL'} — {rule.name}"):
            for key, value in rule.actual.items():
                if isinstance(value, float):
                    value = round(value, 2)
                st.write(f"{key}: {value}")

    st.write("**Volume trend**")
    try:
        chart_path = plot_volume_trend(symbol)
        st.image(str(chart_path))
    except ValueError as e:
        st.caption(f"Volume chart unavailable: {e}")

    st.write("**Base & VCP**")
    base = result.get("base")
    vcp = result.get("vcp")
    if base is None:
        st.caption("No base/VCP data available.")
    else:
        duration = base.duration_weeks if base.duration_weeks is not None else "N/A"
        st.write(f"Base detected: {'✅' if base.detected else '❌'}  (duration: {duration} weeks)")
        if base.volume_trend is not None:
            st.caption(f"Volume trend during base: {base.volume_trend}")
        if not base.detected and base.reason:
            st.caption(f"Reason: {base.reason}")

        if vcp is not None:
            st.write(f"VCP detected: {'✅' if vcp.detected else '❌'}")
            if vcp.contractions:
                depths = ", ".join(f"{c.contraction_pct:.1f}%" for c in vcp.contractions)
                st.caption(f"{len(vcp.contractions)} contraction(s): {depths}")
            st.caption(vcp.reason)
            if vcp.detected:
                st.write(format_pivot_status(vcp))

    st.write("**Market context**")
    context = get_market_context_for_stock(symbol)
    if context:
        st.text(format_market_context(context))
    else:
        st.caption("No universe/index data available.")


# ============================================================
# MAIN
# ============================================================
st.title("TradeForge")

if st.button("Run Scanner", type="primary"):
    run_scanner()

render_outcome_banner()

selected_universes, rs_cutoff, enabled_rules = render_sidebar()

scan_results = st.session_state.get("scan_results")

if scan_results is None:
    st.info("No scan results yet — click **Run Scanner** to start.")
else:
    symbol_universes = st.session_state.get("symbol_universes", {})
    symbol_industries = st.session_state.get("symbol_industries", {})
    stale_symbols = _get_possibly_stale_symbols()
    df = build_results_dataframe(
        scan_results, symbol_universes, symbol_industries, selected_universes, rs_cutoff, enabled_rules, stale_symbols
    )

    show_only_passing = st.checkbox("Show only passing", value=False)
    display_df = df[df["Overall"]] if show_only_passing and not df.empty else df

    st.write(
        f"{len(display_df)} symbol(s) shown "
        f"({df['Overall'].sum() if not df.empty else 0} passing overall)"
    )

    event = st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        column_config={
            "Chart": st.column_config.LinkColumn(
                "Chart", display_text="View Chart"
            )
        },
    )

    csv_bytes = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download filtered results as CSV",
        data=csv_bytes,
        file_name="tradeforge_scan_results.csv",
        mime="text/csv",
    )

    selected_rows = event.selection.rows if event and event.selection else []
    if selected_rows:
        selected_symbol = display_df.iloc[selected_rows[0]]["symbol"]
        selected_result = next((r for r in scan_results if r["symbol"] == selected_symbol), None)
        if selected_result:
            st.divider()
            render_detail(selected_result, symbol_universes, stale_symbols)
