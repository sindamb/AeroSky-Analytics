import sqlite3
import pandas as pd
from datetime import datetime

DATABASE = "aerosky.db"


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
