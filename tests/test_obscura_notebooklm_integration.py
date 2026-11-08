#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration Test: Obscura Harvester + Academic Enricher + Open-Notebook RIS Export
"""
import os
import sys
import unittest
from pathlib import Path

# Đảm bảo import từ thư mục gốc của Web Super
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.shared.obscura_harvester import obscura_harvester
from modules.shared.academic_enricher import academic_enricher
from modules.notebooklm.notebooklm_engine import open_notebook_engine
from modules.harvester.data_harvesting_engine import DataHarvestingEngine

class TestObscuraNotebookLMIntegration(unittest.TestCase):

    def test_01_obscura_availability(self):
        """Kiểm tra nhị phân Obscura có sẵn và hoạt động (bỏ qua an toàn nếu chưa cài đặt CLI)."""
        if not obscura_harvester.is_available():
            self.skipTest("Obscura CLI chưa được cài đặt trên môi trường máy hiện tại.")
        version = obscura_harvester.get_version()
        self.assertIn("obscura", version.lower())
        print(f"\n[OK] Obscura version: {version}")

    def test_02_academic_enricher_doi(self):
        """Kiểm tra làm giàu dữ liệu qua DOI (0 token AI)."""
        sample = {"title": "Sample", "url": "https://doi.org/10.5194/nhess-21-1473-2021"}
        enriched = academic_enricher.enrich(sample)
        self.assertIn("doi", enriched)
        self.assertEqual(enriched.get("year"), 2021)
        self.assertTrue(len(enriched.get("authors", [])) > 0)
        print(f"\n[OK] Enriched metadata: {enriched.get('title')[:60]}... ({enriched.get('year')})")

    def test_03_notebook_add_and_export_ris(self):
        """Kiểm tra tạo Notebook, nạp tài liệu và xuất tệp RIS chuẩn Zotero."""
        nb = open_notebook_engine.create_notebook("Test Obscura RIS Notebook", topic="Môi trường và Viễn thám")
        nb_id = nb["id"]
        
        # Nạp 1 tài liệu mẫu
        src = open_notebook_engine.add_source_from_raw(
            notebook_id=nb_id,
            title="Nghiên cứu xâm nhập mặn Đồng bằng Sông Cửu Long",
            content="Đồng bằng sông Cửu Long đang đối mặt với nguy cơ xâm nhập mặn nghiêm trọng do biến đổi khí hậu và thủy điện thượng nguồn. Độ mặn 4g/l xâm nhập sâu vào các nhánh sông chính.",
            author="Nguyễn Văn A, Trần Thị B",
            year="2024",
            doi="10.1234/env.vn.2024.01"
        )
        self.assertEqual(src["status"], "success")

        # Xuất file RIS
        ris_path = open_notebook_engine.export_notebook_to_ris(nb_id)
        self.assertTrue(ris_path.exists())
        self.assertTrue(ris_path.stat().st_size > 0)
        
        content = ris_path.read_text(encoding="utf-8")
        self.assertIn("TY  - JOUR", content)
        self.assertIn("TI  - Nghiên cứu xâm nhập mặn", content)
        self.assertIn("AU  - Nguyễn Văn A", content)
        self.assertIn("AU  - Trần Thị B", content)
        self.assertIn("PY  - 2024", content)
        self.assertIn("DO  - 10.1234/env.vn.2024.01", content)
        self.assertIn("ER  -", content)
        print(f"\n[OK] Đã xuất tệp RIS thành công tại: {ris_path}")

        # Dọn dẹp notebook test
        open_notebook_engine.delete_notebook(nb_id)

if __name__ == "__main__":
    unittest.main()
