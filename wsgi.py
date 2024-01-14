import os

from application.app import create_app
import src.routes
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

app = create_app(os.getenv("FLASK_CONFIG"), dependency_container_packages=[src.routes])

if __name__ == '__main__':
    app.run(debug=False, port=5000)
