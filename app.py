import os
import datetime
from pathlib import Path
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS

from config import Config
from database.db import init_db, seed_db, get_db_connection
from backend.services.drift_detector import DriftDetector

# Import routes
from backend.routes.dashboard import dashboard_bp
from backend.routes.security_groups import security_groups_bp
from backend.routes.drift import drift_bp
from backend.routes.alerts import alerts_bp
from backend.routes.reports import reports_bp

def create_app():
    frontend_dir = Config.BASE_DIR / "frontend"
    app = Flask(
        __name__,
        static_folder=str(frontend_dir),
        static_url_path=""
    )
    app.config.from_object(Config)
    CORS(app)

    # Initialize database
    init_db()
    seed_db(force=False)

    # Ensure at least one initial baseline scan exists
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM scan_history")
        if cursor.fetchone()[0] == 0:
            conn.close()
            DriftDetector.run_scan(triggered_by="System Initial Boot Scan")
        else:
            conn.close()
    except Exception as e:
        print(f"[WARN] Initial scan check skipped: {e}")

    # Register API blueprints
    app.register_blueprint(dashboard_bp, url_prefix="/api")
    app.register_blueprint(security_groups_bp, url_prefix="/api")
    app.register_blueprint(drift_bp, url_prefix="/api")
    app.register_blueprint(alerts_bp, url_prefix="/api")
    app.register_blueprint(reports_bp, url_prefix="/api")

    # Health check endpoint
    @app.route("/api/health", methods=["GET"])
    def health_check():
        db_status = "connected"
        try:
            conn = get_db_connection()
            conn.execute("SELECT 1")
            conn.close()
        except Exception as e:
            db_status = f"error: {str(e)}"

        return jsonify({
            "status": "healthy" if db_status == "connected" else "degraded",
            "service": "Cloud Network Security Group Guardian – Drift Detector",
            "version": "1.0.0",
            "database": db_status,
            "timestamp": datetime.datetime.now().isoformat()
        }), 200

    # Serve Frontend Single Page App
    @app.route("/")
    def index():
        return send_from_directory(str(frontend_dir), "index.html")

    @app.route("/css/<path:filename>")
    def serve_css(filename):
        return send_from_directory(str(frontend_dir / "css"), filename)

    @app.route("/js/<path:filename>")
    def serve_js(filename):
        return send_from_directory(str(frontend_dir / "js"), filename)

    @app.route("/assets/<path:filename>")
    def serve_assets(filename):
        assets_dir = frontend_dir / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)
        return send_from_directory(str(assets_dir), filename)

    # Global Error Handlers
    @app.errorhandler(404)
    def handle_404(e):
        if request.path.startswith("/api/"):
            return jsonify({"status": "error", "message": "API endpoint not found."}), 404
        return send_from_directory(str(frontend_dir), "index.html")

    @app.errorhandler(500)
    def handle_500(e):
        return jsonify({"status": "error", "message": "Internal server error occurred."}), 500

    return app

app = create_app()

if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 5000))
    print(f"================================================================")
    print(f"  CLOUD NETWORK SECURITY GROUP GUARDIAN – DRIFT DETECTOR")
    print(f"  Running on: http://{host}:{port}")
    print(f"  Simulated Cloud Security Auditing Engine Active")
    print(f"================================================================")
    app.run(host=host, port=port, debug=Config.DEBUG)
