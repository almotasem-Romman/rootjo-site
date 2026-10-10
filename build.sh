#!/usr/bin/env bash
# Usage: ./build.sh [output.mp4]   (run inside the kit folder)
# Optional: PREVIEW="1.3 4.8 7.4 8.4 12.2 13.3 16.6 18.2 19.5" ./build.sh  -> only renders check frames into prev/
set -euo pipefail
cd "$(dirname "$0")"
OUT="${1:-root-promo.mp4}"
if [ -n "${PREVIEW:-}" ]; then
  rm -rf prev && node render.mjs preview prev $PREVIEW
  python3 -I -c "
from PIL import Image;import glob
fs=sorted(glob.glob('prev/*.jpg'));W=360;H=640;c=5;r=(len(fs)+c-1)//c
sh=Image.new('RGB',(W*c,H*r),'black')
for i,f in enumerate(fs):sh.paste(Image.open(f).resize((W,H)),((i%c)*W,(i//c)*H))
sh.save('prev_sheet.jpg',quality=90)"
  echo "preview -> prev_sheet.jpg"; exit 0
fi
rm -rf frames && node render.mjs full frames
python3 -I audio.py audio.wav
ffmpeg -v error -y -framerate 30 -i frames/f%04d.jpg -i audio.wav -c:v libx264 -preset slow -crf 17 \
  -pix_fmt yuv420p -profile:v high -c:a aac -b:a 192k -shortest -movflags +faststart "$OUT"
ffmpeg -v error -y -i "$OUT" -vf "fps=1,scale=180:-1,tile=10x2" -frames:v 1 final_sheet.jpg
echo "done -> $OUT (check final_sheet.jpg)"
