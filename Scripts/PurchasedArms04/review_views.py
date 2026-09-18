"""Extract timestamped contact sheets from the actual first-person video takes."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Saved/PurchasedArms04/Worker'
sys.path.insert(0, str(OUT / 'PythonPackages'))
import av
from PIL import Image, ImageDraw


def main():
    result = []
    for path in sorted((OUT / 'Video').glob('Views01-*.mp4')):
        stamps = [.9, 1.15, 1.4, 1.65, 1.9, 2.15, 2.4, 2.9]
        if 'Released' in path.stem:
            stamps += [3.15, 3.4, 3.7, 4.0]
        frames = []
        with av.open(str(path)) as video:
            for frame in video.decode(video=0):
                frames.append((float(frame.time), frame.to_image()))
        width, height = 640, 455
        sheet = Image.new('RGB', (width * 2, height * ((len(stamps) + 1) // 2)), '#171717')
        draw = ImageDraw.Draw(sheet)
        chosen = []
        for index, stamp in enumerate(stamps):
            actual, view = min(frames, key=lambda item: abs(item[0] - stamp))
            view.thumbnail((width, height - 24))
            x, y = (index % 2) * width, (index // 2) * height
            sheet.paste(view, (x, y + 24))
            draw.text((x + 10, y + 5), f'{path.stem} | video {actual:.3f} s', fill='white')
            chosen.append(actual)
        target = path.with_name(path.stem + '-sequence.jpg')
        assert not target.exists()
        sheet.save(target, quality=92)
        result.append({'video': path.name, 'frames': len(frames), 'selected_video_seconds': chosen,
                       'sheet': target.name, 'sampling': 'Nearest decoded real-time PTS; no simulation pause.'})
    (OUT / 'Video/view-sequences.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result))


if __name__ == '__main__':
    main()
