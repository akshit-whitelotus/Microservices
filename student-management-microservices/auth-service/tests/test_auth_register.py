import pytest



@pytest.mark.asyncio
async def test_register_success(client):

    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username":"john",
            "email":"john@test.com",
            "password":"password123",
        },
    )


    assert response.status_code == 201


    data=response.json()


    assert data["username"]=="john"

    assert data["email"]=="john@test.com"



@pytest.mark.asyncio
async def test_duplicate_email(client):


    payload={
        "username":"john",
        "email":"duplicate@test.com",
        "password":"password123",
    }


    await client.post(
        "/api/v1/auth/register",
        json=payload,
    )


    response=await client.post(
        "/api/v1/auth/register",
        json=payload,
    )


    assert response.status_code==400