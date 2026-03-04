from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
import os
import pymysql
from datetime import date

from pathlib import Path
load_dotenv(Path(__file__).with_name(".env"))

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
            "SELECT client_id, attendance, condition_score FROM daily_records WHERE record_date=%s",
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
    return render_template("client_detail.html", title="利用者詳細", client=client)

@app.route("/records/new")
def record_new():
    client_id = request.args.get("client_id")
    return render_template("record_form.html", client_id=client_id)

@app.route("/records/save", methods=["POST"])
def record_save():
    client_id = int(request.form.get("client_id"))
    attendance = request.form.get("attendance")
    condition = int(request.form.get("condition"))

    today = date.today()

    sql = """
    INSERT INTO daily_records (client_id, record_date, attendance, condition_score)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
      attendance = VALUES(attendance),
      condition_score = VALUES(condition_score);
    """

    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(sql, (client_id, today, attendance, condition))
    conn.commit()
    conn.close()

    return redirect(url_for("client_detail", client_id=client_id))

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html", title="Not Found"), 404

#ルートはこの上に追加していく
if __name__ == "__main__":
    app.run(debug=True)