from typing import Literal

from pydantic import BaseModel


class ScanIssue(BaseModel):
    path: str
    reason: str
    severity: Literal["INFO", "WARNING", "ERROR"]
