#!/bin/bash
# Script to delete customers with no orders in the past year and log the result

LOG_FILE="/tmp/customer_cleanup_log.txt"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

cd "$(dirname "$0")/../.."

COUNT=$(python3 manage.py shell -c "from crm.models import Customer; from django.utils import timezone; from datetime import timedelta; cutoff = timezone.now() - timedelta(days=365); qs = Customer.objects.filter(orders__isnull=True) | Customer.objects.exclude(orders__order_date__gte=cutoff); to_delete = qs.distinct(); deleted = to_delete.count(); to_delete.delete(); print(deleted)")

echo "$TIMESTAMP - Deleted $COUNT inactive customers" >> "$LOG_FILE"
