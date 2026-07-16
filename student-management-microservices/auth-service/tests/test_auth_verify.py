import pytest



@pytest.mark.asyncio
async def test_verify_token(client):


    await client.post(
        "/api/v1/auth/register",
        json={
            "username":"verifyuser",
            "email":"verify@test.com",
            "password":"password123",
        },
    )


    login=await client.post(
        "/api/v1/auth/login",
        data={
            "username":"verifyuser",
            "password":"password123",
        },
    )


    token=login.json()["access_token"]


    response=await client.post(
        "/api/v1/auth/verify",
        headers={
            "Authorization":
            f"Bearer {token}"
        },
    )


    assert response.status_code==200


    body=response.json()


    assert body["iss"]=="auth-service"

    assert body["aud"]=="student-service"

    assert body["sub"]



@pytest.mark.asyncio
async def test_verify_invalid_token(client):


    response=await client.post(
        "/api/v1/auth/verify",
        headers={
            "Authorization":
            "Bearer invalid"
        },
    )


    assert response.status_code==401