"""最小化モード時のオーケストレーター動作テスト。"""

from unittest.mock import MagicMock, call, patch
import pytest

from assistant_orchestrator import AssistantOrchestrator
from screen_capture_service import CaptureResult
from gemini_client import PreloadResult
from session_manager import SessionManager


@pytest.fixture
def mock_widget():
    w = MagicMock()
    w.is_visible.return_value = False
    w.is_minimized.return_value = False
    w.get_last_response.return_value = "テスト応答"
    w.after.side_effect = lambda delay, fn: fn()
    return w


@pytest.fixture
def mock_gemini():
    g = MagicMock()
    g.preload_context.return_value = PreloadResult(
        success=True,
        context_summary="画面を確認しました。",
        chat_session=MagicMock(),
        error_message=None,
        display_message=None,
    )
    g.generate_response.return_value = "返答テキスト"
    g.create_session.return_value = MagicMock()
    return g


@pytest.fixture
def mock_capture():
    c = MagicMock()
    c.capture.return_value = CaptureResult(
        success=True,
        image_base64="dGVzdA==",
        monitor_index=1,
        error_message=None,
    )
    return c


@pytest.fixture
def orchestrator(mock_widget, mock_gemini, mock_capture):
    orch = AssistantOrchestrator(
        hotkey=MagicMock(),
        capture=mock_capture,
        gemini=mock_gemini,
        session_mgr=SessionManager(),
        widget=mock_widget,
        config=MagicMock(),
        clipboard=MagicMock(),
    )
    orch.start()
    return orch


# ── Cycle 3: ホットキー発火時の最小化フロー ─────────────────────────────────

def test_hotkey_when_visible_calls_minimize_before_thread(orchestrator, mock_widget):
    """フル表示中にホットキーを押すと minimize() が呼ばれ、キャプチャが始まる。"""
    mock_widget.is_visible.return_value = True
    mock_widget.is_minimized.return_value = False

    with patch("threading.Thread") as mock_thread:
        mock_thread.return_value.start = MagicMock()
        orchestrator.on_hotkey_triggered()

    mock_widget.minimize.assert_called_once()


def test_hotkey_when_already_minimized_does_not_call_show(orchestrator, mock_widget):
    """最小化中にホットキーを押しても show() は呼ばれない。"""
    mock_widget.is_visible.return_value = False
    mock_widget.is_minimized.return_value = True

    with patch("threading.Thread") as mock_thread:
        mock_thread.return_value.start = MagicMock()
        orchestrator.on_hotkey_triggered()

    mock_widget.show.assert_not_called()


def test_hotkey_when_hidden_calls_show(orchestrator, mock_widget):
    """非表示（最小化でもない）にホットキーを押すと show() が呼ばれる。"""
    mock_widget.is_visible.return_value = False
    mock_widget.is_minimized.return_value = False

    with patch("threading.Thread") as mock_thread:
        mock_thread.return_value.start = MagicMock()
        orchestrator.on_hotkey_triggered()

    mock_widget.show.assert_called_once()


# ── Cycle 4: 応答完了時のトースト表示 ────────────────────────────────────────

def test_response_done_calls_show_toast_when_minimized(orchestrator, mock_widget):
    """最小化モードで応答完了時に show_toast() が呼ばれる。"""
    mock_widget.is_minimized.return_value = True
    mock_widget.get_last_response.return_value = "AIの返答"

    orchestrator._on_response_done(success=True)

    mock_widget.show_toast.assert_called_once_with("AIの返答")


def test_response_done_does_not_call_show_toast_when_visible(orchestrator, mock_widget):
    """フル表示中は show_toast() を呼ばない。"""
    mock_widget.is_minimized.return_value = False

    orchestrator._on_response_done(success=True)

    mock_widget.show_toast.assert_not_called()


def test_response_done_sets_state_done_when_not_minimized(orchestrator, mock_widget):
    """フル表示中は通常通り set_state('DONE') が呼ばれる。"""
    mock_widget.is_minimized.return_value = False

    orchestrator._on_response_done(success=True)

    mock_widget.set_state.assert_called_with("DONE")


# ── Cycle 5: ウォッチドッグタイマー ──────────────────────────────────────────

def test_watchdog_resets_processing_flag(orchestrator, mock_widget):
    """ウォッチドッグ発火で _is_processing が False に戻る。"""
    orchestrator._is_processing = True

    orchestrator._on_watchdog_fired()

    assert orchestrator._is_processing is False


def test_watchdog_sets_state_idle(orchestrator, mock_widget):
    """ウォッチドッグ発火で set_state('IDLE') が呼ばれる。"""
    orchestrator._is_processing = True

    orchestrator._on_watchdog_fired()

    mock_widget.set_state.assert_called_with("IDLE")


def test_watchdog_cancelled_on_response_done(orchestrator, mock_widget):
    """_on_response_done でウォッチドッグがキャンセルされる。"""
    import threading
    timer = threading.Timer(60, lambda: None)
    timer.start()
    orchestrator._watchdog_timer = timer

    mock_widget.is_minimized.return_value = False
    orchestrator._on_response_done(success=True)

    # タイマーがキャンセルされているか（finished または cancelled）
    assert not orchestrator._watchdog_timer


# ── Cycle 6: ホットキーで履歴・チャットをクリア ──────────────────────────────

def test_hotkey_clears_gemini_history(orchestrator, mock_widget, mock_gemini):
    """ホットキー発火で Gemini の会話履歴がクリアされる。"""
    mock_widget.is_visible.return_value = False
    mock_widget.is_minimized.return_value = False

    with patch("threading.Thread") as mock_thread:
        mock_thread.return_value.start = MagicMock()
        orchestrator.on_hotkey_triggered()

    mock_gemini.create_session.assert_called()


def test_hotkey_clears_chat_display(orchestrator, mock_widget):
    """ホットキー発火で clear_chat() が呼ばれる。"""
    mock_widget.is_visible.return_value = False
    mock_widget.is_minimized.return_value = False

    with patch("threading.Thread") as mock_thread:
        mock_thread.return_value.start = MagicMock()
        orchestrator.on_hotkey_triggered()

    mock_widget.clear_chat.assert_called_once()


def test_hotkey_resets_is_processing(orchestrator, mock_widget):
    """ホットキー発火で _is_processing がリセットされる（前の処理が中断される）。"""
    orchestrator._is_processing = True
    mock_widget.is_visible.return_value = False
    mock_widget.is_minimized.return_value = False

    with patch("threading.Thread") as mock_thread:
        mock_thread.return_value.start = MagicMock()
        orchestrator.on_hotkey_triggered()

    assert orchestrator._is_processing is False
