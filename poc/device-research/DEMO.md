# Three-minute presentation

## Prepare before presenting

Choose the real-model run only after completing a successful warm run on the target laptop. Download and warm the model before the demo. Check both source workers and model endpoint; `/health` alone does not verify inference readiness. Keep the dataset small and use non-sensitive portfolio documents.

Start the coordinator with `technical_docs` and `project_notes` labels. Open the dashboard on the phone and mirror it to the presentation screen, or use its desktop layout. Keep the comparison report and a previously exported trace available. Label replays and scripted fixtures clearly. If the hardware cannot finish within the time budget, use an explicitly labeled recorded run; never imply that prerecorded results are live inference.

## Suggested sequence

| Time | Show | Explain |
|---|---|---|
| 0:00–0:20 | Two source collections, phone request, workflow selector | “The researcher can choose tools; the reviewer checks the draft. These are distinct from the document workers.” |
| 0:20–1:15 | Start research + reviewer; watch activity and coverage | “These are actual tool queries and observations. Decisions and call limits are visible.” |
| 1:15–2:00 | Final claims, reviewer checks, open one citation | “A claim points to an exact source passage. A reviewer assessment still needs independent evaluation.” |
| 2:00–2:40 | Stop laptop B's worker with Ctrl+C and rerun | “The source becomes unavailable. The system reports partial coverage instead of pretending the whole corpus was searched.” |
| 2:40–3:00 | Load the measured workflow comparison JSON | “Does the second agent improve supported answers enough to justify its latency and usage? Here are the results, including failures.” |

If a model finishes too slowly to repeat the entire review live, use the already recorded and explicitly labeled failure trace for the outage segment. The presentation target is three minutes; actual inference latency remains hardware-dependent, not guaranteed by the UI.

## Default design-review prompt

“Review this checkout design: payment requests may be retried, webhooks may arrive twice, and order confirmation is synchronous. How can we prevent duplicate charges and handle payment success when the order service is unavailable? Cite evidence and identify missing design details.”

Then demonstrate abstention with: “What was our actual production p99 checkout latency yesterday?” This portfolio contains design material, not yesterday's production telemetry.

## What counts as portfolio evidence

Save actual machine specifications, model tag/version, corpus revision, mode, prompt and model settings; a sanitized trace; reviewer scoring records; and benchmark JSON. Include failed runs. Screenshots of the scripted fixture show only UI and orchestration behavior. Do not reuse their millisecond latency values as model or Wi-Fi performance claims.

The current checked-in artifacts cover automated tests, browser behavior and scripted orchestration on one Linux cloud host. They do not establish Windows deployment, real model correctness, real-device failure recovery or a multi-agent quality improvement.
