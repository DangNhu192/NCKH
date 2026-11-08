"""
modules/inspector/__init__.py
Dual-Pane Evidence Inspector & 4-Layer Pre-Commit Verification Gate Module (v4.2)
"""

from .evidence_inspector_engine import EvidenceInspectorEngine, evidence_inspector_engine
from .inspector_router import inspector_router

__all__ = ["EvidenceInspectorEngine", "evidence_inspector_engine", "inspector_router"]
