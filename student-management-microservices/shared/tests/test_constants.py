from shared.auth.constants import (
    ACCESS_TOKEN_TYPE,
    JWT_SUBJECT,
    JWT_ISSUER,
    JWT_AUDIENCE,
    DEFAULT_PAGE,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    REQUEST_ID_HEADER,
    AUTHORIZATION_HEADER,
    API_V1_PREFIX,
)


def test_access_token_type():

    assert ACCESS_TOKEN_TYPE == "bearer"



def test_jwt_subject():

    assert JWT_SUBJECT == "sub"



def test_jwt_issuer():

    assert JWT_ISSUER == "auth-service"



def test_jwt_audience():

    assert JWT_AUDIENCE == "student-service"


def test_default_pagination():

    assert DEFAULT_PAGE == 1

    assert DEFAULT_PAGE_SIZE == 10

    assert MAX_PAGE_SIZE == 100



def test_headers():

    assert REQUEST_ID_HEADER == "X-Request-ID"

    assert AUTHORIZATION_HEADER == "Authorization"



def test_api_prefix():

    assert API_V1_PREFIX == "/api/v1"