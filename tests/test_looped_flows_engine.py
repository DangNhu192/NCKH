#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit & Integration Tests for Looped Flows Reasoning Protocol (arXiv:2609.11801)
================================================================================
Verifies:
1. LoopedFlowController: relative residuals, ACT q(z), spurious attractor detection,
   stochastic backtracking, and Best-Q trajectory ensembling.
2. LoopedFlowsReasoningService: 5-phase text auditing, overconfidence detection, and hedging audit.
3. Integration with Academic Writer, Editorial Office, and API Endpoints.
"""

import os
import sys
import unittest
from pathlib import Path

# Ensure root directory is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.shared.looped_flows_engine import (
    LoopedFlowController,
    LoopedFlowsReasoningService,
    looped_flows_engine,
)
from modules.editorial_office.editorial_engine import editorial_engine
from modules.academic_writer.academic_writer_engine import academic_writer
from modules.pipeline.pipeline_engine import pipeline_engine


class TestLoopedFlowsEngine(unittest.TestCase):

    def setUp(self):
        self.controller = LoopedFlowController(num_steps=5, gamma=0.2, act_threshold=0.95)
        self.service = LoopedFlowsReasoningService()

    def test_01_compute_relative_residual(self):
        """Kiểm tra tính toán sai số tương đối bước lặp R_i."""
        z_prev = {"claim_1": 1.0, "claim_2": 2.0, "metric": 50.0}
        z_curr = {"claim_1": 1.0, "claim_2": 2.0, "metric": 50.0}
        res_zero = self.controller.compute_relative_residual(z_curr, z_prev)
        self.assertAlmostEqual(res_zero, 0.0, places=4)

        z_diff = {"claim_1": 1.0, "claim_2": 2.5, "metric": 60.0}
        res_diff = self.controller.compute_relative_residual(z_diff, z_prev)
        self.assertGreater(res_diff, 0.0)

    def test_02_evaluate_act_saturation(self):
        """Kiểm tra hàm bão hòa kiểm chứng ACT q(z_t)."""
        # Hoàn hảo: 10/10 claims verified, 0 conflicts, 0 unverified
        act_perfect = self.controller.evaluate_act(
            total_claims=10,
            verified_claims=10,
            logic_conflicts=0,
            unverified_hypotheses=0
        )
        self.assertGreaterEqual(act_perfect["q_score"], 0.95)
        self.assertTrue(act_perfect["is_saturated"])
        self.assertEqual(act_perfect["recommendation"], "EARLY_EXIT_ACCEPT")

        # Kém: Có mâu thuẫn logic và giả định chưa kiểm chứng
        act_poor = self.controller.evaluate_act(
            total_claims=10,
            verified_claims=4,
            logic_conflicts=2,
            unverified_hypotheses=3
        )
        self.assertLess(act_poor["q_score"], 0.70)
        self.assertFalse(act_poor["is_saturated"])
        self.assertEqual(act_poor["recommendation"], "CONTINUE_DENOISING_STEP")

    def test_03_detect_spurious_attractor(self):
        """Kiểm tra phát hiện điểm hấp dẫn giả (Spurious Attractor) / ngụy biện tự tin."""
        # Hội tụ giả: residual rất nhỏ nhưng điểm thực chứng q rất thấp
        stepwise_residuals = [0.4, 0.2, 0.03, 0.02]
        is_spurious = self.controller.detect_spurious_attractor(
            stepwise_residuals=stepwise_residuals,
            act_score=0.60
        )
        self.assertTrue(is_spurious)

        # Hội tụ thật: residual nhỏ và điểm thực chứng q cao
        is_genuine = self.controller.detect_spurious_attractor(
            stepwise_residuals=stepwise_residuals,
            act_score=0.92
        )
        self.assertFalse(is_genuine)

    def test_04_trigger_stochastic_backtrack(self):
        """Kiểm tra cơ chế hồi quy ngẫu nhiên (Stochastic Noise-Backtracking via SDE)."""
        backtrack = self.controller.trigger_stochastic_backtrack(current_step=4)
        self.assertEqual(backtrack["status"], "BACKTRACK_TRIGGERED")
        self.assertEqual(backtrack["backtrack_to_step"], 2)
        self.assertGreater(backtrack["injected_noise_scale"], 0.0)
        self.assertIn("Loại bỏ giả định ngụy biện", backtrack["instruction"])

    def test_05_select_best_q_trajectory(self):
        """Kiểm tra chọn lọc quỹ đạo tối ưu theo Best-Q."""
        trajs = [
            {"id": "traj_1", "act_score": 0.65, "logic_conflicts": 1, "final_residual": 0.08},
            {"id": "traj_2", "act_score": 0.96, "logic_conflicts": 0, "final_residual": 0.02},
            {"id": "traj_3", "act_score": 0.82, "logic_conflicts": 0, "final_residual": 0.04},
        ]
        best = self.controller.select_best_q_trajectory(trajs)
        self.assertEqual(best["id"], "traj_2")
        self.assertTrue(best.get("best_q_selected"))
        self.assertEqual(best.get("total_trajectories_evaluated"), 3)

    def test_06_audit_text_with_looped_flows_clean_hedged(self):
        """Kiểm toán văn bản khoa học chuẩn mực đạt tiết chế học thuật (Epistemic Hedging)."""
        sample_text = """
        Nghiên cứu về chuyển dịch năng lượng và lưới điện thông minh.
        Theo khảo sát thực tế, hiệu suất chuyển đổi đạt 28,5% với sai số đo đạc ±0,05 (Nguyen et al., 2023).
        Kết quả thực nghiệm bước đầu gợi ý rằng mô hình thích ứng có thể giảm phát thải khí nhà kính.
        Trong phạm vi dữ liệu quan sát, các biến số thể hiện tương quan thuận với R² = 0,84.
        """
        audit = self.service.audit_text_with_looped_flows(sample_text, topic="Năng lượng tái tạo")
        self.assertEqual(audit["status"], "success")
        self.assertFalse(audit["spurious_attractor_detected"])
        self.assertGreaterEqual(audit["act_score"], 0.70)
        self.assertIn("Looped Flows", audit["protocol"])
        self.assertGreater(audit["metric_count"], 0)

    def test_07_audit_text_with_looped_flows_spurious_attractor(self):
        """Kiểm toán văn bản có biểu hiện phóng đại / ngụy biện tự tin (Spurious Attractor)."""
        bad_text = """
        Giải pháp này chắc chắn 100% giải quyết triệt để mọi vấn đề năng lượng toàn cầu.
        Đây là bước đột phá chứng minh tuyệt đối chân lý hiển nhiên vượt trội hoàn toàn không thể bác bỏ.
        """
        audit = self.service.audit_text_with_looped_flows(bad_text, topic="Năng lượng")
        self.assertTrue(audit["spurious_attractor_detected"])
        self.assertGreater(len(audit["overconfidence_markers"]), 0)
        self.assertIsNotNone(audit["backtrack_plan"])
        self.assertEqual(audit["backtrack_plan"]["status"], "BACKTRACK_TRIGGERED")

    def test_08_integration_with_editorial_office_q1_and_adversarial(self):
        """Kiểm tra tích hợp Looped Flows vào Rubric Q1 và Phản biện đối kháng."""
        sample_content = """
        Phân tích tác động của tự động hóa đến năng suất lao động.
        Dữ liệu thực nghiệm từ 1.500 doanh nghiệp cho thấy tốc độ tăng trưởng đạt 14,2% (Tran, 2022).
        Kết quả bước đầu gợi ý mối tương quan tích cực giữa đầu tư công nghệ và sản lượng.
        """
        # Rubric Q1
        q1_res = editorial_engine.evaluate_manuscript_q1_rubric(sample_content, topic="Tự động hóa")
        self.assertIn("looped_flows_audit", q1_res)
        self.assertIn("act_score", q1_res["looped_flows_audit"])
        self.assertFalse(q1_res["looped_flows_audit"]["spurious_attractor_detected"])

        # Adversarial Review
        adv_res = editorial_engine.conduct_adversarial_peer_review(sample_content, topic="Tự động hóa")
        self.assertIn("looped_flows_audit", adv_res)
        self.assertIn("adversarial_review", adv_res)

    def test_09_integration_with_pipeline_step1(self):
        """Kiểm tra Bước 1 của Pipeline tích hợp Looped Flows Hypothesis Audit."""
        step1_res = pipeline_engine.run_step(1, "Năng lượng sinh khối Đồng bằng sông Cửu Long")
        self.assertEqual(step1_res["step_no"], 1)
        self.assertIn("looped_flows_audit", step1_res)
        self.assertEqual(step1_res["looped_flows_audit"]["status"], "success")

    def test_10_prompt_guidance_format(self):
        """Kiểm tra mẫu chỉ dẫn prompt chuẩn Looped Flows."""
        guidance = self.service.get_looped_flows_prompt_guidance()
        self.assertIn("LOOPED FLOWS REASONING", guidance)
        self.assertIn("arXiv:2609.11801", guidance)
        self.assertIn("Pha 0 (Khởi tạo Anchor Facts)", guidance)
        self.assertIn("Spurious Attractor Guard", guidance)
        self.assertIn("ACT q(z) >= 0.95", guidance)


if __name__ == "__main__":
    unittest.main()
