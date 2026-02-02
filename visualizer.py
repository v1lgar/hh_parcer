import matplotlib.pyplot as plt
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def plot_daily_stats(df, output_path="daily_stats.png"):
    if df.empty:
        logger.warning("DataFrame is empty, cannot plot daily stats.")
        return

    try:
        daily_counts = df.groupby('date').size().sort_index()
        
        plt.figure(figsize=(10, 6))
        daily_counts.plot(kind='line', marker='o')
        plt.title('Dynamics of Vacancy Publications')
        plt.xlabel('Date')
        plt.ylabel('Number of Vacancies')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        logger.info(f"Daily stats chart saved to {output_path}")
    except Exception as e:
        logger.error(f"Error during plotting: {e}")
