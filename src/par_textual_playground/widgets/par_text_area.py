from __future__ import annotations

from textwrap import dedent
from typing import Literal

from par_ai_core.llm_config import LlmConfig, llm_run_manager
from par_ai_core.llm_providers import LlmProvider
from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.reactive import Reactive, reactive
from textual.suggester import Suggester, SuggestionReady
from textual.widgets import Static, TextArea


class ParSuggest(Suggester):
    """Give completion suggestions via LLM."""

    def __init__(
        self,
        *,
        app: App,
        max_context_tokens: int = 1_500,
        max_words: int = 5,
        llm_config: LlmConfig | None = None,
        debug: bool = False,
    ) -> None:
        """Creates a suggester based off of a given iterable of possibilities.

        Args:
            app: The app to use for logging.
            max_context_tokens: The maximum size of context in tokens to provide to the LLM.
            max_words: The max number of words to generate for each suggestion.
            llm_config: An optional LlmConfig to use for LLM inference.
        """
        super().__init__(case_sensitive=True)
        self.app = app
        self.debug = debug
        self.llm_config = llm_config or LlmConfig(provider=LlmProvider.OLLAMA, model_name="llama3.2:latest")
        self._llm = self.llm_config.build_llm_model()
        self.max_words = max_words
        self.max_context_tokens = max_context_tokens

    async def get_suggestion(self, value: str) -> str | None:
        """Gets a completion from the given possibilities.

        Args:
            value: The current value.

        Returns:
            A valid completion suggestion or `None`.
        """
        if not value.strip():
            return None
        lines = value.splitlines()
        last_line = lines.pop()
        context = "\n".join(lines)
        while 0 < self.max_context_tokens < len(context) // 3:
            context = "\n".join(lines[1:])
            lines = lines[1:]
        prompt = f"""
<context>
{context}
</context>
<current_line>
{last_line}
</current_line>
<instructions>
The context and current_line has been written by the user.
You will continue writing the next few words of the text as if you were the original writer.
Do not begin the text with `...` and don't summarize the text.
Do not explain the text or the completion.
Do not generate more than {self.max_words} words.
Your continuation should not start with the existing current_line.
</instructions>
            """.strip()

        if self.debug and hasattr(self.app, "logit"):
            self.app.logit(prompt)  # type: ignore
        result = await self._llm.ainvoke(
            prompt,
            config=llm_run_manager.get_runnable_config(self._llm.name),
        )

        return " ".join(result.content.rstrip().split(" ")[: self.max_words])


class ParTextArea(TextArea):
    """A TextArea widget with additional features for autocomplete."""

    BINDINGS = [
        Binding("ctrl+t", "accept_suggestion", "Suggestion", show=True),
    ]

    suggester: Suggester | None = None
    _suggestion: Reactive[str] = reactive("")
    _line_string: Reactive[str] = reactive("", init=False)
    suggestion_mode: Reactive[Literal["inline", "float"]] = reactive("inline", init=False)

    def __init__(
        self,
        *args,
        suggester: Suggester | None = None,
        suggestion_mode: Literal["inline", "float"] = "inline",
        debug: bool = False,
        **kwargs,
    ) -> None:
        if "tab_behavior" not in kwargs:
            kwargs["tab_behavior"] = "indent"
        super().__init__(*args, **kwargs)
        self.suggester = suggester
        self.debug = debug
        self.suggestion_mode = suggestion_mode
        self.float_box = Static("", id="float_box")

    def compose(self) -> ComposeResult:
        yield self.float_box

    def _generate_suggestion(self) -> None:
        """Generate a completion suggestion."""
        if not self.suggester:
            return
        line_num, row_num = self.cursor_location
        context = self.document.lines[: line_num + 1]
        context[-1] = context[-1][:row_num]
        self._line_string = "\n".join(context)
        self._suggestion = ""
        if self._line_string:
            self.run_worker(self.suggester._get_suggestion(self, self._line_string))

    # def _on_text_area_changed(self) -> None:
    #     self._check_suggestion()

    def _on_text_area_selection_changed(self, event: TextArea.SelectionChanged) -> None:
        """Handle text area selection."""
        if self.debug and hasattr(self.app, "set_info"):
            self.app.set_info(  # type: ignore
                dedent(
                    f"""
                    Cursor: {self.cursor_location}
                    Cursor SO: {self.cursor_screen_offset}
                    Context Tokens: {len(self.document.text) // 3}
                    """
                ).strip()
            )
        self._suggestion = ""

    async def _on_suggestion_ready(self, event: SuggestionReady) -> None:
        """Handle suggestion messages and set the suggestion for preview."""
        self._suggestion = event.suggestion
        if self.debug and hasattr(self.app, "logit"):
            self.app.logit({"value": event.value, "suggestion": event.suggestion})  # type: ignore

    def _watch__suggestion(self) -> None:
        """Watch for changes to the suggestion and update the text area."""
        self.float_box.update(self._suggestion)
        self.float_box.display = len(self._suggestion) > 0
        self.call_after_refresh(self.update_float_pos)

    def update_float_pos(self) -> None:
        if self.float_box.display:
            ta_size = self.size
            box_size = self.float_box.size
            x_offset_max = ta_size.width - 2 - box_size.width
            y_offset_max = ta_size.height - 2 - box_size.height
            co = self.cursor_screen_offset
            self.app.set_info(  # type: ignore
                dedent(
                    f"""
                    cursor so: {co}
                    offset max: {[x_offset_max, y_offset_max]}
                    edit size: {[ta_size.width - 2, ta_size.height - 2]}
                    box_size {[box_size.width, box_size.height]}
                    """
                ).strip()
            )

            self.float_box.styles.offset = (min(x_offset_max, co.x - 1), min(y_offset_max, co.y - 1))

    def action_accept_suggestion(self) -> None:
        """Accept the suggestion and insert it into the text area."""
        suggestion = self._suggestion
        if not suggestion:
            self._generate_suggestion()
            return
        self._suggestion = ""
        self.insert(suggestion)

    def get_line(self, line_index: int) -> Text:
        """Retrieve the line at the given line index.

        You can stylize the Text object returned here to apply additional
        styling to TextArea content.

        Args:
            line_index: The index of the line.

        Returns:
            A `rich.Text` object containing the requested line.
        """
        if self.suggestion_mode != "inline":
            return super().get_line(line_index)

        line_string = self.document.get_line(line_index)

        line_num, row_num = self.cursor_location
        if line_index == line_num:
            suggestion = self._suggestion
            tl = line_string[0:row_num]
            tr = line_string[row_num:]
            return Text.assemble(tl, (suggestion, "italic"), tr, end="")
        return Text(line_string, end="")
