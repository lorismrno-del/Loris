#!/bin/bash
# rv.sh <module> <Title>   renders 2 halves in parallel, muxes with <name>.mp3 into $OUT/<Title>.mp4
cd "$(dirname "$0")"
OUT=${OUT:-/mnt/user-data/outputs}
n=$1; title=$2
N=$(python3 -c "import $n;print(int($n.DUR*30))"); D=$(python3 -c "import $n;print(round($n.DUR,2))")
python3 render.py $n video 0 $((N/2)) seg_${n}_a.mp4 > log_$n.txt 2>&1 &
python3 render.py $n video $((N/2)) $N seg_${n}_b.mp4 >> log_$n.txt 2>&1 &
wait
mp3=${n#v_}.mp3
printf "file 'seg_${n}_a.mp4'\nfile 'seg_${n}_b.mp4'\n" > list_$n.txt
ffmpeg -v error -y -f concat -safe 0 -i list_$n.txt -i $mp3 -filter_complex "[1:a]apad,loudnorm=I=-15:TP=-1.5:LRA=11[a]" -map 0:v -map "[a]" -c:v libx264 -preset faster -crf 21 -maxrate 6M -bufsize 12M -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k -t $D -movflags +faststart "$OUT/$title.mp4"
echo DONE $title
