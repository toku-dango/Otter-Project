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

def test_minimize_resizes_window_to_toast_size(widget):
    # hide() ではなく resize() で小さくする（hide するとトースト表示できない）
    widget.minimize()
    widget._window.resize.assert_called_once()


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


def test_minimize_enqueues_minimize_mode(widget):
    widget.minimize()
    # resize などの後にキューに minimize_mode=True が積まれる
    found = False
    while True:
        try:
            item = widget._pending_queue.get_nowait()
            if item.get("type") == "minimize_mode" and item.get("value") is True:
                found = True
                break
        except Exception:
            break
    assert found


def test_show_enqueues_full_mode(widget):
    widget._minimized = True
    widget.show()
    found = False
    while True:
        try:
            item = widget._pending_queue.get_nowait()
            if item.get("type") == "minimize_mode" and item.get("value") is False:
                found = True
                break
        except Exception:
            break
    assert found


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
