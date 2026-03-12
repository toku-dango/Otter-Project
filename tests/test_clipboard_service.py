from unittest.mock import patch

from clipboard_service import ClipboardService


def test_copy_returns_true_on_success():
    service = ClipboardService()
    with patch("clipboard_service.pyperclip.copy") as mock_copy:
        result = service.copy("テストテキスト")
    assert result is True
    mock_copy.assert_called_once_with("テストテキスト")


def test_copy_returns_false_on_failure():
    service = ClipboardService()
    with patch("clipboard_service.pyperclip.copy", side_effect=Exception("clipboard error")):
        result = service.copy("テストテキスト")
    assert result is False


def test_copy_does_not_raise_on_failure():
    service = ClipboardService()
    with patch("clipboard_service.pyperclip.copy", side_effect=RuntimeError("error")):
        try:
            service.copy("テスト")
        except Exception:
            assert False, "copy() should not raise exceptions"
