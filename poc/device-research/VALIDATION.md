# Validation record

Prepared on 2026-10-23. Platform: Linux cloud host, Python 3.12.14, system Chromium through Playwright. This is a development verification record, not evidence of real Windows-device deployment or model answer quality.

## Verified

- **24 automated tests passed** using an isolated Python environment with the optional OpenTelemetry dependencies installed. The suite includes the original eight retrieval tests, 15 agent-runtime/API tests, and one OTLP wire integration test.
- The runtime/API tests exercise observation-driven tool calls, rejected arbitrary destinations, invalid citations, finishing before search, bounded repeated searches, reviewer rejection, follow-up and revision, invalid reviewer output, offline sources, run deadline, polling authorization, missing model configuration, bounded history, concurrency, and mocked Ollama protocol/usage parsing.
- The OTLP test exports real protobuf messages to a local HTTP receiver, verifies the coordinator→tool→worker trace and parent IDs, and confirms that source text, question text and the test access token do not appear in exported spans. The model role in this test is scripted. A real Phoenix service was not started.
- A real Chromium browser exercised the actual HTTP dashboard: review/follow-up flow, visible scripted label, source citation expansion, run JSON download without token leakage, a 390-pixel mobile viewport without horizontal overflow, benchmark report loading, offline-source warning, and denied-token feedback. No JavaScript page errors occurred in the passing run.
- The browser check found a stale-status display at the start of a second run. The dashboard now sets “Starting review…” immediately; the complete browser check passed after that correction.

Reproduce the unit/integration suite with:

```powershell
.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

Without the optional dependencies, the OTLP test is explicitly skipped; the rest of the lab remains dependency-free. Run `ui_smoke.py` separately with Playwright installed for browser coverage.

## Checked-in artifacts

- [Desktop dashboard](evidence/dashboard-desktop.png)
- [Mobile layout](evidence/dashboard-mobile.png)
- [Offline-source dashboard](evidence/dashboard-partial.png)
- [Scripted workflow report](evidence/orchestration-results.json)

The report contains three candidate questions × three workflows = **nine completed scripted runs**. It records actual local HTTP/runtime durations but performs no model inference. Its millisecond timings cannot be used as local-model, Wi-Fi or multi-agent performance claims. Human quality fields are blank by design. All three workflows completing a scripted run does not establish that the reviewer improves answers.

The earlier `baseline-results.json` is a separate retrieval-only development evaluation: six of six expected documents found after revising the scorer, with exact passage/file matching. Those six questions influenced the scorer and are not a held-out accuracy benchmark.

## Still required

1. Run a real Ollama model and inspect its tool-selection and JSON-output reliability; test the cloud adapter with a real provider if choosing that option. Neither Ollama nor model API credentials were available in this cloud session.
2. Deploy across both Windows laptops; query from the Android phone and tablet; repeat source outage/recovery with real network failures.
3. Human-review the 30 candidate questions and create a separate held-out set. Score correctness, claim support, and abstention; do not use the reviewer model's own judgment as independent ground truth.
4. Run sufficiently many warm requests per workflow on fixed hardware/model settings. Report failures, p50/p95, usage and quality together. Record cold-start behavior separately. Use actual network measurement if reporting transferred bytes.
5. Run a real telemetry viewer if it will be shown in the presentation. Dashboard observability and OTLP wire export are verified; Phoenix deployment is only documented.
6. Add HTTPS and user/device identity before connecting confidential organizational documents. The current shared-token HTTP topology is a sample-data private-LAN lab.

The demo narrative targets three minutes. Actual real-model run duration and the benefit of adding a reviewer remain hypotheses to test.
