import base64
from unittest.mock import MagicMock, patch

import pytest
from google.api_core import exceptions as google_exceptions

from gemini_client import GeminiClient, PreloadResult


@pytest.fixture
def mock_credentials():
    return MagicMock()


@pytest.fixture
def client(mock_credentials):
    with patch("gemini_client.genai.configure"), patch(
        "gemini_client.genai.GenerativeModel"
    ) as mock_model_cls:
        mock_model_cls.return_value = MagicMock()
        c = GeminiClient(credentials=mock_credentials)
        c._model = mock_model_cls.return_value
        return c


def _dummy_image_base64() -> str:
    from PIL import Image
    from io import BytesIO
    img = Image.new("RGB", (10, 10), color=(0, 0, 0))
    buf = BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def test_preload_context_success(client):
    mock_chat = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "メール作成画面を表示中です。"
    mock_chat.send_message.return_value = mock_response
    client._model.start_chat.return_value = mock_chat

    result = client.preload_context(_dummy_image_base64())

    assert result.success is True
    assert result.context_summary == "メール作成画面を表示中です。"
    assert result.chat_session is mock_chat
    assert result.error_message is None


def test_preload_context_returns_failure_on_error(client):
    client._model.start_chat.side_effect = Exception("connection error")

    result = client.preload_context(_dummy_image_base64())

    assert result.success is False
    assert result.context_summary is None
    assert result.chat_session is None
    assert result.error_message is not None


def test_preload_context_retries_on_retryable_error(client):
    mock_chat = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "画面を把握しました。"
    mock_chat.send_message.side_effect = [
        google_exceptions.ServiceUnavailable("503"),
        mock_response,
    ]
    client._model.start_chat.return_value = mock_chat

    with patch("gemini_client.time.sleep"):
        result = client.preload_context(_dummy_image_base64())

    assert result.success is True


def test_generate_response_success(client):
    mock_chat = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "丁寧な文章に書き換えました。"
    mock_chat.send_message.return_value = mock_response

    result = client.generate_response("丁寧に", mock_chat)

    assert result == "丁寧な文章に書き換えました。"


def test_generate_response_retries_on_retryable_error(client):
    mock_chat = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "応答テキスト"
    mock_chat.send_message.side_effect = [
        google_exceptions.ResourceExhausted("429"),
        google_exceptions.ResourceExhausted("429"),
        mock_response,
    ]

    with patch("gemini_client.time.sleep"):
        result = client.generate_response("短く", mock_chat)

    assert result == "応答テキスト"


def test_generate_response_raises_after_max_retries(client):
    mock_chat = MagicMock()
    mock_chat.send_message.side_effect = google_exceptions.ServiceUnavailable("503")

    with patch("gemini_client.time.sleep"):
        with pytest.raises(google_exceptions.ServiceUnavailable):
            client.generate_response("入力", mock_chat)
