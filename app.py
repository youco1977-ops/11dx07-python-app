from flask import Flask, render_template, request, redirect, url_for, abort
from dotenv import load_dotenv
import os
import pymysql
from datetime import date

from pathlib import Path
env_path = Path(__file__).with_name(".env")
load_dotenv(env_path)

app = Flask(__name__)

# 仮データ（後でMySQLに置き換える）
CLIENTS = [
    {"id": 1, "name": "山田 太郎", "type": "移行"},
    {"id": 2, "name": "佐藤 花子", "type": "A型"},
]
def get_client_name(client_id):
    client = next((c for c in CLIENTS if c["id"] == client_id), None)
    return client["name"] if client else f"id={client_id}"

def get_conn():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASS", ""),
        database=os.getenv("DB_NAME", "jobrich_support"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )

@app.route("/")
def home():
    return render_template("index.html", title="Home")

@app.route("/dashboard")
def dashboard():
    today = date.today()
    low_threshold = 3

    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
    "SELECT client_id, attendance, condition_score, start_time, end_time, note "
     "FROM daily_records WHERE record_date=%s",
    (today,)
    )
        rows = cur.fetchall()
    conn.close()

    total_clients = len(CLIENTS)
    saved_count = len(rows)
    missing_count = total_clients - saved_count

    # 出席 / 欠席 に分ける
    present = [r for r in rows if r["attendance"] == "present"]
    absent  = [r for r in rows if r["attendance"] == "absent"]

    return render_template(
        "dashboard.html",
        title="Dashboard",
        today=today,
        total_clients=total_clients,
        saved_count=saved_count,
        missing_count=missing_count,
        present=present,
        absent=absent,
        low_threshold=low_threshold,
        get_client_name=get_client_name
    )

@app.route("/clients")
def clients():
    return render_template("clients.html", title="利用者一覧", clients=CLIENTS)

@app.route("/clients/<int:client_id>")
def client_detail(client_id):
    client = next((c for c in CLIENTS if c["id"] == client_id), None)
    if not client:
        return "Not Found", 404

    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT record_date, attendance, start_time, end_time, condition_score, note
            FROM daily_records
            WHERE client_id=%s
            ORDER BY record_date DESC
            LIMIT 7
            """,
            (client_id,)
        )
        history = cur.fetchall()
    conn.close()

    return render_template("client_detail.html", title="利用者詳細", client=client, history=history)

@app.route("/records/new")
def record_new():
    client_id = request.args.get("client_id", type=int)
    if not client_id:
        abort(400, description="client_id が必要です")

    client = next((c for c in CLIENTS if c["id"] == client_id), None)
    if not client:
        abort(404, description="利用者が見つかりません")

    return render_template(
        "record_form.html",
        client=client,
        today=date.today().isoformat()
    )

@app.route("/records/save", methods=["POST"])
def record_save():
    client_id = int(request.form.get("client_id"))
    attendance = request.form.get("attendance")

    # 体調
    condition_raw = request.form.get("condition")
    if not condition_raw:
        abort(400, description="体調が未入力です")
    condition = int(condition_raw)

    # 追加：時間とメモ（空はNone）
    start_time = request.form.get("start_time") or None
    end_time   = request.form.get("end_time") or None
    note       = request.form.get("note", "").strip() or None

    # 欠席なら時間はクリア（事故防止）
    if attendance == "absent":
        start_time = None
        end_time = None

    # 時間の前後チェック（両方入ってるときだけ）
    if start_time and end_time and end_time < start_time:
        abort(400, description="退所時間は出所時間より後にしてください")

    today = date.today()

    sql = """
    INSERT INTO daily_records
      (client_id, record_date, attendance, start_time, end_time, condition_score, note)
    VALUES
      (%s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
      attendance = VALUES(attendance),
      start_time = VALUES(start_time),
      end_time = VALUES(end_time),
      condition_score = VALUES(condition_score),
      note = VALUES(note);
    """

    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(sql, (client_id, today, attendance, start_time, end_time, condition, note))
    conn.close()

    return redirect(url_for("client_detail", client_id=client_id))

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html", title="Not Found"), 404

#ルートはこの上に追加していく
if __name__ == "__main__":
    app.run(debug=True)