from pathlib import Path
import os

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")

FYERS_CLIENT_ID = os.getenv("FYERS_CLIENT_ID")
FYERS_SECRET_KEY = os.getenv("FYERS_SECRET_KEY")
FYERS_REDIRECT_URI = os.getenv("FYERS_REDIRECT_URI")
FYERS_ACCESS_TOKEN = os.getenv("FYERS_ACCESS_TOKEN")
RS_WEIGHTS = {
    "12m": 0.40,
    "6m": 0.30,
    "3m": 0.20,
    "1m": 0.10,
}

RS_RANK_CUTOFF = 90

TREND_TEMPLATE_NEAR_52W_HIGH_FACTOR = 0.75
TREND_TEMPLATE_ABOVE_52W_LOW_FACTOR = 1.30

VOLUME_TREND_SLOPE_LOOKBACK = 20
VOLUME_TREND_SLOPE_THRESHOLD_PCT = 0.005  # 0.5% of window mean volume, per day
VOLUME_SPIKE_RATIO_THRESHOLD = 1.5

DISTRIBUTION_DAY_WINDOW = 25
DISTRIBUTION_DAY_DECLINE_PCT = 0.2

FOLLOW_THROUGH_LOOKBACK = 25  # window to find the swing low starting a rally attempt
FOLLOW_THROUGH_MIN_DAY = 4  # rally day 1 = the up-day off the swing low
FOLLOW_THROUGH_MIN_GAIN_PCT = 1.25

BASE_SWING_LOOKBACK = 5  # bars on each side required to confirm a swing high/low
BASE_MIN_PRIOR_UPTREND_PCT = 25.0  # min low->high gain required before a base anchor qualifies
BASE_MIN_DURATION_WEEKS = 5  # Minervini's floor for a valid base
BASE_MAX_DEPTH_PCT = 35.0  # high-to-low depth beyond this reads as a downtrend, not a base

VCP_MIN_CONTRACTIONS = 2  # Minervini's floor for calling a sequence a VCP (typically 2-4)
VCP_TIGHTENING_TOLERANCE_PCT = 2.0  # a contraction may exceed the previous by up to this many
                                     # percentage points and still count as "tightening" — real
                                     # price data rarely decreases strictly monotonically