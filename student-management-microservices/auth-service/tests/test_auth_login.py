import pytest



@pytest.mark.asyncio
async def test_login_success(client):


    await client.post(
        "/api/v1/auth/register",
        json={
            "username":"loginuser",
            "email":"login@test.com",
            "password":"password123",
        },
    )


    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username":"loginuser",
            "password":"password123",
        },
    )


    assert response.status_code == 200


    data=response.json()


    assert "access_token" in data

    assert data["token_type"]=="bearer"



@pytest.mark.asyncio
async def test_invalid_login(client):


    response=await client.post(
        "/api/v1/auth/login",
        data={
            "username":"unknown",
            "password":"wrong",
        },
    )


    assert response.status_code==401