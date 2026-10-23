# Review lab contract

## What the lab demonstrates

A model-driven research loop over two read-only document tools, followed optionally by a reviewer in a separate context. It is designed to teach tool selection, observation-driven decisions, handoff schemas, grounded answers, abstention, failure visibility and evaluation. Multi-agent review must earn its extra inference latency and usage in measured comparisons.

The phone/tablet is a browser client. Windows laptop A hosts the coordinator, local model and technical-reference worker. Windows laptop B hosts project notes. No background Android agent, arbitrary device filesystem access, payment transaction execution or external write tools are included.

## Three workflows

| Mode | Retrieval | Generation / verification |
|---|---|---|
| baseline | Same question sent to every configured source, sequentially | One fixed writer call if a model is configured; otherwise source passages only |
| single | Research model chooses a named tool and query, receives observations, repeats or finishes | Cited claims and missing design details |
| review | Same research loop | Reviewer checks every claim; optionally one additional search, revised draft, and final reviewer pass |

Baseline in this new lab is sequential to make each step visible. The original `/ask` retrieval baseline remains parallel. Record which baseline a report uses; their latency is not interchangeable. Comparisons are not controlled for tool count: tool count is one of the outcomes.

Tool invocation is structured JSON, not shell execution. The runtime maps names to configured URLs; a model cannot supply a destination URL or change the approved document root. Search evidence is deduplicated using source, path and starting line. Citation IDs remain stable throughout a run. Finishing before searching, invalid citations and unrecognized tool names stop a run. Semantic support is assessed by the reviewer model and later human evaluation; valid source IDs alone do not prove correctness.

## Bounded execution

- Two active runs and 32 retained runs per coordinator. Old completed runs are evicted first. Run state lives in memory.
- Four research searches, one reviewer follow-up search, and eight model calls maximum per agent run. No automatic model-call retries.
- 150-second orchestration budget, checked before each operation; individual model socket timeout at most 40 seconds, worker timeout at most three seconds. This is not process-level preemption of a malicious streaming peer.
- Up to 12 retained evidence passages, each at most 12,000 characters, with a total 24,000-character passage budget. This character budget is not an exact tokenizer budget. Model context must also accommodate instructions and structured metadata; local configuration requests an 8,192-token context and at most 1,000 output tokens per call.
- Malformed model output fails visibly and retains evidence. Failed reviewer validation never publishes the unreviewed draft as the final answer.
- Unavailable and unsearched sources remain distinct. A successful answer can still have partial source coverage. Unsupported or uncertain reviewer claims are withheld from the final reviewed answer, with the draft/checks retained for inspection.

## Observability contract

`POST /runs` accepts `{question, mode}` and returns an ID; authenticated `GET /runs/ID` returns live state. Polling updates the viewer every 500 ms. Events describe actions and observations, not internal reasoning. `/health` exposes only role and basic status; it is not a model-readiness check. `/ask` is retained for compatibility with the first increment.

The dashboard displays coverage, step timing, model and tool counts, provider-reported usage when available, structured reviewer checks, final claims, evidence and open questions. Token usage is not estimated when the provider omits it. Exact monetary costs are not reported without a pricing configuration. Evidence bytes are serialized final evidence size, not total network traffic.

OTLP spans form `review.run → agent.researcher / tool.search → worker.search`, plus reviewer and writer spans when applicable. Source query text, document content, model outputs and credentials stay out of exported spans. Error exports use status without raw exception messages. The run dashboard and downloaded run JSON do contain question/evidence content and belong only on the approved demo network.

The same shared bearer token authorizes all workers and run access. HTTP is provided for a trusted sample-data LAN demo. HTTPS, identity per user/device, durable audit storage, distributed rate limiting and authenticated telemetry ingestion remain required before use with private organizational documents.

## Evaluation contract

Compare identical documents, question set, model tag and inference settings. Keep successful, failed and abstained outcomes separate. Report model latency, tool calls, token counts and source coverage alongside human-scored correctness and claim support. Inspect the ten candidate unanswerable questions for hallucination and appropriate abstention. Candidate questions must be reviewed and a separate held-out set created before calling the results a benchmark.

Scripted simulation exercises the real HTTP tools and runtime but uses deterministic model fixtures. It must be visibly labeled in the UI, reports, screenshots and presentations. It cannot establish reasoning quality, model latency, token cost or superiority of multiple agents.
