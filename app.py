# -*- coding: utf-8 -*-
"""DualFuse-CD Web：上传边列表，返回社区划分与统计图表数据。"""
import os
import tempfile
import traceback
from functools import wraps
from urllib.parse import urlparse

import matplotlib

matplotlib.use("Agg")

from flask import (
    Flask,
    jsonify,
    redirect,
    request,
    send_from_directory,
    session,
    url_for,
)

from auth_db import (
    create_user,
    ensure_default_admin,
    init_db,
    verify_password,
)
from final import run_louvain_snn_web

app = Flask(__name__, static_folder="static", static_url_path="")

app.secret_key = os.environ.get("SECRET_KEY") or "dev-only-change-SECRET_KEY"

_instance = os.path.join(os.path.dirname(os.path.abspath(__file__)), "instance")
DATABASE = os.environ.get("USER_DATABASE") or os.path.join(_instance, "users.db")


def _safe_next(target):
    """仅允许本站相对路径或同 host 的 URL，防止开放重定向。"""
    if not target:
        return url_for("index")
    if isinstance(target, str) and target.startswith("/") and not target.startswith("//"):
        return target
    try:
        p = urlparse(target)
    except Exception:
        return url_for("index")
    if not p.scheme and not p.netloc and p.path.startswith("/"):
        return target.split("#", 1)[0]
    host_req = (request.host or "").split(":")[0].lower()
    ph = (p.hostname or "").lower()
    if ph and ph != host_req:
        return url_for("index")
    path = p.path or "/"
    if p.query:
        path = path + "?" + p.query
    return path


def _current_user():
    uid = session.get("user_id")
    name = session.get("username")
    if uid and name:
        return {"id": uid, "username": name}
    return None


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not _current_user():
            if request.path.startswith("/api/"):
                return jsonify({"ok": False, "error": "请先登录。"}), 401
            return redirect(url_for("login", next=request.url))
        return view(*args, **kwargs)

    return wrapped


@app.before_request
def _load_session_user():
    request.user = _current_user()


@app.after_request
def _cors(resp):
    """本地开发时允许从其它端口页面、或 file:// 调试页访问 API。"""
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return resp


def _parse_edges_to_tempfile(edges_text):
    """每行 'u v' 或 'u,v'，写入临时文件。返回路径。"""
    lines = []
    for raw in edges_text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.replace(",", " ").split()
        if len(parts) < 2:
            continue
        u, v = int(parts[0]), int(parts[1])
        lines.append(f"{u} {v}\n")
    if len(lines) < 1:
        raise ValueError("至少需要一条边（每行两个整数节点编号）。")
    fd, path = tempfile.mkstemp(suffix=".txt", prefix="louvain_web_")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    return path


def _bootstrap_db():
    init_db(DATABASE)
    default_pw = os.environ.get("DEFAULT_ADMIN_PASSWORD")
    ensure_default_admin(DATABASE, default_pw)


_bootstrap_db()


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if _current_user():
            return redirect(_safe_next(request.args.get("next")))
        return send_from_directory(app.static_folder, "login.html")

    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""
    if request.is_json:
        data = request.get_json(silent=True) or {}
        username = (data.get("username") or username).strip()
        password = data.get("password") or password

    user = verify_password(DATABASE, username, password)
    if not user:
        err = "用户名或密码错误。"
        if request.is_json:
            return jsonify({"ok": False, "error": err}), 401
        return redirect(url_for("login", failed=1))

    session.clear()
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session.permanent = bool(os.environ.get("PERMANENT_SESSION"))

    nxt = request.args.get("next")
    if request.is_json:
        data = request.get_json(silent=True) or {}
        nxt = data.get("next") or nxt
    nxt = _safe_next(nxt)

    if request.is_json:
        return jsonify({"ok": True, "username": user["username"], "next": nxt})
    return redirect(nxt)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        if _current_user():
            return redirect(url_for("index"))
        return send_from_directory(app.static_folder, "register.html")

    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""
    password2 = request.form.get("password2") or ""
    if request.is_json:
        data = request.get_json(silent=True) or {}
        username = (data.get("username") or username).strip()
        password = data.get("password") or password
        password2 = data.get("password2") or password2

    if password != password2:
        err = "两次输入的密码不一致。"
        if request.is_json:
            return jsonify({"ok": False, "error": err}), 400
        return redirect(url_for("register", err="mismatch"))

    try:
        uid = create_user(DATABASE, username, password)
    except ValueError as e:
        if request.is_json:
            return jsonify({"ok": False, "error": str(e)}), 400
        return redirect(url_for("register", err="invalid"))

    if uid is None:
        err = "该用户名已被占用。"
        if request.is_json:
            return jsonify({"ok": False, "error": err}), 400
        return redirect(url_for("register", err="taken"))

    session.clear()
    session["user_id"] = uid
    session["username"] = username
    session.permanent = bool(os.environ.get("PERMANENT_SESSION"))

    if request.is_json:
        return jsonify({"ok": True, "username": username})
    return redirect(url_for("index"))


@app.route("/logout", methods=["POST", "GET"])
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/api/me")
def api_me():
    u = _current_user()
    if not u:
        return jsonify({"ok": False, "logged_in": False}), 401
    return jsonify({"ok": True, "logged_in": True, "username": u["username"]})


@app.route("/")
@login_required
def index():
    return send_from_directory(app.static_folder, "index.html")


def _edges_text_from_request():
    """从上传文件、表单字段 edges_text 或 JSON 中取边列表文本。"""
    up = request.files.get("edges_file")
    if up and up.filename:
        raw = up.read()
        if not raw:
            raise ValueError("上传的文件为空。")
        return raw.decode("utf-8", errors="replace")
    form_text = (request.form.get("edges_text") or "").strip()
    if form_text:
        return form_text
    if request.is_json:
        data = request.get_json(silent=True) or {}
        return (data.get("edges_text") or "") or ""
    data = request.get_json(silent=True, force=True) or {}
    return (data.get("edges_text") or "") or ""


def _params_from_request():
    """sim_threshold、num_runs：multipart 表单字段优先，否则 JSON。"""
    if request.form and any(
        k in request.form for k in ("sim_threshold", "num_runs")
    ):
        sim = request.form.get("sim_threshold", type=float)
        runs = request.form.get("num_runs", type=int)
        return (
            float(sim if sim is not None else 0.4),
            int(runs if runs is not None else 15),
        )
    if request.is_json:
        data = request.get_json(silent=True) or {}
        return (
            float(data.get("sim_threshold", 0.4)),
            int(data.get("num_runs", 15)),
        )
    return (0.4, 15)


@app.route("/api/run", methods=["POST", "OPTIONS"])
@login_required
def api_run():
    if request.method == "OPTIONS":
        return "", 204
    try:
        edges_text = _edges_text_from_request()
        sim_thread, num_runs = _params_from_request()
        num_runs = max(1, min(num_runs, 80))

        if not (edges_text or "").strip():
            raise ValueError(
                "未接收到边数据：请上传边列表文件（字段名 edges_file），"
                "或在 JSON / 表单中提供 edges_text。"
            )
        path = _parse_edges_to_tempfile(edges_text)
        try:
            result = run_louvain_snn_web(path, sim_thread=sim_thread, num_runs=num_runs)
        finally:
            try:
                os.remove(path)
            except OSError:
                pass
        return jsonify({"ok": True, "result": result})
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    except Exception:
        return jsonify(
            {"ok": False, "error": traceback.format_exc()}
        ), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
