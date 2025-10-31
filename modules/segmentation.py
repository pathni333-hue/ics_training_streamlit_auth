import streamlit as st
import networkx as nx
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import utils, db, json, inspect

# Optional utilities import (safe fallback if utils lacks the functions)
try:
    from utils import sample_network, score_segmentation
except ImportError:
    def sample_network(*args, **kwargs):
        st.warning("sample_network not available.")
        return nx.DiGraph()
    def score_segmentation(*args, **kwargs):
        st.warning("score_segmentation not available.")
        return 0

def draw_network_plotly(G):
    pos = nx.spring_layout(G, seed=42)
    edge_x, edge_y = [], []
    for u, v in G.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]
    node_x, node_y, text, sizes = [], [], [], []
    for n in G.nodes(data=True):
        x, y = pos[n[0]]
        node_x.append(x)
        node_y.append(y)
        text.append(f"{n[0]}<br>{n[1].get('role','')}")
        sizes.append(20 if n[1].get('level',1) == 1 else 30)
    edge_trace = go.Scatter(x=edge_x, y=edge_y, mode='lines', line=dict(width=1), hoverinfo='none')
    node_trace = go.Scatter(
        x=node_x, y=node_y, mode='markers+text', textposition='top center',
        marker=dict(size=sizes), text=list(G.nodes()),
        hovertext=text, hoverinfo='text'
    )
    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(showlegend=False, margin=dict(l=0, r=0, t=20, b=0))
    return fig

def calc_violations(G):
    violations = []
    for u, v in G.edges():
        lu = G.nodes[u].get('level', 2)
        lv = G.nodes[v].get('level', 1)
        if abs(lu - lv) > 1:
            violations.append(f"{u}->{v}")
    return violations

def app(user_context=None):
    st.header('ICS Network Segmentation Trainer')
    st.write('Upload a small network CSV or generate a sample. Identify segmentation violations and get scored.')

    if st.button('Generate sample network'):
        G = sample_network()
        st.session_state['seg_graph'] = G

    uploaded = st.file_uploader('Upload network CSV (optional)', type=['csv'])
    if uploaded is not None:
        df = pd.read_csv(uploaded)
        G = nx.from_pandas_edgelist(df, 'source', 'target', edge_attr=True, create_using=nx.DiGraph())
        for _, r in df.iterrows():
            if 'source_level' in r and not pd.isna(r['source_level']):
                G.nodes[r['source']]['level'] = int(r['source_level'])
            if 'target_level' in r and not

