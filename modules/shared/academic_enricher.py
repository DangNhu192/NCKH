#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Academic Enricher - Zero-Token Metadata Enrichment
===================================================
Module làm giàu siêu dữ liệu học thuật mở (CrossRef, OpenAlex, arXiv)
Kế thừa giải thuật từ tiện ích NotebookLM to Zotero (Zero-AI Cost)
dùng chung cho Web Super (Harvester, NotebookLM, Zotero).
"""

import re
import sys
import json
import urllib.request
import urllib.parse
from difflib import SequenceMatcher
from typing import Dict, Any, Optional, List

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

# Regex trích xuất DOI
DOI_PATTERNS = [
    r'10\.\d{4,9}/[-._;()/:A-Za-z0-9]+',
    r'doi\.org/(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)',
    r'doi[:\s]+(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)'
]

ARXIV_PATTERN = r'arxiv\.org/(?:abs|pdf)/(\d+\.\d+)'

class AcademicEnricher:
    """Tự động làm giàu siêu dữ liệu học thuật bằng CrossRef, OpenAlex và arXiv."""

    @staticmethod
    def extract_doi(text: str = "", url: str = "") -> Optional[str]:
        """Tìm mã DOI từ tiêu đề bài viết hoặc liên kết web."""
        combined = f"{text} {url}"
        for pattern in DOI_PATTERNS:
            match = re.search(pattern, combined, re.IGNORECASE)
            if match:
                raw_doi = match.group(1) if match.groups() else match.group(0)
                clean_doi = re.sub(r'^(?:https?://(?:dx\.)?doi\.org/|doi:?\s*)', '', raw_doi, flags=re.IGNORECASE).strip()
                clean_doi = clean_doi.rstrip('.,;)')
                return clean_doi
        return None

    @staticmethod
    def extract_arxiv_id(url: str = "") -> Optional[str]:
        """Tìm mã arXiv từ URL."""
        match = re.search(ARXIV_PATTERN, url, re.IGNORECASE)
        return match.group(1) if match else None

    @staticmethod
    def calculate_title_similarity(a: str, b: str) -> float:
        """Đo lường mức độ tương đồng giữa hai tiêu đề."""
        def normalize(s):
            return re.sub(r'[^\w\s]', '', s.lower()).strip()
        return SequenceMatcher(None, normalize(a), normalize(b)).ratio()

    @classmethod
    def query_crossref_by_doi(cls, doi: str) -> Optional[Dict[str, Any]]:
        """Truy vấn siêu dữ liệu bài báo chính thống từ CrossRef bằng DOI."""
        encoded_doi = urllib.parse.quote(doi)
        url = f"https://api.crossref.org/works/{encoded_doi}"
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'AcademicEnricher/1.0 (mailto:academic-researcher@websuper.local; Python/urllib)',
                'Accept': 'application/json'
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode('utf-8'))
                    work = data.get('message', {})
                    
                    authors = []
                    for a in work.get('author', []):
                        family = a.get('family', '')
                        given = a.get('given', '')
                        if family and given:
                            authors.append(f"{given} {family}")
                        elif family or a.get('name'):
                            authors.append(family or a.get('name'))
                            
                    date_parts = work.get('published', {}).get('date-parts') or work.get('created', {}).get('date-parts')
                    year = date_parts[0][0] if date_parts and date_parts[0] else None

                    journal_titles = work.get('container-title', [])
                    journal = journal_titles[0] if journal_titles else ""

                    return {
                        'title': (work.get('title') or [''])[0],
                        'authors': authors,
                        'journal': journal,
                        'volume': work.get('volume', ''),
                        'issue': work.get('issue', ''),
                        'pages': work.get('page', ''),
                        'year': year,
                        'doi': work.get('DOI', doi),
                        'issn': (work.get('ISSN') or [''])[0],
                        'publisher': work.get('publisher', ''),
                        'url': work.get('URL') or f"https://doi.org/{doi}",
                        'abstract': work.get('abstract', ''),
                        'confidence': 1.0,
                        'source_api': 'CrossRef (DOI)'
                    }
        except Exception:
            pass
        return None

    @classmethod
    def query_openalex_by_title(cls, title: str) -> Optional[Dict[str, Any]]:
        """Truy vấn bài báo mờ trên OpenAlex bằng tiêu đề."""
        clean_title = re.sub(r'[\r\n\t]+', ' ', title).strip()
        encoded_query = urllib.parse.quote(clean_title)
        url = f"https://api.openalex.org/works?search={encoded_query}&per-page=3"
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'AcademicEnricher/1.0 (mailto:academic-researcher@websuper.local)'
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode('utf-8'))
                    results = data.get('results', [])
                    for item in results:
                        candidate_title = item.get('title') or item.get('display_name') or ''
                        sim = cls.calculate_title_similarity(clean_title, candidate_title)
                        if sim >= 0.70:
                            authors = [auth.get('author', {}).get('display_name', '') for auth in item.get('authorships', [])]
                            primary_location = item.get('primary_location') or {}
                            source_info = primary_location.get('source') or {}
                            
                            return {
                                'title': candidate_title,
                                'authors': [a for a in authors if a],
                                'journal': source_info.get('display_name', ''),
                                'volume': item.get('biblio', {}).get('volume', ''),
                                'issue': item.get('biblio', {}).get('issue', ''),
                                'pages': f"{item.get('biblio', {}).get('first_page', '')}-{item.get('biblio', {}).get('last_page', '')}".strip('-'),
                                'year': item.get('publication_year'),
                                'doi': (item.get('doi') or '').replace('https://doi.org/', ''),
                                'issn': (source_info.get('issn') or [''])[0],
                                'publisher': source_info.get('host_organization_name', ''),
                                'url': item.get('doi') or primary_location.get('landing_page_url', ''),
                                'abstract': '',
                                'confidence': sim,
                                'source_api': 'OpenAlex'
                            }
        except Exception:
            pass
        return None

    @classmethod
    def query_arxiv(cls, arxiv_id: str) -> Optional[Dict[str, Any]]:
        """Truy vấn siêu dữ liệu từ arXiv API."""
        url = f"https://export.arxiv.org/api/query?id_list={arxiv_id}"
        req = urllib.request.Request(url, headers={'User-Agent': 'AcademicEnricher/1.0'})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                xml_text = resp.read().decode('utf-8')
                title_match = re.search(r'<entry>.*?<title>(.*?)</title>', xml_text, re.DOTALL)
                published_match = re.search(r'<published>(\d{4})', xml_text)
                authors = re.findall(r'<author>.*?<name>(.*?)</name>', xml_text, re.DOTALL)
                summary_match = re.search(r'<summary>(.*?)</summary>', xml_text, re.DOTALL)

                if title_match:
                    return {
                        'title': re.sub(r'\s+', ' ', title_match.group(1)).strip(),
                        'authors': [re.sub(r'\s+', ' ', a).strip() for a in authors],
                        'journal': 'arXiv Preprint',
                        'year': int(published_match.group(1)) if published_match else None,
                        'doi': f"10.48550/arXiv.{arxiv_id}",
                        'url': f"https://arxiv.org/abs/{arxiv_id}",
                        'abstract': re.sub(r'\s+', ' ', summary_match.group(1)).strip() if summary_match else '',
                        'confidence': 0.95,
                        'source_api': 'arXiv API'
                    }
        except Exception:
            pass
        return None

    @classmethod
    def enrich(cls, source: Dict[str, Any]) -> Dict[str, Any]:
        """Tự động làm giàu một tài nguyên bất kỳ bằng DOI, arXiv hoặc OpenAlex."""
        title = source.get('title', '')
        url = source.get('url', '')
        
        # 1. Tìm DOI trước tiên
        doi = cls.extract_doi(title, url)
        if doi:
            meta = cls.query_crossref_by_doi(doi)
            if meta:
                source.update(meta)
                return source

        # 2. Kiểm tra arXiv
        arxiv_id = cls.extract_arxiv_id(url)
        if arxiv_id:
            meta = cls.query_arxiv(arxiv_id)
            if meta:
                source.update(meta)
                return source

        # 3. Tra cứu mờ qua tiêu đề trên OpenAlex
        if len(title) > 15:
            meta = cls.query_openalex_by_title(title)
            if meta:
                source.update(meta)
                return source

        return source


# Singleton instance sẵn dùng
academic_enricher = AcademicEnricher()
