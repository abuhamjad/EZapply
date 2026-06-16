# Flask API Server — Job Apply Bot Backend
import os, json, time, sys

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from flask import Flask, request, jsonify, Response, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from bot_manager import BotManager
from resume_parser import extract_text, parse_resume_with_ai, list_resumes
from ai_matcher import AIMatcher
import constants

app = Flask(__name__, static_folder="frontend", static_url_path="")
CORS(app)

RESUMES_DIR = os.path.join(os.getcwd(), "resumes")
DATA_DIR = os.path.join(os.getcwd(), "data")
os.makedirs(RESUMES_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

bot_manager = BotManager()
current_config = dict(constants.DEFAULT_CONFIG)
parsed_resume_cache = {}

@app.route("/")
def index():
    return send_from_directory("frontend", "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("frontend", path)

# --- API Endpoints ---

@app.route("/api/status")
def api_status():
    return jsonify(bot_manager.get_status())

@app.route("/api/resumes", methods=["GET"])
def api_resumes():
    return jsonify(list_resumes(RESUMES_DIR))

@app.route("/api/upload-resume", methods=["POST"])
def api_upload_resume():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    f = request.files["file"]
    if not f.filename:
        return jsonify({"error": "No file selected"}), 400
    ext = os.path.splitext(f.filename)[1].lower()
    if ext not in (".pdf", ".docx", ".doc", ".txt"):
        return jsonify({"error": "Unsupported file type"}), 400
    # Clear existing resumes — only one at a time
    for old in os.listdir(RESUMES_DIR):
        try:
            os.remove(os.path.join(RESUMES_DIR, old))
        except Exception:
            pass
    parsed_resume_cache.clear()
    fname = secure_filename(f.filename)
    fpath = os.path.join(RESUMES_DIR, fname)
    f.save(fpath)
    return jsonify({"message": "Resume uploaded", "name": fname})

@app.route("/api/delete-resume", methods=["POST"])
def api_delete_resume():
    data = request.json or {}
    fname = data.get("filename", "")
    if not fname:
        return jsonify({"error": "No filename provided"}), 400
    fpath = os.path.join(RESUMES_DIR, secure_filename(fname))
    if os.path.exists(fpath):
        os.remove(fpath)
        parsed_resume_cache.pop(fname, None)
        return jsonify({"message": "Resume deleted"})
    return jsonify({"error": "File not found"}), 404

@app.route("/api/parse-resume", methods=["POST"])
def api_parse_resume():
    data = request.json or {}
    fname = data.get("filename", "")
    if not fname:
        # Use first resume found
        resumes = list_resumes(RESUMES_DIR)
        if not resumes:
            return jsonify({"error": "No resumes found"}), 404
        fname = resumes[0]["name"]
    fpath = os.path.join(RESUMES_DIR, fname)
    if not os.path.exists(fpath):
        return jsonify({"error": "Resume not found"}), 404
    text = extract_text(fpath)
    if not text:
        return jsonify({"error": "Could not extract text"}), 400
    api_key = current_config.get("groq_api_key", "")
    parsed = parse_resume_with_ai(text, api_key)
    parsed_resume_cache[fname] = parsed
    return jsonify(parsed)

@app.route("/api/config", methods=["GET"])
def api_get_config():
    safe = {k: v for k, v in current_config.items() if "password" not in k}
    safe["linkedin_email"] = current_config.get("linkedin_email", "")
    safe["naukri_email"] = current_config.get("naukri_email", "")
    safe["has_linkedin_pass"] = bool(current_config.get("linkedin_password"))
    safe["has_naukri_pass"] = bool(current_config.get("naukri_password"))
    safe["has_groq_key"] = bool(current_config.get("groq_api_key"))
    return jsonify(safe)

@app.route("/api/config", methods=["POST"])
def api_set_config():
    global current_config
    data = request.json or {}
    for k, v in data.items():
        if k in current_config:
            current_config[k] = v
    return jsonify({"message": "Config updated"})

@app.route("/api/start", methods=["POST"])
def api_start():
    data = request.json or {}
    # Merge incoming config
    for k, v in data.items():
        if k in current_config:
            current_config[k] = v
    # Get resume data
    resume_data = {}
    resumes = list_resumes(RESUMES_DIR)
    if resumes:
        preferred = current_config.get("preferred_resume", "")
        target = preferred if preferred else resumes[0]["name"]
        if target in parsed_resume_cache:
            resume_data = parsed_resume_cache[target]
        else:
            fpath = os.path.join(RESUMES_DIR, target)
            if os.path.exists(fpath):
                text = extract_text(fpath)
                api_key = current_config.get("groq_api_key", "")
                resume_data = parse_resume_with_ai(text, api_key)
                parsed_resume_cache[target] = resume_data
        # Set resume file path for upload
        current_config["resume_path"] = os.path.join(RESUMES_DIR, target)
    # Generate keywords from resume if none set
    if not current_config.get("keywords") and resume_data.get("search_keywords"):
        current_config["keywords"] = resume_data["search_keywords"]
    result = bot_manager.start(current_config, resume_data)
    return jsonify(result)

@app.route("/api/stop", methods=["POST"])
def api_stop():
    return jsonify(bot_manager.stop())

@app.route("/api/respond", methods=["POST"])
def api_respond():
    data = request.json or {}
    answer = data.get("answer", "")
    if not answer:
        return jsonify({"error": "No answer provided"}), 400
    return jsonify(bot_manager.submit_response(answer))

@app.route("/api/logs")
def api_logs():
    def stream():
        for event in bot_manager.get_events():
            yield f"data: {json.dumps(event)}\n\n"
    return Response(stream(), mimetype="text/event-stream", headers={"Cache-Control":"no-cache","X-Accel-Buffering":"no"})

@app.route("/api/log-history")
def api_log_history():
    return jsonify(bot_manager.log_history[-100:])

@app.route("/api/stats")
def api_stats():
    return jsonify(bot_manager.combined_stats)

ANSWERS_FILE = os.path.join(os.getcwd(), "user_answers.json")

@app.route("/api/saved-answers")
def api_get_saved_answers():
    try:
        if os.path.exists(ANSWERS_FILE):
            with open(ANSWERS_FILE, "r", encoding="utf-8") as f:
                return jsonify(json.load(f))
    except Exception:
        pass
    return jsonify({})

@app.route("/api/saved-answers", methods=["POST"])
def api_update_saved_answers():
    data = request.json or {}
    try:
        existing = {}
        if os.path.exists(ANSWERS_FILE):
            with open(ANSWERS_FILE, "r", encoding="utf-8") as f:
                existing = json.load(f)
        existing.update(data)
        with open(ANSWERS_FILE, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)
        return jsonify({"message": "Answers saved", "count": len(existing)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/saved-answers", methods=["DELETE"])
def api_clear_saved_answers():
    try:
        if os.path.exists(ANSWERS_FILE):
            os.remove(ANSWERS_FILE)
        return jsonify({"message": "All saved answers cleared"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/delete-answer", methods=["POST"])
def api_delete_answer():
    data = request.json or {}
    key = data.get("key", "")
    if not key:
        return jsonify({"error": "No key provided"}), 400
    try:
        if os.path.exists(ANSWERS_FILE):
            with open(ANSWERS_FILE, "r", encoding="utf-8") as f:
                existing = json.load(f)
            existing.pop(key, None)
            with open(ANSWERS_FILE, "w", encoding="utf-8") as f:
                json.dump(existing, f, indent=2, ensure_ascii=False)
            return jsonify({"message": f"Answer for '{key}' deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    print("\n🤖 Job Apply Bot Server Starting...")
    print("📍 Dashboard: http://localhost:5000")
    print("📂 Put resumes in: ./resumes/\n")
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
