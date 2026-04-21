# Fine-Tuning Path

The current backend uses open-source OCR plus document-specific parsing rules. If you want to move toward a fine-tuned document understanding model, use this path:

1. Generate synthetic identity document images with layout variants for Aadhaar, PAN, and driving license templates.
2. Store paired annotations in a LayoutLM-style token classification format or Donut-style JSON targets.
3. Fine-tune a document model to predict normalized JSON fields.
4. Compare model output with the current rule-based extractor and use the higher-confidence result.

## Recommended open-source options

- LayoutLMv3 for token classification on OCR text + boxes
- Donut for OCR-free document parsing if training data quality is high
- PaddleOCR-VL-style pipelines when multilingual expansion is needed later

## Suggested labels

- `name`
- `date_of_birth`
- `gender`
- `aadhaar_number`
- `pan_number`
- `license_number`
- `father_name`
- `valid_till`

## Hybrid production strategy

- Keep OCR preprocessing and validation regardless of model choice.
- Use the fine-tuned model for field detection.
- Run regex validators as a final safety layer before persistence.
