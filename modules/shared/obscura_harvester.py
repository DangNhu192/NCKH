#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Obscura Harvester - High-Performance Stealth Browser Harvesting Wrapper
========================================================================
Wrapper Python tích hợp công cụ Obscura (Rust V8 Headless Browser)
dành cho các tác vụ trong Web Super:
1. Vượt qua lớp kiểm duyệt bot / Cloudflare bằng chế độ tàng hình (--stealth).
2. Render mã JavaScript cho các trang web Single-Page Application (SPA).
3. Bóc tách văn bản thô (text), HTML đã hydrate, và danh sách siêu liên kết (links).
4. Tải tệp nhị phân trực tiếp (PDF, hình ảnh, tập dữ liệu) bằng luồng nguyên bản (--dump original).
5. Quét song song hàng loạt đường dẫn (batch scraping) với tốc độ cao.
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Union

# Chuẩn hóa mã hóa console đầu ra trên Windows chống lỗi encoding
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


class ObscuraHarvester:
    """Điều khiển Obscura CLI phục vụ thu thập dữ liệu và tải tệp tàng hình."""

    def __init__(self, binary_path: Optional[str] = None):
        """Khởi tạo ObscuraHarvester, tự động tìm kiếm obscura trong PATH hoặc thư mục local."""
        if binary_path:
            self.binary = binary_path
        else:
            found = shutil.which("obscura") or shutil.which("obscura.exe")
            if not found:
                local_bin = Path.home() / ".local" / "bin" / "obscura.exe"
                if local_bin.exists():
                    found = str(local_bin)
            self.binary = found or "obscura"

    def is_available(self) -> bool:
        """Kiểm tra xem nhị phân obscura có sẵn sàng hoạt động hay không."""
        try:
            res = subprocess.run(
                [self.binary, "--version"],
                capture_output=True,
                text=True,
                check=False,
                timeout=5
            )
            return res.returncode == 0
        except Exception:
            return False

    def get_version(self) -> str:
        """Lấy thông tin phiên bản Obscura."""
        try:
            res = subprocess.run(
                [self.binary, "--version"],
                capture_output=True,
                text=True,
                check=True,
                timeout=5
            )
            return res.stdout.strip()
        except Exception as e:
            return f"Unknown ({e})"

    def fetch_text(
        self,
        url: str,
        stealth: bool = True,
        timeout: int = 30,
        wait_seconds: Optional[int] = None,
        proxy: Optional[str] = None
    ) -> str:
        """
        Bóc tách toàn bộ nội dung văn bản (text) từ trang web sau khi chạy JavaScript.
        Loại bỏ mã HTML thừa, trả về văn bản sạch sẵn sàng nạp cho LLM.
        """
        cmd = [self.binary]
        if stealth:
            cmd.append("--stealth")
        if proxy:
            cmd.extend(["--proxy", proxy])
        
        cmd.extend(["fetch", url, "--dump", "text", "--timeout", str(timeout)])
        if wait_seconds is not None:
            cmd.extend(["--wait", str(wait_seconds)])

        res = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=timeout + 10)
        if res.returncode != 0:
            raise RuntimeError(f"Obscura fetch_text thất bại (code {res.returncode}): {res.stderr.strip()}")
        
        lines = res.stdout.splitlines()
        content_lines = []
        skip_header = True
        for line in lines:
            if skip_header:
                if line.startswith("Page loaded:") or line.startswith("Fetching "):
                    continue
                skip_header = False
            content_lines.append(line)
            
        return "\n".join(content_lines).strip()

    def fetch_html(
        self,
        url: str,
        stealth: bool = True,
        timeout: int = 30,
        wait_seconds: Optional[int] = None,
        proxy: Optional[str] = None
    ) -> str:
        """Bóc tách toàn bộ mã HTML đã hydrate hoàn chỉnh (rendered DOM)."""
        cmd = [self.binary]
        if stealth:
            cmd.append("--stealth")
        if proxy:
            cmd.extend(["--proxy", proxy])
            
        cmd.extend(["fetch", url, "--dump", "html", "--timeout", str(timeout)])
        if wait_seconds is not None:
            cmd.extend(["--wait", str(wait_seconds)])

        res = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=timeout + 10)
        if res.returncode != 0:
            raise RuntimeError(f"Obscura fetch_html thất bại (code {res.returncode}): {res.stderr.strip()}")
            
        return res.stdout

    def fetch_links(
        self,
        url: str,
        filter_extension: Optional[str] = None,
        stealth: bool = True,
        timeout: int = 30
    ) -> List[str]:
        """
        Trích xuất toàn bộ siêu liên kết (URLs) có trên trang web.
        Có thể lọc theo phần mở rộng (ví dụ '.pdf', '.docx', '.zip').
        """
        cmd = [self.binary]
        if stealth:
            cmd.append("--stealth")
        cmd.extend(["fetch", url, "--dump", "links", "--timeout", str(timeout)])

        res = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=timeout + 10)
        if res.returncode != 0:
            raise RuntimeError(f"Obscura fetch_links thất bại: {res.stderr.strip()}")

        links = []
        for line in res.stdout.splitlines():
            clean = line.strip()
            if clean and clean.startswith(("http://", "https://", "/")):
                clean_url = clean.split("\t")[0].strip()
                if filter_extension:
                    if clean_url.lower().endswith(filter_extension.lower()) or (f"{filter_extension.lower()}?" in clean_url.lower()):
                        links.append(clean_url)
                else:
                    links.append(clean_url)
        return links

    def evaluate_js(
        self,
        url: str,
        js_expression: str,
        stealth: bool = True,
        timeout: int = 30
    ) -> str:
        """Thực thi biểu thức JavaScript trên trang web và trả về kết quả."""
        cmd = [self.binary]
        if stealth:
            cmd.append("--stealth")
        cmd.extend(["fetch", url, "--eval", js_expression, "--timeout", str(timeout)])

        res = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=timeout + 10)
        if res.returncode != 0:
            raise RuntimeError(f"Obscura evaluate_js thất bại: {res.stderr.strip()}")
        return res.stdout.strip()

    def download_file(
        self,
        url: str,
        output_path: Union[str, Path],
        stealth: bool = True,
        timeout: int = 60,
        proxy: Optional[str] = None
    ) -> bool:
        """
        Tải tệp nhị phân trực tiếp (PDF, Word, Ảnh, Dataset) bằng luồng nguyên bản (--dump original).
        Không xử lý qua DOM, bảo toàn 100% byte dữ liệu gốc và duy trì TLS/User-Agent tàng hình.
        """
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)

        cmd = [self.binary]
        if stealth:
            cmd.append("--stealth")
        if proxy:
            cmd.extend(["--proxy", proxy])
            
        cmd.extend(["fetch", url, "--dump", "original", "--timeout", str(timeout)])

        with open(out_file, "wb") as f:
            res = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, check=False, timeout=timeout + 10)

        if res.returncode != 0:
            if out_file.exists():
                out_file.unlink(missing_ok=True)
            raise RuntimeError(f"Obscura download_file thất bại: {res.stderr.decode('utf-8', errors='ignore').strip()}")

        return out_file.exists() and out_file.stat().st_size > 0

    def capture_screenshot(
        self,
        url: str,
        output_png_path: Union[str, Path],
        stealth: bool = True,
        timeout: int = 30,
        wait_seconds: Optional[int] = None
    ) -> bool:
        """Chụp ảnh màn hình trực quan không cần cài đặt Chromium."""
        out_path = Path(output_png_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        cmd = [self.binary]
        if stealth:
            cmd.append("--stealth")
        cmd.extend(["fetch", url, "--screenshot", str(out_path), "--timeout", str(timeout)])
        if wait_seconds is not None:
            cmd.extend(["--wait", str(wait_seconds)])

        res = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=timeout + 10)
        return res.returncode == 0 and out_path.exists() and out_path.stat().st_size > 0

    def scrape_batch(
        self,
        urls: List[str],
        eval_js: Optional[str] = None,
        concurrency: int = 10,
        stealth: bool = True,
        proxy: Optional[str] = None
    ) -> List[Dict]:
        """Quét song song hàng loạt URL bằng lệnh obscura scrape với tiến trình ngầm."""
        if not urls:
            return []

        cmd = [self.binary]
        if stealth:
            cmd.append("--stealth")
        if proxy:
            cmd.extend(["--proxy", proxy])
            
        cmd.extend(["scrape", *urls, "--concurrency", str(concurrency), "--format", "json", "--quiet"])
        if eval_js:
            cmd.extend(["--eval", eval_js])

        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if res.returncode != 0:
            raise RuntimeError(f"Obscura scrape_batch thất bại: {res.stderr.strip()}")

        try:
            return json.loads(res.stdout)
        except json.JSONDecodeError:
            results = []
            for line in res.stdout.splitlines():
                line = line.strip()
                if line:
                    try:
                        results.append(json.loads(line))
                    except Exception:
                        pass
            return results


# Singleton instance sẵn dùng cho toàn hệ thống Web Super
obscura_harvester = ObscuraHarvester()
