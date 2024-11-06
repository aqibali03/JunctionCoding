import requests
import networkx as nx
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from apscheduler.schedulers.background import BackgroundScheduler
import time
from typing import List, Dict


class SwapService:
    def __init__(self, chain_id: str, api_url: str):
        self.chain_id = chain_id
        self.api_url = api_url
        self.graph = nx.DiGraph()
        self.token_data = {}
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

    def fetch_token_data(self):
        """Fetch token data from an external API (e.g., CoinGecko)."""
        print("Fetching token data...")
        url = f"{self.api_url}/coins/markets"
        params = {"vs_currency": "usd", "ids": "bitcoin,ethereum,litecoin"}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            token_list = response.json()
            self.token_data = {token["id"]: token for token in token_list}
            self.update_graph()
        else:
            print("Error fetching token data.")

    def update_graph(self):
        """Update the graph with token-pool information."""
        self.graph.clear()
        for token_id, token in self.token_data.items():
            self.graph.add_node(token_id, name=token["name"], symbol=token["symbol"])

        self.graph.add_edge("bitcoin", "ethereum", weight=0.1)
        self.graph.add_edge("ethereum", "litecoin", weight=0.2)

    def find_optimal_route(self, source_token: str, target_token: str) -> List[str]:
        """Find the optimal route (shortest path) between two tokens."""
        if source_token not in self.graph or target_token not in self.graph:
            return []

        try:
            path = nx.shortest_path(self.graph, source=source_token, target=target_token, weight="weight")
            return path
        except nx.NetworkXNoPath:
            return []

    def schedule_token_refresh(self, interval_seconds: int):
        """Schedule token data refresh."""
        self.scheduler.add_job(self.fetch_token_data, 'interval', seconds=interval_seconds)

    def get_tokens(self):
        """Return the list of available tokens."""
        return list(self.token_data.keys())

class SwapServiceGraphQL:
    def __init__(self, swap_service: SwapService):
        self.swap_service = swap_service
        self.transport = RequestsHTTPTransport(url="http://localhost:5000/graphql")
        self.client = Client(transport=self.transport, fetch_schema_from_transport=True)

    def get_all_tokens(self) -> List[str]:
        """GraphQL query to return all available tokens."""
        query = gql("""
        query {
            tokens {
                id
            }
        }
        """)
        result = self.client.execute(query)
        return result["tokens"]

    def get_best_route(self, source_token: str, target_token: str) -> Dict[str, List[str]]:
        """GraphQL query to return the best route between two tokens."""
        query = gql("""
        query ($source_token: String!, $target_token: String!) {
            best_route(source_token: $source_token, target_token: $target_token) {
                path
            }
        }
        """)
        variables = {"source_token": source_token, "target_token": target_token}
        result = self.client.execute(query, variable_values=variables)
        return result['best_route']

if __name__ == "__main__":
    swap_service = SwapService(chain_id="ethereum", api_url="https://api.coingecko.com/api/v3")
    swap_service.fetch_token_data()

    # Schedule token refresh every 5 minutes
    swap_service.schedule_token_refresh(300)

    graphql_service = SwapServiceGraphQL(swap_service)

    print("Tokens available:", swap_service.get_tokens())
    optimal_route = swap_service.find_optimal_route("bitcoin", "litecoin")
    print("Optimal route from Bitcoin to Litecoin:", optimal_route)


    while True:
        time.sleep(60)
