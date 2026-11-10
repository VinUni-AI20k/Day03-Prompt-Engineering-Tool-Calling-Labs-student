from __future__ import annotations

import re
from typing import Any

# Bộ từ khóa nhận diện sắc thái cảm xúc (hỗ trợ Anh + Việt)
POSITIVE_WORDS = {
    "good", "great", "excellent", "awesome", "amazing", "love", "best", "fantastic",
    "breakthrough", "growth", "success", "innovative", "gain", "positive", "high",
    "profit", "win", "impressive", "bullish", "solid", "perfect",
    "tốt", "hay", "tuyệt", "xuất sắc", "thành công", "tăng trưởng", "đột phá", "thích",
    "đẹp", "lợi nhuận", "ấn tượng", "ổn định", "hoàn hảo", "phát triển"
}

NEGATIVE_WORDS = {
    "bad", "terrible", "awful", "horrible", "hate", "worst", "fail", "failure",
    "crash", "loss", "decline", "bug", "vulnerability", "risk", "negative", "poor",
    "lag", "slow", "error", "drop", "bearish", "scam", "danger",
    "kém", "tệ", "dở", "thất bại", "lỗi", "suy giảm", "nguy hiểm", "chậm", "lag",
    "rủi ro", "lỗ", "lừa đảo", "sụp đổ", "nghiêm trọng"
}


def analyze_sentiment(text: str = "") -> dict[str, Any]:
    """Phân tích sắc thái cảm xúc của văn bản (positive, negative, neutral)."""
    try:
        # Xử lý trường hợp đầu vào rỗng hoặc sai kiểu dữ liệu
        if not text or not isinstance(text, str) or not text.strip():
            return {
                "tool": "sentiment_analyzer",
                "status": "ok",
                "sentiment": "neutral",
                "score": 0.0,
                "confidence": 0.0,
                "summary": "Văn bản rỗng, mặc định trung tính.",
                "details": {
                    "positive_keywords": [],
                    "negative_keywords": [],
                    "word_count": 0,
                },
            }

        cleaned_text = text.lower()
        words = re.findall(r"\w+", cleaned_text, flags=re.UNICODE)
        total_words = len(words)

        pos_matches = [w for w in words if w in POSITIVE_WORDS]
        neg_matches = [w for w in words if w in NEGATIVE_WORDS]

        pos_count = len(pos_matches)
        neg_count = len(neg_matches)

        if pos_count == 0 and neg_count == 0:
            score = 0.0
            sentiment = "neutral"
        else:
            diff = pos_count - neg_count
            total_matched = pos_count + neg_count
            score = round(diff / total_matched, 2)
            if score > 0.15:
                sentiment = "positive"
            elif score < -0.15:
                sentiment = "negative"
            else:
                sentiment = "neutral"

        return {
            "tool": "sentiment_analyzer",
            "status": "ok",
            "sentiment": sentiment,
            "score": score,
            "details": {
                "positive_keywords": pos_matches,
                "negative_keywords": neg_matches,
                "word_count": total_words,
            },
            "summary": f"Văn bản có sắc thái {sentiment} (score: {score}).",
        }
    except Exception as exc:
        return {
            "tool": "sentiment_analyzer",
            "status": "error",
            "error": str(exc),
            "sentiment": "neutral",
            "score": 0.0,
        }


# Alias để tương thích cả 2 cách gọi
sentiment_analyzer = analyze_sentiment
