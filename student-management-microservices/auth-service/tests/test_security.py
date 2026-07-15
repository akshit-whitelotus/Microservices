from app.core.security import (
    get_password_hash,
    verify_password,
)



def test_password_hash():

    password = "password123"


    hashed = get_password_hash(
        password
    )


    assert hashed != password


    assert verify_password(
        password,
        hashed,
    )



def test_wrong_password():

    hashed = get_password_hash(
        "password123"
    )


    assert not verify_password(
        "wrong",
        hashed,
    )