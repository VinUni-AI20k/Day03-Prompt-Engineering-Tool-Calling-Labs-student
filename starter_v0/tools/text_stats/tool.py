from typing import Any, Dict


def text_stats(text: str, wpm: int = 200) -> Dict[str, Any]:
    """Calculate word count, character count, and reading time for a text."""
    # 1. Kiểm tra kiểu dữ liệu và chuỗi rỗng (Input xấu từ model)
    if not isinstance(text, str) or not text.strip():
        return {
            "tool": "text_stats",
            "status": "error",
            "error": "Parameter 'text' must be a non-empty string.",
            "items": [],
        }

    # 2. Xử lý khi model truyền wpm dạng chuỗi (ví dụ "200") hoặc số âm/bằng 0 (Nhánh lỗi)
    try:
        wpm_val = int(wpm)
    except (ValueError, TypeError):
        return {
            "tool": "text_stats",
            "status": "error",
            "error": "Parameter 'wpm' must be a valid integer.",
            "items": [],
        }

    if wpm_val <= 0:
        return {
            "tool": "text_stats",
            "status": "error",
            "error": "Parameter 'wpm' must be greater than 0.",
            "items": [],
        }

    # 3. Happy path: Tính toán thống kê
    cleaned_text = text.strip()
    words = cleaned_text.split()
    word_count = len(words)
    char_count = len(cleaned_text)
    reading_time_sec = round((word_count / wpm_val) * 60, 1)

    stat_item = {
        "title": "Text Statistics",
        "word_count": word_count,
        "char_count": char_count,
        "wpm": wpm_val,
        "estimated_reading_seconds": reading_time_sec,
        "snippet": f"{word_count} words, {char_count} chars (~{reading_time_sec}s read at {wpm_val} wpm).",
    }

    return {
        "tool": "text_stats",
        "status": "ok",
        "word_count": word_count,
        "char_count": char_count,
        "estimated_reading_seconds": reading_time_sec,
        "items": [stat_item],
    }