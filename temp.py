from app import app
from utils.database import init_db

if __name__ == '__main__':
    with app.app_context():
        init_db()
