#!/bin/bash
# Script to delete customers with no orders in the past year and log the result

LOG_FILE="/tmp/customer_cleanup_log.txt"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Move to project root (assume script is in crm/cron_jobs)
cwd=$(pwd)
if [[ "$cwd" != *"alx-backend-graphql_crm"* ]]; then
    cd "$SCRIPT_DIR/../.."
else
    cd "$cwd"
fi

COUNT=$(python3 manage.py shell -c "from crm.models import Customer; from django.utils import timezone; from datetime import timedelta; cutoff = timezone.now() - timedelta(days=365); qs = Customer.objects.filter(orders__isnull=True) | Customer.objects.exclude(orders__order_date__gte=cutoff); to_delete = qs.distinct(); deleted = to_delete.count(); to_delete.delete(); print(deleted)")

echo "$TIMESTAMP - Deleted $COUNT inactive customers" >> "$LOG_FILE"
