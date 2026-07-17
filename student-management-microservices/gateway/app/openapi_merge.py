from copy import deepcopy
import time
import httpx


_cache = {
    "timestamp": 0,
    "spec": None,
}



async def fetch_spec(
    url: str,
) -> dict:


    async with httpx.AsyncClient(
        timeout=5
    ) as client:

        response = await client.get(url)

        response.raise_for_status()

        return response.json()



def rename_refs(
    obj: dict | list,
    mapping: dict[str, str],
) -> None:


    if isinstance(obj, dict):

        for key, value in obj.items():

            if key == "$ref":

                for old, new in mapping.items():

                    obj[key] = value.replace(
                        old,
                        new,
                    )

            else:

                rename_refs(
                    value,
                    mapping,
                )


    elif isinstance(obj, list):

        for item in obj:

            rename_refs(
                item,
                mapping,
            )



async def merged_openapi(
    auth_url: str,
    student_url: str,
    document_url: str,
):


    now = time.time()


    if (
        _cache["spec"]
        and now - _cache["timestamp"] < 60
    ):

        return _cache["spec"]



    auth = await fetch_spec(
        f"{auth_url}/openapi.json"
    )


    student = await fetch_spec(
        f"{student_url}/openapi.json"
    )


    document = await fetch_spec(
        f"{document_url}/openapi.json"
    )


    # ---------------------------------
    # Start valid OpenAPI document
    # ---------------------------------

    merged = {

        "openapi": "3.1.0",

        "info": {

            "title":
            "Unified Gateway API",

            "version":
            "1.0.0",

        },

        "paths": {},

        "components": {

            "schemas": {}

        }

    }


    # ---------------------------------
    # Merge paths
    # ---------------------------------

    merged["paths"].update(
        auth.get(
            "paths",
            {},
        )
    )


    merged["paths"].update(
        student.get(
            "paths",
            {},
        )
    )


    merged["paths"].update(
        document.get(
            "paths",
            {},
        )
    )


    # ---------------------------------
    # Merge schemas
    # ---------------------------------

    schemas = (
        merged["components"]["schemas"]
    )


    for spec in [
        auth,
        student,
        document,
    ]:


        for name, schema in (
            spec
            .get(
                "components",
                {}
            )
            .get(
                "schemas",
                {}
            )
            .items()
        ):


            new_name = name


            if new_name in schemas:

                new_name = (
                    f"Gateway_{name}"
                )


            schemas[new_name] = schema



    _cache["spec"] = merged

    _cache["timestamp"] = now


    return merged