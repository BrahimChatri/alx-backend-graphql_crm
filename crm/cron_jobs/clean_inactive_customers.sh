#!/bin/bash

# Navigate to the project directory
cd "$(dirname "$0")/../.."

# Execute Django management command to delete inactive customers
DELETED_COUNT=$(python manage.py shell -c "
from crm.models import Customer, Order
from datetime import datetime, timedelta
from django.utils import timezone

# Calculate date one year ago
one_year_ago = timezone.now() - timedelta(days=365)

# Find customers with no orders since a year ago
inactive_customers = Customer.objects.exclude(
    orders__order_date__gte=one_year_ago
).distinct()

# Get count before deletion
count = inactive_customers.count()

# Delete inactive customers
inactive_customers.delete()

print(count)
" 2>/dev/null)

# Log the result with timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "[$TIMESTAMP] Deleted $DELETED_COUNT inactive customers" >> /tmp/customer_cleanup_log.txt

echo "Customer cleanup completed. Deleted $DELETED_COUNT customers."
