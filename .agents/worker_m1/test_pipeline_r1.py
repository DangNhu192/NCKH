# .agents/worker_m1/test_pipeline_r1.py
import os
import sys
import unittest

# Ensure project root is in path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from modules.harvester.data_harvesting_engine import data_harvester
from modules.pipeline.pipeline_engine import pipeline_engine


class TestPipelineR1(unittest.TestCase):
    def setUp(self):
        self.topic = "Ứng dụng Trí tuệ Nhân tạo và Học sâu trong Chẩn đoán Ung thư Phổi"

    def test_01_research_trends(self):
        """Test Research Trends retrieval from OpenAlex, EuropePMC, arXiv"""
        print("\n[TEST 1] Testing fetch_research_trends...")
        trends = data_harvester.fetch_research_trends(self.topic, "deep learning lung cancer diagnosis")
        
        self.assertIn("growth_metrics", trends)
        self.assertIn("yearly_distribution", trends)
        self.assertIn("total_papers_indexed", trends)
        self.assertGreater(trends["total_papers_indexed"], 0)
        
        yearly = trends["yearly_distribution"]
        self.assertEqual(len(yearly), 7)
        years = [y["year"] for y in yearly]
        self.assertEqual(years, ["2019", "2020", "2021", "2022", "2023", "2024", "2025"])
        
        cagr = trends["growth_metrics"]["cagr_percent"]
        print(f"  -> Total papers: {trends['total_papers_indexed']}, CAGR: {cagr}%, Peak: {trends['growth_metrics']['peak_year']}")
        self.assertIsInstance(cagr, (int, float))

    def test_02_evidence_vault_multi_format_ingestion(self):
        """Test Multi-format Ingestion (.docx, .md, .pdf, .txt) into Evidence Vault"""
        print("\n[TEST 2] Testing Evidence Vault Multi-Format Ingestion...")
        pipeline_engine.clear_vault()
        
        # Test markdown ingestion
        md_content = b"""# Nghien Cuu Ve Tri Tue Nhan Tao Trong Y Te
Tac gia: Nguyen Van A, Tran Van B (2024)
DOI: 10.1016/j.lungcancer.2024.01.002
Chung toi phat trien mo hinh Vision Transformer dat do chinh xac 98.5% tren tap du lieu LIDC-IDRI.
"""
        item_md = pipeline_engine.ingest_document_to_vault(md_content, "test_article.md")
        self.assertEqual(item_md["format"], "md")
        self.assertIn("10.1016/j.lungcancer.2024.01.002", item_md["doi"])
        
        # Test plain text ingestion
        txt_content = b"AI and Lung Cancer Analysis\nAuthor: John Doe et al. (2023)\nDOI: 10.1109/TBME.2023.123456\nDeep neural networks achieved 96.2% sensitivity."
        item_txt = pipeline_engine.ingest_document_to_vault(txt_content, "clinical_notes.txt")
        self.assertEqual(item_txt["format"], "txt")
        
        vault_items = pipeline_engine.get_vault_items()
        self.assertEqual(len(vault_items), 2)
        print(f"  -> Successfully ingested 2 items into Evidence Vault (Total: {len(vault_items)})")
        
        # Test remove item
        removed = pipeline_engine.remove_vault_item(item_txt["id"])
        self.assertTrue(removed)
        self.assertEqual(len(pipeline_engine.get_vault_items()), 1)
        print("  -> Successfully removed 1 item from Vault")

    def test_03_seven_step_sequential_pipeline(self):
        """Test all 7 steps of PipelineEngine sequentially"""
        print("\n[TEST 3] Testing 7-Step Sequential Pipeline Execution...")
        
        # Step 1: Scope PICO & Trends
        res1 = pipeline_engine.run_step(1, self.topic, {"language": "en"})
        self.assertEqual(res1["status"], "success")
        self.assertEqual(res1["step_no"], 1)
        self.assertIn("research_trends", res1)
        self.assertIn("scope", res1)
        print("  -> Step 1 (Scope PICO & Trends): SUCCESS")
        
        # Step 2: Evidence Vault
        res2 = pipeline_engine.run_step(2, self.topic, {"max_papers": 3, "language": "en"})
        self.assertEqual(res2["status"], "success")
        self.assertEqual(res2["step_no"], 2)
        self.assertIn("vault_items", res2)
        self.assertGreater(len(res2["vault_items"]), 0)
        print(f"  -> Step 2 (Evidence Vault Lock): SUCCESS ({len(res2['vault_items'])} items locked)")
        
        # Step 3: Knowledge Sync & Matrix
        res3 = pipeline_engine.run_step(3, self.topic, {"saved_papers": res2["vault_items"]})
        self.assertEqual(res3["status"], "success")
        self.assertEqual(res3["step_no"], 3)
        self.assertIn("sync_result", res3)
        print("  -> Step 3 (Knowledge Sync & Matrix): SUCCESS")
        
        # Step 4: Structure Lock & BigQuery AI/ML
        res4 = pipeline_engine.run_step(4, self.topic, {"core_insights": res3["sync_result"].get("core_insights")})
        self.assertEqual(res4["status"], "success")
        self.assertEqual(res4["step_no"], 4)
        self.assertIn("outline", res4)
        print("  -> Step 4 (Structure & BigQuery AI/ML): SUCCESS")
        
        # Step 5: Draft 2-Files
        res5 = pipeline_engine.run_step(5, self.topic, {
            "outline": res4["outline"],
            "saved_papers": res2["vault_items"],
            "target_words": 1500
        })
        self.assertEqual(res5["status"], "success")
        self.assertEqual(res5["step_no"], 5)
        self.assertIn("writer_result", res5)
        file_a_rel = res5["writer_result"]["file_a"]["rel_path"]
        print(f"  -> Step 5 (Draft 2-Files): SUCCESS (File A: {file_a_rel})")
        
        # Step 6: Zotero Dynamic Codes
        res6 = pipeline_engine.run_step(6, self.topic, {"file_a_rel": file_a_rel, "zotero_mode": "A"})
        self.assertEqual(res6["status"], "success")
        self.assertEqual(res6["step_no"], 6)
        self.assertIn("zotero_result", res6)
        print("  -> Step 6 (Zotero Dynamic XML): SUCCESS")
        
        # Step 7: Final QA & Publishing
        res7 = pipeline_engine.run_step(7, self.topic, {"file_a_rel": file_a_rel})
        self.assertEqual(res7["status"], "success")
        self.assertEqual(res7["step_no"], 7)
        self.assertIn("qa_scorecard", res7)
        self.assertIn("final_artifact", res7)
        print(f"  -> Step 7 (Final QA & Publishing): SUCCESS (Total QA Score: {res7['qa_scorecard'].get('total_score', 100)}/100)")

    def test_04_full_chained_pipeline(self):
        """Test run_full_pipeline execution (1-click 7/7 steps)"""
        print("\n[TEST 4] Testing Full Chained Pipeline (1-Click)...")
        res_full = pipeline_engine.run_full_pipeline(self.topic, {"max_papers": 3, "target_words": 1200})
        self.assertEqual(res_full["status"], "success")
        self.assertEqual(res_full["steps_completed"], 7)
        self.assertIn("step_1", res_full["results"])
        self.assertIn("step_2", res_full["results"])
        self.assertIn("step_3", res_full["results"])
        self.assertIn("step_4", res_full["results"])
        self.assertIn("step_5", res_full["results"])
        self.assertIn("step_6", res_full["results"])
        self.assertIn("step_7", res_full["results"])
        print("  -> Full Chained Pipeline (7/7 Steps): COMPLETED PERFECTLY")


if __name__ == "__main__":
    unittest.main()
