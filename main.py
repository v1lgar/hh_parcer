import click
import logging
import sys
import time
import random
from db_manager import DBManager
from hh_parser import HHParser
from analytics_manager import AnalyticsManager
from visualizer import plot_daily_stats
from exporter import export_to_json, export_to_csv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


@click.command()
@click.option('--keyword', prompt='Enter keyword (e.g., Python)', help='Job keyword to search for.')
@click.option('--region', default=None, help='Region name (e.g., Москва).')
@click.option('--days', default=30, type=int, help='Search depth in days (default 30).')
@click.option('--limit', default=None, type=int, help='Limit number of vacancies to process (for testing).')
@click.option('--proxy', default=None, help='Proxy URL (e.g., http://user:pass@host:port).')
def main(keyword, region, days, limit, proxy):
    """Job vacancy parser with analytics."""
    logger.info(f"Starting search for '{keyword}' in region '{region}' for the last {days} days.")
    parser = HHParser(proxy=proxy)
    db = DBManager()
    # 1. Resolve region
    area_id = None
    if region:
        logger.info(f"Resolving region ID for '{region}'...")
        area_id = parser.get_area_id(region)
        if not area_id:
            logger.warning(f"Could not find region ID for '{region}'. Searching everywhere.")
        else:
            logger.info(f"Region ID for '{region}' is {area_id}.")

    # 2. Fetch vacancies
    logger.info("Fetching vacancies list...")
    vacancies = parser.get_vacancies(keyword, area_id, days)
    logger.info(f"Found {len(vacancies)} vacancies.")

    if not vacancies:
        logger.info("No vacancies found. Exiting.")
        return

    if limit:
        vacancies = vacancies[:limit]
        logger.info(f"Limited to {len(vacancies)} vacancies for processing.")

    # 3. Fetch details (skills) for each vacancy
    logger.info("Fetching vacancy details (this may take a while)...")
    for i, v in enumerate(vacancies):
        logger.info(f"Processing vacancy {i+1}/{len(vacancies)}: {v['title']}")
        skills = parser.get_vacancy_details(v['id'])
        v['skills'] = skills
        time.sleep(random.uniform(0.5, 1.5))  # Be nice to the API

    # 4. Save to DB
    logger.info("Saving to database...")
    db.save_vacancies(vacancies)

    # 5. Analytics
    logger.info("Analyzing data...")
    all_data = db.get_all_vacancies()
    analytics = AnalyticsManager(all_data)
    stats = analytics.calculate_stats()

    # 6. Output stats to console
    click.echo("\n--- Statistics ---")
    click.echo(f"Total vacancies: {stats['total_jobs']}")
    click.echo(f"Average salary: {stats['avg_salary']:.2f} RUB")
    click.echo("\nAverage salary by region:")
    for area, sal in stats['avg_salary_by_region'].items():
        click.echo(f"  - {area}: {sal:.2f} RUB")
    click.echo("\nTop 5 Skills:")
    for skill, count in stats['top_skills']:
        click.echo(f"  - {skill}: {count}")

    # 7. Visualize and Export
    logger.info("Generating report and chart...")
    plot_daily_stats(analytics.get_df())
    export_to_json(stats)
    export_to_csv(analytics.get_df())
    click.echo("\nResults saved to vacancies.db, report.json, vacancies.csv, and daily_stats.png")
    logger.info("Done.")


if __name__ == "__main__":
    main()
