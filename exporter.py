import json
import csv
import logging
import pandas as pd

logger = logging.getLogger(__name__)


def export_to_json(stats, output_path="report.json"):
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=4)
        logger.info(f"Report exported to JSON: {output_path}")
    except Exception as e:
        logger.error(f"Error exporting to JSON: {e}")


def export_to_csv(df, output_path="vacancies.csv"):
    try:
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        logger.info(f"Vacancies exported to CSV: {output_path}")
    except Exception as e:
        logger.error(f"Error exporting to CSV: {e}")
