from rich.theme import Theme

MARK_FAILED = "✗"
MARK_SENT = "✓"
STYLE_BORDER = "view.border"
STYLE_ERROR = "view.error"
STYLE_FAILURE = "view.failure"
STYLE_HINT = "view.hint"
STYLE_KEY = "view.key"
STYLE_SUCCESS = "view.success"
STYLE_TITLE = "view.title"

THEME = Theme(
    {
        STYLE_BORDER: "dim",
        STYLE_ERROR: "red",
        STYLE_FAILURE: "red",
        STYLE_HINT: "dim",
        STYLE_KEY: "bold cyan",
        STYLE_SUCCESS: "green",
        STYLE_TITLE: "bold",
    }
)
