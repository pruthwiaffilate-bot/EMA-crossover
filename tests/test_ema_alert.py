from src.ema_alert import detect_cross, ema, should_alert


def test_ema_basic():
    values = [100.0, 102.0, 101.0, 103.0, 104.0]
    result = ema(values, 3)
    assert len(result) == len(values)
    assert result[0] == 100.0
    assert result[-1] > 100.0


def test_detect_bullish_cross():
    prev = [10.0, 12.0, 12.0, 14.0]
    current = [14.5, 15.0]
    assert detect_cross(prev, current) == "bullish"


def test_detect_bearish_cross():
    prev = [15.0, 14.0, 14.0, 12.0]
    current = [12.5, 11.0]
    assert detect_cross(prev, current) == "bearish"


def test_should_alert_only_for_new_cross():
    assert should_alert("bullish", None) is True
    assert should_alert("bullish", "bullish") is False
    assert should_alert("bearish", "bullish") is True
    assert should_alert(None, "bullish") is False
