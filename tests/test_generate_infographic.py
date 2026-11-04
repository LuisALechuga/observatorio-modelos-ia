import sys
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
import re

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from generate_infographic import latest_models, build_svg, declared_date


def model(name, date=None, provider="openai", **extras):
    return dict(id=name, name=name, release_date=date, provider_id=provider, **extras)


class SelectionTests(unittest.TestCase):
    def test_home_image_assets_exist_inside_published_folder(self):
        site = Path(__file__).resolve().parents[1] / "site"
        page = (site / "index.html").read_text(encoding="utf-8")
        references = re.findall(r'(?:src|href)="(assets/[^"?#]+)', page)
        self.assertTrue(references)
        for reference in references:
            self.assertTrue((site / reference).is_file(), f"Falta imagen publicable: {reference}")

    def test_newest_three_even_without_validation_or_active_status(self):
        models = [model("old", "2025-01-01"), model("new", "2026-10-01"),
                  model("third", "2026-08-01", status="deprecated"),
                  model("second", "2026-09-01", validated=False),
                  model("reseller", "2027-01-01", provider="reseller")]
        self.assertEqual([m["name"] for m in latest_models(models, "openai")], ["new", "second", "third"])

    def test_missing_dates_last_and_fewer_records_do_not_invent_models(self):
        result = latest_models([model("unknown", "invalid"), model("dated", "2026-01-01")], "openai")
        self.assertEqual([m["name"] for m in result], ["dated", "unknown"])
        self.assertEqual(declared_date(result[-1]), "Sin fecha declarada")
        self.assertEqual(latest_models([], "openai"), [])

    def test_aliases_and_ties(self):
        models = [model("A (latest)", "2026-01-01"), model("A", "2026-01-01"), model("B", "2026-01-01")]
        self.assertEqual([m["name"] for m in latest_models(models, "openai")], ["A", "B"])

    def test_svg_is_valid_and_escapes_model_names(self):
        svg = build_svg([("openai", "OpenAI", [model('A & <B>', "2026-01-01")])], "04/11/2026 20:00 UTC")
        root = ET.fromstring(svg)
        text = "".join(root.itertext())
        self.assertIn("A & <B>", text)
        self.assertIn("No validado", text)
        self.assertIn("04/11/2026", text)


if __name__ == "__main__":
    unittest.main()
