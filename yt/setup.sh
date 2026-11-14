#!/bin/bash
pip install --break-system-packages -q pycairo pillow opencv-python-headless numpy rembg onnxruntime 2>&1 | tail -1
