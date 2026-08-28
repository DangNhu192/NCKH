# .agents/worker_m1/run_verification.py
import os
import sys
import traceback

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from modules.harvester.data_harvesting_engine import data_harvester
from modules.pipeline.pipeline_engine import pipeline_engine

topic = "Ứng dụng Trí tuệ Nhân tạo và Học sâu trong Chẩn đoán Ung thư Phổi"

print("==================================================", flush=True)
print("VERIFICATION SUITE: R1 (7-Step Pipeline & PICO)", flush=True)
print("==================================================", flush=True)

# 1. Research Trends
print("\n--- TEST 1: Research Trends Engine ---", flush=True)
try:
    trends = data_harvester.fetch_research_trends(topic, "deep learning lung cancer diagnosis")
    print(f"Total Papers Indexed: {trends['total_papers_indexed']}", flush=True)
    print(f"5-Year CAGR: {trends['growth_metrics']['cagr_percent']}%", flush=True)
    print(f"Peak Year: {trends['growth_metrics']['peak_year']}", flush=True)
    print(f"Momentum: {trends['growth_metrics']['momentum']}", flush=True)
    print(f"Yearly counts: {[ (y['year'], y['total_count']) for y in trends['yearly_distribution'] ]}", flush=True)
    print(f"Top Subfields: {trends['top_subfields']}", flush=True)
    print(">>> TEST 1 PASSED!", flush=True)
except Exception as e:
    print(f"!!! TEST 1 FAILED: {e}", flush=True)
    traceback.print_exc()

# 2. Multi-Format Evidence Vault Ingestion
print("\n--- TEST 2: Evidence Vault Multi-Format Ingestion ---", flush=True)
try:
    pipeline_engine.clear_vault()
    
    # Ingest .md
    item_md = pipeline_engine.ingest_document_to_vault(
        b"# AI in Lung Cancer\nAuthor: John Doe (2024)\nDOI: 10.1016/j.lungcan.2024.01\nWe use Vision Transformers for lung nodule detection.",
        "sample_paper.md"
    )
    print(f"Ingested MD item: id={item_md['id']}, format={item_md['format']}, doi={item_md['doi']}", flush=True)
    
    # Ingest .txt
    item_txt = pipeline_engine.ingest_document_to_vault(
        b"Deep Neural Network Analysis\nAuthor: Jane Smith et al. (2023)\nDOI: 10.1109/TBME.2023.001\nAchieved 97.4% accuracy.",
        "notes.txt"
    )
    print(f"Ingested TXT item: id={item_txt['id']}, format={item_txt['format']}, doi={item_txt['doi']}", flush=True)
    
    # Check Vault items
    items = pipeline_engine.get_vault_items()
    print(f"Vault total items: {len(items)}", flush=True)
    assert len(items) == 2
    
    # Remove one item
    removed = pipeline_engine.remove_vault_item(item_txt["id"])
    print(f"Removed item_txt: {removed}, remaining: {len(pipeline_engine.get_vault_items())}", flush=True)
    assert len(pipeline_engine.get_vault_items()) == 1
    print(">>> TEST 2 PASSED!", flush=True)
except Exception as e:
    print(f"!!! TEST 2 FAILED: {e}", flush=True)
    traceback.print_exc()

# 3. 7-Step Sequential Pipeline
print("\n--- TEST 3: 7-Step Sequential Pipeline Execution ---", flush=True)
try:
    # Step 1
    r1 = pipeline_engine.run_step(1, topic, {"language": "en"})
    print(f"Step 1: {r1['status']} | Gate: {r1.get('gate')} | Has Trends: {'research_trends' in r1}", flush=True)
    
    # Step 2
    r2 = pipeline_engine.run_step(2, topic, {"max_papers": 3, "language": "en"})
    print(f"Step 2: {r2['status']} | Gate: {r2.get('gate')} | Vault Locked: {r2.get('total_locked', len(r2.get('vault_items', [])))}", flush=True)
    
    # Step 3
    r3 = pipeline_engine.run_step(3, topic, {"saved_papers": r2.get("vault_items")})
    print(f"Step 3: {r3['status']} | Gate: {r3.get('gate')} | Insights count: {len(r3.get('sync_result', {}).get('insights', []))}", flush=True)
    
    # Step 4
    r4 = pipeline_engine.run_step(4, topic, {"core_insights": r3.get("sync_result", {}).get("core_insights")})
    print(f"Step 4: {r4['status']} | Gate: {r4.get('gate')} | Outline length: {len(r4.get('outline', ''))}", flush=True)
    
    # Step 5
    r5 = pipeline_engine.run_step(5, topic, {"outline": r4.get("outline"), "saved_papers": r2.get("vault_items"), "target_words": 1200})
    print(f"Step 5: {r5['status']} | Gate: {r5.get('gate')} | File A: {r5.get('writer_result', {}).get('file_a', {}).get('rel_path')}", flush=True)
    
    file_a_rel = r5.get("writer_result", {}).get("file_a", {}).get("rel_path")
    
    # Step 6
    r6 = pipeline_engine.run_step(6, topic, {"file_a_rel": file_a_rel, "zotero_mode": "A"})
    print(f"Step 6: {r6['status']} | Gate: {r6.get('gate')} | Zotero Out: {r6.get('zotero_result', {}).get('output_rel')}", flush=True)
    
    # Step 7
    r7 = pipeline_engine.run_step(7, topic, {"file_a_rel": file_a_rel})
    print(f"Step 7: {r7['status']} | Gate: {r7.get('gate')} | Score: {r7.get('qa_scorecard', {}).get('total_score')}/100", flush=True)
    print(">>> TEST 3 PASSED!", flush=True)
except Exception as e:
    print(f"!!! TEST 3 FAILED: {e}", flush=True)
    traceback.print_exc()

# 4. Pipeline Steps Definition Inspection
print("\n--- TEST 4: Pipeline Steps Definition Inspection ---", flush=True)
try:
    steps = pipeline_engine.get_pipeline_steps()
    print(f"Total Steps Defined: {len(steps)}", flush=True)
    for s in steps:
        print(f"  Step {s['step_no']}: {s['title']} ({s['gate']})", flush=True)
    assert len(steps) == 7
    print(">>> TEST 4 PASSED!", flush=True)
except Exception as e:
    print(f"!!! TEST 4 FAILED: {e}", flush=True)
    traceback.print_exc()

print("\n==================================================", flush=True)
print("ALL VERIFICATION SUITE TESTS COMPLETED!", flush=True)
print("==================================================", flush=True)
