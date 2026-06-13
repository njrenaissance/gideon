"""RedactionService — keyword replacement and metadata scrubbing for PDF and DOCX."""

from __future__ import annotations

import contextlib
import io
import re


class RedactionService:
    """Replace a keyword list in PDF/DOCX files and scrub document metadata."""

    def build_keyword_map(self, keywords: frozenset[str]) -> dict[str, str]:
        """Assign deterministic ``[REDACTED_N]`` placeholders to each keyword.

        Deduplicates case-insensitively so ``John`` and ``john`` map to the
        same placeholder.  Sorted before assignment for a stable ordering.
        """
        seen: dict[str, str] = {}  # lowercase -> placeholder
        counter = 1
        for kw in sorted(keywords):
            lower = kw.lower()
            if lower not in seen:
                seen[lower] = f"[REDACTED_{counter}]"
                counter += 1
        # Build final map: original casing -> placeholder
        result: dict[str, str] = {}
        for kw in sorted(keywords):
            result[kw] = seen[kw.lower()]
        return result

    def redact_text(
        self, text: str, keyword_map: dict[str, str]
    ) -> tuple[str, dict[str, int]]:
        """Replace keywords in plain text.

        Sorts keywords longest-first to prevent shorter substrings from
        shadowing longer ones.  Returns ``(redacted_text, {placeholder: count})``.
        """
        counts: dict[str, int] = {}
        for original in sorted(keyword_map, key=len, reverse=True):
            placeholder = keyword_map[original]
            pattern = re.compile(r"\b" + re.escape(original) + r"\b", re.IGNORECASE)
            new_text, n = pattern.subn(placeholder, text)
            text = new_text
            if n:
                counts[placeholder] = counts.get(placeholder, 0) + n
        return text, counts

    def redact_pdf(
        self, file_bytes: bytes, keyword_map: dict[str, str]
    ) -> tuple[bytes, dict[str, int], dict[str, str]]:
        """Redact keywords in a PDF using PyMuPDF.

        Returns ``(redacted_bytes, {placeholder: count}, original_metadata)``.
        Metadata is captured before scrubbing so the manifest records what
        was present in the original file.
        """
        import fitz  # type: ignore[import-untyped]  # pymupdf

        doc = fitz.open(stream=file_bytes, filetype="pdf")
        original_metadata: dict[str, str] = {k: v for k, v in doc.metadata.items() if v}

        # Scrub metadata fields
        doc.set_metadata({})

        counts: dict[str, int] = {}
        # Sort keywords longest-first to avoid partial-match shadowing
        for original in sorted(keyword_map, key=len, reverse=True):
            placeholder = keyword_map[original]
            for page in doc:
                rects = page.search_for(original, quads=False)
                for rect in rects:
                    page.add_redact_annot(
                        rect,
                        text=placeholder,
                        text_color=(0, 0, 0),
                        fill=(1, 1, 1),
                    )
                    counts[placeholder] = counts.get(placeholder, 0) + 1
                page.apply_redactions()

        buf = io.BytesIO()
        doc.save(buf, garbage=4, deflate=True)
        doc.close()
        return buf.getvalue(), counts, original_metadata

    def redact_docx(
        self, file_bytes: bytes, keyword_map: dict[str, str]
    ) -> tuple[bytes, dict[str, int], dict[str, str]]:
        """Redact keywords in a DOCX using python-docx.

        Returns ``(redacted_bytes, {placeholder: count}, original_metadata)``.
        Works at the run level; keywords spanning multiple runs may not be
        caught (acceptable for MVP).
        """
        from docx import Document
        from docx.oxml.ns import qn

        doc = Document(io.BytesIO(file_bytes))

        # Capture metadata before scrubbing
        props = doc.core_properties
        original_metadata: dict[str, str] = {}
        for attr in (
            "author",
            "last_modified_by",
            "subject",
            "description",
            "category",
        ):
            val = getattr(props, attr, None)
            if val:
                original_metadata[attr] = str(val)

        # Scrub metadata
        for attr in ("author", "last_modified_by", "subject", "description"):
            with contextlib.suppress(Exception):
                setattr(props, attr, "")

        counts: dict[str, int] = {}

        def _redact_runs(runs: list) -> None:  # type: ignore[type-arg]
            for run in runs:
                for original in sorted(keyword_map, key=len, reverse=True):
                    placeholder = keyword_map[original]
                    pattern = re.compile(
                        r"\b" + re.escape(original) + r"\b", re.IGNORECASE
                    )
                    new_text, n = pattern.subn(placeholder, run.text)
                    if n:
                        run.text = new_text
                        counts[placeholder] = counts.get(placeholder, 0) + n

        for para in doc.paragraphs:
            _redact_runs(para.runs)

        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        _redact_runs(para.runs)

        # Headers and footers
        for section in doc.sections:
            for hf in (
                section.header,
                section.footer,
                section.even_page_header,
                section.even_page_footer,
            ):
                if hf is not None:
                    with contextlib.suppress(Exception):
                        for para in hf.paragraphs:
                            _redact_runs(para.runs)

        # Remove custom XML properties that may carry author info
        with contextlib.suppress(Exception):
            cp = doc.part.package.part_related_by(
                "http://schemas.openxmlformats.org/officeDocument/2006/"
                "relationships/custom-properties"
            )
            cp._element.getparent().remove(cp._element)  # noqa: SLF001

        # Strip rsid (revision save identifiers) that embed author info
        for el in doc.element.body.iter():
            for attr in list(el.attrib):
                if qn("w:rsidR") in attr or "rsid" in attr.lower():
                    del el.attrib[attr]

        buf = io.BytesIO()
        doc.save(buf)
        return buf.getvalue(), counts, original_metadata
