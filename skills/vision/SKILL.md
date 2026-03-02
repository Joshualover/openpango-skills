---
name: vision
description: Computer vision and image analysis with OCR support
version: 1.0.0
dependencies: []
---

# Computer Vision Skill

Image analysis, OCR, and vision model integration.

## Features

- Image description via vision models
- OCR with Tesseract
- Base64 encoding for API integration
- Local and cloud vision model support

## Usage

```python
from image_analyzer import ImageAnalyzer

analyzer = ImageAnalyzer()

# Describe image
desc = analyzer.describe_image("photo.jpg")

# OCR text extraction
text = analyzer.ocr("document.png")
```
