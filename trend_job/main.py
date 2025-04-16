import time
import schedule
import argparse
from trend_analyzer import analyze_trends
from api_clients import logger

def schedule_jobs(domain=None):
    def run_analysis():
        analyze_trends(domain)
    
    schedule.every(30).minutes.do(run_analysis)
    
    # Run immediately on startup
    run_analysis()
    
    # Keep the script running and execute scheduled jobs
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description="Social Media Trend Analysis Service with AI Insights")
    parser.add_argument("--domain", type=str, help="Domain keywords to filter trends (comma-separated)")
    args = parser.parse_args()
    
    domain = args.domain
    
    logger.info(f"Starting Social Media Trend Analysis Service with Gemini AI{' for domain: ' + domain if domain else ''}")
    schedule_jobs(domain)
