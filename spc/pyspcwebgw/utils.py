import logging


_LOGGER = logging.getLogger(__name__)


def _load_enum(enum, value, default=None):
    """Parse an enum with fallback."""
    try:
        return enum(value)
    except ValueError:
        return default
