"""Optional OpenTelemetry export. Export metadata, never questions or passages."""
from contextlib import contextmanager
import os

_enabled = False
_provider = None


def configure(endpoint=None):
    global _enabled, _provider
    endpoint = endpoint or os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not endpoint:
        return False
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    _provider = TracerProvider(resource=Resource.create({"service.name": "payment-review-lab"}))
    _provider.add_span_processor(BatchSpanProcessor(
        OTLPSpanExporter(endpoint=endpoint.rstrip("/") + "/v1/traces", timeout=3)))
    trace.set_tracer_provider(_provider)
    _enabled = True
    return True


@contextmanager
def span(name, attributes=None, incoming=None):
    if not _enabled:
        yield None
        return
    from opentelemetry import trace, propagate
    context = propagate.extract(incoming) if incoming is not None else None
    kind = ("CHAIN" if name == "review.run" else "LLM" if name.startswith("agent.")
            else "RETRIEVER" if name == "worker.search" else "TOOL")
    with trace.get_tracer("payment-review-lab").start_as_current_span(
            name, context=context, attributes={"openinference.span.kind": kind, **(attributes or {})}, record_exception=False,
            set_status_on_exception=False) as current:
        try:
            yield current
        except Exception:
            # Do not export exceptions that may contain credentials or source content.
            current.set_status(trace.StatusCode.ERROR)
            raise


def headers():
    if not _enabled:
        return {}
    from opentelemetry import propagate
    carrier = {}
    propagate.inject(carrier)
    return carrier


def trace_id():
    if not _enabled:
        return None
    from opentelemetry import trace
    return format(trace.get_current_span().get_span_context().trace_id, "032x")


def flush():
    if _provider:
        _provider.force_flush(timeout_millis=5000)
