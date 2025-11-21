from types import SimpleNamespace
from dataclasses import dataclass


@dataclass
class Keyboards:
    grm: str
    start: str


@dataclass
class Types:
    inline: str
    row: str


myKeyboards = Keyboards(
    grm="/grm",
    start="/start",
)


@dataclass
class Keyboards:
    grm: str
    start: str


myTypes = Types(
    inline="inline",
    row="row",
)

user_states = {}
