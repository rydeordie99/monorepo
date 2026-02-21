import contextlib
import re

import httpx

RE_URL = re.compile(r"\[([^\[]+)]\(([^)]+)\)")
RE_BOLD = re.compile(r"\*\*(.*?)\*\*")


def get_key_by_path(dict_obj: dict, path_string: str) -> str:
    path_list = path_string.split("/")[1:]
    obj_ptr = dict_obj
    for elem in path_list:
        with contextlib.suppress(ValueError):
            elem = int(elem)
        obj_ptr = obj_ptr[elem]
    return str(obj_ptr)


def docker_version_check(docker_url: str, version: str) -> bool:
    if docker_url.startswith("linuxserver"):
        version = version.replace("v", "version-")

    r_docker_auth = httpx.get(
        f"https://auth.docker.io/token?service=registry.docker.io&scope=repository:{docker_url}:pull"
    ).json()
    headers = {"Authorization": "Bearer " + r_docker_auth["access_token"]}
    httpx.get(f"https://index.docker.io/v2/{docker_url}/manifests/{version}", headers=headers)
    return True
