# Domain Entities — Unit 2: UI & Configuration

## エンティティ一覧

| Entity | 種別 | 説明 |
|---|---|---|
| WidgetState | Enum | FloatingWidget の表示状態 |
| AnimationState | Enum | Otter アニメーションの状態 |
| WidgetConfig | Value Object | ウィジェット位置・サイズ設定 |
| AppConfig | Value Object | アプリ全体設定 |

---

## WidgetState（Enum）

Unit 1 の `AssistantOrchestrator` が `set_state()` で指定する。

```python
class WidgetState(Enum):
    IDLE = "IDLE"           # 待機中・入力受付可能
    THINKING = "THINKING"   # AI処理中・入力無効
    DONE = "DONE"           # 応答表示完了・コピーボタン表示
```

**状態遷移**:
```
起動 → THINKING（preload中）→ IDLE（完了/失敗）
IDLE → THINKING（ユーザー送信）→ DONE（成功）/ IDLE（失敗）
DONE → IDLE（次の入力時）
```

---

## AnimationState（Enum）

```python
class AnimationState(Enum):
    IDLE = "idle"
    THINKING = "thinking"
    DONE = "done"           # 1回再生後 IDLE に自動遷移
```

**GIF ファイルマッピング**:
| AnimationState | GIF ファイル | プレースホルダー |
|---|---|---|
| IDLE | `assets/idle.gif` | 🦦 |
| THINKING | `assets/thinking.gif` | 🦦💭 |
| DONE | `assets/done.gif` | 🦦✨ |

---

## WidgetConfig（Value Object）

ウィジェットの表示位置・サイズを保持する。`ConfigManager` が JSON で永続化する。

```python
@dataclass
class WidgetConfig:
    x: int = -1              # -1 はデフォルト位置を意味する
    y: int = -1
    width: int = 400
    height: int = 500

    def is_default(self) -> bool:
        return self.x == -1 or self.y == -1
```

---

## AppConfig（Value Object）

`ConfigManager` が `config.json` に保存するアプリ全体の設定。

```python
@dataclass
class AppConfig:
    widget: WidgetConfig = field(default_factory=WidgetConfig)
    # 将来拡張: hotkey_combo, theme, excluded_apps 等
```
