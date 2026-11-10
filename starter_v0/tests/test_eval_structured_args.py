from run_eval import compare_subset, normalize_value


def test_structured_items_compare_without_sorting_dictionaries():
    items = [{"url": "https://example.com/a"}, {"url": "https://example.com/b"}]
    assert compare_subset({"items": items}, {"items": items})[0]


def test_reordered_source_items_are_not_equal():
    items = [{"url": "https://example.com/a"}, {"url": "https://example.com/b"}]
    assert not compare_subset({"items": items}, {"items": list(reversed(items))})[0]


def test_scalar_list_normalization_remains_order_insensitive():
    assert normalize_value([" B ", "a"]) == ["a", "b"]
