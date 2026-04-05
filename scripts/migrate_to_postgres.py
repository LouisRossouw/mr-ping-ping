import os
import sys
import json
from datetime import datetime

# Add root folder to sys.path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.settings import Settings
from core.database import DatabaseManager
from core.utils import read_json

def migrate():
    settings = Settings()
    if not settings.use_postgresql:
        print("PostgreSQL is not enabled in config.json. Please enable it first.")
        return

    db = DatabaseManager(settings)
    data_dir = settings.data_dir
    pings_data_dir = settings.pings_data_dir

    # 1. Migrate App Pings
    if os.path.exists(pings_data_dir):
        apps = os.listdir(pings_data_dir)
        for app_slug in apps:
            app_path = os.path.join(pings_data_dir, app_slug)
            if os.path.isdir(app_path):
                print(f"Migrating pings for app: {app_slug}...")
                json_files = [f for f in os.listdir(app_path) if f.endswith('.json')]
                for json_file in json_files:
                    file_path = os.path.join(app_path, json_file)
                    try:
                        data = read_json(file_path)
                        for timestamp_str, stats in data.items():
                            db.save_ping(app_slug, stats, timestamp=timestamp_str)
                    except Exception as e:
                        print(f"Error migrating {file_path}: {e}")

    # 2. Migrate Ping Ping status
    ping_ping_dir = os.path.join(data_dir, 'ping_ping')
    if os.path.exists(ping_ping_dir):
        print("Migrating mr-ping-ping status...")
        json_files = [f for f in os.listdir(ping_ping_dir) if f.endswith('.json')]
        for json_file in json_files:
            file_path = os.path.join(ping_ping_dir, json_file)
            try:
                data = read_json(file_path)
                for timestamp_str, stats in data.items():
                    db.save_ping('ping_ping', stats, timestamp=timestamp_str)
            except Exception as e:
                print(f"Error migrating {file_path}: {e}")

    print("Migration complete!")

if __name__ == "__main__":
    migrate()
