# crm/tasks.py

from celery import shared_task
from django.db import connection
from django.utils import timezone
from decimal import Decimal
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@shared_task
def generate_crm_report():
    """
    Generate a weekly CRM report with total customers, orders, and revenue.
    Logs the report to /tmp/crm_report_log.txt with timestamp.
    """
    try:
        # Use raw SQL to get the data (simulating GraphQL query results)
        with connection.cursor() as cursor:
            # Get total customers
            cursor.execute("SELECT COUNT(*) FROM crm_customer")
            total_customers = cursor.fetchone()[0]
            
            # Get total orders
            cursor.execute("SELECT COUNT(*) FROM crm_order")
            total_orders = cursor.fetchone()[0]
            
            # Get total revenue (sum of total_amount from orders)
            cursor.execute("SELECT COALESCE(SUM(total_amount), 0) FROM crm_order")
            total_revenue = cursor.fetchone()[0] or Decimal('0')
        
        # Format the report
        timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        report_line = f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, {total_revenue} revenue\n"
        
        # Log to file
        log_file_path = "/tmp/crm_report_log.txt"
        
        # Create directory if it doesn't exist (for Windows compatibility)
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        
        with open(log_file_path, 'a', encoding='utf-8') as log_file:
            log_file.write(report_line)
        
        logger.info(f"CRM report generated: {total_customers} customers, {total_orders} orders, {total_revenue} revenue")
        
        return {
            'status': 'success',
            'customers': total_customers,
            'orders': total_orders,
            'revenue': float(total_revenue),
            'timestamp': timestamp
        }
        
    except Exception as e:
        error_message = f"Error generating CRM report: {str(e)}"
        logger.error(error_message)
        
        # Log error to file as well
        try:
            timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            error_line = f"{timestamp} - ERROR: {error_message}\n"
            
            log_file_path = "/tmp/crm_report_log.txt"
            os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
            
            with open(log_file_path, 'a', encoding='utf-8') as log_file:
                log_file.write(error_line)
        except Exception as log_error:
            logger.error(f"Failed to log error to file: {log_error}")
        
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': timestamp
        }

@shared_task
def test_celery_task():
    """Test task to verify Celery is working correctly"""
    logger.info("Test Celery task executed successfully")
    return "Test task completed"
