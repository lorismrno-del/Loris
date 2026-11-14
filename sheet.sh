#!/bin/bash
# sheet.sh <video.mp4>   contact sheet (one frame every 2.5 s) -> test/k.png
cd "$(dirname "$0")"; mkdir -p test
ffprobe -v error -show_entries format=duration -of csv=p=0 "$1"
rm -f test/k_*.png; ffmpeg -v error -i "$1" -vf "fps=1/2.5,scale=150:266" test/k_%03d.png
python3 -c "
from PIL import Image; import glob
fs=sorted(glob.glob('test/k_*.png')); cols=13; rows=(len(fs)+cols-1)//cols
s=Image.new('RGB',(150*cols,266*rows))
for i,f in enumerate(fs): s.paste(Image.open(f),((i%cols)*150,(i//cols)*266))
s.save('test/k.png')"
