"""Reproduce the retrieval baseline over real HTTP servers on one host."""
from pathlib import Path
import json
import statistics
import threading
import assistant as app

CASES = [
    ("How should we handle duplicate webhooks?", "04-idempotency-and-duplicates.md"),
    ("How does the transactional outbox handle partial failure?", "07-partial-failure-handling.md"),
    ("How do we debug payments with observability?", "08-observability-and-debugging.md"),
    ("How does reconciliation compare settlement amounts?", "09-reconciliation-and-settlement.md"),
    ("How can simultaneous transactions avoid race conditions?", "05-simultaneous-transactions.md"),
    ("How do we achieve low latency?", "06-low-latency-design.md"),
]


def main():
    repo = Path(__file__).resolve().parents[2]
    token = "evaluation-only-token-not-for-deployment"
    servers, threads, origins = [], [], []
    rows = []
    try:
        for label, root in [("technical-docs", repo / "docs"), ("project-notes", repo / "case-studies")]:
            server = app.make_server("127.0.0.1", 0, token, corpus=app.Corpus(root, label))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            servers.append(server)
            threads.append(thread)
            origins.append(f"http://127.0.0.1:{server.server_port}")
        coordinator = app.make_server("127.0.0.1", 0, token, workers=origins)
        thread = threading.Thread(target=coordinator.serve_forever, daemon=True)
        thread.start()
        servers.append(coordinator)
        threads.append(thread)
        for question, expected in CASES:
            result = app.request_json(f"http://127.0.0.1:{coordinator.server_port}/ask",
                                      {"question": question}, token)
            citations_valid = True
            for evidence in result["evidence"]:
                root = repo / ("docs" if evidence["device"] == "technical-docs" else "case-studies")
                lines = (root / evidence["path"]).read_text(encoding="utf-8").splitlines()
                start = evidence["line"] - 1
                citations_valid &= "\n".join(lines[start:start + 30]) == evidence["text"]
            rows.append({"question": question, "expected_document": expected,
                         "hit_at_6": any(e["path"] == expected for e in result["evidence"]),
                         "citation_spans_match_files": citations_valid,
                         "latency_ms": result["latency_ms"], "evidence_bytes": result["evidence_bytes"]})
        report = {"scope": "Single-host HTTP simulation; no LLM; curated six-question development set, not a held-out benchmark",
                  "questions": len(rows), "hit_at_6": sum(r["hit_at_6"] for r in rows) / len(rows),
                  "all_citation_spans_match_files": all(r["citation_spans_match_files"] for r in rows),
                  "median_retrieval_ms": statistics.median(r["latency_ms"] for r in rows), "results": rows}
        print(json.dumps(report, indent=2))
    finally:
        for server in servers:
            server.shutdown()
            server.server_close()
        for thread in threads:
            thread.join()


if __name__ == "__main__":
    main()
