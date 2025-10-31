import streamlit as st
import random
import pandas as pd
import plotly.express as px
import db

TECHNIQUES = [
    {'id':'T101','name':'Reconnaissance - Network Scanning','mitigations':['Network segmentation','Monitor network flows','Access control']},
    {'id':'T102','name':'Initial Access - Spearphishing','mitigations':['User training','Email filtering','MFA']},
    {'id':'T103','name':'Lateral Movement - Pass-the-Hash','mitigations':['Credential hygiene','Endpoint protection','Least privilege']},
    {'id':'T104','name':'Command and Control - Outbound C2','mitigations':['Egress filtering','DNS monitoring','Proxy gateways']},
]

def app(user_context=None):
    st.header('Threat-to-Mitigation Mapping Challenge')
    st.write('Match techniques to mitigations.')

    if 'score' not in st.session_state:
        st.session_state['score'] = 0
        st.session_state['attempts'] = 0

    if st.button('New challenge'):
        st.session_state['current'] = random.choice(TECHNIQUES)

    if 'current' not in st.session_state:
        st.info('Click "New challenge" to begin.')
        return

    cur = st.session_state['current']
    st.subheader(f"Technique: {cur['id']} — {cur['name']}")
    all_mits = list({m for t in TECHNIQUES for m in t['mitigations']})
    picks = st.multiselect('Select correct mitigations (one or more)', all_mits)
    if st.button('Submit answer'):
        st.session_state['attempts'] += 1
        correct_set = set(cur['mitigations'])
        pick_set = set(picks)
        success = (pick_set == correct_set or pick_set.issuperset(correct_set))
        st.session_state['score'] += 1 if success else 0
        if success:
            st.success('Correct!')
        else:
            st.error('Not fully correct. Correct mitigations are:')
            st.write(cur['mitigations'])
        # save attempt
        if user_context:
            try:
                db.save_progress(user_context['user_id'], 'Threat-to-Mitigation Mapping Challenge', 100 if success else 0, {'technique':cur['id'],'picked':list(pick_set)})
                st.success('Progress saved.')
            except Exception as e:
                st.error(f'Failed to save progress: {e}')

    st.write(f"Score: {st.session_state['score']} / {st.session_state['attempts']}")
    coverage = []
    for t in TECHNIQUES:
        covered = any(m in st.session_state.get('last_picks',[]) for m in t['mitigations'])
        coverage.append({'technique':t['id'],'covered':covered})
    cov_df = pd.DataFrame(coverage)
    fig = px.bar(cov_df, x='technique', y='covered', title='Simple coverage chart (placeholder)')
    st.plotly_chart(fig, use_container_width=True)
