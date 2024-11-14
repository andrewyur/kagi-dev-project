import sqlite3
import os


def init_db():
    db_path = "rss.db"

    if os.path.exists("rss.db"):
        choice = input(f"delete database found at {db_path}? (y/n)")

        if choice == "y":
            os.remove(db_path)
        else:
            exit()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
      CREATE TABLE IF NOT EXISTS feeds (
         feed_id CHAR(21) PRIMARY KEY NOT NULL,
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
