from app.main import E164_PATTERN


def test_e164_validation_accepts_and_rejects_expected_values():
    assert E164_PATTERN.fullmatch("+919876543210")
    assert E164_PATTERN.fullmatch("+14155551234")
    assert not E164_PATTERN.fullmatch("9876543210")
    assert not E164_PATTERN.fullmatch("+91 98765 43210")
    assert not E164_PATTERN.fullmatch("+0123456789")
