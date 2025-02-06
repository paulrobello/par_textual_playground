from __future__ import annotations

from par_ai_core.llm_config import LlmConfig, llm_run_manager
from par_ai_core.llm_providers import LlmProvider
from rich.text import Text
from textual.app import App
from textual.binding import Binding
from textual.reactive import Reactive, reactive
from textual.suggester import Suggester, SuggestionReady
from textual.widgets import TextArea


class ParSuggest(Suggester):
    """Give completion suggestions via LLM."""

    def __init__(self, *, app: App, llm_config: LlmConfig | None = None) -> None:
        """Creates a suggester based off of a given iterable of possibilities.

        Args:
            llm_config: An optional LlmConfig to use for LLM inference.
        """
        super().__init__(case_sensitive=True)
        self.llm_config = llm_config or LlmConfig(provider=LlmProvider.OLLAMA, model_name="llama3.2:latest")
        self.llm = self.llm_config.build_llm_model()
        self.app = app

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
        context, last_line = "\n".join(lines[:-1]), lines[-1]
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
Do not generate more than 5 words.
Your continuation should not start with the existing current_line
</instructions>
            """.strip()

        self.app.logit(prompt)
        result = await self.llm.ainvoke(
            prompt,
            config=llm_run_manager.get_runnable_config(self.llm.name),
        )

        return str(result.content.rstrip())


class ParTextArea(TextArea):
    """A TextArea widget with additional features for autocomplete."""

    BINDINGS = [
        Binding("ctrl+t", "accept_suggestion", "Suggestion", show=True),
    ]

    suggester: Suggester | None = None
    _suggestion = reactive("")
    _line_string: Reactive[str] = reactive("", init=False)

    def __init__(self, *args, suggester: Suggester | None = None, **kwargs) -> None:
        if "tab_behavior" not in kwargs:
            kwargs["tab_behavior"] = "indent"
        super().__init__(*args, **kwargs)
        self.suggester = suggester

    def _generate_suggestion(self) -> None:
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
        self.app.set_info(f"Cursor: {self.cursor_location}")

    async def _on_suggestion_ready(self, event: SuggestionReady) -> None:
        """Handle suggestion messages and set the suggestion for preview."""
        self._suggestion = event.suggestion
        self.app.logit({"value": event.value, "suggestion": event.suggestion})

    def action_accept_suggestion(self) -> None:
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
        line_string = self.document.get_line(line_index)

        line_num, row_num = self.cursor_location
        if line_index == line_num:
            suggestion = self._suggestion
            tl = line_string[0:row_num]
            tr = line_string[row_num:]
            return Text.assemble(tl, (suggestion, "italic red"), tr, end="")
        return Text(line_string, end="")
