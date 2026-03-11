from flask import Flask, render_template, request, redirect, url_for, abort, send_file
from dotenv import load_dotenv
import os
import pymysql
import mimetypes
from datetime import date
from pathlib import Path

env_path = Path(__file__).with_name(".env")
load_dotenv(env_path)

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
CLIENT_FILES_DIR = BASE_DIR / "data"

VIEWABLE_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".txt"}


def get_client_name(client_id):
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT name FROM clients WHERE id=%s", (client_id,))
        row = cur.fetchone()
    conn.close()
    return row["name"] if row else f"id={client_id}"


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


def create_client_folder(client_code, name):
    folder_name = f"{client_code}_{name}"
    folder_path = os.path.join("data", folder_name)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path


def get_client_folder_path(client):
    folder_name = f"{client['client_code']}_{client['name']}"
    return CLIENT_FILES_DIR / folder_name


# ここから＠デコレーター（URL案内タグ）
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

        cur.execute("SELECT COUNT(*) AS cnt FROM clients")
        total_clients = cur.fetchone()["cnt"]
    conn.close()

    saved_count = len(rows)
    missing_count = total_clients - saved_count

    present = [r for r in rows if r["attendance"] == "present"]
    absent = [r for r in rows if r["attendance"] == "absent"]

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
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT id, client_code, name, type, storage_folder FROM clients ORDER BY id")
        clients = cur.fetchall()
    conn.close()
    return render_template("clients.html", title="利用者一覧", clients=clients)


@app.route("/clients/<int:client_id>")
def client_detail(client_id):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, client_code, name, type, storage_folder FROM clients WHERE id=%s",
                (client_id,)
            )
            client = cur.fetchone()

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
    finally:
        conn.close()

    if not client:
        return "Not Found", 404

    folder = get_client_folder_path(client)
    files = []

    if folder.exists():
        for f in sorted(folder.iterdir()):
            if f.is_file() and f.suffix.lower() in VIEWABLE_EXTENSIONS:
                files.append(f.name)

    return render_template(
        "client_detail.html",
        title="利用者詳細",
        client=client,
        history=history,
        files=files
    )


@app.route("/clients/<int:client_id>/files/<path:filename>")
def client_file_view(client_id, filename):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, client_code, name, type, storage_folder FROM clients WHERE id=%s",
                (client_id,)
            )
            client = cur.fetchone()
    finally:
        conn.close()

    if not client:
        abort(404)

    folder = get_client_folder_path(client)
    file_path = folder / filename

    try:
        file_path.resolve().relative_to(folder.resolve())
    except ValueError:
        abort(404)

    if not file_path.exists() or not file_path.is_file():
        abort(404)

    if file_path.suffix.lower() not in VIEWABLE_EXTENSIONS:
        abort(404)

    mime_type, _ = mimetypes.guess_type(str(file_path))
    return send_file(file_path, mimetype=mime_type)

#フォルダオープン
@app.route("/clients/<int:client_id>/open-folder")
def open_client_folder(client_id):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, client_code, name, type, storage_folder FROM clients WHERE id=%s",
                (client_id,)
            )
            client = cur.fetchone()
    finally:
        conn.close()

    if not client:
        abort(404)

    folder = get_client_folder_path(client)

    if not folder.exists() or not folder.is_dir():
        abort(404, description="フォルダが見つかりません")

    os.startfile(folder)
    return redirect(url_for("client_detail", client_id=client_id))

# 利用者登録
@app.route("/clients/new", methods=["GET", "POST"])
def client_new():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        ctype = (request.form.get("type") or "").strip()

        if not name or not ctype:
            abort(400, description="氏名・種別は必須です")

        conn = get_conn()
        try:
            with conn.cursor() as cur:
                # いま登録されている最大の利用者コードを取得
                cur.execute("SELECT MAX(client_code) AS max_code FROM clients")
                row = cur.fetchone()

                if row and row["max_code"]:
                    client_code = str(int(row["max_code"]) + 1)
                else:
                    client_code = "2603001"

                storage_folder = create_client_folder(client_code, name)

                cur.execute(
                    """
                    INSERT INTO clients (client_code, name, type, storage_folder)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (client_code, name, ctype, storage_folder)
                )
        finally:
            conn.close()

        return redirect(url_for("clients"))

    return render_template("client_new.html", title="利用者登録")


@app.route("/records/new")
def record_new():
    client_id = request.args.get("client_id", type=int)
    if not client_id:
        abort(400, description="client_id が必要です")

    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT id, name, type, client_code FROM clients WHERE id=%s", (client_id,))
        client = cur.fetchone()
    conn.close()

    if not client:
        abort(404, description="利用者が見つかりません")

    return render_template("record_form.html", client=client, today=date.today().isoformat())


@app.route("/records/save", methods=["POST"])
def record_save():
    client_id = int(request.form.get("client_id"))
    attendance = request.form.get("attendance")

    condition_raw = request.form.get("condition")
    if not condition_raw:
        abort(400, description="体調が未入力です")
    condition = int(condition_raw)

    start_time = request.form.get("start_time") or None
    end_time = request.form.get("end_time") or None
    note = request.form.get("note", "").strip() or None

    if attendance == "absent":
        start_time = None
        end_time = None

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


# ルートはこの上に追加していく
if __name__ == "__main__":
    app.run(debug=True)