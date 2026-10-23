from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import assistant
from agent_lab import Model, RunStore, ScriptedModel, response_schema

TOKEN = "testing-only-long-token-never-deploy"


class QueueModel:
    config = {"model": "test-fixture", "backend": "test"}

    def __init__(self, outputs):
        self.outputs = iter(outputs)
        self.inputs = []

    def complete(self, role, data, timeout):
        self.inputs.append((role, data))
        return next(self.outputs), {"input_tokens": 4, "output_tokens": 3}


def search(tool="technical_docs"):
    return {"action": "search", "tool": tool, "query": "duplicate webhook outbox"}


def finish(citations=None):
    return {"action": "finish", "claims": [{"text": "Deduplicate webhook events.",
            "citations": citations or [1]}], "open_questions": ["What retry window is required?"]}


class AgentLabTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        (root / "design.md").write_text("Deduplicate webhook events. Persist an outbox before publishing.")
        self.servers, self.threads, self.stores = [], [], []
        self.worker = self.serve(corpus=assistant.Corpus(root, "technical-docs"))

    def tearDown(self):
        for store in self.stores:
            for thread in store.threads:
                thread.join(timeout=5)
        for server in self.servers:
            server.shutdown()
            server.server_close()
        for thread in self.threads:
            thread.join(timeout=5)
        self.tmp.cleanup()

    def serve(self, **kwargs):
        server = assistant.make_server("127.0.0.1", 0, TOKEN, **kwargs)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.servers.append(server)
        self.threads.append(thread)
        if server.runs:
            self.stores.append(server.runs)
        return f"http://127.0.0.1:{server.server_port}"

    def store(self, model, **kwargs):
        store = RunStore([self.worker], TOKEN, model, labels=["technical_docs"], **kwargs)
        self.stores.append(store)
        return store

    def wait(self, store, mode="single"):
        run_id = store.start("How do we handle duplicate webhook events?", mode)
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            run = store.snapshot(run_id)
            if run["state"] != "running":
                for thread in store.threads:
                    thread.join(timeout=1)
                return store.snapshot(run_id)
            time.sleep(.01)
        self.fail("Run did not finish")

    def test_agent_sees_tool_results_before_finishing(self):
        model = QueueModel([search(), finish()])
        run = self.wait(self.store(model))
        self.assertEqual(run["state"], "completed")
        self.assertEqual(run["metrics"]["tool_calls"], 1)
        self.assertEqual(run["metrics"]["model_calls"], 2)
        self.assertEqual(run["metrics"]["input_tokens"], 8)
        self.assertEqual(model.inputs[1][1]["observations"][0]["status"], "available")
        self.assertEqual(run["coverage"], {"technical_docs": "available"})
        self.assertNotIn("deadline", run)

    def test_unconfigured_tool_is_rejected_without_network_access(self):
        run = self.wait(self.store(QueueModel([search("http://attacker.invalid")])) )
        self.assertEqual(run["state"], "failed")
        self.assertEqual(run["metrics"]["tool_calls"], 0)
        self.assertEqual(run["claims"], [])

    def test_invalid_citation_stops_answer(self):
        run = self.wait(self.store(QueueModel([search(), finish([99]), finish([99])])))
        self.assertEqual(run["state"], "failed")
        self.assertTrue(run["evidence"])
        self.assertEqual(run["claims"], [])
        self.assertIn("integer citation IDs", run["notice"])
        self.assertEqual(run["metrics"]["repair_attempts"], 1)

    def test_agent_cannot_answer_without_searching(self):
        run = self.wait(self.store(QueueModel([finish()])))
        self.assertEqual(run["state"], "failed")

    def test_search_loop_is_bounded(self):
        run = self.wait(self.store(QueueModel([search()] * 6)))
        self.assertEqual(run["state"], "failed")
        self.assertEqual(run["metrics"]["tool_calls"], 4)
        self.assertEqual(run["metrics"]["model_calls"], 6)
        self.assertIn("Search budget reached", run["notice"])

    def test_reviewer_removes_unsupported_claim(self):
        review = {"checks": [{"claim": 1, "verdict": "unsupported", "note": "Source does not support claim."}],
                  "open_questions": ["Need provider contract."], "followup": None}
        run = self.wait(self.store(QueueModel([search(), finish(), review])), "review")
        self.assertEqual(run["state"], "completed")
        self.assertEqual(run["claims"], [])
        self.assertEqual(run["review"]["draft"]["claims"][0]["text"], finish()["claims"][0]["text"])
        self.assertIn("Need provider contract.", run["open_questions"])

    def test_invalid_reviewer_cannot_publish_unreviewed_draft(self):
        run = self.wait(self.store(QueueModel([search(), finish(), {"checks": []}])), "review")
        self.assertEqual(run["state"], "failed")
        self.assertEqual(run["claims"], [])

    def test_scripted_review_followup_is_explicit_and_bounded(self):
        store = RunStore([self.worker, self.worker], TOKEN, ScriptedModel(),
                         labels=["technical_docs", "project_notes"])
        self.stores.append(store)
        run = self.wait(store, "review")
        self.assertTrue(run["simulation"])
        self.assertEqual(run["review"]["pass"], 2)
        self.assertEqual(run["metrics"]["tool_calls"], 2)
        self.assertEqual(run["metrics"]["model_calls"], 5)
        self.assertEqual(run["coverage"]["project_notes"], "available")

    def test_offline_worker_is_visible(self):
        server = self.servers[0]
        server.shutdown()
        server.server_close()
        model = QueueModel([search(), {"action": "finish", "claims": [], "open_questions": ["Source offline"]}])
        run = self.wait(self.store(model))
        self.assertEqual(run["coverage"]["technical_docs"], "unavailable")
        self.assertEqual(run["claims"], [])
        self.assertTrue(any(event.get("error_type") for event in run["events"]))

    def test_deadline_prevents_model_calls(self):
        run = self.wait(self.store(QueueModel([]), budget_seconds=0))
        self.assertEqual(run["state"], "failed")
        self.assertEqual(run["metrics"]["model_calls"], 0)

    def test_run_polling_requires_auth(self):
        base = self.serve(workers=[self.worker], lab_model=ScriptedModel())
        result = assistant.request_json(base + "/runs", {"question": "webhook", "mode": "single"}, TOKEN)
        with self.assertRaises(urllib.error.HTTPError) as error:
            urllib.request.urlopen(base + "/runs/" + result["id"])
        self.assertEqual(error.exception.code, 401)
        request = urllib.request.Request(base + "/runs/" + result["id"],
                                         headers={"Authorization": "Bearer " + TOKEN})
        with urllib.request.urlopen(request) as response:
            self.assertEqual(response.status, 200)

    def test_agent_mode_requires_model(self):
        with self.assertRaises(ValueError):
            self.store(None).start("webhook", "single")
        with self.assertRaises(ValueError):
            self.store(None).start("webhook", {"invalid": "mode"})

    def test_run_history_is_bounded(self):
        store = self.store(ScriptedModel(), max_runs=2)
        for _ in range(3):
            self.wait(store)
        self.assertEqual(len(store.runs), 2)

    def test_concurrency_limit(self):
        store = self.store(ScriptedModel())
        store.slots.acquire()
        store.slots.acquire()
        try:
            with self.assertRaises(RuntimeError):
                store.start("webhook", "single")
        finally:
            store.slots.release()
            store.slots.release()

    def test_ollama_adapter_protocol_and_usage(self):
        model = Model({"backend": "ollama", "model": "example", "endpoint": "http://localhost:11434"})
        response = {"message": {"content": '{"action":"search","tool":"technical_docs","query":"webhook"}'},
                    "prompt_eval_count": 10, "eval_count": 5}
        data = {"question": "test", "tools": [{"name": "technical_docs"}],
                "evidence": [], "observations": [], "searches_remaining": 4}
        with patch.object(assistant, "request_json", return_value=response) as request:
            result, usage = model.complete("researcher", data, 1)
        self.assertEqual(result["action"], "search")
        self.assertEqual(usage["input_tokens"], 10)
        self.assertEqual(request.call_args.args[0], "http://localhost:11434/api/chat")
        schema = request.call_args.args[1]["format"]
        self.assertEqual(schema["properties"]["action"], {"const": "search"})
        data["observations"] = [{"status": "available"}]
        data["searches_remaining"] = 0
        schema = response_schema("researcher", data)
        self.assertEqual(schema["properties"]["action"], {"const": "finish"})

    def test_invalid_output_gets_one_correction_and_then_completes(self):
        model = QueueModel([search(), finish([99]), finish()])
        run = self.wait(self.store(model))
        self.assertEqual(run["state"], "completed")
        self.assertEqual(run["metrics"]["repair_attempts"], 1)
        self.assertEqual(run["metrics"]["model_calls"], 3)
        self.assertIn("validation_feedback", model.inputs[2][1])
        self.assertTrue(any(e["kind"] == "retry" for e in run["events"]))

    def test_budget_exhaustion_can_be_corrected_to_finish(self):
        model = QueueModel([search()] * 5 + [finish()])
        run = self.wait(self.store(model))
        self.assertEqual(run["state"], "completed")
        self.assertEqual(run["metrics"]["tool_calls"], 4)
        self.assertEqual(run["metrics"]["repair_attempts"], 1)

    def test_untrusted_model_text_is_not_echoed_as_a_diagnostic(self):
        response = {"action": "private-secret-marker"}
        run = self.wait(self.store(QueueModel([response, response])))
        self.assertEqual(run["state"], "failed")
        self.assertIn("Researcher action must be", run["notice"])
        self.assertNotIn("private-secret-marker", str(run))


if __name__ == "__main__":
    unittest.main()
