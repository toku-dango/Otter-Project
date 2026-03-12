from unittest.mock import MagicMock, patch

import pytest

from assistant_orchestrator import AssistantOrchestrator
from screen_capture_service import CaptureResult
from gemini_client import PreloadResult
from session_manager import SessionManager


@pytest.fixture
def mock_widget():
    w = MagicMock()
    w.is_visible.return_value = False
    w.get_last_response.return_value = "テスト応答"
    # after() を同期的に実行するモック
    w.after.side_effect = lambda delay, fn: fn()
    return w


@pytest.fixture
def mock_gemini():
    g = MagicMock()
    g.preload_context.return_value = PreloadResult(
        success=True,
        context_summary="メール画面を確認しました。",
        chat_session=MagicMock(),
        error_message=None,
    )
    g.generate_response.return_value = "丁寧な文章に書き換えました。"
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
    session_mgr = SessionManager()
    orch = AssistantOrchestrator(
        hotkey=MagicMock(),
        capture=mock_capture,
        gemini=mock_gemini,
        session_mgr=session_mgr,
        widget=mock_widget,
        config=MagicMock(),
        clipboard=MagicMock(),
    )
    orch.start()
    return orch


def test_start_registers_hotkey(mock_widget, mock_gemini, mock_capture):
    mock_hotkey = MagicMock()
    session_mgr = SessionManager()
    orch = AssistantOrchestrator(
        hotkey=mock_hotkey,
        capture=mock_capture,
        gemini=mock_gemini,
        session_mgr=session_mgr,
        widget=mock_widget,
        config=MagicMock(),
        clipboard=MagicMock(),
    )
    orch.start()
    mock_hotkey.register.assert_called_once()


def test_on_hotkey_triggered_when_widget_hidden_shows_widget(orchestrator, mock_widget):
    mock_widget.is_visible.return_value = False

    with patch("threading.Thread") as mock_thread:
        mock_thread.return_value.start = MagicMock()
        orchestrator.on_hotkey_triggered()

    mock_widget.show.assert_called_once()
    mock_widget.set_state.assert_called_with("THINKING")


def test_on_hotkey_triggered_when_widget_visible_shows_dialog(orchestrator, mock_widget):
    mock_widget.is_visible.return_value = True

    with patch("assistant_orchestrator.messagebox.askyesno", return_value=True):
        orchestrator.on_hotkey_triggered()

    mock_widget.hide.assert_called_once()


def test_on_hotkey_triggered_cancel_dialog_does_not_hide(orchestrator, mock_widget):
    mock_widget.is_visible.return_value = True

    with patch("assistant_orchestrator.messagebox.askyesno", return_value=False):
        orchestrator.on_hotkey_triggered()

    mock_widget.hide.assert_not_called()


def test_on_user_input_empty_string_is_ignored(orchestrator, mock_widget, mock_gemini):
    orchestrator.on_user_input("")
    orchestrator.on_user_input("   ")
    mock_gemini.generate_response.assert_not_called()


def test_on_user_input_calls_generate_response(orchestrator, mock_gemini, mock_widget):
    with patch("threading.Thread") as mock_thread:
        instance = MagicMock()
        mock_thread.return_value = instance
        orchestrator.on_user_input("丁寧に")
        instance.start.assert_called_once()


def test_on_copy_requested_calls_clipboard(orchestrator, mock_widget):
    orchestrator._clipboard = MagicMock()
    orchestrator.on_copy_requested()
    orchestrator._clipboard.copy.assert_called_once_with("テスト応答")


def test_stop_unregisters_hotkey(orchestrator):
    orchestrator.stop()
    orchestrator._hotkey.unregister.assert_called_once()


def test_capture_failure_shows_error_message(orchestrator, mock_capture, mock_widget):
    mock_capture.capture.return_value = CaptureResult(
        success=False,
        image_base64=None,
        monitor_index=None,
        error_message="mss error",
    )
    orchestrator._preload_worker()
    mock_widget.set_status_message.assert_called()
    msg = mock_widget.set_status_message.call_args[0][0]
    assert "失敗" in msg
