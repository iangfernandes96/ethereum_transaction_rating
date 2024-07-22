import random
from locust import HttpUser, task, between


class FastAPIUser(HttpUser):
    wait_time = between(1, 5)
    host = "http://localhost:8000/api"

    def on_start(self):
        # Initialize tokens for both free and paid users
        self.free_token = self.get_token("user", "password")
        self.paid_token = self.get_token("paid_user", "password")
        self.latest_txn_key = "latest_transaction_hashes"
        self.old_txn_key = "old_transaction_hashes"
        self.checked_hashes = []
        self.latest_hashes = []
        self.old_hashes = []
        with self.client.get(
            "/transaction/old-hashes",
            headers={"Authorization": f"Bearer {self.free_token}"},
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                self.old_hashes.extend(response.json()[self.old_txn_key])

        with self.client.get(
            "/transaction/latest-hashes",
            headers={"Authorization": f"Bearer {self.free_token}"},
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                self.latest_hashes.extend(response.json()[self.latest_txn_key])

    def get_token(self, username, password):
        response = self.client.post(
            "/user/token", data={"username": username, "password": password}
        )
        response_data = response.json()
        return response_data["access_token"]

    @task(5)
    def fetch_latest_hashes(self):
        with self.client.get(
            "/transaction/latest-hashes",
            headers={"Authorization": f"Bearer {self.free_token}"},
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                self.latest_hashes.extend(response.json()[self.latest_txn_key])
                self.latest_hashes = list(set(self.latest_hashes))

    @task(5)
    def fetch_old_hashes(self):
        with self.client.get(
            "/transaction/old-hashes",
            headers={"Authorization": f"Bearer {self.free_token}"},
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                self.old_hashes.extend(response.json()[self.old_txn_key])
                self.old_hashes = list(set(self.old_hashes))

    @task(4)
    def query_latest_hash_rating(self):
        if self.latest_hashes:
            tx_hash = random.choice(self.latest_hashes)
            with self.client.get(
                f"/transaction/rating?transaction_hash={tx_hash}",
                headers={"Authorization": f"Bearer {self.paid_token}"},
                name="/transaction/rating (old)",
            ) as resp:
                if resp.status_code == 200:
                    pass

    @task(4)
    def query_old_hash_rating(self):
        if self.latest_hashes:
            tx_hash = random.choice(self.old_hashes)
            with self.client.get(
                f"/transaction/rating?transaction_hash={tx_hash}",
                headers={"Authorization": f"Bearer {self.free_token}"},
                name="/transaction/rating (latest)",
            ) as resp:
                if resp.status_code == 200:
                    pass
