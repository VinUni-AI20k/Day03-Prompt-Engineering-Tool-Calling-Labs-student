"""Offline tool behavior and failure handling; all HTTP is mocked."""
from __future__ import annotations

import requests
import pytest
from conftest import FakeResponse
from tools import TOOL_FUNCTIONS as T


def test_clarify_choice_returns_options_and_awaits_user():
    result = T['clarify']('Chọn nguồn?', 'choice', ['Web', 'X'])
    assert result['options'] == ['Web', 'X']
    assert result['awaiting_user'] is True


def test_format_sections_groups_items_by_section():
    result = T['format']([{'section': x, 'title': x} for x in ['A', 'B', 'A']], 'sections')
    assert result['markdown'].count('## A') == 1
    assert result['markdown'].count('## B') == 1


def test_format_thread_numbers_items():
    lines = T['format']([{'title': 'A'}, {'title': 'B'}], 'thread')['markdown'].split('\n\n')
    assert lines[0].startswith('1/ ')
    assert lines[1].startswith('2/ ')


@pytest.mark.parametrize('items', [None, []])
def test_format_empty_items_does_not_crash(items):
    assert T['format'](items)['item_count'] == 0


def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http):
    monkeypatch.setenv('TELEGRAM_BOT_TOKEN', 'fake-token')
    monkeypatch.setenv('TELEGRAM_CHAT_ID', '-10042')
    calls = fake_http(FakeResponse({'ok': True}))
    assert T['send']('Bản tin', True)['status'] == 'sent'
    assert len(calls) == 1
    assert calls[0]['method'] == 'POST'
    assert calls[0]['url'] == 'https://api.telegram.org/botfake-token/sendMessage'
    assert calls[0]['json']['chat_id'] == '-10042'
    assert calls[0]['json']['text'] == 'Bản tin'


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http):
    calls = fake_http(FakeResponse())
    assert T['send']('Bản tin', True)['error'] == 'RuntimeError'
    assert calls == []


def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http):
    monkeypatch.setenv('TAVILY_API_KEY', 'fake')
    calls = fake_http(FakeResponse({'results': []}))
    assert T['lookup']('GPU', timeframe=None)['items'] == []
    assert 'time_range' not in calls[0]['json']


def test_fetch_maps_firecrawl_response(monkeypatch, fake_http):
    monkeypatch.setenv('FIRECRAWL_API_KEY', 'fake')
    fake_http(FakeResponse({'data': {'markdown': 'Nội dung', 'metadata': {'title': 'T', 'sourceURL': 'https://example.com/article'}}}))
    item = T['fetch']('https://example.com/article')['items'][0]
    assert item == {'title': 'T', 'url': 'https://example.com/article', 'source': 'example.com', 'summary': 'Nội dung'}


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http):
    monkeypatch.setenv('FIRECRAWL_API_KEY', 'fake')
    fake_http(FakeResponse({'data': {'markdown': 'x' * 5000}}))
    assert len(T['fetch']('https://example.com')['items'][0]['summary']) == 4000


def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http):
    monkeypatch.setenv('RAPIDAPI_KEY', 'fake')
    fake_http(FakeResponse({'timeline': [{'text': 'missing'}] + [{'tweet_id': str(i), 'screen_name': 'sama', 'text': 'tweet'} for i in range(6)]}))
    items = T['timeline']('sama', 3)['items']
    assert [x['url'] for x in items] == [f'https://x.com/sama/status/{i}' for i in range(3)]


@pytest.mark.parametrize('sort', ['Top', 'Latest'])
def test_social_search_passes_search_type(monkeypatch, fake_http, sort):
    monkeypatch.setenv('RAPIDAPI_KEY', 'fake')
    calls = fake_http(FakeResponse({'tweets': []}))
    T['social_search']('GPU', sort)
    assert calls[0]['params'] == {'query': 'GPU', 'search_type': sort}


def test_policy_empty_query_returns_no_results():
    assert T['policy']('')['results'] == []


def test_policy_area_filter_only_returns_that_area():
    results = T['policy']('data privacy', 'data_privacy')['results']
    assert results
    assert all(r['policy_area'] == 'data_privacy' for r in results)


def test_policy_instruction_like_lines_go_to_untrusted_text():
    results = T['policy']('source citation', 'source_citation', 50)['results']
    injection = [r for r in results if r['untrusted_text']]
    assert injection
    assert any('ignore' in line for r in injection for line in r['untrusted_text'])
    assert all('ignore the citation policy' not in r['facts'] for r in results)


def test_deduplicate_preserves_first_item_and_input():
    items = [{'url': 'https://example.com/a?utm_source=x#part', 'title': 'First'}, {'url': 'https://EXAMPLE.com/a', 'title': 'Second'}, {'url': 'https://example.com/b'}]
    result = T['deduplicate'](items)
    assert result['items'] == [items[0], items[2]]
    assert result['duplicate_count'] == 1
    assert result['item_count'] == 2
    assert len(items) == 3


@pytest.mark.parametrize('items', [None, 'bad', [None], [{'url': 42}], [{'url': 'file:///secret'}]])
def test_deduplicate_invalid_input_returns_error(items):
    assert T['deduplicate'](items)['error'] == 'ValueError'


def test_deduplicate_processing_failure_returns_error(monkeypatch):
    import importlib
    module = importlib.import_module('tools.deduplicate.tool')
    def broken(*args):
        raise RuntimeError('parser unavailable')
    monkeypatch.setattr(module, 'urlsplit', broken)
    result = T['deduplicate']([{'url': 'https://example.com'}])
    assert result['error'] == 'RuntimeError'
    assert result['message'] == 'parser unavailable'


def test_deduplicate_keeps_distinct_content_queries():
    items = [{'url': f'https://example.com/?id={i}'} for i in [1, 2]]
    assert T['deduplicate'](items)['items'] == items
    assert T['deduplicate']([])['items'] == []
