import sqlite3
import json
import logging

logger = logging.getLogger(__name__)


class DBManager:
    def __init__(self, db_path="vacancies.db"):
        self.db_path = db_path
        self.create_table()

    def create_table(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS vacancies (
                        id TEXT PRIMARY KEY,
                        title TEXT,
                        company TEXT,
                        salary_from REAL,
                        salary_to REAL,
                        currency TEXT,
                        skills TEXT,
                        published_at TEXT,
                        area TEXT
                    )
                """)
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Database error during table creation: {e}")

    def save_vacancies(self, vacancies_list):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for v in vacancies_list:
                    cursor.execute("""
                        INSERT OR REPLACE INTO vacancies (
                            id, title, company, salary_from, salary_to, currency, skills, published_at, area
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        v['id'],
                        v['title'],
                        v['company'],
                        v.get('salary_from'),
                        v.get('salary_to'),
                        v.get('currency'),
                        json.dumps(v.get('skills', [])),
                        v['published_at'],
                        v['area']
                    ))
                conn.commit()
            logger.info(f"Successfully saved {len(vacancies_list)} vacancies to database.")
        except sqlite3.Error as e:
            logger.error(f"Database error during insertion: {e}")

    def get_all_vacancies(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM vacancies")
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Database error during selection: {e}")
            return []
