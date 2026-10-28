"""Behavioral tests for OpenTelemetry setup."""

from fastapi import FastAPI

from app.observability import tracing


def _unexpected_exporter(*args, **kwargs):
    raise AssertionError("disabled telemetry attempted to create an OTLP exporter")


def test_setup_tracing_respects_disabled_sdk(monkeypatch):
    """OTEL_SDK_DISABLED must leave the application uninstrumented."""
    monkeypatch.setenv("OTEL_SDK_DISABLED", "true")
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://collector:4318")
    monkeypatch.setenv("OTEL_TRACES_EXPORTER", "otlp")
    monkeypatch.setattr(tracing, "OTLPSpanExporter", _unexpected_exporter)
    monkeypatch.setattr(tracing, "OTLPLogExporter", _unexpected_exporter)

    app = FastAPI()
    tracing.setup_tracing(app)


def test_setup_tracing_respects_disabled_exporters(monkeypatch):
    """Disabled exporters must not create telemetry middleware."""
    monkeypatch.delenv("OTEL_SDK_DISABLED", raising=False)
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "")
    monkeypatch.setenv("OTEL_TRACES_EXPORTER", "none")
    monkeypatch.setenv("OTEL_LOGS_EXPORTER", "none")
    monkeypatch.setattr(tracing, "OTLPSpanExporter", _unexpected_exporter)
    monkeypatch.setattr(tracing, "OTLPLogExporter", _unexpected_exporter)

    app = FastAPI()
    tracing.setup_tracing(app)
