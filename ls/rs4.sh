#!/bin/bash
cd "$(dirname "$0")"
export THEME=yunus
N=$(python3 -c "import sys;sys.path.insert(0,'.');import base;print(int(base.DUR*50))")
D=$(python3 -c "import sys;sys.path.insert(0,'.');import base;print(round(base.DUR,2))")
H=$((N/2))
FPS=50 python3 lr.py s2d video 0 $H seg_d_a.mp4 > /tmp/d_a.log 2>&1 &
FPS=50 python3 lr.py s2d video $H $N seg_d_b.mp4 > /tmp/d_b.log 2>&1 &
wait
printf "file 'seg_d_a.mp4'\nfile 'seg_d_b.mp4'\n" > ld.txt
ffmpeg -v error -y -f concat -safe 0 -i ld.txt -i yunus.mp3 -filter_complex "[1:a]apad,loudnorm=I=-15:TP=-1.5:LRA=11[a]" \
  -map 0:v -map "[a]" -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p -r 50 \
  -c:a aac -b:a 192k -t $D -movflags +faststart "/mnt/user-data/outputs/Yunus_Stilmuster_50fps.mp4"
echo DONE >> /tmp/d.log
