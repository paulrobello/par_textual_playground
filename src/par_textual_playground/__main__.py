from pathlib import Path

import clipman
from dotenv import load_dotenv

from par_textual_playground import __application_binary__
from par_textual_playground.app import ParApp

load_dotenv(Path(f"~/.{__application_binary__}.env").expanduser())

try:
    clipman.init()
except Exception as _:
    pass


def run() -> None:
    """Run the application."""
    ParApp().run()


if __name__ == "__main__":
    run()
