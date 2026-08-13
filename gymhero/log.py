"""Structured (JSON) logging: stdlib loggers routed through structlog."""

import logging
import sys

import structlog

_configured = False


def configure_logging(level: str = "INFO") -> None:
    """Render stdlib + structlog logs as JSON on stdout. Idempotent."""
    global _configured
    if _configured:
        return

    structlog.configure(
        processors=[structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.contextvars.merge_contextvars,  # request_id etc.
            structlog.stdlib.ExtraAdder(),
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.JSONRenderer(),
        ],
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    for noisy in ("sqlalchemy.engine", "asyncio", "aiosqlite"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    _configured = True


def get_logger(name: str | None = None) -> logging.Logger:
    configure_logging()
    return logging.getLogger(name)
