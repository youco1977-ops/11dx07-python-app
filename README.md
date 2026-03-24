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
- MariaDB（xampp）
- HTML / CSS / Jinja2

## 起動方法（先生確認用）
※ 本アプリは Flask + MariaDB（XAMPP）で動作します。確認時は XAMPP の MySQL を起動した状態で `start_for_teacher.bat` を実行してください。

1. XAMPP を起動し、MySQL を Start
2. プロジェクトフォルダ内の `start_for_teacher.bat` をダブルクリック
3. ブラウザで `http://127.0.0.1:5000` にアクセス

## DB（サンプルデータ）
```bash
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS jobrich_support CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;"
mysql -u root -p jobrich_support < db/schema.sql
mysql -u root -p jobrich_support < db/seed.sql
   ```

### 補足
- 初回起動時は仮想環境の作成とライブラリのインストールを行います
- `.env` が存在しない場合は `env.example` をもとに自動作成します
- MySQL が起動していない場合は接続エラーになります

## 機能一覧
1. **利用者登録（新規）**
   - 利用者コードを自動採番
   - 利用者ごとのフォルダを自動生成
2. **利用者一覧表示**：DBに登録された利用者一覧を表示
3. **利用者詳細表示**
   - 利用者ごとの詳細画面 
   - 専用フォルダ
   - ファイル一覧表示（PDF・画像・txt）
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
| カラム名           | 型            | 内容     |
| -------------- | ------------ | ------ |
| id             | INT          | 主キー    |
| client_code    | INT          | 利用者コード |
| name           | VARCHAR(100) | 氏名     |
| type           | VARCHAR(50)  | 種別     |
| created_at     | DATETIME     | 作成日時   |
| storage_folder | VARCHAR(255) | 保存フォルダ |


### テーブル：daily_records
| カラム名            | 型           | 内容     |
| --------------- | ----------- | ------ |
| id              | INT         | 主キー    |
| client_id       | INT         | 利用者ID  |
| record_date     | DATE        | 記録日    |
| attendance      | VARCHAR(20) | 出席状況   |
| start_time      | TIME        | 利用開始時間 |
| end_time        | TIME        | 利用終了時間 |
| condition_score | INT         | 体調     |
| note            | TEXT        | メモ     |
| created_at      | DATETIME    | 作成日時   |




## 今後の拡張予定
- 月間出席一覧表示
- CSV出力
- 管理者ログイン機能
- 添付ファイル対応の拡張


