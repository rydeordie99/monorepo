from collections.abc import Sequence
from pathlib import Path

import cv2
import numpy as np
import pypdfium2


def pdf_to_images(pdf_path: Path) -> list[np.ndarray]:
    pdf_images = []
    pdf = pypdfium2.PdfDocument(pdf_path)
    for i in range(len(pdf)):
        page = pdf[i]
        img_cv = page.render(scale=4, grayscale=True).to_numpy()
        pdf_images.append(img_cv)
    return pdf_images


def threshold_image(img: cv2.typing.MatLike) -> np.ndarray:
    return cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]


def remove_horizontal_lines(img: cv2.typing.MatLike) -> np.ndarray:
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 10))
    return cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)


def horizontal_blur(img: cv2.typing.MatLike) -> np.ndarray:
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 12))
    return cv2.dilate(img, kernel, iterations=3)


def return_contours(img: cv2.typing.MatLike) -> Sequence[cv2.typing.MatLike]:
    return cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]


def get_contours(img: np.ndarray) -> Sequence[cv2.typing.MatLike]:
    img = threshold_image(img)
    img = remove_horizontal_lines(img)
    img = horizontal_blur(img)

    return return_contours(img)
