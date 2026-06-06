import sqlite3

def create_table():

    conn = sqlite3.connect("studybuddy.db")

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS progress(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT,
        score INTEGER
    )
    """)

    conn.commit()
    conn.close()


def save_score(topic, score):

    conn = sqlite3.connect("studybuddy.db")

    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO progress(topic, score) VALUES (?, ?)",
        (topic, score)
    )

    conn.commit()
    conn.close()