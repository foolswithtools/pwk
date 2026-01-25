"""OpenTelemetry instrumentation setup for GPWK."""

import logging
import os
import structlog
from typing import Optional

from opentelemetry import trace, metrics, _logs
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, AggregationTemporality
from opentelemetry.sdk.metrics.view import View
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.instrumentation.requests import RequestsInstrumentor

from .models import GPWKConfig

# Global providers for shutdown
_meter_provider: Optional[MeterProvider] = None
_trace_provider: Optional[TracerProvider] = None
_logger_provider: Optional[LoggerProvider] = None


def _setup_minimal_logging() -> None:
    """
    Setup minimal logging without OpenTelemetry export.

    Used in CI/CD environments where telemetry export may hang.
    """
    # Setup structured logging without OTLP export
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=False,
    )

    # Configure console output
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=structlog.dev.ConsoleRenderer(),
        )
    )
    console_handler.setLevel(logging.INFO)

    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    if not any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers):
        root_logger.addHandler(console_handler)


def setup_telemetry(config: GPWKConfig) -> None:
    """
    Setup OpenTelemetry instrumentation.

    This configures:
    - Distributed tracing with OTLP export to Grafana Alloy
    - Metrics export to Grafana Alloy
    - Structured logging with trace context
    - Automatic instrumentation of requests library

    Args:
        config: GPWK configuration with OTLP endpoint
    """
    # Skip telemetry setup in CI/CD environments where export may fail
    # This prevents hanging on shutdown when Grafana Cloud is unreachable
    if os.getenv("CI") or os.getenv("GITHUB_ACTIONS"):
        _setup_minimal_logging()
        return

    # Create resource identifying this service
    resource = Resource(attributes={
        SERVICE_NAME: config.service_name,
        SERVICE_VERSION: "1.0.0",
        "deployment.environment": "development",
    })

    # Setup tracing
    global _trace_provider
    _trace_provider = TracerProvider(resource=resource)
    otlp_trace_exporter = OTLPSpanExporter(
        endpoint=config.otlp_endpoint,
        insecure=True  # Use insecure for local Alloy agent
    )
    _trace_provider.add_span_processor(
        BatchSpanProcessor(otlp_trace_exporter)
    )
    trace.set_tracer_provider(_trace_provider)

    # Setup metrics with CUMULATIVE temporality (required by Grafana Cloud)
    # Configure all instrument types to use CUMULATIVE temporality
    from opentelemetry.sdk.metrics._internal.instrument import (
        Counter, Histogram, UpDownCounter,
        ObservableCounter, ObservableGauge, ObservableUpDownCounter
    )

    cumulative_temporality = {
        Counter: AggregationTemporality.CUMULATIVE,
        UpDownCounter: AggregationTemporality.CUMULATIVE,
        Histogram: AggregationTemporality.CUMULATIVE,
        ObservableCounter: AggregationTemporality.CUMULATIVE,
        ObservableGauge: AggregationTemporality.CUMULATIVE,
        ObservableUpDownCounter: AggregationTemporality.CUMULATIVE,
    }

    otlp_metric_exporter = OTLPMetricExporter(
        endpoint=config.otlp_endpoint,
        insecure=True,
        preferred_temporality=cumulative_temporality
    )
    metric_reader = PeriodicExportingMetricReader(
        otlp_metric_exporter,
        export_interval_millis=30000  # Export every 30 seconds
    )
    global _meter_provider
    _meter_provider = MeterProvider(
        resource=resource,
        metric_readers=[metric_reader]
    )
    metrics.set_meter_provider(_meter_provider)

    # Setup logs export via OTLP
    global _logger_provider
    otlp_log_exporter = OTLPLogExporter(
        endpoint=config.otlp_endpoint,
        insecure=True
    )
    _logger_provider = LoggerProvider(resource=resource)
    _logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(otlp_log_exporter)
    )
    _logs.set_logger_provider(_logger_provider)

    # Attach OTLP logging handler to Python's root logger
    handler = LoggingHandler(
        level=logging.INFO,
        logger_provider=_logger_provider
    )
    logging.getLogger().addHandler(handler)

    # Instrument requests library automatically
    RequestsInstrumentor().instrument()

    # Setup structured logging with trace context
    # Use stdlib logging so OTLP handler can capture logs
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            _add_trace_context,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=False,
    )

    # Configure console formatter for pretty console output
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=structlog.dev.ConsoleRenderer(),
        )
    )
    console_handler.setLevel(logging.INFO)

    # Get root logger and configure it
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    # Only add console handler if not already present
    if not any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers if h != handler):
        root_logger.addHandler(console_handler)


def _add_trace_context(logger, method_name, event_dict):
    """Add trace context to log records."""
    span = trace.get_current_span()
    if span and span.get_span_context().is_valid:
        ctx = span.get_span_context()
        event_dict["trace_id"] = format(ctx.trace_id, "032x")
        event_dict["span_id"] = format(ctx.span_id, "016x")
    return event_dict


def get_tracer(name: str) -> trace.Tracer:
    """Get a tracer for a module."""
    return trace.get_tracer(name)


def get_meter(name: str) -> metrics.Meter:
    """Get a meter for a module."""
    return metrics.get_meter(name)


def shutdown_telemetry() -> None:
    """
    Shutdown telemetry and force flush all pending data.

    CRITICAL: This must be called before the process exits to ensure
    all metrics are exported. The PeriodicExportingMetricReader has
    a 30-second export interval, so metrics will be lost if the process
    exits before the interval fires.

    This function force-flushes:
    - All pending metrics
    - All pending traces
    - All pending logs

    In CI/CD environments, telemetry is disabled, so this is a no-op.
    """
    # Skip if running in CI/CD (telemetry was never set up)
    if os.getenv("CI") or os.getenv("GITHUB_ACTIONS"):
        return

    if _meter_provider:
        _meter_provider.force_flush()
        _meter_provider.shutdown()

    if _trace_provider:
        _trace_provider.force_flush()
        _trace_provider.shutdown()

    if _logger_provider:
        _logger_provider.force_flush()
        _logger_provider.shutdown()
