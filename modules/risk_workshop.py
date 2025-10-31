import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import db

def risk_score_row(row):
    return row.get('impact',1) * row.get('likelihood',1)

def app(user_context=None):
    st.header('OT Risk Scoring Workshop')
    st.write('Input device characteristics or upload CSV (name, age_years, exposure, protocol, impact, likelihood).')

    uploaded = st.file_uploader('Upload devices CSV', type=['csv'])
    if uploaded is not None:
        df = pd.read_csv(uploaded)
    else:
        df = pd.DataFrame([
            {'name':'PLC-1','age_years':8,'exposure':3,'protocol':'Modbus','impact':5,'likelihood':4},
            {'name':'HMI-1','age_years':4,'exposure':2,'protocol':'OPC','impact':4,'likelihood':2},
            {'name':'Historian-1','age_years':6,'exposure':3,'protocol':'MQTT','impact':4,'likelihood':3},
        ])

    st.dataframe(df)

    if st.button('Score devices'):
        df['risk'] = df.apply(lambda r: risk_score_row(r), axis=1)
        fig = px.scatter(df, x='likelihood', y='impact', size='risk', hover_name='name', title='Risk heatmap (bubble)')
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df[['name','impact','likelihood','risk']])
        # save average risk score
        avg = df['risk'].mean() if 'risk' in df else 0.0
        if user_context:
            try:
                db.save_progress(user_context['user_id'], 'OT Risk Scoring Workshop', avg, {'devices': df.to_dict(orient='records')})
                st.success('Progress saved.')
            except Exception as e:
                st.error(f'Failed to save progress: {e}')

    mitigate = st.checkbox('Apply mitigation: reduce likelihood by 1 for selected devices')
    if mitigate:
        sel = st.multiselect('Select devices to mitigate', df['name'].tolist())
        if st.button('Recalculate after mitigation'):
            df2 = df.copy()
            df2.loc[df2['name'].isin(sel),'likelihood'] = (df2.loc[df2['name'].isin(sel),'likelihood'] - 1).clip(lower=1)
            df2['risk'] = df2.apply(risk_score_row, axis=1)
            fig2 = px.scatter(df2, x='likelihood', y='impact', size='risk', hover_name='name', title='Post-mitigation risk')
            st.plotly_chart(fig2, use_container_width=True)
            st.dataframe(df2[['name','impact','likelihood','risk']])
            if user_context:
                try:
                    db.save_progress(user_context['user_id'], 'OT Risk Scoring Workshop (post-mitigation)', df2['risk'].mean(), {'devices': df2.to_dict(orient='records')})
                    st.success('Post-mitigation progress saved.')
                except Exception as e:
                    st.error(f'Failed to save progress: {e}')
