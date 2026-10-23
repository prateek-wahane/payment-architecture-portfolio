"""Optional real OTLP wire test, isolated because OTel provider setup is process-global."""
from pathlib import Path
import subprocess
import sys
import unittest

try:
    import opentelemetry.sdk
    AVAILABLE = True
except ImportError:
    AVAILABLE = False


@unittest.skipUnless(AVAILABLE, "Install requirements-observability.txt for the OTLP integration check")
class TelemetryTests(unittest.TestCase):
    def test_otlp_export_parentage_and_content_redaction(self):
        script = r'''
import gzip, json, tempfile, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest
import assistant, telemetry
from agent_lab import RunStore, ScriptedModel
received = []
class Collector(BaseHTTPRequestHandler):
    def log_message(self, *args): pass
    def do_POST(self):
        assert self.path == '/v1/traces'
        raw = self.rfile.read(int(self.headers['Content-Length']))
        if self.headers.get('Content-Encoding') == 'gzip': raw = gzip.decompress(raw)
        message = ExportTraceServiceRequest()
        message.ParseFromString(raw)
        for resource in message.resource_spans:
            for scope in resource.scope_spans:
                received.extend(scope.spans)
        self.send_response(200)
        self.end_headers()
collector = ThreadingHTTPServer(('127.0.0.1',0),Collector)
thread = threading.Thread(target=collector.serve_forever,daemon=True)
thread.start()
telemetry.configure(f'http://127.0.0.1:{collector.server_port}')
with tempfile.TemporaryDirectory() as folder:
    Path(folder,'sample.md').write_text('private-source-marker duplicate webhook outbox')
    worker = assistant.make_server('127.0.0.1',0,'secret-token-marker-at-least-24',
                                   corpus=assistant.Corpus(folder,'test-worker'))
    wt = threading.Thread(target=worker.serve_forever,daemon=True)
    wt.start()
    store = RunStore([f'http://127.0.0.1:{worker.server_port}'], 'secret-token-marker-at-least-24',
                     ScriptedModel(),labels=['docs'])
    rid = store.start('private-question-marker duplicate webhook', 'single')
    for t in store.threads: t.join(timeout=5)
    run = store.snapshot(rid)
    assert run['state'] == 'completed', run
    telemetry.flush()
    root = next(s for s in received if s.name == 'review.run')
    tool = next(s for s in received if s.name == 'tool.search')
    remote = next(s for s in received if s.name == 'worker.search')
    assert root.trace_id == tool.trace_id == remote.trace_id
    assert remote.parent_span_id == tool.span_id
    assert tool.parent_span_id == root.span_id
    assert run['trace_id'] == root.trace_id.hex()
    wire = str(received)
    for secret in ['private-source-marker','private-question-marker','secret-token-marker']:
        assert secret not in wire, secret
    worker.shutdown(); worker.server_close(); wt.join()
collector.shutdown(); collector.server_close(); thread.join()
print('OTLP protobuf export, distributed parentage, and content redaction: passed')
'''
        result = subprocess.run([sys.executable, "-B", "-c", script],
                                cwd=Path(__file__).resolve().parents[1],
                                text=True, capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
