# Performance Test Instructions — Project Otter

## 概要

Project Otter はシングルユーザー向けデスクトップアプリのため、従来の負荷テスト（多数の同時リクエスト）は対象外。
代わりに「レスポンスタイム」と「メモリ使用量」を主軸とした性能テストを実施する。

---

## 性能要件（NFR）

| 指標 | 目標値 | 優先度 |
|---|---|---|
| ホットキー → ウィジェット表示 | < 500ms | High |
| スクリーンキャプチャ完了 | < 2s | High |
| プリロード完了（Gemini API） | < 10s（タイムアウト設定値）| Medium |
| 質問 → 応答表示 | < 30s（タイムアウト設定値）| Medium |
| アプリ起動（OAuth 認証済み） | < 3s | Medium |
| メモリ使用量（起動後安定状態） | < 200MB | Low |

---

## テスト 1: 起動時間計測

**目的**: アプリ起動（`python main.py`）から操作可能状態までの時間計測

```bash
# PowerShell（Windows）
$sw = [System.Diagnostics.Stopwatch]::StartNew()
python main.py &
# ウィジェットが表示されたら手動でストップ
$sw.Stop()
Write-Host "起動時間: $($sw.ElapsedMilliseconds)ms"
```

**期待値**: 3000ms 以内（OAuth キャッシュ済み）

---

## テスト 2: ホットキー応答時間

**目的**: `Ctrl+Shift+Space` 押下 → ウィジェット表示までのレイテンシ確認

**手順**:
1. アプリ起動・ウィジェット非表示状態
2. `Ctrl+Shift+Space` を押下した瞬間から目視でカウント
3. ウィジェットが表示されるまでの時間を記録
4. 5回繰り返して平均を取る

**期待値**: 500ms 以内（体感でほぼ瞬時）

---

## テスト 3: スクリーンキャプチャ性能

**目的**: `ScreenCaptureService.capture()` の実行時間計測

```python
# tests/perf_capture.py（手動実行用スクリプト）
import time
from screen_capture_service import ScreenCaptureService

svc = ScreenCaptureService()
times = []

for i in range(10):
    start = time.perf_counter()
    result = svc.capture()
    elapsed = time.perf_counter() - start
    times.append(elapsed * 1000)
    print(f"Run {i+1}: {elapsed*1000:.1f}ms | success={result.success} | size={len(result.image_base64) if result.image_base64 else 0} bytes")

print(f"\n平均: {sum(times)/len(times):.1f}ms | 最大: {max(times):.1f}ms")
```

```bash
cd project-otter
python tests/perf_capture.py
```

**期待値**: 平均 < 2000ms

---

## テスト 4: メモリ使用量モニタリング

**目的**: 長時間使用でのメモリリーク確認

```bash
# Windows — タスクマネージャーで python.exe のメモリを観察
# または PowerShell で定期計測:
$process = Get-Process -Name python | Sort-Object StartTime -Descending | Select-Object -First 1
while ($true) {
    $mem = [math]::Round($process.WorkingSet64 / 1MB, 1)
    Write-Host "$(Get-Date -Format 'HH:mm:ss') Memory: ${mem}MB"
    Start-Sleep -Seconds 30
}
```

**テスト手順**:
1. アプリ起動後 30 分間、10〜20 回のホットキー起動・質問送信を繰り返す
2. メモリ使用量の推移を記録

**期待値**: 起動時比 +100MB 以内（200MB 未満が理想）

---

## テスト 5: Gemini API 応答時間（実測）

**目的**: preload_context / generate_response の実際の応答時間確認

**確認方法**: `app.log` のタイムスタンプ差分で計測

```bash
# ログから API 呼び出し時間を抽出
Select-String -Path "$env:USERPROFILE\.config\project-otter\app.log" -Pattern "preload|generate"
```

**期待値**:
- preload_context: < 10s（タイムアウト前に完了）
- generate_response: < 30s（タイムアウト前に完了）

---

## 性能問題の対処

| 問題 | 原因候補 | 対処 |
|---|---|---|
| ウィジェット表示が遅い | tkinter 初期化 | `withdraw()` → `deiconify()` パターン確認 |
| キャプチャが遅い | 4K モニター | mss の解像度設定を確認 |
| Gemini が常にタイムアウト | ネットワーク / API 負荷 | タイムアウト値を NFR 設計に沿って調整 |
| メモリが増加し続ける | Pillow PhotoImage GC リーク | `label.image = frame` 参照保持を確認 |
