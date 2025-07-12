#!/usr/bin/env python3
import sys
import os
from datetime import datetime, timedelta
import requests

try:
    from gql import gql, Client
    from gql.transport.requests import RequestsHTTPTransport
except ImportError:
    print("The 'gql' library is required. Install it with: pip install gql[requests]")
    sys.exit(1)

LOG_FILE = "/tmp/order_reminders_log.txt"
GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"

# Calculate date range for the last 7 days
now = datetime.now()
week_ago = now - timedelta(days=7)

# GraphQL query for orders in the last week
query = gql('''
query($dateGte: DateTime!) {
  orders(filter: {orderDateGte: $dateGte}) {
    id
    orderDate
    customer {
      email
    }
  }
}
''')

transport = RequestsHTTPTransport(url=GRAPHQL_ENDPOINT, verify=False)
client = Client(transport=transport, fetch_schema_from_transport=False)

try:
    variables = {"dateGte": week_ago.isoformat()}
    result = client.execute(query, variable_values=variables)
    orders = result.get("orders", [])
except Exception as e:
    print(f"GraphQL query failed: {e}")
    sys.exit(1)

with open(LOG_FILE, "a") as f:
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    for order in orders:
        order_id = order.get("id")
        customer_email = order.get("customer", {}).get("email", "N/A")
        f.write(f"{timestamp} - Order ID: {order_id}, Customer Email: {customer_email}\n")

print("Order reminders processed!")
