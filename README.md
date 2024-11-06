# JunctionCoding
Token Swap Service
Overview
This service allows you to find the optimal route to swap between cryptocurrency tokens. It fetches token data from the CoinGecko API, represents tokens and pools in a graph, and uses a GraphQL API to query available tokens and best swap routes.

Features:
Fetch token data from CoinGecko.
Represent tokens as nodes and pools as weighted edges in a graph.
Find the best swap route between two tokens using Dijkstra’s algorithm.
Expose a GraphQL API for querying tokens and best swap routes.
Periodic data refresh to keep token data up to date.


Installation
Requirements:
Python 3.7+
Install dependencies:
pip install requests networkx gql apscheduler

Run the application:
python server.py
This will start the service, fetch token data, and run the GraphQL API.

Usage
Once the service is running, you can use the following GraphQL queries:

Get all tokens:
graphql
query {
  tokens {
    id
  }
}
Get best route between two tokens:
graphql
query {
  best_route(source_token: "bitcoin", target_token: "litecoin") {
    path
  }
}
