import pytest
from session_manager import SessionManager


@pytest.fixture
def manager():
    return SessionManager()


def test_start_session_returns_session_with_id(manager):
    session = manager.start_session()
    assert session.session_id is not None
    assert len(session.session_id) > 0


def test_start_session_stores_session(manager):
    session = manager.start_session()
    assert manager.get_session(session.session_id) is session


def test_add_exchange_appends_to_history(manager):
    session = manager.start_session()
    manager.add_exchange(session.session_id, "丁寧に", "かしこまりました。")
    assert len(session.history) == 1
    assert session.history[0].user_input == "丁寧に"
    assert session.history[0].ai_response == "かしこまりました。"


def test_add_exchange_accumulates_history(manager):
    session = manager.start_session()
    manager.add_exchange(session.session_id, "入力1", "応答1")
    manager.add_exchange(session.session_id, "入力2", "応答2")
    assert len(session.history) == 2


def test_end_session_removes_session(manager):
    session = manager.start_session()
    manager.end_session(session.session_id)
    assert manager.get_session(session.session_id) is None


def test_get_session_returns_none_for_unknown_id(manager):
    assert manager.get_session("nonexistent-id") is None


def test_add_exchange_on_nonexistent_session_does_not_raise(manager):
    manager.add_exchange("nonexistent-id", "入力", "応答")


def test_update_preload_summary(manager):
    session = manager.start_session()
    manager.update_preload_summary(session.session_id, "メール作成画面を表示中")
    assert session.preload_summary == "メール作成画面を表示中"


def test_multiple_sessions_are_independent(manager):
    s1 = manager.start_session()
    s2 = manager.start_session()
    manager.add_exchange(s1.session_id, "入力A", "応答A")
    assert len(s2.history) == 0
