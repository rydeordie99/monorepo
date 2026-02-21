import os
from base64 import b64encode

import cv2
import httpx
import numpy as np


def google_vision_ocr(img: np.ndarray) -> str:
    img_str = b64encode(cv2.imencode(".png", img)[1].tobytes()).decode()
    img_list = [
        {"image": {"content": img_str}, "features": [{"type": "TEXT_DETECTION", "maxResults": 1}]}
    ]

    data = {"requests": img_list}
    params = {"key": os.environ.get("GOOGLE_VISION_API_KEY")}
    headers = {"referer": "hstia.com"}

    r = httpx.post(
        "https://vision.googleapis.com/v1/images:annotate",
        json=data,
        params=params,
        headers=headers,
    ).json()

    try:
        return r["responses"][0]["fullTextAnnotation"]["text"].strip()
    except KeyError:
        return ""
