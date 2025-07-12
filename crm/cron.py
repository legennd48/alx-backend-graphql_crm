import os
from datetime import datetime
from gql.transport.requests import RequestsHTTPTransport
from gql import gql, Client

def log_crm_heartbeat():
    log_file = "/tmp/crm_heartbeat_log.txt"
    now = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    # Use gql to check GraphQL hello field
    try:
        transport = RequestsHTTPTransport(url="http://localhost:8000/graphql", verify=False)
        client = Client(transport=transport, fetch_schema_from_transport=False)
        query = gql('{ hello }')
        result = client.execute(query)
        hello = result.get("hello", "unavailable")
        msg = f"{now} CRM is alive (hello: {hello})\n"
    except Exception:
        msg = f"{now} CRM is alive (GraphQL unreachable)\n"
    with open(log_file, "a") as f:
        f.write(msg)

def update_low_stock():
    log_file = "/tmp/low_stock_updates_log.txt"
    now = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    try:
        transport = RequestsHTTPTransport(url="http://localhost:8000/graphql", verify=False)
        client = Client(transport=transport, fetch_schema_from_transport=False)
        mutation = gql('''
            mutation {
                updateLowStockProducts {
                    updatedProducts {
                        name
                        stock
                    }
                    success
                    message
                }
            }
        ''')
        result = client.execute(mutation)
        updates = result.get("updateLowStockProducts", {})
        products = updates.get("updatedProducts", [])
        msg = f"{now} Restocked products:\n"
        for p in products:
            msg += f"  - {p['name']}: new stock {p['stock']}\n"
        if not products:
            msg += "  (No products needed restocking)\n"
    except Exception as e:
        msg = f"{now} Error updating low stock: {e}\n"
    with open(log_file, "a") as f:
        f.write(msg)
