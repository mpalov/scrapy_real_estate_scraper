import subprocess
import logging
import smtplib
from email.mime.text import MIMEText


def send_notification(subject, message):
    sender_email = "your_email@example.com"
    receiver_email = "receiver@example.com"
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    try:
        with smtplib.SMTP('smtp.example.com', 587) as server:
            server.starttls()
            server.login("your_email@example.com", "your_password")
            server.sendmail(sender_email, receiver_email, msg.as_string())
    except Exception as e:
        logging.error(f"Failed to send notification: {e}")


def test_spider(spider_name):
    try:
        result = subprocess.run([
            'scrapy', 'crawl', spider_name, '-a', 'check=True', '--nolog'
        ], capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            logging.info(f"{spider_name} health check successful.")
            return True
        else:
            logging.error(f"Health check error in {spider_name}: {result.stderr}")
            return False
    except Exception as e:
        logging.error(f"Exception in {spider_name}: {e}")
        return False


def run_health_checks():
    spiders = ["london", "paris", "madrid", "rome", "lisbon"]
    success = True

    for spider in spiders:
        if not test_spider(spider):
            success = False

    if success:
        send_notification("Health Check Passed", "All spiders passed the health check.")
    else:
        send_notification("Health Check Failed", "One or more spiders failed the health check.")
