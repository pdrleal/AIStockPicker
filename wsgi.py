import os

from application.app import create_app
import src.routes

app = create_app(os.environ["FLASK_CONFIG"], dependency_container_packages=[src.routes])