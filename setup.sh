#!/bin/bash
# installs fonts and python deps for the engine
cd "$(dirname "$0")"
mkdir -p ~/.fonts && cp fonts/*.ttf ~/.fonts/ && fc-cache -f >/dev/null 2>&1
python3 -c "import cairo, numpy, scipy, PIL" 2>/dev/null || pip install --break-system-packages -q pycairo numpy scipy pillow
mkdir -p test
echo "engine ready"
