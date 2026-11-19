#!/bin/bash
cd "$(dirname "$0")"
OUT=${OUT:-/mnt/user-data/outputs}
n=$1; title=$2; part=$3
N=$(python3 -c "import $n;print(int($n.DUR*50))")
if [ "$part" = "a" ]; then
  FPS50=1 python3 render.py $n video 0 $((N/2)) seg_${n}_a.mp4 2>&1 | tail -1
elif [ "$part" = "b" ]; then
  FPS50=1 python3 render.py $n video $((N/2)) $N seg_${n}_b.mp4 2>&1 | tail -1
else
  D=$(python3 -c "import $n;print(round($n.DUR,2))")
  mp3=${n#v_}.mp3
  printf "file 'seg_${n}_a.mp4'\nfile 'seg_${n}_b.mp4'\n" > list_$n.txt
  ffmpeg -v error -y -f concat -safe 0 -i list_$n.txt -i $mp3 -filter_complex "[1:a]apad,loudnorm=I=-15:TP=-1.5:LRA=11[a]" -map 0:v -map "[a]" -c:v libx264 -preset slow -crf 19 -maxrate 10M -bufsize 20M -pix_fmt yuv420p -r 50 -c:a aac -b:a 192k -t $D -movflags +faststart "$OUT/$title.mp4"
  echo DONE $title
fi
