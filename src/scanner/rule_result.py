from dataclasses import dataclass
from typing import Any


@dataclass
class RuleResult:
    name: str
    passed: bool
    actual: dict[str, Any]