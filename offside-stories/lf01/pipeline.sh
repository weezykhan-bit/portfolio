#!/bin/bash
cd /home/user/offside-stories/lf01
sleep 1800
for round in 1 2 3 4; do
  find assets/photos/raw -size 0 -delete
  python3 -u treat.py >> photos.log 2>&1
  n=$(ls assets/photos/*.jpg | wc -l)
  echo "round $round photos $n"
  [ "$n" -ge 9 ] && break
  sleep 1800
done
n=$(ls assets/photos/*.jpg | wc -l)
if [ "$n" -lt 9 ]; then echo "PHOTOS_INCOMPLETE $n"; exit 2; fi
python3 build.py && node /home/user/portfolio/.claude/skills/hyperframes/scripts/plugin-cli.mjs render -o offside-stories-lf01-leicester.mp4 > render.log 2>&1
echo "RENDER_EXIT $?"; ls -la offside-stories-lf01-leicester.mp4
