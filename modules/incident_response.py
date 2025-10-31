import streamlit as st
import random
import pandas as pd
import db

SCENARIOS = [
    {'id':'S1','title':'Ransomware on Engineering Workstation','description':'Files encrypted on HMI workstation, starting to propagate.'},
    {'id':'S2','title':'PLC Tampering Detected','description':'Unexpected setpoints observed on PLC-3.'},
    {'id':'S3','title':'Historian Data Corruption','description':'Historian shows gaps and altered entries.'},
]

ACTIONS = [
    'Isolate affected node',
    'Notify OT manager',
    'Collect volatile evidence',
    'Restore from backup',
    'Re-image workstation',
    'Block suspicious IPs',
    'Apply patch',
]

def score_sequence(seq, scenario):
    score = 0
    if scenario['id']=='S1':
        if 'Isolate affected node' in seq: score += 3
        if 'Block suspicious IPs' in seq: score += 1
        if 'Restore from backup' in seq: score += 2
    if scenario['id']=='S2':
        if 'Isolate affected node' in seq: score += 3
        if 'Collect volatile evidence' in seq: score += 2
        if 'Notify OT manager' in seq: score += 1
    if scenario['id']=='S3':
        if 'Collect volatile evidence' in seq: score += 2
        if 'Restore from backup' in seq: score += 3
    return score

def app(user_context=None):
    st.header('OT Incident Response Simulation')
    st.write('Select a scenario and choose IR steps. Score and debrief provided.')

    scenario = st.selectbox('Pick scenario', SCENARIOS, format_func=lambda s: f"{s['id']} - {s['title']}")
    st.write(scenario['description'])

    chosen = st.multiselect('Select ordered steps (choose helpful actions)', ACTIONS)

    if st.button('Submit IR decisions'):
        score = score_sequence(chosen, scenario)
        st.metric('IR score', score)
        st.write('Debrief:')
        if scenario['id']=='S1':
            st.write('- Prioritise isolation, communication, and backup recovery. Consider forensics after containment.')
        elif scenario['id']=='S2':
            st.write('- Contain and preserve evidence; avoid immediate changes to PLCs until safe.')
        else:
            st.write('- Validate backups and maintain chain-of-custody for data restoration.')
        if user_context:
            try:
                db.save_progress(user_context['user_id'], 'OT Incident Response Simulation', score, {'scenario':scenario['id'],'actions':chosen})
                st.success('Progress saved.')
            except Exception as e:
                st.error(f'Failed to save progress: {e}')
