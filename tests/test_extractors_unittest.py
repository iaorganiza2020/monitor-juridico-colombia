import unittest

from monitor_juridico.extractors import ConstitutionalRelatoria, PenalNormativeCatalog, SupremePenalBulletins


class ExtractorTests(unittest.TestCase):
    def test_supreme_bulletin_is_not_decision_text(self):
        html = '<a href="https://archivodigitalapi.cortesuprema.gov.co/boletin.pdf">Boletín septiembre 2026 (08-10-2026)</a>'
        row, = SupremePenalBulletins().extract(html)
        self.assertEqual(row.publication_date, "2026-10-08")
        self.assertEqual(row.verification_status, "referencia_oficial_boletin")
        self.assertFalse(row.text_available)
        self.assertIsNone(row.identifier)

    def test_constitutional_extractor_rejects_unofficial_host(self):
        html = ('<a href="https://www.corteconstitucional.gov.co/relatoria/2026/C-101-26.htm">C-101/26</a>'
                '<a href="https://example.org/relatoria/2026/C-102-26.htm">C-102/26</a>')
        rows = ConstitutionalRelatoria().extract(html)
        self.assertEqual([r.identifier for r in rows], ["C-101-26"])
        self.assertFalse(rows[0].text_available)

    def test_normative_reference_does_not_claim_validity(self):
        html = '<a href="https://www.suin-juriscol.gov.co/viewDocument.asp?id=1">Ley 906 de 2004</a>'
        row, = PenalNormativeCatalog().extract(html, "https://www.suin-juriscol.gov.co/suin/")
        self.assertEqual(row.identifier, "Ley 906 de 2004")
        self.assertIn("vigencia_pendiente", row.verification_status)

    def test_non_official_normative_links_are_ignored(self):
        html = '<a href="https://example.org/doc">Ley 599 de 2000</a>'
        self.assertEqual(PenalNormativeCatalog().extract(html, "https://example.org"), [])


if __name__ == "__main__":
    unittest.main()
