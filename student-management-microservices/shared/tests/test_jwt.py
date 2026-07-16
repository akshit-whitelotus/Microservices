import pytest

from jose import JWTError

from shared.auth.jwt import (
    create_access_token,
    decode_access_token,
)



def test_create_token(
    jwt_secret,
    jwt_algorithm,
    jwt_issuer,
    jwt_audience,
):

    token = create_access_token(
        subject="123",
        secret_key=jwt_secret,
        algorithm=jwt_algorithm,
        expires_minutes=30,
        issuer=jwt_issuer,
        audience=jwt_audience,
    )


    assert token is not None

    assert isinstance(
        token,
        str,
    )



def test_decode_token_success(
    jwt_secret,
    jwt_algorithm,
    jwt_issuer,
    jwt_audience,
):

    token = create_access_token(
        subject="123",
        secret_key=jwt_secret,
        algorithm=jwt_algorithm,
        expires_minutes=30,
        issuer=jwt_issuer,
        audience=jwt_audience,
    )


    payload = decode_access_token(
        token=token,
        secret_key=jwt_secret,
        algorithm=jwt_algorithm,
        issuer=jwt_issuer,
        audience=jwt_audience,
    )


    assert payload["sub"] == "123"

    assert payload["iss"] == jwt_issuer

    assert payload["aud"] == jwt_audience

    assert "iat" in payload

    assert "exp" in payload



def test_invalid_secret(
    jwt_secret,
    jwt_algorithm,
    jwt_issuer,
    jwt_audience,
):

    token = create_access_token(
        subject="123",
        secret_key=jwt_secret,
        algorithm=jwt_algorithm,
        expires_minutes=30,
        issuer=jwt_issuer,
        audience=jwt_audience,
    )


    with pytest.raises(JWTError):

        decode_access_token(
            token=token,
            secret_key="wrong-secret",
            algorithm=jwt_algorithm,
            issuer=jwt_issuer,
            audience=jwt_audience,
        )



def test_invalid_issuer(
    jwt_secret,
    jwt_algorithm,
    jwt_issuer,
    jwt_audience,
):

    token = create_access_token(
        subject="123",
        secret_key=jwt_secret,
        algorithm=jwt_algorithm,
        expires_minutes=30,
        issuer=jwt_issuer,
        audience=jwt_audience,
    )


    with pytest.raises(JWTError):

        decode_access_token(
            token=token,
            secret_key=jwt_secret,
            algorithm=jwt_algorithm,
            issuer="wrong-service",
            audience=jwt_audience,
        )



def test_invalid_audience(
    jwt_secret,
    jwt_algorithm,
    jwt_issuer,
    jwt_audience,
):

    token = create_access_token(
        subject="123",
        secret_key=jwt_secret,
        algorithm=jwt_algorithm,
        expires_minutes=30,
        issuer=jwt_issuer,
        audience=jwt_audience,
    )


    with pytest.raises(JWTError):

        decode_access_token(
            token=token,
            secret_key=jwt_secret,
            algorithm=jwt_algorithm,
            issuer=jwt_issuer,
            audience="wrong-audience",
        )



def test_expired_token(
    jwt_secret,
    jwt_algorithm,
    jwt_issuer,
    jwt_audience,
):

    token = create_access_token(
        subject="123",
        secret_key=jwt_secret,
        algorithm=jwt_algorithm,
        expires_minutes=-1,
        issuer=jwt_issuer,
        audience=jwt_audience,
    )


    with pytest.raises(JWTError):

        decode_access_token(
            token=token,
            secret_key=jwt_secret,
            algorithm=jwt_algorithm,
            issuer=jwt_issuer,
            audience=jwt_audience,
        )