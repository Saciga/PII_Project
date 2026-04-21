from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import fitz
import numpy as np


@dataclass
class PreprocessedImage:
    image: np.ndarray
    debug_steps: list[str]


def load_image(path: Path) -> np.ndarray:
    image = cv2.imread(str(path))
    if image is None:
        raise ValueError("Unable to load image for OCR processing")
    return image


def convert_pdf_to_image(path: Path, page_index: int = 0) -> np.ndarray:
    """Extracts a page from a PDF and returns it as a BGR numpy array."""
    doc = fitz.open(str(path))
    if page_index >= len(doc):
        raise ValueError(f"PDF page index {page_index} out of range (total pages: {len(doc)})")

    page = doc[page_index]
    # DPI 300 for high quality OCR: 300 / 72 = 4.166...
    zoom = 300 / 72
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)

    # Convert pixmap to numpy array
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)

    # Convert RGB/RGBA to BGR
    if pix.n == 4:
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
    elif pix.n == 3:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    elif pix.n == 1:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    return img


def preprocess_image(path: Path) -> PreprocessedImage:
    debug_steps: list[str] = []
    if path.suffix.lower() == ".pdf":
        image = convert_pdf_to_image(path)
        debug_steps.append("pdf-to-image")
    else:
        image = load_image(path)

    resized = resize_for_ocr(image)
    debug_steps.append("resized")

    deskewed = correct_rotation(resized)
    debug_steps.append("deskewed")

    enhanced = enhance_contrast(deskewed)
    debug_steps.append("contrast-enhanced")

    denoised = cv2.fastNlMeansDenoisingColored(enhanced, None, 7, 7, 7, 21)
    debug_steps.append("denoised")

    return PreprocessedImage(image=denoised, debug_steps=debug_steps)


def resize_for_ocr(image: np.ndarray, min_width: int = 1200) -> np.ndarray:
    height, width = image.shape[:2]
    if width >= min_width:
        return image
    scale = min_width / width
    return cv2.resize(image, (int(width * scale), int(height * scale)), interpolation=cv2.INTER_CUBIC)


def correct_rotation(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)
    coords = np.column_stack(np.where(gray > 0))
    if coords.size == 0:
        return image

    angle = cv2.minAreaRect(coords)[-1]
    angle = -(90 + angle) if angle < -45 else -angle
    if abs(angle) < 0.5:
        return image

    height, width = image.shape[:2]
    center = (width // 2, height // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(
        image,
        matrix,
        (width, height),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE,
    )


def enhance_contrast(image: np.ndarray) -> np.ndarray:
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l_channel)
    merged = cv2.merge((cl, a_channel, b_channel))
    return cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
