import logging
from pathlib import Path

import cv2
import numpy as np
from myutils.ocr.google import google_vision_ocr
from tesserocr import PSM, PyTessBaseAPI

THIS_DIR = Path(__file__).parent
tessdata = str(THIS_DIR.parents[2] / "host/tessdata")
tessdataosd = str(THIS_DIR.parents[2] / "host/tessdata/osd")
IMG_COLOR = 3

OCR_THRESHOLD = 86


class OCR(PyTessBaseAPI):
    def __init__(self, path: str, psm: PSM = PSM.AUTO) -> None:
        super().__init__()
        self.psm = psm
        self.path = path

    def SetCVImage(self, image: cv2.typing.MatLike) -> None:  # noqa: N802
        bytes_per_pixel = image.shape[2] if len(image.shape) == IMG_COLOR else 1
        height, width = image.shape[:2]
        bytes_per_line = bytes_per_pixel * width

        self.SetImageBytes(image.tobytes(), width, height, bytes_per_pixel, bytes_per_line)  # type: ignore

    def get_text(self, img: cv2.typing.MatLike) -> str:
        self.SetCVImage(img)
        ocr_text = self.GetUTF8Text().strip()
        confidences = self.AllWordConfidences()
        logging.info("ocr_text: %s", ocr_text)
        logging.info("confidences: %s", confidences)

        if not confidences:
            return google_vision_ocr(img) if ocr_text == "" else ocr_text

        if all(x >= OCR_THRESHOLD for x in confidences) and ocr_text != "":
            if "6" in ocr_text:
                google_ocr = google_vision_ocr(img)
                logging.info("google ocr because of '6': %s", google_ocr)
                if ocr_text != google_ocr:
                    fixed_ocr = ""
                    for i, char in enumerate(ocr_text):
                        if char == "6" and google_ocr[i] == "4":
                            fixed_ocr += "4"
                            continue
                        fixed_ocr += char
                    logging.info("fixed ocr: %s", fixed_ocr)
                    ocr_text = fixed_ocr
        else:
            ocr_text = google_vision_ocr(img)
            logging.info("ocr_text_google_vision: %s", ocr_text)
        return ocr_text

    def get_text_without_google(self, img: np.ndarray) -> str:
        self.SetCVImage(img)
        return self.GetUTF8Text().strip()
