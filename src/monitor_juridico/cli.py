import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from .extractors import ConstitutionalRelatoria, PenalNormativeCatalog, SupremePenalBulletins

SOURCES = {
    "csj_penal": "https://cortesuprema.gov.co/sala-de-casacion-penal-relatoria-boletines/",
    "corte_constitucional": "https://www.corteconstitucional.gov.co/relatoria/",
    "suin": "https://www.suin-juriscol.gov.co/suin/",
    "diario_oficial": "https://svrpubindc.imprenta.gov.co/diario/view/diarioficial/consultarDiarios.xhtml",
}


def fetch(url: str, timeout: int = 12) -> tuple[int | None, str | None, str | None]:
    request = urllib.request.Request(url, headers={"User-Agent": "monitor-juridico-colombia/0.1 (+public-interest; low-rate; contact configured by operator)"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return response.status, response.read().decode(charset, "replace"), None
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return None, None, f"{type(exc).__name__}: {exc}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Consulta de solo lectura a fuentes oficiales identificadas.")
    parser.add_argument("--output", type=Path, default=Path("reports/run.json"))
    parser.add_argument("--timeout", type=int, default=12)
    args = parser.parse_args()
    status: dict[str, dict] = {}
    rows = []
    for name, url in SOURCES.items():
        code, html, error = fetch(url, args.timeout)
        status[name] = {"url": url, "http_status": code, "ok": html is not None, "error": error}
        if html is None:
            continue
        if name == "csj_penal": rows.extend(r.to_dict() for r in SupremePenalBulletins().extract(html))
        if name == "corte_constitucional": rows.extend(r.to_dict() for r in ConstitutionalRelatoria().extract(html))
        if name in {"suin", "diario_oficial"}:
            rows.extend(r.to_dict() for r in PenalNormativeCatalog().extract(html, url))
    result = {
        "run_at_utc": datetime.now(timezone.utc).isoformat(),
        "overall_status": "partial" if any(not x["ok"] for x in status.values()) else "ok",
        "sources": status,
        "records": rows,
        "record_count": len(rows),
        "notice": "Los registros de índice o boletín no se elevan a texto íntegro ni a conclusión sobre vigencia o cambio de precedente.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("overall_status", "record_count", "sources")}, ensure_ascii=False, indent=2))
    if result["overall_status"] != "ok":
        sys.exit(2)


if __name__ == "__main__":
    main()
