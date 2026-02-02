import pandas as pd
import json
import logging
from collections import Counter

logger = logging.getLogger(__name__)


class AnalyticsManager:
    CURRENCY_RATES = {
        "RUR": 1,
        "RUB": 1,
        "USD": 90,
        "EUR": 100,
        "KZT": 0.2,
        "BYR": 30,
        "UAH": 2.5
    }

    def __init__(self, data):
        self.df = pd.DataFrame(data)
        if not self.df.empty:
            self._preprocess()

    def _preprocess(self):
        # Convert skills from JSON string to list
        self.df['skills'] = self.df['skills'].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
        # Calculate average salary in RUB

        def convert_to_rub(row):
            rate = self.CURRENCY_RATES.get(row['currency'], 1)
            sal_from = row['salary_from']
            sal_to = row['salary_to']
            if sal_from is not None and sal_to is not None:
                avg = (sal_from + sal_to) / 2
            elif sal_from is not None:
                avg = sal_from
            elif sal_to is not None:
                avg = sal_to
            else:
                return None
            return avg * rate

        self.df['salary_rub'] = self.df.apply(convert_to_rub, axis=1)
        # Convert date
        self.df['published_at'] = pd.to_datetime(self.df['published_at'])
        self.df['date'] = self.df['published_at'].dt.date

    def calculate_stats(self):
        if self.df.empty:
            return {
                "total_jobs": 0,
                "avg_salary": 0,
                "avg_salary_by_region": {},
                "top_skills": [],
                "daily_stats": {}
            }

        total_jobs = len(self.df)
        avg_salary = self.df['salary_rub'].mean()
        avg_salary_by_region = self.df.groupby('area')['salary_rub'].mean().dropna().to_dict()
        all_skills = [skill for skills_list in self.df['skills'] for skill in skills_list]
        top_skills = Counter(all_skills).most_common(5)
        daily_stats = self.df.groupby('date').size().to_dict()
        # Convert date keys to strings for JSON serializability
        daily_stats = {str(k): v for k, v in daily_stats.items()}

        return {
            "total_jobs": total_jobs,
            "avg_salary": float(avg_salary) if pd.notna(avg_salary) else 0,
            "avg_salary_by_region": {k: float(v) for k, v in avg_salary_by_region.items()},
            "top_skills": top_skills,
            "daily_stats": daily_stats
        }

    def get_df(self):
        return self.df
