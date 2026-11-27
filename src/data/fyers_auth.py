from fyers_apiv3 import fyersModel

from src.config.settings import (
    FYERS_CLIENT_ID,
    FYERS_SECRET_KEY,
    FYERS_REDIRECT_URI,
)


def generate_auth_url():
    session = fyersModel.SessionModel(
        client_id=FYERS_CLIENT_ID,
        secret_key=FYERS_SECRET_KEY,
        redirect_uri=FYERS_REDIRECT_URI,
        response_type="code",
        grant_type="authorization_code",
    )
    return session.generate_authcode()


def generate_access_token(auth_code):
    session = fyersModel.SessionModel(
        client_id=FYERS_CLIENT_ID,
        secret_key=FYERS_SECRET_KEY,
        redirect_uri=FYERS_REDIRECT_URI,
        response_type="code",
        grant_type="authorization_code",
    )

    session.set_token(auth_code)

    return session.generate_token()