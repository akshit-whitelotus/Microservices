import pytest



@pytest.mark.asyncio
async def test_get_current_user(client):


    await client.post(
        "/api/v1/auth/register",
        json={
            "username":"meuser",
            "email":"me@test.com",
            "password":"password123",
        },
    )


    login=await client.post(
        "/api/v1/auth/login",
        data={
            "username":"meuser",
            "password":"password123",
        },
    )


    token=login.json()["access_token"]


    response=await client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization":
            f"Bearer {token}"
        },
    )


    assert response.status_code==200


    assert response.json()["username"]=="meuser"