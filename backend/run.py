from app import create_app
from app.config import Config

app = create_app()

if __name__ == "__main__":
    print(f"Starting server on port {Config.PORT}...")
    print(f"Health check: http://localhost:{Config.PORT}/api/health")
    app.run(host="0.0.0.0", port=Config.PORT, debug=Config.DEBUG)
