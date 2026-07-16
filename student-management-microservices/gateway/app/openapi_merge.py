import copy,time,httpx

_cache={
    "timestamp":0,
    "spec":None
}
async def fetch_spec(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()

def rename_refs(obj,mapping):
    if isinstance(obj,dict):
        for key , value in obj.items():
            if key == "$ref":
                for old,new in mapping.items():
                    obj[key]=value.replace(old,new)
            else:
                rename_refs(value,mapping)
    elif isinstance(obj,list):
        for item in obj:
            rename_refs(item,mapping)

async def merged_openapi(auth_url,student_url):
    now=time.time()
    if (_cache["spec"] and now - _cache["timestamp"]<60):
        return _cache["spec"]
    auth=await fetch_spec(f"{auth_url}/openapi.json")
    student=await fetch_spec(f"{student_url}/openapi.json")
    merged=copy.deepcopy(auth)
    merged["paths"].update(
        student.get("paths",{})
    )
    schemas=merged.setdefault("components",{}).setdefault("schemas",{})
    ref_mapping={}

    for name ,schema in student.get("components",{}).get("schemas",{}).items():
        new_name=name
        if new_name in schemas:
            new_name=(f"StudentService_{name}")
        ref_mapping[f"#/components/schemas/{name}"]=(f"#/components/schemas/{new_name}")
        schemas[new_name]=schema
    rename_refs(merged,ref_mapping)

    _cache["spec"]=merged
    _cache["timestamp"]=now

    return merged

