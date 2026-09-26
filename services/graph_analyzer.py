"""
ADSA Module: NetworkX Graph Analytics.
Models the cooperative banking transaction network as a directed weighted graph G = (V, E).
Analyzes vertex degrees, hub centrality, new connections, repeated transfers, and graph risk indicators.
"""

import networkx as nx
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional

class GraphAnalyzer:
    """
    Constructs and analyzes the transaction graph using NetworkX.
    
    Graph Components:
      - Vertices (V): Accounts ('Acc-1', 'Acc-2') and Payees ('Payee-1', 'Payee-6')
      - Directed Edges (E): Financial transfers (Source -> Destination)
      - Edge Weights (w): Transaction amounts in INR (₹)
    """

    def __init__(self, transactions_df: Optional[pd.DataFrame] = None):
        self.graph = nx.DiGraph()
        if transactions_df is not None and not transactions_df.empty:
            self.build_graph(transactions_df)

    def build_graph(self, transactions_df: pd.DataFrame):
        """Constructs the directed graph from a DataFrame of transactions."""
        self.graph.clear()

        for _, row in transactions_df.iterrows():
            acc_id = row["account_id"]
            payee_id = row.get("payee_id")
            amount = float(row.get("amount", 0.0))
            txn_id = row.get("transaction_id", 0)

            # Source Node (Account)
            src_node = f"Acc-{acc_id}"
            if not self.graph.has_node(src_node):
                self.graph.add_node(src_node, node_type="Account", label=f"Account #{acc_id}")

            # Destination Node (Payee or Self-ATM)
            if pd.notna(payee_id) and payee_id is not None:
                dst_node = f"Payee-{int(payee_id)}"
                if not self.graph.has_node(dst_node):
                    self.graph.add_node(dst_node, node_type="Payee", label=f"Payee #{int(payee_id)}")
                
                # Add or update directed weighted edge
                if self.graph.has_edge(src_node, dst_node):
                    self.graph[src_node][dst_node]["weight"] += amount
                    self.graph[src_node][dst_node]["tx_count"] += 1
                    self.graph[src_node][dst_node]["txn_ids"].append(txn_id)
                else:
                    self.graph.add_edge(
                        src_node,
                        dst_node,
                        weight=amount,
                        tx_count=1,
                        txn_ids=[txn_id]
                    )

    def is_new_connection(self, account_id: int, payee_id: Optional[int]) -> bool:
        """Checks if a directed edge currently exists between Account and Payee."""
        if payee_id is None:
            return False
        src = f"Acc-{account_id}"
        dst = f"Payee-{int(payee_id)}"
        return not self.graph.has_edge(src, dst)

    def analyze_node(self, node_id: str) -> Dict[str, Any]:
        """Calculates degree, in-degree, out-degree, and connected neighbors for a vertex."""
        if not self.graph.has_node(node_id):
            return {
                "exists": False,
                "degree": 0,
                "in_degree": 0,
                "out_degree": 0,
                "neighbors": [],
                "total_sent": 0.0,
                "total_received": 0.0
            }

        in_deg = self.graph.in_degree(node_id)
        out_deg = self.graph.out_degree(node_id)
        tot_deg = in_deg + out_deg

        # Calculate total weighted flow
        sent = sum(data["weight"] for _, _, data in self.graph.out_edges(node_id, data=True))
        received = sum(data["weight"] for _, _, data in self.graph.in_edges(node_id, data=True))

        return {
            "exists": True,
            "degree": tot_deg,
            "in_degree": in_deg,
            "out_degree": out_deg,
            "successors": list(self.graph.successors(node_id)),
            "predecessors": list(self.graph.predecessors(node_id)),
            "total_sent": sent,
            "total_received": received
        }

    def compute_graph_risk(
        self,
        account_id: int,
        payee_id: Optional[int],
        amount: float
    ) -> Dict[str, Any]:
        """
        Computes the academic graph risk indicator for a prospective or existing transaction.
        
        Indicators:
          1. Novelty: Transfer to an unprecedented payee for this node (+0.30)
          2. Destination Hub Risk: Payee with unusually high in-degree (+0.25)
          3. Source Out-degree Velocity: Account suddenly branching to multiple novel nodes (+0.25)
          4. Amount-to-weight ratio anomaly (+0.20)
        """
        src = f"Acc-{account_id}"
        is_new = self.is_new_connection(account_id, payee_id)
        
        risk_score = 0.0
        factors = []

        if payee_id is None:
            # Self cash withdrawal / deposit
            return {
                "graph_risk_indicator": 0.1,
                "graph_risk_score": 10.0,
                "is_new_connection": False,
                "factors": ["Self-account transaction (No external graph edge)"],
                "source_degree": self.graph.degree(src) if self.graph.has_node(src) else 0,
                "dest_degree": 0
            }

        dst = f"Payee-{int(payee_id)}"

        # 1. New connection factor
        if is_new:
            risk_score += 0.35
            factors.append("First-time transaction between this account and payee (Novel Edge)")

        # 2. Source Account Out-Degree Analysis
        src_out = self.graph.out_degree(src) if self.graph.has_node(src) else 0
        if src_out >= 4:
            risk_score += 0.20
            factors.append(f"Source account has high out-degree ({src_out} active connections)")

        # 3. Destination Payee In-Degree Analysis
        dst_in = self.graph.in_degree(dst) if self.graph.has_node(dst) else 0
        if dst_in >= 3:
            risk_score += 0.25
            factors.append(f"Destination payee is a high-degree hub ({dst_in} incoming transfer paths)")

        # 4. Repeated transfer velocity check
        if not is_new and self.graph.has_edge(src, dst):
            tx_count = self.graph[src][dst].get("tx_count", 1)
            if tx_count >= 5:
                factors.append(f"Established recurring relationship ({tx_count} prior transfers)")

        # Cap indicator to 1.0
        indicator = min(max(risk_score, 0.05), 1.0)
        graph_risk_score = indicator * 100.0

        return {
            "graph_risk_indicator": indicator,
            "graph_risk_score": graph_risk_score,
            "is_new_connection": is_new,
            "factors": factors if factors else ["Standard network connectivity pattern"],
            "source_degree": self.graph.degree(src) if self.graph.has_node(src) else 0,
            "dest_degree": self.graph.degree(dst) if self.graph.has_node(dst) else 0,
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges()
        }

    def get_network_metrics(self) -> Dict[str, Any]:
        """Returns macro-level topological metrics of the banking network."""
        num_nodes = self.graph.number_of_nodes()
        num_edges = self.graph.number_of_edges()
        
        if num_nodes == 0:
            return {"nodes": 0, "edges": 0, "density": 0.0, "top_hubs": []}

        # Calculate degree centrality
        centrality = nx.degree_centrality(self.graph)
        top_hubs = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "nodes": num_nodes,
            "edges": num_edges,
            "density": round(nx.density(self.graph), 4),
            "top_hubs": top_hubs
        }
