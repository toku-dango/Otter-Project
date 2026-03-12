import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Exchange:
    user_input: str
    ai_response: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Session:
    session_id: str
    chat_session: Any
    history: list[Exchange] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    preload_summary: str | None = None


class SessionManager:
    """アプリ起動中の会話セッションをメモリ上で管理する。ディスクへの書き込みは行わない。"""

    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}

    def start_session(self, chat_session: Any = None) -> Session:
        """新しいセッションを開始して返す。session_id は UUID4 で自動生成。"""
        session = Session(
            session_id=str(uuid.uuid4()),
            chat_session=chat_session,
        )
        self._sessions[session.session_id] = session
        logger.debug("Session started: session_id=%s", session.session_id)
        return session

    def end_session(self, session_id: str) -> None:
        """セッションを終了し、全履歴をメモリから消去する。"""
        if session_id in self._sessions:
            self._sessions.pop(session_id)
            logger.debug("Session ended: session_id=%s", session_id)

    def add_exchange(self, session_id: str, user_input: str, ai_response: str) -> None:
        """会話1往復（ユーザー入力＋AI応答）を履歴に追加する。"""
        session = self._sessions.get(session_id)
        if session is None:
            logger.warning("add_exchange: session not found: session_id=%s", session_id)
            return
        session.history.append(Exchange(user_input=user_input, ai_response=ai_response))
        logger.debug(
            "Exchange added: session_id=%s, history_length=%d",
            session_id,
            len(session.history),
        )

    def get_session(self, session_id: str) -> Session | None:
        """セッションIDからセッションオブジェクトを返す。存在しない場合は None。"""
        return self._sessions.get(session_id)

    def update_preload_summary(self, session_id: str, summary: str) -> None:
        """最新の画面把握サマリーを更新する。ホットキー押下のたびに上書き。"""
        session = self._sessions.get(session_id)
        if session:
            session.preload_summary = summary
            logger.debug("Preload summary updated: session_id=%s", session_id)
