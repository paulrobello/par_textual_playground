from pathlib import Path

from rich.console import ConsoleRenderable, RichCast
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, RichLog, TabbedContent, TextArea

from par_textual_playground.widgets.par_markdown import ParMarkdown
from par_textual_playground.widgets.par_text_area import ParSuggest, ParTextArea


class ParApp(App[None]):
    CSS_PATH = "app.tcss"

    def __init__(self) -> None:
        super().__init__()
        my_suggester = ParSuggest(app=self, max_words=20, debug=True)

        self.editor_float = ParTextArea(
            id="editor",
            text=(Path(__file__).parent / "story.md").read_text(),
            suggester=my_suggester,
            debug=True,
            suggestion_mode="float",
        )
        self.editor_inline = ParTextArea(
            id="editor",
            text=(Path(__file__).parent / "story.md").read_text(),
            suggester=my_suggester,
            debug=True,
            suggestion_mode="inline",
        )
        self.md = ParMarkdown((Path(__file__).parent / "fence.md").read_text(), id="mdv")
        self.logview = RichLog(id="log")
        self.logview.border_title = "Log"
        self.info = TextArea(id="info")
        self.info.border_title = "Debug Info"

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        self.title = "Par Widget Test"
        yield Header()
        yield Footer()
        with Horizontal(id="main"):
            # yield self.mdv
            with TabbedContent("Suggest Float", "Suggest Inline", "Markdown Fence", id="tc"):
                yield self.editor_float
                yield self.editor_inline
                yield self.md
            with Vertical():
                yield self.info
                yield self.logview
        self.editor_float.focus()

    def logit(self, msg: ConsoleRenderable | RichCast | str | object) -> None:
        """Log a message to the RichLog widget."""
        self.logview.write(msg)

    def set_info(self, msg: str) -> None:
        """Set the text of the info TextArea."""
        self.info.text = msg
