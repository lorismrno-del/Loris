#!/bin/bash
# ./mux.sh <video_ohne_ton.mp4> <stimme.m4a/wav> <out.mp4>
# Haengt das einfach.dawah Intro (12 s, 30 fps, mit Ton) vorne an. Das Video selbst beginnt bei t=0 OHNE Intro.
set -e
YT=${YT_ROOT:-$HOME/yt_engine/yt}
ffmpeg -v error -y -i $YT/assets/intro.mp4 -i "$1" -i "$2" -filter_complex \
 "[0:v]scale=1920:1080,setsar=1,fps=30,format=yuv420p[v0];[1:v]fps=30,format=yuv420p[v1];[v0][v1]concat=n=2:v=1:a=0[v];\
  [0:a]aresample=44100,aformat=channel_layouts=stereo,apad=whole_dur=12,atrim=0:12[a0];\
  [2:a]aresample=44100,aformat=channel_layouts=stereo,loudnorm=I=-16:TP=-1.5[a1];[a0][a1]concat=n=2:v=0:a=1[a]" \
 -map "[v]" -map "[a]" -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k -movflags +faststart "$3"
ffprobe -v error -show_entries format=duration,size -of csv=p=0 "$3"
