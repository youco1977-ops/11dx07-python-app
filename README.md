# 11dx07-python-app

##株式会社ジョブリッチ様向け提案 
#利用者出欠管理システム

## 概要
就労移行支援事業所・就労継続支援A型事業所向けの **利用者出欠管理システム（Webアプリ）** です。  
利用者ごとの出席状況・体調を日単位で記録し、データベースに保存できます。

## 開発環境
- Python 3.x
- Flask
- MySQL（XAMPP）
- PyMySQL
- HTML / Jinja2

## 起動方法
1. XAMPP を起動（MySQL を Start）
2. ライブラリをインストール
    ```bash
    pip install -r requirements.txt
3. env.example をコピーして .env 作成
4. 起動
   python app.py


## 機能一覧
1. **利用者一覧表示**：仮データで利用者一覧を表示  
2. **利用者詳細表示**：利用者ごとの詳細画面  
3. **日次記録入力**
   - 出席（出席 / 欠席）
   - 体調（1〜10）
4. **データベース保存**
   - MySQLへ記録保存
   - 同一日付は上書き更新（`ON DUPLICATE KEY`）

## 画面URL（ローカル）
- Home：`http://127.0.0.1:5000/`
- Dashboard：`http://127.0.0.1:5000/dashboard`
- 利用者一覧：`http://127.0.0.1:5000/clients`
- 利用者詳細（例）：`http://127.0.0.1:5000/clients/1`
- 日次記録入力（例）：`http://127.0.0.1:5000/records/new?client_id=1`

## データベース設計
### テーブル：daily_records
| カラム名 | 型 | 内容 |
|---|---|---|
| id | INT | 主キー |
| client_id | INT | 利用者ID |
| record_date | DATE | 記録日 |
| attendance | VARCHAR(20) | 出席状況 |
| condition_score | INT | 体調 |
| created_at | DATETIME | 作成日時 |

## 今後の拡張予定
- 利用者をDB管理に変更
- 月間出席一覧表示
- CSV出力
- 管理者ログイン機能

## ポイント（面接・実習説明用）
- ChatGPTとGitHubを併用して作成
- Flaskを用いたWebアプリ構築
- MySQLとの接続処理実装
- POST処理・フォーム送信対応
- `ON DUPLICATE KEY` による更新処理
- 環境変数（`.env`）を利用した設定管理
