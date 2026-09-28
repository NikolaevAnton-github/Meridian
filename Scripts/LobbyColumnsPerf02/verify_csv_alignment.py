"""Check corrected CSV summaries against the controller's independent audit."""
import json
import math
from collections import defaultdict
from summarize import ROOT, summarize

out = ROOT / 'Saved/LobbyColumnsPerf02'
reference = json.loads((out / 'csv-integrity-aligned-summary.json').read_text(encoding='utf-8'))
groups = defaultdict(dict)
checks = []
for name, expected in reference['captures'].items():
    actual = summarize(ROOT / expected['source_path'])
    integrity = actual['_integrity']
    assert integrity['sha256'] == expected['sha256']
    assert integrity['retained_frame_count'] == expected['retained_frame_count']
    assert integrity['metrics']['RenderThreadTime']['near_zero_count'] == expected['rt_near_zero_count']
    for metric, values in expected['summaries_ms']['all'].items():
        if metric not in actual:
            continue
        for stat in ['n', 'mean', 'median', 'p95', 'p99']:
            assert math.isclose(actual[metric][stat], values[stat], rel_tol=1e-12, abs_tol=1e-12), (name, metric, stat)
    prefix = name.removeprefix('LobbyColumnsPerf02-').rsplit('-', 1)[0]
    groups[prefix][name] = actual
    checks.append(dict(capture=name, frames=integrity['retained_frame_count'],
                       rt_near_zero_count=expected['rt_near_zero_count'], matches=True))
for prefix, captures in groups.items():
    (out / ('summary-' + prefix + '-aligned.json')).write_text(json.dumps(captures, indent=2), encoding='utf-8')
result = dict(all_match=True, compared_statistics=['n', 'mean', 'median', 'p95', 'p99'], captures=checks)
(out / 'csv-alignment-verification05.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(dict(all_match=True, captures=len(checks),
                     retained_frames=sum(check['frames'] for check in checks),
                     preserved_rt_anomalies=sum(check['rt_near_zero_count'] for check in checks))))
