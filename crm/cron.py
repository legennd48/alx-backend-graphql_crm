import os
from datetime import datetime
import requests

def log_crm_heartbeat():
    log_file = "/tmp/crm_heartbeat_log.txt"
    now = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    # Optionally check GraphQL hello field
    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": "{ hello }"},
            timeout=5
        )
        if response.ok:
            hello = response.json().get("data", {}).get("hello", "unavailable")
            msg = f"{now} CRM is alive (hello: {hello})\n"
        else:
            msg = f"{now} CRM is alive (GraphQL error)\n"
    except Exception:
        msg = f"{now} CRM is alive (GraphQL unreachable)\n"
    with open(log_file, "a") as f:
        f.write(msg)
