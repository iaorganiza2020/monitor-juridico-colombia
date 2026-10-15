"""Conservadores extractores HTML. No adivinan identificadores ni vigencia."""
from __future__ import annotations

from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

from .models import LegalRecord


class _Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._href: str | None = None
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            self._href = dict(attrs).get("href")
            self._text = []

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._href is not None:
            self.links.append((self._href, " ".join(" ".join(self._text).split())))
            self._href = None
            self._text = []


def _links(html: str) -> list[tuple[str, str]]:
    parser = _Links()
    parser.feed(html)
    return parser.links


def _date_from_dmy(text: str) -> str | None:
    import re
    match = re.search(r"\b(\d{2})-(\d{2})-(\d{4})\b", text)
    if not match:
        return None
    day, month, year = match.groups()
    return f"{year}-{month}-{day}"


class SupremePenalBulletins:
    source_id = "csj_penal_boletines"
    base_url = "https://cortesuprema.gov.co/sala-de-casacion-penal-relatoria-boletines/"

    def extract(self, html: str) -> list[LegalRecord]:
        records = []
        for href, title in _links(html):
            if "boletín" not in title.lower() and "boletin" not in title.lower():
                continue
            url = urljoin(self.base_url, href)
            if urlparse(url).hostname not in {"cortesuprema.gov.co", "archivodigitalapi.cortesuprema.gov.co"}:
                continue
            records.append(LegalRecord(
                source_id=self.source_id,
                record_type="boletin_jurisprudencial",
                corporation="Corte Suprema de Justicia",
                chamber="Sala de Casación Penal",
                identifier=None,
                docket=None,
                decision_date=None,
                publication_date=_date_from_dmy(title),
                title=title,
                topic=None,
                official_url=url,
                verification_status="referencia_oficial_boletin",
                verification_note="Enlace y rótulo publicados en la página oficial; no equivale al texto íntegro de cada providencia reseñada.",
                text_available=False,
            ))
        return records


class ConstitutionalRelatoria:
    """Extrae providencias si el HTML oficial incluye enlaces directos identificables."""
    source_id = "c_constitucional_relatoria"
    base_url = "https://www.corteconstitucional.gov.co/relatoria/"

    def extract(self, html: str) -> list[LegalRecord]:
        import re
        records = []
        pattern = re.compile(r"/(?:relatoria/)?(\d{4})/((?:C|T|SU|A)-?[^/?#]+\.(?:htm|html|pdf))$", re.I)
        for href, title in _links(html):
            url = urljoin(self.base_url, href)
            if urlparse(url).hostname != "www.corteconstitucional.gov.co":
                continue
            match = pattern.search(urlparse(url).path)
            if not match:
                continue
            year, file_name = match.groups()
            identifier = file_name.rsplit(".", 1)[0]
            records.append(LegalRecord(
                source_id=self.source_id,
                record_type="providencia",
                corporation="Corte Constitucional",
                chamber=None,
                identifier=identifier,
                docket=None,
                decision_date=None,
                publication_date=None,
                title=title or identifier,
                topic=None,
                official_url=url,
                verification_status="referencia_oficial_texto_pendiente",
                verification_note=f"Enlace individual hallado en índice oficial ({year}); texto y fechas requieren lectura directa.",
                text_available=False,
            ))
        return records


class PenalNormativeCatalog:
    """Reconoce normas penales explícitamente enlazadas en catálogos oficiales."""
    source_id = "normativa_penal_catalogos"
    official_hosts = {"www.suin-juriscol.gov.co", "suin-juriscol.gov.co", "svrpubindc.imprenta.gov.co", "www.imprenta.gov.co"}

    def extract(self, html: str, base_url: str) -> list[LegalRecord]:
        import re
        records = []
        law = re.compile(r"\b(ley|decreto legislativo|decreto|acto legislativo)\s+(\d+)\s+de\s+(\d{4})\b", re.I)
        for href, title in _links(html):
            url = urljoin(base_url, href)
            if urlparse(url).hostname not in self.official_hosts:
                continue
            match = law.search(title)
            if not match:
                continue
            label, number, year = match.groups()
            records.append(LegalRecord(
                source_id=self.source_id,
                record_type="norma_referenciada",
                corporation="Estado colombiano",
                chamber=None,
                identifier=f"{label.title()} {number} de {year}",
                docket=None,
                decision_date=None,
                publication_date=None,
                title=title,
                topic="posible materia penal; clasificación requiere revisión",
                official_url=url,
                verification_status="referencia_oficial_vigencia_pendiente",
                verification_note="Referencia encontrada en portal oficial; no afirma vigencia ni que la norma sea penal sin revisar el texto y sus afectaciones.",
                text_available=False,
            ))
        return records


def run_metadata() -> dict[str, str]:
    return {"checked_at_utc": datetime.now(timezone.utc).isoformat(), "run_status": "metadata_only"}
