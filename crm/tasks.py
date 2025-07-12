from celery import shared_task
from datetime import datetime
from gql.transport.requests import RequestsHTTPTransport
from gql import gql, Client

@shared_task
def generate_crm_report():
    log_file = "/tmp/crm_report_log.txt"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        transport = RequestsHTTPTransport(url="http://localhost:8000/graphql", verify=False)
        client = Client(transport=transport, fetch_schema_from_transport=False)
        query = gql('''
        query {
            customers { id }
            orders { id totalAmount }
        }
        ''')
        result = client.execute(query)
        num_customers = len(result.get("customers", []))
        orders = result.get("orders", [])
        num_orders = len(orders)
        total_revenue = sum(float(o.get("totalAmount", 0)) for o in orders)
        msg = f"{now} - Report: {num_customers} customers, {num_orders} orders, {total_revenue} revenue\n"
    except Exception as e:
        msg = f"{now} - Report error: {e}\n"
    with open(log_file, "a") as f:
        f.write(msg)
