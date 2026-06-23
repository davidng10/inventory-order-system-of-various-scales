import requests
from concurrent.futures import ThreadPoolExecutor


backend_url = "http://localhost:8000"


def create_order_request(order_amt: int):
    url = f"{backend_url}/orders"
    payload = {"product_id": "019ec67f-a502-7f48-a1e3-7b2fd4d62f4a", "count": order_amt}
    headers = {"x-user-id": "019ec67f-a502-7dbb-8dad-74e16ac913d7"}

    response = requests.post(url, json=payload, headers=headers)
    print({"status": response.status_code, "response": response.json()})


def main():
    # Test double sell concurrency
    with ThreadPoolExecutor(max_workers=2) as executor:
        executor.map(create_order_request, [1, 1])


if __name__ == "__main__":
    main()
