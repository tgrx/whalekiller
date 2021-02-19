import sentry_sdk

from framework.config import settings

_configured = False


def configure():
    global _configured
    if _configured:
        return

    if not settings.MODE_DEBUG and settings.SENTRY_DSN:
        sentry_sdk.init(settings.SENTRY_DSN, traces_sample_rate=1.0)

    _configured = True
