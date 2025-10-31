import streamlit as st
import networkx as nx
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils import sample_network, score_segmentation if False else None
import utils, db, json, inspect

def draw_network_plotly(G):
    pos = nx.spring_layout(G, seed=42)
    edge_x = []
    edge_y = []
    for u,v in G.edges():
        x0,y0 = pos[u]
        x1,y1 = pos[v]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]
    node_x = []
    node_y = []
    text = []
    sizes = []
    for n in G.nodes(data=True):
        x,y = pos[n[0]]
        node_x.append(x)
        node_y.append(y)
        text.append(f"{n[0]}<br>{n[1].get('role','')}")
        sizes.append(20 if n[1].get('level',1)==1 else 30)
    edge_trace = go.Scatter(x=edge_x, y=edge_y, mode='lines', line=dict(width=1), hoverinfo='none')
    node_trace = go.Scatter(x=node_x, y=node_y, mode='markers+text', textposition='top center',
                            marker=dict(size=sizes), text=[n for n in list(G.nodes())],
                            hovertext=text, hoverinfo='text')
    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(showlegend=False, margin=dict(l=0,r=0,t=20,b=0))
    return fig

def calc_violations(G):
    violations = []
    for u,v in G.edges():
        lu = G.nodes[u].get('level',2)
        lv = G.nodes[v].get('level',1)
        if abs(lu - lv) > 1:
            violations.append(f"{u}->{v}")
    return violations

def app(user_context=None):
    st.header('ICS Network Segmentation Trainer')
    st.write('Upload a small network CSV or generate a sample. Identify segmentation violations and get scored.')

    if st.button('Generate sample network'):
        G = utils.sample_network()
        st.session_state['seg_graph'] = G
    uploaded = st.file_uploader('Upload network CSV (optional)', type=['csv'])
    if uploaded is not None:
        df = pd.read_csv(uploaded)
        G = nx.from_pandas_edgelist(df, 'source', 'target', edge_attr=True, create_using=nx.DiGraph())
        for _,r in df.iterrows():
            if 'source_level' in r and not pd.isna(r['source_level']):
                G.nodes[r['source']]['level'] = int(r['source_level'])
            if 'target_level' in r and not pd.isna(r['target_level']):
                G.nodes[r['target']]['level'] = int(r['target_level'])
        st.session_state['seg_graph'] = G

    if 'seg_graph' not in st.session_state:
        st.info('No network loaded. Click "Generate sample network" or upload a CSV.')
        return
    G = st.session_state['seg_graph']
    st.plotly_chart(draw_network_plotly(G), use_container_width=True)

    st.markdown('**Identify violations**')
    edges = list(G.edges())
    edge_strs = [f"{u} -> {v}" for u,v in edges]
    picked = st.selectbox('Pick edge', ['']+edge_strs)
    verdict = st.radio('Is this a segmentation violation?', ['Unknown','Yes','No'])
    comment = st.text_input('Comment / remediation suggestion')
    if st.button('Submit identification'):
        if picked=='':
            st.warning('Pick an edge first.')
        else:
            anns = st.session_state.get('seg_annotations', [])
            anns.append({'edge':picked, 'verdict':verdict, 'comment':comment})
            st.session_state['seg_annotations'] = anns
            st.success('Recorded.')

    st.markdown('**Scoring**')
    anns = st.session_state.get('seg_annotations', [])
    df_ann = pd.DataFrame(anns) if anns else pd.DataFrame(columns=['edge','verdict','comment'])
    st.dataframe(df_ann)
    if st.button('Calculate compliance score'):
        # compute true violations and f1-like score
        true_violations = calc_violations(G)
        user_violations = [a['edge'] for a in anns if a.get('verdict')=='Yes']
        true_set = set(true_violations)
        user_set = set(user_violations)
        tp = len(true_set & user_set)
        fp = len(user_set - true_set)
        fn = len(true_set - user_set)
        precision = tp / (tp+fp) if (tp+fp)>0 else 0.0
        recall = tp / (tp+fn) if (tp+fn)>0 else 0.0
        f1 = 2*precision*recall/(precision+recall) if (precision+recall)>0 else 0.0
        score_pct = round(f1*100,1)
        st.metric('Segmentation compliance', f"{score_pct}%")
        st.write({'true_violations':list(true_set),'detected':list(user_set),'tp':tp,'fp':fp,'fn':fn})
        # save progress if user context provided
        if user_context:
            try:
                db.save_progress(user_context['user_id'], 'Network Segmentation Trainer', score_pct, {'tp':tp,'fp':fp,'fn':fn})
                st.success('Progress saved.')
            except Exception as e:
                st.error(f'Failed to save progress: {e}')
