from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from src.config.settings import VOLUME_SPIKE_RATIO_THRESHOLD
from src.data.price_repository import load_candles
from src.indicators.volume import add_volume_indicators

OUTPUT_DIR = Path("reports/volume_charts")
ROLLING_AVG_WINDOW_DAYS = 10

BAR_COLOR = "#4C78A8"
SPIKE_COLOR = "#E45756"
ROLLING_AVG_COLOR = "#333333"
REFERENCE_LINE_COLOR = "#999999"


def _safe_filename(symbol: str) -> str:
    return symbol.replace(":", "_") + ".png"


def plot_volume_trend(symbol: str, weeks: int = 10) -> Path:
    n_days = weeks * 5

    df = load_candles(symbol)

    if df.empty:
        raise ValueError(f"No historical data available for {symbol}")

    df = add_volume_indicators(df)
    df["ROLL_AVG_10"] = df["volume"].rolling(ROLLING_AVG_WINDOW_DAYS).mean()

    window = df.tail(n_days).reset_index(drop=True)

    if window.empty:
        raise ValueError(f"No data in the trailing {n_days}-day window for {symbol}")

    reference_avg = window["AVG_VOL_50"].iloc[-1]

    colors = [
        SPIKE_COLOR if ratio >= VOLUME_SPIKE_RATIO_THRESHOLD else BAR_COLOR
        for ratio in window["VOLUME_RATIO"]
    ]

    fig, ax = plt.subplots(figsize=(14, 6))

    ax.bar(window["date"], window["volume"], color=colors, width=0.8)
    ax.plot(
        window["date"],
        window["ROLL_AVG_10"],
        color=ROLLING_AVG_COLOR,
        linewidth=1.5,
        label=f"{ROLLING_AVG_WINDOW_DAYS}-day rolling avg",
    )

    if reference_avg == reference_avg:  # not NaN
        ax.axhline(
            reference_avg,
            color=REFERENCE_LINE_COLOR,
            linestyle="--",
            linewidth=1,
            label="50-day avg volume",
        )

    ax.set_title(f"{symbol} — Volume Trend (last {n_days} trading days)")
    ax.set_ylabel("Volume")
    ax.set_xticks(window["date"][:: max(len(window) // 10, 1)])
    ax.tick_params(axis="x", rotation=45)

    handles = [
        plt.Line2D([0], [0], color=ROLLING_AVG_COLOR, lw=1.5),
        plt.Line2D([0], [0], color=REFERENCE_LINE_COLOR, ls="--", lw=1),
        plt.Rectangle((0, 0), 1, 1, color=BAR_COLOR),
        plt.Rectangle((0, 0), 1, 1, color=SPIKE_COLOR),
    ]
    labels = [
        f"{ROLLING_AVG_WINDOW_DAYS}-day rolling avg",
        "50-day avg volume",
        "Daily volume",
        f"≥{VOLUME_SPIKE_RATIO_THRESHOLD}x 50-day avg",
    ]
    ax.legend(handles, labels, loc="upper left")

    fig.tight_layout()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / _safe_filename(symbol)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

    return output_path


def plot_volume_trend_batch(symbols: list[str], weeks: int = 10) -> list[dict]:
    results = []

    for symbol in symbols:
        try:
            path = plot_volume_trend(symbol, weeks=weeks)
            results.append({"symbol": symbol, "status": "ok", "path": str(path)})
        except Exception as e:
            results.append({"symbol": symbol, "status": "error", "detail": str(e)})

    return results
