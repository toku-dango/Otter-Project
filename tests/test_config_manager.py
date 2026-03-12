import json
import tempfile
from pathlib import Path

import pytest

from config_manager import ConfigManager


@pytest.fixture
def tmp_config(tmp_path):
    config_file = tmp_path / "config.json"
    return ConfigManager(config_file=config_file)


def test_get_setting_returns_default_when_not_set(tmp_config):
    assert tmp_config.get_setting("widget_x", -1) == -1


def test_set_and_get_setting(tmp_config):
    tmp_config.set_setting("widget_x", 100)
    tmp_config.set_setting("widget_y", 200)
    assert tmp_config.get_setting("widget_x") == 100
    assert tmp_config.get_setting("widget_y") == 200


def test_set_setting_persists_to_file(tmp_path):
    config_file = tmp_path / "config.json"
    mgr = ConfigManager(config_file=config_file)
    mgr.set_setting("widget_width", 500)

    # 新しいインスタンスで読み込んでも値が保持されること
    mgr2 = ConfigManager(config_file=config_file)
    assert mgr2.get_setting("widget_width") == 500


def test_corrupted_config_falls_back_to_defaults(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text("{ invalid json }", encoding="utf-8")

    # 破損ファイルでも例外を上げずにデフォルト設定で起動すること
    mgr = ConfigManager(config_file=config_file)
    assert mgr.get_setting("widget_width", 400) == 400


def test_widget_config_default_is_default_position(tmp_config):
    wc = tmp_config.get_widget_config()
    assert wc.is_default() is True


def test_widget_config_after_position_set(tmp_config):
    tmp_config.set_setting("widget_x", 300)
    tmp_config.set_setting("widget_y", 400)
    wc = tmp_config.get_widget_config()
    assert wc.is_default() is False
