"""Widget Test."""

from __future__ import annotations

import os

from par_textual_playground.app import ParApp

__author__ = "Paul Robello"
__credits__ = ["Paul Robello"]
__maintainer__ = "Paul Robello"
__email__ = "probello@gmail.com"
__version__ = "0.1.0"
__application_title__ = "PAR Textual Playground"
__application_binary__ = "ptp"
__licence__ = "MIT"


os.environ["USER_AGENT"] = f"{__application_title__} {__version__}"


__all__: list[str] = [
    "__author__",
    "__credits__",
    "__maintainer__",
    "__email__",
    "__version__",
    "__application_binary__",
    "__licence__",
    "__application_title__",
    "ParApp",
]
