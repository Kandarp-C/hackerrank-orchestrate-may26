import os
import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Article:
    filepath: str
    domain: str
    category: str
    title: str
    content: str

def load_corpus(base_dir: str = "../data") -> List[Article]:
    """
    Walks through the data directory and loads all .md files.
    """
    base_path = Path(base_dir).resolve()
    articles = []

    for md_file in base_path.rglob("*.md"):
        # Skip index files if we want, but the plan says to include them
        # as they provide category mappings.
        
        relative_path = md_file.relative_to(base_path)
        parts = relative_path.parts
        
        if not parts:
            continue
            
        domain = parts[0].lower()
        category = parts[1] if len(parts) > 1 else "root"
        
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                raw_text = f.read()
        except Exception as e:
            print(f"Error reading {md_file}: {e}")
            continue

        # Simple frontmatter extraction
        title = ""
        content = raw_text
        
        # Check for YAML frontmatter
        if raw_text.startswith("---"):
            match = re.search(r"^---\s*\n(.*?)\n---\s*\n", raw_text, re.DOTALL)
            if match:
                frontmatter = match.group(1)
                # Look for title: "..." or title: ...
                title_match = re.search(r"^title:\s*[\"']?(.*?)[\"']?$", frontmatter, re.MULTILINE)
                if title_match:
                    title = title_match.group(1)
                content = raw_text[match.end():].strip()

        # If no title in frontmatter, try H1
        if not title:
            h1_match = re.search(r"^#\s+(.*)$", content, re.MULTILINE)
            if h1_match:
                title = h1_match.group(1)
            else:
                title = md_file.stem.replace("-", " ").capitalize()

        articles.append(Article(
            filepath=str(relative_path),
            domain=domain,
            category=category,
            title=title,
            content=content
        ))

    return articles

def get_domain_map(articles: List[Article]) -> Dict[str, List[Article]]:
    domain_map = {}
    for art in articles:
        if art.domain not in domain_map:
            domain_map[art.domain] = []
        domain_map[art.domain].append(art)
    return domain_map

if __name__ == "__main__":
    # Test loader
    test_articles = load_corpus()
    print(f"Loaded {len(test_articles)} articles.")
    d_map = get_domain_map(test_articles)
    for dom, arts in d_map.items():
        print(f" - {dom}: {len(arts)} articles")
