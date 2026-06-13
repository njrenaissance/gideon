"""Redaction result models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class KeywordReplacement:
    original: str
    placeholder: str
    occurrence_count: int


@dataclass(frozen=True)
class RedactionManifest:
    document_id: str
    metadata_removed: dict[str, str]
    keyword_replacements: list[KeywordReplacement] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "document_id": self.document_id,
            "metadata_removed": self.metadata_removed,
            "keyword_replacements": [
                {
                    "original": r.original,
                    "placeholder": r.placeholder,
                    "occurrence_count": r.occurrence_count,
                }
                for r in self.keyword_replacements
            ],
            "total_replacements": sum(
                r.occurrence_count for r in self.keyword_replacements
            ),
        }
