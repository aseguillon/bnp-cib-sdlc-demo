from app.main import validate_trade


def test_valid_trade():
    assert validate_trade({"currency": "EUR", "notional": 1_000_000, "side": "BUY"}) == []


def test_bad_currency():
    assert "unsupported currency" in validate_trade({"currency": "XXX", "notional": 1, "side": "BUY"})


def test_notional_limit():
    assert "notional exceeds limit" in validate_trade({"currency": "USD", "notional": 99_000_000, "side": "SELL"})
