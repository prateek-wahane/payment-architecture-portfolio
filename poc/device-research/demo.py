"""Start a single-host lab with two real HTTP workers. Not a two-device deployment."""
import argparse
import os
from pathlib import Path
import threading

import assistant
from agent_lab import ScriptedModel
import telemetry


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scripted", action="store_true", help="Labeled simulation; no LLM inference")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--model", default="qwen2.5:3b")
    parser.add_argument("--otel-endpoint")
    args = parser.parse_args()
    token = os.environ.get("RESEARCH_TOKEN", "")
    if len(token) < 24:
        parser.error("Set RESEARCH_TOKEN to at least 24 random characters")
    telemetry.configure(args.otel_endpoint)
    repo = Path(__file__).resolve().parents[2]
    servers, threads, origins = [], [], []
    try:
        for name, folder in [("technical-docs", "docs"), ("project-notes", "case-studies")]:
            server = assistant.make_server("127.0.0.1", 0, token,
                                           corpus=assistant.Corpus(repo / folder, name))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            servers.append(server)
            threads.append(thread)
            origins.append(f"http://127.0.0.1:{server.server_port}")
        model_config = None if args.scripted else {
            "backend": "ollama", "model": args.model, "endpoint": "http://127.0.0.1:11434"}
        coordinator = assistant.make_server("127.0.0.1", args.port, token, workers=origins,
            model_config=model_config, lab_model=ScriptedModel() if args.scripted else None,
            worker_labels=["technical_docs", "project_notes"])
        servers.append(coordinator)
        print("Single-host simulation: two HTTP workers and coordinator", flush=True)
        print("SCRIPTED — NO MODEL INFERENCE" if args.scripted else "Local Ollama inference configured", flush=True)
        print(f"Dashboard listening on port {args.port}; Ctrl+C stops these services", flush=True)
        coordinator.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        # Only worker threads use serve_forever in background; stop those we started.
        for server in servers[:len(threads)]:
            server.shutdown()
        for server in servers:
            server.server_close()
        for thread in threads:
            thread.join()
        telemetry.flush()


if __name__ == "__main__":
    main()
