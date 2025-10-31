import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import db

QUESTIONS = [
    {'q':'Are OT systems patched regularly?','key':'patching'},
    {'q':'Are unique credentials used per device?','key':'credentials'},
    {'q':'Are backups performed and tested?','key':'backups'},
    {'q':'Is network monitoring enabled for OT segments?','key':'monitoring'},
    {'q':'Are least-privilege principles enforced?','key':'least_privilege'},
]

def app(user_context=None):
    st.header('OT Cyber Hygiene Assessment Dashboard')
    st.write('Quick questionnaire to produce a maturity radar and top-3 suggestions.')

    responses = {}
    cols = st.columns(2)
    for i,q in enumerate(QUESTIONS):
        val = cols[i%2].selectbox(q['q'], ['No','Partial','Yes'], key=q['key'])
        responses[q['key']] = {'No':0,'Partial':1,'Yes':2}[val]

    df = pd.DataFrame([responses]).T.reset_index()
    df.columns = ['metric','score']
    st.dataframe(df)

    fig = px.bar_polar(df, r='score', theta='metric', title='Hygiene radar (simple)')
    st.plotly_chart(fig, use_container_width=True)

    total = df['score'].sum()
    maturity_pct = total / (len(QUESTIONS)*2) * 100
    st.metric('Maturity', f"{maturity_pct:.0f}%")

    suggestions = []
    low = df.nsmallest(3,'score')
    for _,row in low.iterrows():
        suggestions.append(f"Improve {row['metric']}: consider policy, automation, or monitoring.")
    st.write('Top suggestions:')
    for s in suggestions:
        st.write('- ' + s)

    if st.button('Save hygiene result'):
        if user_context:
            try:
                db.save_progress(user_context['user_id'], 'OT Cyber Hygiene Assessment Dashboard', maturity_pct, {'responses':responses})
                st.success('Progress saved.')
            except Exception as e:
                st.error(f'Failed to save progress: {e}')
