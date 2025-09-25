# app/__init__.py
import os
from flask import Flask
from .routes import main

def create_app():
    app = Flask(__name__)

    # Load GA ID from env
    app.config["GA_MEASUREMENT_ID"] = os.getenv("GA_MEASUREMENT_ID")

    # Enable GA only when NOT in debug and an ID exists
    app.config["GA_ENABLED"] = (not app.debug) and bool(app.config["GA_MEASUREMENT_ID"])

    @app.context_processor
    def inject_ga():
        return {
            "GA_MEASUREMENT_ID": app.config.get("GA_MEASUREMENT_ID"),
            "GA_ENABLED": app.config.get("GA_ENABLED"),
        }

    app.register_blueprint(main)
    return app


