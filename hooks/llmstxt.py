"""Keep llms.txt output at the root of the default-language site."""

from mkdocs.plugins import event_priority


@event_priority(-110)
def on_config(config):
    llmstxt = config.plugins["llmstxt"]
    i18n = config.plugins["i18n"]

    for event_name in ("files", "post_build"):
        handler = getattr(llmstxt, f"on_{event_name}")
        handlers = config.plugins.events[event_name]
        if handler in handlers:
            handlers[handlers.index(handler)] = _default_language_only(handler, i18n)


def _default_language_only(handler, i18n):
    def run(*args, **kwargs):
        if i18n.is_default_language_build:
            return handler(*args, **kwargs)

    return run
