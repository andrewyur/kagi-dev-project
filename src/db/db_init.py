import sqlite3
import os


def init_db():
    db_path = "src/rss.db"

    if os.path.exists(db_path):
        exit()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
      CREATE TABLE IF NOT EXISTS feeds (
         feed_id CHAR(21) PRIMARY KEY NOT NULL,
         user_id TEXT NOT NULL,
         homepage VARCHAR(50) NOT NULL,
         channel_title VARCHAR(50) NOT NULL,
         channel_description TEXT NOT NULL,
         item_title TEXT NOT NULL,
         item_link TEXT NOT NULL,
         item_pubDate TEXT,
         item_description TEXT
      )
   """
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
