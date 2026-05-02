import re
from typing import List
from corpus_loader import Article

def get_keywords(text: str) -> set:
    """Extract lowercase keywords from text."""
    return set(re.findall(r'\w+', text.lower()))

def score_article(article: Article, query_keywords: set) -> float:
    """Simple scoring based on keyword frequency in title and content."""
    title_keywords = get_keywords(article.title)
    content_keywords = get_keywords(article.content)
    
    # Weight title higher
    title_matches = len(query_keywords.intersection(title_keywords))
    content_matches = len(query_keywords.intersection(content_keywords))
    
    return (title_matches * 3) + content_matches

def retrieve(issue: str, subject: str, company: str, corpus: List[Article], top_k: int = 8) -> List[Article]:
    """
    Retrieves the most relevant articles using domain filtering and keyword scoring.
    Includes context stuffing for small domains and index files.
    """
    query_text = f"{subject} {issue}"
    query_keywords = get_keywords(query_text)
    
    normalized_company = company.lower().strip() if company else "none"
    
    # Tier 1: Domain Filtering
    if normalized_company in ["hackerrank", "claude", "visa"]:
        domain_articles = [a for a in corpus if a.domain == normalized_company]
    else:
        # If None/Unknown, search all but prioritize index files
        domain_articles = corpus

    # Strategy: Always include index.md files for the specific domain or all domains
    selected_articles = []
    
    # If Visa, just return all 14 files as it's tiny
    if normalized_company == "visa":
        return domain_articles
    
    # For others, include index files + top-K keyword matches
    indices = [a for a in domain_articles if "index.md" in a.filepath or a.filepath.endswith("support.md")]
    
    # Score remaining articles
    others = [a for a in domain_articles if a not in indices]
    scored_others = []
    for art in others:
        score = score_article(art, query_keywords)
        if score > 0:
            scored_others.append((score, art))
    
    # Sort by score descending
    scored_others.sort(key=lambda x: x[0], reverse=True)
    
    # Build final list
    selected_articles.extend(indices)
    selected_articles.extend([art for score, art in scored_others[:top_k]])
    
    return selected_articles
