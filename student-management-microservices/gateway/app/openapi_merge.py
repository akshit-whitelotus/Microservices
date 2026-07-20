from __future__ import annotations

import logging
import time
from copy import deepcopy

import httpx

logger = logging.getLogger(__name__)

CACHE_TTL = 60

_cache = {
    "timestamp": 0.0,
    "spec": None,
}


async def fetch_spec(url: str) -> dict | None:
    """
    Fetch OpenAPI specification from a microservice.

    Returns None if the service is unavailable.
    """

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()

    except Exception as exc:
        logger.warning("Unable to fetch OpenAPI from %s : %s", url, exc)
        return None


def rename_refs(obj, mapping):
    """
    Rename $ref schema names recursively.
    """

    if isinstance(obj, dict):

        for key, value in obj.items():

            if key == "$ref":

                for old, new in mapping.items():
                    obj[key] = value.replace(old, new)

            else:
                rename_refs(value, mapping)

    elif isinstance(obj, list):

        for item in obj:
            rename_refs(item, mapping)


async def merged_openapi(
    auth_url: str,
    student_url: str,
    document_url: str,
    ai_service_url: str,
):

    now = time.time()

    if (
        _cache["spec"] is not None
        and now - _cache["timestamp"] < CACHE_TTL
    ):
        return _cache["spec"]

    services = [
        ("auth", auth_url),
        ("student", student_url),
        ("document", document_url),
        ("ai", ai_service_url),
    ]

    merged = {
        "openapi": "3.1.0",
        "info": {
            "title": "Unified Gateway API",
            "version": "1.0.0",
        },
        "paths": {},
        "components": {
            "schemas": {}
        },
    }

    schemas = merged["components"]["schemas"]

    for service_name, service_url in services:

        spec = await fetch_spec(f"{service_url}/openapi.json")

        if spec is None:
            logger.warning("%s service unavailable.", service_name)
            continue

        #
        # Merge Paths
        #
        merged["paths"].update(
            deepcopy(
                spec.get("paths", {})
            )
        )

        #
        # Merge Schemas
        #
        spec_schemas = (
            spec.get("components", {})
            .get("schemas", {})
        )

        rename_map = {}

        for schema_name in spec_schemas.keys():

            if schema_name in schemas:

                new_name = f"{service_name}_{schema_name}"

                rename_map[
                    f"#/components/schemas/{schema_name}"
                ] = (
                    f"#/components/schemas/{new_name}"
                )

        copied = deepcopy(spec_schemas)

        if rename_map:

            rename_refs(copied, rename_map)

        for schema_name, schema in copied.items():

            final_name = schema_name

            if schema_name in schemas:
                final_name = f"{service_name}_{schema_name}"

            schemas[final_name] = schema

    _cache["spec"] = merged
    _cache["timestamp"] = now

    return merged