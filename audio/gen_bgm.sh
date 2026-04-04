#!/bin/bash
FFMPEG=$1
OUT=$2

$FFMPEG -y -f lavfi -i "aevalsrc='
  0.2*sin(2*PI*392*t)+0.15*sin(2*PI*523*t)+0.1*sin(2*PI*659*t)+0.08*sin(2*PI*784*t):
  s=44100:d=30
'" -af "aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo,aecho=0.8:0.9:500|600:0.3|0.2,afade=t=in:st=0:d=3,afade=t=out:st=25:d=5,volume=0.35" -c:a libmp3lame -b:a 128k "$OUT" 2>&1 | tail -3
