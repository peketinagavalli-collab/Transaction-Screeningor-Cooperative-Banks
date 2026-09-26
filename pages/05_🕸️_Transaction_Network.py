"""
ADSA Module: Interactive NetworkX Transaction Graph & Centrality Analyzer.

Models accounts and payees as a directed weighted graph G = (V, E).
"""

import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go

from database.db_connection import DatabaseManager
from services.graph_analyzer import GraphAnalyzer


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Transaction Network | Coop Bank AI",
    page_icon="🕸️",
    layout="wide"
)


# ============================================================
# ACADEMIC HEADER
# ============================================================

st.markdown(
    """
    <div style='background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%);
                padding: 1.5rem 2rem;
                border-radius: 10px;
                color: white;
                margin-bottom: 1.2rem;'>

        <h1 style='color: white;
                   margin: 0;
                   font-size: 1.8rem;
                   font-weight: 800;'>
            🕸️ ADSA Module: NetworkX Transaction Graph
        </h1>

        <p style='color: #93C5FD;
                  margin: 0.3rem 0 0 0;
                  font-size: 0.95rem;'>
            Directed Weighted Graph Analytics, Degree Centrality & Hub Identification
        </p>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# FETCH TRANSACTION DATA
# ============================================================

try:

    df_txns = DatabaseManager.execute_query(
        """
        SELECT
            t.transaction_id,
            t.account_id,
            t.payee_id,
            t.amount,
            t.transaction_type,
            t.status,
            c.customer_name,
            COALESCE(p.payee_name, 'Self / ATM') AS payee_name

        FROM "TRANSACTION" t

        JOIN ACCOUNT a
            ON t.account_id = a.account_id

        JOIN CUSTOMER c
            ON a.customer_id = c.customer_id

        LEFT JOIN PAYEE p
            ON t.payee_id = p.payee_id
        """
    )

except Exception as e:

    st.error(f"Error fetching network data: {e}")
    st.stop()


# ============================================================
# CHECK DATA
# ============================================================

if df_txns is None:

    st.warning("No transaction data was returned from the database.")
    st.stop()


if not isinstance(df_txns, pd.DataFrame):

    df_txns = pd.DataFrame(df_txns)


# ============================================================
# INITIALIZE GRAPH ANALYZER
# ============================================================

try:

    analyzer = GraphAnalyzer(df_txns)
    G = analyzer.graph

except Exception as e:

    st.error(f"Error creating transaction graph: {e}")
    st.stop()


# ============================================================
# 1. ADSA THEORY OVERVIEW
# ============================================================

st.markdown("### 📚 ADSA Graph Concepts & Definitions")

col_c1, col_c2, col_c3, col_c4 = st.columns(4)


# ------------------------------------------------------------
# CARD 1 - VERTICES
# ------------------------------------------------------------

with col_c1:

    number_of_nodes = G.number_of_nodes()

    st.markdown(
        """
        **1. Vertices ($\\mathcal{{V}}$):**

        - Account Nodes ($Acc_i$)
        - Payee Nodes ($Payee_j$)
        - Total Vertices: **{}**
        """.format(number_of_nodes)
    )


# ------------------------------------------------------------
# CARD 2 - EDGES
# ------------------------------------------------------------

with col_c2:

    number_of_edges = G.number_of_edges()

    st.markdown(
        """
        **2. Directed Edges ($\\mathcal{{E}}$):**

        - Transfer arrows ($u \\to v$)
        - Direction indicates flow of funds
        - Total Directed Edges: **{}**
        """.format(number_of_edges)
    )


# ------------------------------------------------------------
# CARD 3 - WEIGHTED EDGES
# ------------------------------------------------------------

with col_c3:

    if number_of_nodes > 0:
        density = nx.density(G)
    else:
        density = 0

    st.markdown(
        """
        **3. Weighted Edges ($w$):**

        - Cumulative transfer volume (₹)
        - Thicker edges = higher amounts
        - Network Density: **{:.3f}**
        """.format(density)
    )


# ------------------------------------------------------------
# CARD 4 - DEGREE
# ------------------------------------------------------------

with col_c4:

    st.markdown(
        """
        **4. Vertex Degree ($d$):**

        - $d_{{in}}$: Incoming funds
        - $d_{{out}}$: Outgoing transfers
        - Degree Centrality hubs
        """
    )


st.markdown("---")


# ============================================================
# 2. INTERACTIVE NETWORK GRAPH
# ============================================================

st.markdown("### 🌐 Visual Transaction Graph Map")


if G.number_of_nodes() > 0:

    # --------------------------------------------------------
    # SPRING LAYOUT
    # --------------------------------------------------------

    pos = nx.spring_layout(
        G,
        k=1.2,
        seed=42
    )


    # --------------------------------------------------------
    # EDGE TRACES
    # --------------------------------------------------------

    edge_x = []
    edge_y = []

    for u, v, d in G.edges(data=True):

        x0, y0 = pos[u]
        x1, y1 = pos[v]

        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])


    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,

        line=dict(
            width=1.5,
            color="#94A3B8"
        ),

        hoverinfo="none",
        mode="lines"
    )


    # --------------------------------------------------------
    # NODE TRACES
    # --------------------------------------------------------

    node_x = []
    node_y = []

    node_colors = []
    node_sizes = []
    node_labels = []
    node_hover_texts = []


    for node in G.nodes():

        x, y = pos[node]

        node_x.append(x)
        node_y.append(y)

        try:

            node_info = analyzer.analyze_node(node)

        except Exception:

            node_info = {
                "in_degree": 0,
                "out_degree": 0,
                "degree": 0,
                "total_sent": 0,
                "total_received": 0
            }


        in_d = node_info.get("in_degree", 0)
        out_d = node_info.get("out_degree", 0)
        tot_d = node_info.get("degree", 0)

        total_sent = node_info.get("total_sent", 0)
        total_received = node_info.get("total_received", 0)


        # Account node
        if str(node).startswith("Acc"):

            node_colors.append("#2563EB")

        # Payee node
        else:

            node_colors.append("#10B981")


        node_sizes.append(
            max(
                20,
                min(
                    tot_d * 10 + 15,
                    45
                )
            )
        )


        node_labels.append(str(node))


        node_hover_texts.append(
            f"<b>Node:</b> {node}<br>"
            f"<b>Total Degree:</b> {tot_d} "
            f"(In: {in_d}, Out: {out_d})<br>"
            f"<b>Total Sent:</b> ₹{total_sent:,.2f}<br>"
            f"<b>Total Received:</b> ₹{total_received:,.2f}"
        )


    node_trace = go.Scatter(

        x=node_x,
        y=node_y,

        mode="markers+text",

        hoverinfo="text",

        text=node_labels,

        textposition="top center",

        hovertext=node_hover_texts,

        marker=dict(
            color=node_colors,
            size=node_sizes,

            line=dict(
                width=2,
                color="#FFFFFF"
            )
        )
    )


    # --------------------------------------------------------
    # CREATE FIGURE
    # --------------------------------------------------------

    fig_net = go.Figure(

        data=[
            edge_trace,
            node_trace
        ],

        layout=go.Layout(

            showlegend=False,

            hovermode="closest",

            margin=dict(
                b=20,
                l=20,
                r=20,
                t=20
            ),

            xaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False
            ),

            yaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False
            ),

            height=480,

            plot_bgcolor="#F8FAFC"
        )
    )


    st.plotly_chart(
        fig_net,
        use_container_width=True
    )


    st.caption(
        "🔵 Blue Nodes = Source Member Accounts | "
        "🟢 Green Nodes = Beneficiary / Payee Entities | "
        "Hover over any vertex to inspect degrees and funds flow."
    )


else:

    st.info("Graph is currently empty.")


# ============================================================
# 3. NODE DEGREE TABLE & HUB ANALYSIS
# ============================================================

st.markdown("---")

c_deg1, c_deg2 = st.columns(
    [1.2, 1.0]
)


# ============================================================
# LEFT COLUMN - DEGREE TABLE
# ============================================================

with c_deg1:

    st.markdown(
        "#### 📊 Vertex Degree Centrality Table"
    )

    degree_data = []


    for node in G.nodes():

        try:

            info = analyzer.analyze_node(node)

        except Exception:

            info = {
                "in_degree": 0,
                "out_degree": 0,
                "degree": 0,
                "total_sent": 0,
                "total_received": 0
            }


        degree_data.append(
            {
                "Vertex": node,

                "Type":
                    "Account"
                    if str(node).startswith("Acc")
                    else "Payee",

                "In-Degree (d_in)":
                    info.get("in_degree", 0),

                "Out-Degree (d_out)":
                    info.get("out_degree", 0),

                "Total Degree (d)":
                    info.get("degree", 0),

                "Total Transferred":
                    f"₹{info.get('total_sent', 0):,.2f}",

                "Total Received":
                    f"₹{info.get('total_received', 0):,.2f}"
            }
        )


    if degree_data:

        df_deg = pd.DataFrame(
            degree_data
        )

        df_deg = df_deg.sort_values(
            "Total Degree (d)",
            ascending=False
        )

        st.dataframe(
            df_deg,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No vertices available.")


# ============================================================
# RIGHT COLUMN - HUB ANALYSIS
# ============================================================

with c_deg2:

    st.markdown(
        "#### 🌟 High-Connectivity Hubs & Novel Connections"
    )


    try:

        metrics = analyzer.get_network_metrics()

    except Exception as e:

        metrics = {
            "top_hubs": []
        }

        st.warning(
            f"Unable to calculate network metrics: {e}"
        )


    st.markdown(
        "##### 🏆 Top Centrality Hub Nodes:"
    )


    top_hubs = metrics.get(
        "top_hubs",
        []
    )


    if top_hubs:

        for hub_node, centrality_score in top_hubs:

            node_type = (
                "Account"
                if str(hub_node).startswith("Acc")
                else "Payee Beneficiary"
            )

            st.write(
                f"- **{hub_node}** "
                f"({node_type}) — "
                f"Degree Centrality: "
                f"`{centrality_score:.3f}`"
            )

    else:

        st.info(
            "No centrality hubs available."
        )


    st.markdown("---")


    # --------------------------------------------------------
    # GRAPH RISK FORMULA
    # --------------------------------------------------------

    st.markdown(
        "##### 🔎 Graph-Based Risk Indicator Formula:"
    )


    st.markdown(
        """
        Academic Graph Risk ($G_{{risk}}$) combines:

        $$\\text{{GraphRisk}} =
        0.35(\\text{{Novelty}})
        + 0.25(\\text{{Hub In-Degree}})
        + 0.20(\\text{{Out Velocity}})$$

        - **Novel Edge ($N$):**
          Unprecedented connection between account and destination.

        - **Hub Risk:**
          Concentration of high velocity transfers into a single
          third-party payee.
        """
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "Academic prototype: NetworkX is used to model accounts and "
    "payees as vertices and transactions as directed weighted edges."
)