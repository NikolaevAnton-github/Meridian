"""Automatic metadata-only native run measurements, reusing the benchmark parser."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
from context_budget import digest, encode, read_json, report

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('benchmark_usage', ROOT / 'Scripts/Benchmarks/OrchestrationAB/snapshot_controller_usage.py')
benchmark = importlib.util.module_from_spec(spec)
spec.loader.exec_module(benchmark)
COMPATIBLE = ('native_version', 'model', 'effort', 'service_tier', 'session_kind', 'profile_sha256', 'effective_config_sha256', 'mcp_sha256', 'launch_args_sha256', 'brief_sha256', 'checkpoint_sha256', 'workload', 'measurement_schema')


def collect(home, thread_id, since, binding):
    candidates = list((home / 'sessions').glob('**/*' + thread_id + '*.jsonl')) if thread_id else []
    if len(candidates) != 1:
        return {'coverage': 'missing_or_ambiguous_native_trace', 'thread_id': thread_id, 'binding': binding}
    result = benchmark.collect_native_usage(candidates[0], since, thread_id, binding.get('ended_at'))
    contexts = result['contexts']
    models = sorted({c['model'] for c in contexts if c.get('model')})
    efforts = sorted({c['effort'] for c in contexts if c.get('effort')})
    requested_prior = binding.get('prior_session_id')
    actual_kind = 'resumed' if requested_prior and requested_prior == thread_id else 'cold_resume' if binding.get('resume_expected') else 'fresh'
    result.update(schema_version=2, coverage='recorded' if result['unique_response_count'] else 'no_native_response_records',
                  thread_id=thread_id, since=since, binding=binding, source_path=str(candidates[0]),
                  semantics={'first_input': 'First native response within this run boundary',
                             'after_bootstrap_proxy': 'Second observed request; bootstrap completion is not independently tagged',
                             'cached_input': 'Included in input; shown separately, never added again',
                             'output': 'Includes reasoning; reasoning is never added again'})
    result['comparison_key'] = {'native_version': result['native'].get('cli_version'), 'model': models, 'effort': efforts,
                                'service_tier': binding.get('service_tier'), 'session_kind': actual_kind,
                                'profile_sha256': binding.get('profile_sha256'), 'workload': binding.get('workload'), 'measurement_schema': 4}
    for key in ('effective_config_sha256', 'mcp_sha256', 'launch_args_sha256', 'brief_sha256', 'checkpoint_sha256'):
        result['comparison_key'][key] = binding.get(key)
    result['service_tier_evidence'] = 'Configured native override; actual service tier is not asserted when native turn metadata omits it'
    result['settings_match'] = (models == [binding.get('model')] and efforts == ['max'] and binding.get('service_tier') == 'default')
    return result


def automatic_baseline(root, value):
    # Baselines are immutable observations of completed runs with complete keys.
    # A changed native config/workload starts a separate series automatically.
    key = value.get('comparison_key', {})
    if value.get('binding', {}).get('comparison_unavailable'):
        return {'status': 'incomparable', 'reason': value['binding']['comparison_unavailable']}
    if not value.get('binding', {}).get('completed') or not value.get('binding', {}).get('ended_at') or value.get('coverage') != 'recorded' or not value.get('settings_match') or any(key.get(k) in (None, '', []) for k in COMPATIBLE):
        return {'status': 'not_eligible', 'reason': 'Incomplete/unfinished native evidence or comparison key'}
    path = root / 'Saved/ContextBudget02/baselines' / (digest(encode(key)) + '.json')
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open('xb') as stream:
            stream.write(encode(value))
        return {'status': 'baseline_recorded', 'path': str(path)}
    except FileExistsError:
        return {'status': 'compared', 'baseline': str(path), **compare(read_json(path), value)}


def compare(baseline, current):
    mismatches = [k for k in COMPATIBLE if baseline.get('comparison_key', {}).get(k) != current.get('comparison_key', {}).get(k)
                  or baseline.get('comparison_key', {}).get(k) in (None, '', [])]
    if baseline.get('coverage') != 'recorded' or current.get('coverage') != 'recorded':
        mismatches.append('coverage')
    if baseline.get('binding', {}).get('comparison_unavailable') or current.get('binding', {}).get('comparison_unavailable'):
        mismatches.append('semantic_identity_unavailable')
    if not baseline.get('settings_match') or not current.get('settings_match'):
        mismatches.append('native_settings')
    if not baseline.get('output_includes_reasoning_check') or not current.get('output_includes_reasoning_check'):
        mismatches.append('native_token_semantics')
    if mismatches:
        return {'compatible': False, 'mismatches': mismatches}
    metrics = ('first_input_tokens', 'input_after_first_response_tokens', 'peak_input_tokens', 'observed_growth_tokens')
    deltas = {k: current[k]-baseline[k] for k in metrics if isinstance(current.get(k), int) and isinstance(baseline.get(k), int)}
    return {'compatible': True, 'deltas': deltas, 'observed_increases': [k for k, v in deltas.items() if v > 0],
            'regression_policy': 'Directional increases are reported for review; no unapproved numeric threshold or pass/fail claim.',
            'native_usage_deltas': {k: current['native_usage'][k]-baseline['native_usage'][k] for k in benchmark.FIELDS}}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=ROOT)
    sub = p.add_subparsers(dest='command', required=True)
    c = sub.add_parser('collect')
    c.add_argument('--codex-home', type=Path, required=True)
    c.add_argument('--thread-id', default='')
    c.add_argument('--since', required=True)
    c.add_argument('--binding', type=Path, required=True)
    c.add_argument('--output', required=True)
    c = sub.add_parser('compare')
    c.add_argument('--baseline', type=Path, required=True)
    c.add_argument('--current', type=Path, required=True)
    c.add_argument('--output', required=True)
    args = p.parse_args()
    try:
        if args.command == 'collect':
            value = collect(args.codex_home, args.thread_id, args.since, read_json(args.binding))
            value['baseline_comparison'] = automatic_baseline(args.root.resolve(), value)
        else:
            value = compare(read_json(args.baseline), read_json(args.current))
        report(args.root.resolve(), value, args.output, 'usage')
        sys.exit(2 if value.get('compatible') is False else 0)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        report(args.root.resolve(), {'passed': False, 'failures': [str(exc)]}, args.output, 'usage')
        sys.exit(1)
