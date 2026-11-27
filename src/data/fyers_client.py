from fyers_apiv3 import fyersModel

from src.config.settings import (
    FYERS_CLIENT_ID,
    FYERS_ACCESS_TOKEN,
)

fyers = fyersModel.FyersModel(
    client_id=FYERS_CLIENT_ID,
    token=FYERS_ACCESS_TOKEN,
    is_async=False,
    log_path=""
)