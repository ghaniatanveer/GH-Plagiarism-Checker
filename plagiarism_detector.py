from __future__ import annotations

import json
import pickle
import re
import ssl
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from urllib.parse import quote_plus
from urllib.request import urlopen

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from .utils import clamp_percentage


class PlagiarismDetector:
    def __init__(
        self,
        corpus_dir: str | Path,
        embeddings_file: str | Path,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        top_k: int = 3,
    ) -> None:
        self.corpus_dir = Path(corpus_dir)
        self.embeddings_file = Path(embeddings_file)
        self.top_k = top_k
        self.model = SentenceTransformer(model_name)
        self.corpus_embeddings: np.ndarray | None = None
        self.sources: list[dict] = []
        self.web_cache: dict[str, list[dict]] = {}
        self.stopwords = {"the", "and", "for", "with", "this", "that", "from", "using", "report", "study", "project"}
        self.load_embeddings()

    def load_embeddings(self) -> None:
        if not self.embeddings_file.exists():
            raise FileNotFoundError("Corpus embeddings not found. Run precompute_embeddings.py first.")
        with self.embeddings_file.open("rb") as file:
            payload = pickle.load(file)
        self.corpus_embeddings = np.array(payload["embeddings"])
        self.sources = payload.get("metadata", [])
        if not self.sources:
            names = payload.get("filenames", [])
            self.sources = [{"filename": n, "title": n, "url": "", "source_type": "Local Corpus"} for n in names]

    def analyze(self, text: str) -> tuple[float, list[dict]]:
        web_sources = self._fetch_open_sources(text)
        if web_sources:
            return self._analyze_against_web_sources(text, web_sources)
        return self._analyze_against_local_corpus(text)

    def _analyze_against_local_corpus(self, text: str) -> tuple[float, list[dict]]:
        if self.corpus_embeddings is None:
            raise ValueError("Corpus embeddings unavailable.")
        chunks = self._chunk_text(text, max_chunks=4)
        query_embeddings = self.model.encode(chunks, convert_to_numpy=True)
        scores = np.mean(cosine_similarity(query_embeddings, self.corpus_embeddings), axis=0)
        top_indices = np.argsort(scores)[::-1][: self.top_k]
        plagiarism = clamp_percentage(float(np.mean(scores[top_indices])) * 100)
        top_sources = [
            {
                "filename": self.sources[i]["filename"],
                "title": self.sources[i].get("title", self.sources[i]["filename"]),
                "url": "",
                "source_type": "Local Corpus Fallback",
                "similarity": clamp_percentage(float(scores[i]) * 100),
            }
            for i in top_indices
        ]
        return plagiarism, top_sources

    def _analyze_against_web_sources(self, text: str, web_sources: list[dict]) -> tuple[float, list[dict]]:
        chunks = self._chunk_text(text, max_chunks=4)
        chunk_emb = self.model.encode(chunks, convert_to_numpy=True)
        cand_emb = self.model.encode([s["abstract"] for s in web_sources], convert_to_numpy=True)
        scores = np.mean(cosine_similarity(chunk_emb, cand_emb), axis=0)
        top_indices = np.argsort(scores)[::-1][: self.top_k]
        plagiarism = clamp_percentage(float(np.mean(scores[top_indices])) * 100)
        top_sources = [
            {
                "filename": web_sources[i]["url"],
                "title": web_sources[i]["title"],
                "url": web_sources[i]["url"],
                "source_type": web_sources[i]["source_type"],
                "similarity": clamp_percentage(float(scores[i]) * 100),
            }
            for i in top_indices
        ]
        return plagiarism, top_sources

    def _build_query(self, text: str, max_terms: int = 6) -> str:
        tokens = re.findall(r"[A-Za-z][A-Za-z0-9\-]{2,}", text.lower())
        filtered = [t for t in tokens if t not in self.stopwords]
        if not filtered:
            return "research paper"
        freq = Counter(filtered)
        return " ".join([term for term, _ in freq.most_common(max_terms)])

    def _fetch_open_sources(self, text: str, max_results: int = 8) -> list[dict]:
        key = self._build_query(text, max_terms=6)
        if key in self.web_cache:
            return self.web_cache[key]
        sources = self._fetch_arxiv_sources(text, max_results=max_results)
        if len(sources) < 3:
            sources.extend(self._fetch_crossref_sources(text, max_results=max_results))
        seen, deduped = set(), []
        for s in sources:
            k = (s.get("url", ""), s.get("title", "").lower())
            if k in seen:
                continue
            seen.add(k)
            deduped.append(s)
        final = deduped[: max_results * 2]
        self.web_cache[key] = final
        return final

    def _fetch_arxiv_sources(self, text: str, max_results: int = 8) -> list[dict]:
        query = self._build_query(text)
        url = f"http://export.arxiv.org/api/query?search_query=all:{quote_plus(query)}&start=0&max_results={max_results}"
        try:
            with urlopen(url, timeout=6, context=ssl._create_unverified_context()) as r:
                root = ET.fromstring(r.read())
        except Exception:
            return []
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        sources = []
        for e in root.findall("atom:entry", ns):
            title = (e.findtext("atom:title", default="", namespaces=ns) or "").strip()
            summary = (e.findtext("atom:summary", default="", namespaces=ns) or "").strip()
            link = (e.findtext("atom:id", default="", namespaces=ns) or "").strip()
            if title and summary and link:
                sources.append({"title": re.sub(r"\s+", " ", title), "abstract": re.sub(r"\s+", " ", summary), "url": link, "source_type": "arXiv"})
        return sources

    def _fetch_crossref_sources(self, text: str, max_results: int = 8) -> list[dict]:
        query = self._build_query(text, max_terms=8)
        url = f"https://api.crossref.org/works?query.bibliographic={quote_plus(query)}&rows={max_results}"
        try:
            with urlopen(url, timeout=6, context=ssl._create_unverified_context()) as r:
                payload = json.loads(r.read().decode("utf-8", errors="ignore"))
        except Exception:
            return []
        items = payload.get("message", {}).get("items", [])
        out = []
        for item in items:
            title = (item.get("title", [""])[0] or "").strip()
            if not title:
                continue
            abstract = re.sub(r"<[^>]+>", " ", item.get("abstract", "") or "").strip() or title
            doi = item.get("DOI", "")
            link = f"https://doi.org/{doi}" if doi else item.get("URL", "")
            if not link:
                continue
            out.append({"title": re.sub(r"\s+", " ", title), "abstract": re.sub(r"\s+", " ", abstract), "url": link, "source_type": "Crossref/DOI"})
        return out

    def _chunk_text(self, text: str, chunk_size: int = 180, max_chunks: int = 4) -> list[str]:
        words = text.split()
        if len(words) <= chunk_size:
            return [text]
        return [" ".join(words[i : i + chunk_size]) for i in range(0, min(len(words), chunk_size * max_chunks), chunk_size)]
