"""PyWebViewWidget の最小化モードとトースト通知のテスト。"""

from unittest.mock import MagicMock, patch
import queue

import pytest


@pytest.fixture
def widget():
    with patch("webview.create_window"), patch("webview.start"):
        from pywebview_widget import PyWebViewWidget
        w = PyWebViewWidget(config=MagicMock())
        w._window = MagicMock()
        return w


# ── Cycle 1: minimize / is_minimized ──────────────────────────────────────

def test_minimize_hides_window(widget):
    widget.minimize()
    widget._window.hide.assert_called_once()


def test_minimize_sets_minimized_flag(widget):
    widget.minimize()
    assert widget.is_minimized() is True


def test_show_clears_minimized_flag(widget):
    widget._minimized = True
    widget._visible = False
    widget.show()
    assert widget.is_minimized() is False


def test_is_minimized_returns_false_by_default(widget):
    assert widget.is_minimized() is False


def test_minimize_sets_visible_false(widget):
    widget._visible = True
    widget.minimize()
    assert widget.is_visible() is False


# ── Cycle 2: show_toast ────────────────────────────────────────────────────

def test_show_toast_enqueues_toast_type(widget):
    widget.show_toast("AIの応答テキスト")
    update = widget._pending_queue.get_nowait()
    assert update["type"] == "toast"


def test_show_toast_enqueues_correct_text(widget):
    widget.show_toast("AIの応答テキスト")
    update = widget._pending_queue.get_nowait()
    assert update["value"] == "AIの応答テキスト"


def test_show_toast_with_empty_string(widget):
    widget.show_toast("")
    update = widget._pending_queue.get_nowait()
    assert update["type"] == "toast"
    assert update["value"] == ""
