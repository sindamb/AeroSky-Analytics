import sqlite3
import pandas as pd
from datetime import datetime
import os

# Create an absolute path to the database file relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "aerosky.db")


def initialize_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS suggestions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            operator TEXT,
            suggestion TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# Ensure the database and table exist immediately upon import
initialize_database()


def save_operator_suggestion(operator, suggestion):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO suggestions(timestamp, operator, suggestion)
            VALUES (?, ?, ?)
        """, (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            operator if operator.strip() else "Anonymous",
            suggestion
        ))

        conn.commit()
        conn.close()

        return True, "Suggestion saved successfully."

    except Exception as e:
        return False, str(e)


def get_suggestions():
    conn = sqlite3.connect(DATABASE)

    df = pd.read_sql_query("""
        SELECT
            id AS ID,
            timestamp AS Timestamp,
            operator AS Operator,
            suggestion AS Suggestion
        FROM suggestions
        ORDER BY id ASC
    """, conn)

    conn.close()

    return df


def delete_suggestion(suggestion_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM suggestions WHERE id=?",
        (suggestion_id,)
    )

    conn.commit()
    conn.close()


def get_global_mock_status():
    """Reads if the system is forced into mock data globally."""
    if not os.path.exists("stream_status.txt"):
        return False
    with open("stream_status.txt", "r") as f:
        return f.read().strip() == "True"

def set_global_mock_status(status: bool):
    """Sets the global data stream status."""
    with open("stream_status.txt", "w") as f:
        f.write(str(status))
