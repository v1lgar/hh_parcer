import requests
import time
import logging
import random
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class HHParser:
    BASE_URL = "https://api.hh.ru"
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "HH-Vacancy-Analyzer/1.0 (contact@example.com)"
    ]

    def __init__(self, proxy=None):
        self.session = requests.Session()
        self._rotate_user_agent()
        if proxy:
            self.session.proxies = {"http": proxy, "https": proxy}

    def _rotate_user_agent(self):
        new_ua = random.choice(self.USER_AGENTS)
        logger.info(f"Using User-Agent: {new_ua}")
        self.session.headers.update({"User-Agent": new_ua})

    def _get(self, url, params=None):
        retries = 3
        while retries > 0:
            try:
                response = self.session.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    logger.warning("Rate limit exceeded (429). Waiting 15 seconds...")
                    time.sleep(15)
                    retries -= 1
                elif response.status_code == 403:
                    logger.warning("Access forbidden (403). Attempting to rotate User-Agent and retry after delay...")
                    time.sleep(30)
                    self._rotate_user_agent()
                    # Retry once for 403
                    response = self.session.get(url, params=params, timeout=10)
                    if response.status_code == 200:
                        return response.json()
                    logger.error("Access still forbidden after retry.")
                    return None
                else:
                    logger.error(f"Error {response.status_code} for URL {url}: {response.text}")
                    return None
            except requests.RequestException as e:
                logger.error(f"Request failed: {e}")
                retries -= 1
                time.sleep(1)
        return None

    def get_area_id(self, area_name):
        if not area_name:
            return None
        data = self._get(f"{self.BASE_URL}/suggests/areas", params={"text": area_name})
        if data and data.get("items"):
            # Return the first match
            return data["items"][0]["id"]
        return None

    def get_vacancies(self, keyword, area_id=None, days=30):
        vacancies = []
        date_from = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S")
        params = {
            "text": keyword,
            "date_from": date_from,
            "per_page": 100,
            "page": 0
        }
        if area_id:
            params["area"] = area_id

        while True:
            data = self._get(f"{self.BASE_URL}/vacancies", params=params)
            if not data:
                break
            items = data.get("items", [])
            for item in items:
                vacancy = {
                    "id": item["id"],
                    "title": item["name"],
                    "company": item["employer"]["name"],
                    "salary_from": item["salary"]["from"] if item.get("salary") else None,
                    "salary_to": item["salary"]["to"] if item.get("salary") else None,
                    "currency": item["salary"]["currency"] if item.get("salary") else None,
                    "published_at": item["published_at"],
                    "area": item["area"]["name"],
                    "url": item["url"]
                }
                vacancies.append(vacancy)
            if data["page"] >= data["pages"] - 1:
                break
            params["page"] += 1
            time.sleep(random.uniform(0.2, 0.5)) # Respectful randomized delay
        return vacancies

    def get_vacancy_details(self, vacancy_id):
        data = self._get(f"{self.BASE_URL}/vacancies/{vacancy_id}")
        if data:
            skills = [skill["name"] for skill in data.get("key_skills", [])]
            return skills
        return []
