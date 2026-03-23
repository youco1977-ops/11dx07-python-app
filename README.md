# 11dx07-python-app

##株式会社ジョブリッチ様向け提案 
#支援記録システム

## 概要
就労移行支援事業所・就労継続支援A型事業所向けの **支援記録システム（Webアプリ）** です。  
利用者ごとの出席状況・体調を日単位で記録し、データベースに保存できます。  
あわせて、利用者ごとのフォルダ管理やファイル確認も行えます。

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
    ```
3. env.example をコピーして .env 作成
4. 起動
      ```bash
      python app.py
      ```

## 機能一覧
1. **利用者登録（新規）**
   - 利用者コードを自動採番
   - 利用者ごとのフォルダを自動生成
2. **利用者一覧表示**：DBに登録された利用者一覧を表示
3. **利用者詳細表示**
   - 利用者ごとの詳細画面 
   - 専用フォルダ
   - ファイル一覧表示（PDF・画像・txt
4. **日次記録入力**
   - 出席（出席 / 欠席）
   - 体調（1〜10）
   - 利用時間
   - メモ
5. **データベース保存**
   - MySQLへ記録保存
   - 同一日付は上書き更新（`ON DUPLICATE KEY`）
6. **ダッシュボード表示**
   - 今日の日付
   - 記録済み件数
   - 未入力件数
   - 出席 / 欠席一覧

## 画面URL（ローカル）
- Home：`http://127.0.0.1:5000/`
- Dashboard：`http://127.0.0.1:5000/dashboard`
- 利用者一覧：`http://127.0.0.1:5000/clients`
- 利用者詳細（例）：`http://127.0.0.1:5000/clients/1`
- 日次記録入力（例）：`http://127.0.0.1:5000/records/new?client_id=1`

## データベース設計

### テーブル：clients
| カラム名 | 型 | 内容 |
|---|---|---|
| id | INT | 主キー |
| client_code | VARCHAR | 利用者コード |
| name | VARCHAR | 氏名 |
| type | VARCHAR | 種別 |
| storage_folder | VARCHAR | 保存フォルダ |

### テーブル：daily_records
| カラム名 | 型 | 内容 |
|---|---|---|
| id | INT | 主キー |
| client_id | INT | 利用者ID |
| record_date | DATE | 記録日 |
| attendance | VARCHAR(20) | 出席状況 |
| start_time | TIME | 利用開始時間 |
| end_time | TIME | 利用終了時間 |
| condition_score | INT | 体調 |
| note | TEXT | メモ |

## DB（サンプルデータ）

   ```bash
mysql -u root -p jobrich_support < db/schema.sql
mysql -u root -p jobrich_support < db/seed.sql
   ```

## 今後の拡張予定
- 月間出席一覧表示
- CSV出力
- 管理者ログイン機能
- 添付ファイル対応の拡張

## ポイント（面接・実習説明用）
- ChatGPTとGitHubを併用して作成
- Flaskを用いたWebアプリ構築
- MySQLとの接続処理実装
- POST処理・フォーム送信対応
- `ON DUPLICATE KEY` による更新処理
- 環境変数（`.env`）を利用した設定管理
- 利用者フォルダの自動生成とファイル表示機能を実装
