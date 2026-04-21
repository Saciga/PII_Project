from __future__ import annotations

from functools import lru_cache
from typing import Any

import cv2


class OCRUnavailableError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def get_ocr_engine() -> Any:
    try:
        from paddleocr import PaddleOCR  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise OCRUnavailableError(
            "PaddleOCR is not installed or could not be imported. Install backend requirements first."
        ) from exc

    return PaddleOCR(use_angle_cls=True, lang="en", show_log=False)


def run_ocr(image) -> list[dict[str, Any]]:
    engine = get_ocr_engine()
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = engine.ocr(rgb, cls=True)
    lines: list[dict[str, Any]] = []

    for page in results or []:
        for item in page or []:
            points, payload = item
            text, confidence = payload
            lines.append(
                {
                    "text": text.strip(),
                    "confidence": float(confidence),
                    "bbox": points,
                }
            )

    return [line for line in lines if line["text"]]
