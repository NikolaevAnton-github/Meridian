# MSQ-63 additional turn coverage

2026-09-18. Supplement to the registered [controller review](PurchasedArms03Review.md).
The worker subsequently added an interpolated reference comparison using the
same recordings, reviewed independently as supplementary evidence. It covers
1,860 evaluations across all 24 fifteen-degree yaw bins, with residuals of
0.011481 cm / 0.029260 degrees. The largest interpolation bracket is 0.166667
cycle; approximation error is not measured separately, and the synthesized
phase difference of zero is not an exact sampled-phase match. This supplement
does not replace the stricter measured results in the registered review. No
gameplay rerun occurred. See `Worker/analysis03.json` and the final addendum in
`Controller/fix-review.md`, both under `Saved/PurchasedArms03/`.

This late report is kept separately to preserve the already registered review
fingerprint. A validation check detected the initial appended paragraph; the
registered review was restored exactly and this supplementary record preserves
the additional finding without silently replacing registry evidence.

During closure, CLI rejected `--no-start` combined with `--unassign`; status
closure still succeeded, but the following controller comment created another
queue before unassignment was retried. Runtime shutdown cancelled environment
preparation: that record has no start timestamp or messages and performed no
work. The issue is done and unassigned, both duplicate queues are terminal, and
the runtime is restored to its initially stopped state. Evidence is in
`Controller/runs-closed.json` and `Controller/closure-duplicate-messages.json`.
