#!/bin/bash
cd "$(dirname "$0")"
export THEME=$1
N=$(python3 -c "import sys;sys.path.insert(0,'.');import base;print(int(base.DUR*30))")
D=$(python3 -c "import sys;sys.path.insert(0,'.');import base;print(round(base.DUR,2))")
H=$((N/2))
FPS=30 python3 lr.py s2c video 0 $H seg_c_a.mp4 > /tmp/c_a.log 2>&1 &
FPS=30 python3 lr.py s2c video $H $N seg_c_b.mp4 > /tmp/c_b.log 2>&1 &
wait
printf "file 'seg_c_a.mp4'\nfile 'seg_c_b.mp4'\n" > lc.txt
ffmpeg -v error -y -f concat -safe 0 -i lc.txt -i yunus.mp3 -filter_complex "[1:a]apad,loudnorm=I=-15:TP=-1.5:LRA=11[a]" \
  -map 0:v -map "[a]" -c:v libx264 -preset veryfast -crf 21 -pix_fmt yuv420p -r 30 \
  -c:a aac -b:a 160k -t $D -movflags +faststart "/mnt/user-data/outputs/Stil2_Braun_Islamisch_$2.mp4"
echo DONE >> /tmp/s2c.log
