# Google OAuth セットアップ手順

Project Otter を起動するために必要な、Google Cloud Console の初期設定手順です。

---

## 所要時間: 約5〜10分

---

## 手順

### 1. Google Cloud Console にアクセス
https://console.cloud.google.com/

### 2. プロジェクト作成
- 画面上部「プロジェクトを選択」→「新しいプロジェクト」
- プロジェクト名: `project-otter`（任意）
- 「作成」をクリック

### 3. Generative Language API を有効化
- 左メニュー「APIとサービス」→「ライブラリ」
- 検索: `Generative Language API`
- 「有効にする」をクリック

### 4. OAuth 同意画面の設定
- 左メニュー「APIとサービス」→「OAuth 同意画面」
- ユーザーの種類: **外部** → 「作成」
- アプリ名: `Project Otter`
- サポートメール: 自分のメールアドレス
- 「保存して次へ」を3回クリック（スコープ・テストユーザーはスキップ）

### 5. OAuth クライアントID を作成
- 左メニュー「APIとサービス」→「認証情報」
- 「認証情報を作成」→「OAuth クライアントID」
- アプリケーションの種類: **デスクトップアプリ**
- 名前: `Project Otter Desktop`（任意）
- 「作成」をクリック

### 6. JSON をダウンロード
- 作成されたクライアントID の右端「↓」ボタンをクリック
- ダウンロードされたファイルを `client_secrets.json` にリネーム
- `project-otter/` フォルダに配置

### 7. テストユーザーの追加（重要）
- 左メニュー「APIとサービス」→「OAuth 同意画面」→「テストユーザー」
- 「ユーザーを追加」→ 自分の Google アカウントのメールアドレスを入力
- 「保存」をクリック

---

## 初回起動

```bash
cd project-otter
python main.py
```

ブラウザが自動で開きます。Google アカウントでログインして「許可」を押せば完了。
2回目以降はブラウザが開かずそのまま起動します。

---

## ファイル配置の確認

```
project-otter/
  client_secrets.json   ← ここに配置（手順6）
  main.py
  requirements.txt
  ...
```

---

## トラブルシューティング

| エラー | 原因 | 対処 |
|---|---|---|
| `client_secrets.json が見つかりません` | ファイルが未配置 | 手順6を再確認 |
| `アクセスブロック` 画面が表示される | テストユーザー未登録 | 手順7を実施 |
| ブラウザが開かない | ポートブロック | `python main.py` を管理者権限で実行 |
