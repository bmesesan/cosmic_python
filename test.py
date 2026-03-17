import json
import os
import sys

import psycopg2


def load_json_from_env(env_var_name):
    # Get the file path from environment variable
    file_path = os.getenv(env_var_name)

    if not file_path:
        raise ValueError(f"Environment variable '{env_var_name}' is not set.")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found at path: {file_path}")

    # Load and return JSON data
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in file: {e}")

def main():
    data = load_json_from_env("ALERTER_DB_CREDENTIALS_LOCAL")

    conn = psycopg2.connect(
        dbname=data["dbname"],
        user=data["user"],
        password=data["pw"],
        host=data["host"],
        port=data["port"]
    )

    conn.close()

if __name__ == "__main__":
    main()