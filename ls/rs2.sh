#!/bin/bash
cd "$(dirname "$0")"
export PAL=$1 PALNAME=$2
N=$(python3 -c "import sys;sys.path.insert(0,'.');import base;print(int(base.DUR*30))")
D=$(python3 -c "import sys;sys.path.insert(0,'.');import base;print(round(base.DUR,2))")
FPS=30 python3 lr.py s2b video 0 $N seg_s2b_$1.mp4 > /tmp/r2_$1.log 2>&1
ffmpeg -v error -y -i seg_s2b_$1.mp4 -i yunus.mp3 -filter_complex "[1:a]apad,loudnorm=I=-15:TP=-1.5:LRA=11[a]" \
  -map 0:v -map "[a]" -c:v libx264 -preset veryfast -crf 22 -pix_fmt yuv420p -r 30 \
  -c:a aac -b:a 160k -t $D -movflags +faststart "/mnt/user-data/outputs/Stil2_$2.mp4"
echo DONE $2 >> /tmp/s2b.log
