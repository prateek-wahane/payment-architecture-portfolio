"""Compare workflows on one configured coordinator; never infer semantic quality from IDs."""
import argparse
from collections import defaultdict
import json
import math
import os
from pathlib import Path
import statistics
import time
import urllib.request

from assistant import request_json


def percentile(values, p):
    return sorted(values)[max(0, math.ceil(len(values) * p) - 1)] if values else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coordinator", default="http://127.0.0.1:8000")
    parser.add_argument("--cases", type=Path, default=Path(__file__).with_name("evaluation-cases.json"))
    parser.add_argument("--modes", nargs="+", choices=["baseline", "single", "review"],
                        default=["baseline", "single", "review"])
    parser.add_argument("--limit", type=int)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output already exists; choose a new file to preserve previous evidence")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    token = os.environ.get("RESEARCH_TOKEN", "")
    if len(token) < 24:
        parser.error("Set RESEARCH_TOKEN first")
    cases = json.loads(args.cases.read_text(encoding="utf-8"))
    if args.limit is not None:
        if args.limit < 1:
            parser.error("Limit must be positive")
        cases = cases[:args.limit]
    rows = []
    for case in cases:
        for mode in args.modes:
            started = time.perf_counter()
            try:
                run_id = request_json(args.coordinator.rstrip("/") + "/runs", {
                    "question": case["question"], "mode": mode}, token)["id"]
                deadline = time.monotonic() + 170
                while True:
                    request = urllib.request.Request(args.coordinator.rstrip("/") + "/runs/" + run_id,
                                                     headers={"Authorization": "Bearer " + token})
                    with urllib.request.urlopen(request, timeout=5) as response:
                        run = json.load(response)
                    if run["state"] != "running":
                        break
                    if time.monotonic() > deadline:
                        raise TimeoutError("Polling deadline exceeded")
                    time.sleep(.1)
                rows.append({"case_id": case["id"], "mode": mode, "state": run["state"],
                             "simulation": run["simulation"], "model": run["model"],
                             "elapsed_ms": run["metrics"]["elapsed_ms"], "metrics": run["metrics"],
                             "abstained": run["state"] == "completed" and not run["claims"],
                             "coverage": run["coverage"], "claims": run["claims"],
                             "evidence": run["evidence"], "open_questions": run["open_questions"],
                             "human_scores": {"correct": None, "supported_claims": None,
                                              "total_claims": len(run["claims"]), "notes": ""}})
            except (OSError, ValueError, KeyError):
                rows.append({"case_id": case["id"], "mode": mode, "state": "request_failed",
                             "elapsed_ms": round((time.perf_counter() - started) * 1000, 2)})
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["mode"]].append(row)
    summary = {}
    for mode, results in grouped.items():
        timings = [r["elapsed_ms"] for r in results if r["state"] == "completed"]
        summary[mode] = {"runs": len(results), "completed": len(timings),
                         "failed": len(results) - len(timings),
                         "completed_p50_ms": statistics.median(timings) if timings else None,
                         "completed_p95_ms": percentile(timings, .95),
                         "quality": "Not scored: requires human review of claims and sources"}
    report = {"scope": "Candidate cases, not a reviewed held-out benchmark. Sequential runs; warm/cold state uncontrolled.",
              "simulation": any(r.get("simulation") for r in rows),
              "percentile_method": "p50 median; p95 nearest rank; completed runs only, failures reported separately",
              "summary": summary, "results": rows}
    with args.output.open("x", encoding="utf-8") as output:
        json.dump(report, output, indent=2)
    print(json.dumps({"simulation": report["simulation"], "summary": summary}, indent=2))
    if any(r["state"] != "completed" for r in rows):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
