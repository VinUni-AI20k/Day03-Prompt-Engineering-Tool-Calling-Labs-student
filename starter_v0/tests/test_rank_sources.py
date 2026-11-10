from tools.rank_sources.tool import rank_sources


def test_more_matching_keywords_rank_first():
    items = [
        {"title": "AI news", "summary": ""},
        {"title": "New AI chip", "summary": "Chip for computers"},
    ]

    result = rank_sources(items, query="AI chip", limit=5)

    assert result["items"][0]["title"] == "New AI chip"
    assert result["items"][1]["title"] == "AI news"
    assert result["ranked_count"] == 2


def test_limit_restricts_number_of_results():
    items = [
        {"title": "AI chip"},
        {"title": "AI model"},
        {"title": "Other news"},
    ]

    result = rank_sources(items, query="AI", limit=1)

    assert len(result["items"]) == 1
    assert result["ranked_count"] == 3


def test_invalid_input_returns_error_dict():
    result = rank_sources(items="not a list", query="AI", limit=5)

    assert result["error"] == "invalid_input"