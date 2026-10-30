import logging
import os
from typing import Any, Dict

from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def server_request_hook(span, scope: Dict[str, Any]) -> None:
    """Кастомный hook для обогащения spans атрибутами."""
    if path := scope.get("path"):
        span.set_attribute("http.url.path", path)

    if query_string := scope.get("query_string"):
        span.set_attribute("http.url.query", query_string.decode())

    if event_type := scope.get("type"):
        span.set_attribute("asgi.event_type", event_type)


def setup_tracing(app) -> None:
    """
    Настройка OpenTelemetry для traces и logs согласно CNCF практикам.
    Production-ready конфигурация для Kubernetes.
    """
    sdk_disabled = os.getenv("OTEL_SDK_DISABLED", "false").strip().lower() in {
        "1",
        "true",
        "yes",
    }
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "").strip().rstrip("/")
    traces_enabled = os.getenv("OTEL_TRACES_EXPORTER", "none").strip().lower() == "otlp"
    logs_enabled = os.getenv("OTEL_LOGS_EXPORTER", "none").strip().lower() == "otlp"

    if sdk_disabled or not otlp_endpoint or not (traces_enabled or logs_enabled):
        logging.getLogger(__name__).info("OpenTelemetry export disabled")
        return

    resource = Resource(attributes={
        "service.name": os.getenv("OTEL_SERVICE_NAME", "chat-api"),
        "service.version": os.getenv("APP_VERSION", "0.1.0"),
        "deployment.environment": os.getenv("ENVIRONMENT", "production"),
        "k8s.pod.name": os.getenv("K8S_POD_NAME", "unknown"),
        "k8s.namespace": os.getenv("K8S_NAMESPACE", "chat"),
        "k8s.node.name": os.getenv("K8S_NODE_NAME", "unknown"),
        "k8s.deployment.name": os.getenv("K8S_DEPLOYMENT_NAME", "chat-api"),
        "k8s.container.name": os.getenv("K8S_CONTAINER_NAME", "chat-api"),
        "k8s.pod.uid": os.getenv("K8S_POD_UID", "unknown"),
    })

    # OTLP/HTTP exporters require a signal-specific path.
    traces_endpoint = f"{otlp_endpoint}/v1/traces" if not otlp_endpoint.endswith("/v1/traces") else otlp_endpoint
    logs_endpoint = f"{otlp_endpoint}/v1/logs" if not otlp_endpoint.endswith("/v1/logs") else otlp_endpoint

    provider = None
    if traces_enabled:
        provider = TracerProvider(resource=resource)

        otlp_trace_exporter = OTLPSpanExporter(
            endpoint=traces_endpoint,
            headers={"X-Scope-OrgID": os.getenv("GRAFANA_TENANT_ID", "1")}
            if os.getenv("GRAFANA_TENANT_ID")
            else None,
        )

        trace_processor = BatchSpanProcessor(
            otlp_trace_exporter,
            max_queue_size=2048,
            max_export_batch_size=512,
            schedule_delay_millis=5000,
        )
        provider.add_span_processor(trace_processor)
        trace.set_tracer_provider(provider)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    if logs_enabled:
        log_provider = LoggerProvider(resource=resource)

        otlp_log_exporter = OTLPLogExporter(
            endpoint=logs_endpoint,
            headers={"X-Scope-OrgID": os.getenv("GRAFANA_TENANT_ID", "1")}
            if os.getenv("GRAFANA_TENANT_ID")
            else None,
        )

        log_processor = BatchLogRecordProcessor(
            otlp_log_exporter,
            max_queue_size=2048,
            max_export_batch_size=512,
            schedule_delay_millis=5000,
        )
        log_provider.add_log_record_processor(log_processor)
        set_logger_provider(log_provider)
        root_logger.addHandler(LoggingHandler(level=logging.INFO, logger_provider=log_provider))

    if os.getenv("ENVIRONMENT") == "production":
        import json

        class JSONFormatter(logging.Formatter):
            def format(self, record: logging.LogRecord) -> str:
                log_obj = {
                    "timestamp": self.formatTime(record),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                    "pathname": record.pathname,
                    "lineno": record.lineno,
                }
                # Correlate JSON log records with the active span.
                span = trace.get_current_span()
                if span.is_recording():
                    ctx = span.get_span_context()
                    trace_id: int = ctx.trace_id
                    span_id: int = ctx.span_id
                    log_obj["trace_id"] = format(trace_id, '032x')
                    log_obj["span_id"] = format(span_id, '016x')
                return json.dumps(log_obj)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(console_handler)
    else:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        root_logger.addHandler(console_handler)

    if provider is not None:
        FastAPIInstrumentor().instrument_app(
            app,
            tracer_provider=provider,
            server_request_hook=server_request_hook,
        )

    logger = logging.getLogger(__name__)
    logger.info(
        "OpenTelemetry initialized",
        extra={
            "otlp_endpoint": otlp_endpoint,
            "service_name": resource.attributes.get("service.name"),
            "environment": resource.attributes.get("deployment.environment"),
        }
    )
