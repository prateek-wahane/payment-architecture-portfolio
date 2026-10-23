import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import assistant as app

TOKEN = "test-only-token-with-at-least-24-characters"


class ResearchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        (root / "webhooks.md").write_text("Deduplicate webhook deliveries using provider_event_id.")
        (root / ".private.md").write_text("hidden confidential marker")
        (root / "credential.env").write_text("secret")
        self.corpus = app.Corpus(root, "laptop-a")
        self.servers = []
        self.threads = []

    def tearDown(self):
        for server in self.servers:
            server.shutdown()
            server.server_close()
        for thread in self.threads:
            thread.join()
        self.tmp.cleanup()

    def serve(self, **kwargs):
        server = app.make_server("127.0.0.1", 0, TOKEN, **kwargs)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.servers.append(server)
        self.threads.append(thread)
        return f"http://127.0.0.1:{server.server_port}"

    def test_search_citations_and_scope(self):
        result = self.corpus.search("webhook")
        self.assertEqual(result[0]["path"], "webhooks.md")
        self.assertEqual(result[0]["line"], 1)
        self.assertEqual(self.corpus.search("confidential"), [])
        self.assertEqual(len(self.corpus.chunks), 1)

    def test_symlink_escape_excluded(self):
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside) / "outside.md"
            target.write_text("outside secret")
            try:
                (Path(self.tmp.name) / "escape.md").symlink_to(target)
            except OSError:
                self.skipTest("Symlinks not available")
            corpus = app.Corpus(self.tmp.name, "test")
            self.assertEqual(corpus.search("outside"), [])

    def test_two_workers_and_coordinator(self):
        a = self.serve(corpus=self.corpus)
        b = self.serve(corpus=app.Corpus(self.tmp.name, "laptop-b"))
        coordinator = self.serve(workers=[a, b])
        result = app.request_json(coordinator + "/ask", {"question": "webhook"}, TOKEN)
        self.assertEqual(result["status"], "complete")
        self.assertEqual({e["device"] for e in result["evidence"]}, {"laptop-a", "laptop-b"})

    def test_offline_device_reports_partial(self):
        a = self.serve(corpus=self.corpus)
        offline = self.serve(corpus=self.corpus)
        self.servers[-1].shutdown()
        self.servers[-1].server_close()
        result = app.investigate("webhook", [a, offline], TOKEN)
        self.assertEqual(result["status"], "partial")
        self.assertEqual(len(result["evidence"]), 1)

    def test_authorization_and_validation(self):
        worker = self.serve(corpus=self.corpus)
        for token, question, expected in [("wrong", "webhook", 401), (TOKEN, "", 400),
                                          (TOKEN, "x" * 9000, 413)]:
            with self.assertRaises(urllib.error.HTTPError) as error:
                app.request_json(worker + "/search", {"question": question}, token)
            self.assertEqual(error.exception.code, expected)

    def test_no_evidence_abstains_without_model_call(self):
        with patch.object(app, "request_json") as request:
            result = app.generate_answer("weather", [], "ollama", "test", "http://localhost")
            self.assertEqual(result["status"], "abstained")
            request.assert_not_called()

    def test_generated_citation_contract(self):
        evidence = self.corpus.search("webhook")
        for citation, valid in [(1, True), (2, False), (True, False)]:
            response = {"response": json.dumps({"claims": [{"text": "Deduplicate webhooks.",
                                                           "citations": [citation]}]})}
            with patch.object(app, "request_json", return_value=response):
                if valid:
                    result = app.generate_answer("webhook", evidence, "ollama", "test", "http://localhost")
                    self.assertEqual(result["status"], "generated")
                else:
                    with self.assertRaises(ValueError):
                        app.generate_answer("webhook", evidence, "ollama", "test", "http://localhost")

    def test_model_failure_preserves_evidence(self):
        worker = self.serve(corpus=self.corpus)
        coordinator = self.serve(workers=[worker], model_config={
            "backend": "ollama", "model": "test", "endpoint": "http://localhost"})
        with patch.object(app, "generate_answer", side_effect=ValueError("bad citation")):
            result = app.request_json(coordinator + "/ask", {"question": "webhook"}, TOKEN)
        self.assertEqual(result["answer"]["status"], "unavailable_or_invalid")
        self.assertTrue(result["evidence"])


if __name__ == "__main__":
    unittest.main()
