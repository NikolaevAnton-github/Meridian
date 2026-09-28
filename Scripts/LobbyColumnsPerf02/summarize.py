"""Summarize one shared physical CSV frame window; retain anomaly diagnostics."""
import csv
import hashlib
import json
import math
import statistics
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KEYS = ['FrameTime', 'GameThreadTime', 'RenderThreadTime', 'GPUTime',
        'RenderThreadTime_CriticalPath', 'Exclusive/RenderThread/EventWait/Shadows',
        'Exclusive/AllWorkers/ShadowInitDynamic']


def quantile(values, fraction):
    values = sorted(values)
    position = (len(values) - 1) * fraction
    lower = int(position)
    return values[lower] + (values[min(lower + 1, len(values) - 1)] - values[lower]) * (position - lower)


def ranges(lines):
    result = []
    for line in lines:
        if result and line == result[-1][1] + 1:
            result[-1][1] = line
        else:
            result.append([line, line])
    return result


def summarize(path):
    records = []
    with path.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.reader(stream)
        for row in reader:
            records.append((reader.line_num, row))
    header_indices = [i for i, (_, row) in enumerate(records) if row and row[0] == 'EVENTS']
    assert len(header_indices) >= 2, f'{path}: missing final header'
    first, last = header_indices[0], header_indices[-1]
    header = records[last][1]
    assert all(header[:len(records[i][1])] == records[i][1] for i in header_indices), f'{path}: header reordered'
    duplicates = {name: count for name, count in Counter(header).items() if count > 1}
    selected = [name for name in header if name in KEYS or name.startswith(('ProjectileBlockers/', 'LobbyColumns/'))]
    assert not any(name in duplicates for name in selected), f'{path}: ambiguous selected metric'
    assert all(name in selected for name in KEYS[:4]), f'{path}: required metric absent'

    # Exclude headers/footer before conversion or trimming. Preserve body rows
    # even if one timing cell is invalid; all metrics share the same window.
    frames = [(line, row) for i, (line, row) in enumerate(records)
              if first < i < last and i not in header_indices and row]
    assert len(frames) > 10, f'{path}: insufficient physical frames'
    assert all(len(row) <= len(header) and not row[0].startswith('[HasHeaderRowAtEnd]')
               for _, row in frames), f'{path}: invalid body structure'
    window = frames[5:-5]
    result = {}
    diagnostics = dict(
        source_path=path.relative_to(ROOT).as_posix(),
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        first_header_csv_line=records[first][0], final_header_csv_line=records[last][0],
        first_header_is_final_header_prefix=True, duplicate_header_names=duplicates,
        body_frame_count=len(frames), retained_frame_count=len(window),
        retained_csv_line_range=[window[0][0], window[-1][0]],
        data_field_count_distribution=dict(Counter(len(row) for _, row in frames)),
        metrics={})
    for name in selected:
        index = header.index(name)
        values, invalid, near_zero, negative = [], [], [], []
        for line, row in window:
            try:
                value = float(row[index])
                if not math.isfinite(value):
                    raise ValueError('nonfinite')
            except (IndexError, ValueError):
                invalid.append(line)
                continue
            values.append(value)
            if value < 0:
                negative.append(line)
            if name.startswith('RenderThreadTime') and 0 <= value < .01:
                near_zero.append(line)
        diagnostics['metrics'][name] = dict(
            invalid_count=len(invalid), invalid_csv_line_ranges=ranges(invalid),
            negative_count=len(negative), negative_csv_line_ranges=ranges(negative),
            near_zero_count=len(near_zero), near_zero_csv_line_ranges=ranges(near_zero))
        if values:
            # Include finite near-zero/negative samples. The handoff rejects
            # final captures with anomalies or invalid required metrics.
            result[name] = dict(n=len(values), window_n=len(window), mean=statistics.mean(values),
                                median=statistics.median(values), p95=quantile(values, .95),
                                p99=quantile(values, .99), minimum=min(values), maximum=max(values))
    result['_integrity'] = diagnostics
    return result


def main():
    prefix = sys.argv[1]
    paths = sorted((ROOT / 'Saved/Profiling/CSV').glob('LobbyColumnsPerf02-' + prefix + '*.csv'))
    assert paths, f'No captures for {prefix}'
    output = {path.stem: summarize(path) for path in paths}
    destination = ROOT / 'Saved/LobbyColumnsPerf02' / ('summary-' + prefix + '-aligned.json')
    destination.write_text(json.dumps(output, indent=2), encoding='utf-8')
    print(json.dumps({name: dict(frames=result['_integrity']['retained_frame_count'],
                               medians={key: round(result[key]['median'], 3) for key in KEYS[:4]},
                               rt_anomalies=result['_integrity']['metrics']['RenderThreadTime'])
                      for name, result in output.items()}, indent=2))


if __name__ == '__main__':
    main()
