"""
scientific_chart_builder.py
===========================
Engine vẽ biểu đồ khoa học và sơ đồ quy trình công nghệ chuẩn 300 DPI,
hỗ trợ hiển thị 100% Tiếng Việt có dấu (Times New Roman / Arial) và bảng màu chuẩn Nature/Elsevier.
Tích hợp tìm kiếm và tối ưu ảnh thực tế chất lượng cao từ Wikimedia Commons.
"""

import os
import sys
import time
import urllib.request
import json
from typing import List, Tuple, Dict, Optional, Any
from pathlib import Path
from PIL import Image
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

# Configure Vietnamese Font
def setup_vietnamese_fonts(font_family: str = "Times New Roman"):
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    preferred_fonts = [font_family, "Times New Roman", "Arial", "Calibri", "Segoe UI", "DejaVu Sans"]
    chosen_font = "DejaVu Sans"
    for f in preferred_fonts:
        if f in available_fonts:
            chosen_font = f
            break
            
    matplotlib.rcParams['font.family'] = chosen_font
    matplotlib.rcParams['font.sans-serif'] = [chosen_font, 'Arial', 'DejaVu Sans']
    matplotlib.rcParams['font.serif'] = [chosen_font, 'Times New Roman', 'DejaVu Serif']
    matplotlib.rcParams['axes.unicode_minus'] = False
    matplotlib.rcParams['figure.dpi'] = 300
    matplotlib.rcParams['savefig.dpi'] = 300
    matplotlib.rcParams['font.size'] = 11
    matplotlib.rcParams['axes.labelsize'] = 12
    matplotlib.rcParams['axes.titlesize'] = 13
    matplotlib.rcParams['xtick.labelsize'] = 10
    matplotlib.rcParams['ytick.labelsize'] = 10
    matplotlib.rcParams['legend.fontsize'] = 10

setup_vietnamese_fonts()

ACADEMIC_COLORS = [
    "#1f77b4", "#d62728", "#2ca02c", "#ff7f0e", "#9467bd",
    "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
]


class ScientificChartGenerator:
    """Tạo biểu đồ khoa học Tiếng Việt 300 DPI."""
    
    def __init__(self, style: str = "default"):
        setup_vietnamese_fonts("Times New Roman")
        
    def plot_bar_chart(
        self,
        categories: List[str],
        values: List[float],
        errors: Optional[List[float]] = None,
        title: str = "Biểu đồ cột khoa học",
        xlabel: str = "Chỉ số / Nhóm",
        ylabel: str = "Giá trị đo lường",
        output_path: str = "output_bar.png",
        figsize: Tuple[float, float] = (7.0, 4.5),
        color: str = "#1f77b4"
    ) -> str:
        fig, ax = plt.subplots(figsize=figsize)
        bars = ax.bar(categories, values, yerr=errors, capsize=5, color=color, edgecolor="#0d47a1", alpha=0.9, width=0.55)
        ax.set_title(title, pad=12, fontweight="bold")
        ax.set_xlabel(xlabel, labelpad=8)
        ax.set_ylabel(ylabel, labelpad=8)
        ax.grid(axis='y', linestyle='--', alpha=0.6)
        
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.2f}' if isinstance(height, float) else f'{height}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', fontsize=9, fontweight='bold')
                        
        plt.tight_layout()
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        return output_path

    def plot_line_chart(
        self,
        x_data: List[Any],
        series_dict: Dict[str, List[float]],
        title: str = "Biểu đồ đường xu hướng",
        xlabel: str = "Thời gian / Giai đoạn",
        ylabel: str = "Giá trị",
        output_path: str = "output_line.png",
        figsize: Tuple[float, float] = (7.5, 4.5)
    ) -> str:
        fig, ax = plt.subplots(figsize=figsize)
        for i, (label, y_values) in enumerate(series_dict.items()):
            c = ACADEMIC_COLORS[i % len(ACADEMIC_COLORS)]
            ax.plot(x_data, y_values, marker='o', linewidth=2.2, label=label, color=c)
            
        ax.set_title(title, pad=12, fontweight="bold")
        ax.set_xlabel(xlabel, labelpad=8)
        ax.set_ylabel(ylabel, labelpad=8)
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.legend(frameon=True, loc='best')
        plt.tight_layout()
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        return output_path


class FlowchartBuilder:
    """Tạo sơ đồ quy trình công nghệ và lưu đồ khối 300 DPI."""
    
    def __init__(self):
        setup_vietnamese_fonts("Times New Roman")
        
    def build_linear_process(
        self,
        steps: List[Dict[str, str]],
        title: str = "Sơ đồ quy trình công nghệ",
        output_path: str = "output_process.png"
    ) -> str:
        n = len(steps)
        fig, ax = plt.subplots(figsize=(max(9.0, n * 2.8), 4.2))
        ax.set_xlim(0, n * 3.0)
        ax.set_ylim(0, 4)
        
        for i, step in enumerate(steps):
            x = 1.5 + i * 3.0
            y = 2.0
            t = step.get('title', f'Bước {i+1}')
            d = step.get('desc', '')
            full_txt = f"{t}\n({d})" if d else t
            
            c = ACADEMIC_COLORS[i % len(ACADEMIC_COLORS)]
            ax.text(
                x, y, full_txt, ha='center', va='center', fontsize=10.5,
                bbox=dict(boxstyle="round,pad=0.7,rounding_size=0.25", facecolor="#f8fafc", edgecolor=c, linewidth=2.2)
            )
            
            if i < n - 1:
                ax.annotate(
                    '', xy=(x + 1.4, y), xytext=(x + 0.8, y),
                    arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.6", lw=2.2, color="#475569")
                )
                
        ax.set_title(title, pad=14, fontsize=13, fontweight='bold')
        ax.axis('off')
        plt.tight_layout()
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        return output_path


def download_and_optimize_image(url: str, output_path: str, max_dim: int = 1600) -> Optional[str]:
    """Tải ảnh từ URL, chuẩn hóa sang RGB 300 DPI."""
    headers = {'User-Agent': 'AcademicResearchBot/2.0 (GraduateSchoolResearch; contact@research.edu.vn)'}
    temp_file = output_path + ".tmp"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=25) as resp, open(temp_file, 'wb') as f:
            f.write(resp.read())
            
        with Image.open(temp_file) as img:
            img = img.convert('RGB')
            if max(img.size) > max_dim:
                scale = max_dim / max(img.size)
                new_size = (int(img.size[0] * scale), int(img.size[1] * scale))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            img.save(output_path, 'PNG', dpi=(300, 300))
            
        if os.path.exists(temp_file):
            os.remove(temp_file)
        return output_path
    except Exception as e:
        if os.path.exists(temp_file):
            os.remove(temp_file)
        return None
