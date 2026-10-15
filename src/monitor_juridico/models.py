from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class LegalRecord:
    source_id: str
    record_type: str
    corporation: str
    chamber: str | None
    identifier: str | None
    docket: str | None
    decision_date: str | None
    publication_date: str | None
    title: str
    topic: str | None
    official_url: str
    verification_status: str
    verification_note: str
    text_available: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
