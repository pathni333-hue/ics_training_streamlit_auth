import streamlit as st
import pandas as pd
from utils import sample_asset_csv
import db

ASSET_CLASSES = ['PLC','HMI','Historian','Sensor','Actuator','Switch','Firewall','Unknown']

def app(user_context=None):
    st.header('Asset Discovery & Classification Lab')
    st.write('Upload a CSV with fake OT devices or use the sample. Then assign each device to a class.')

    if st.button('Generate sample CSV'):
        sample_asset_csv()
        st.success('Sample CSV written to data/sample_assets.csv')

    uploaded = st.file_uploader('Upload devices CSV', type=['csv'])
    if uploaded is None:
        try:
            df = pd.read_csv('data/sample_assets.csv')
        except Exception as e:
            st.info('No sample CSV yet — click "Generate sample CSV" or upload your own.')
            return
    else:
        df = pd.read_csv(uploaded)

    st.write('Devices:')
    st.dataframe(df)

    st.markdown('**Classify devices**')
    # Using session to track assignments
    if 'asset_assignments' not in st.session_state:
        st.session_state['asset_assignments'] = {}
    for idx,row in df.iterrows():
        cols = st.columns([3,2,2])
        cols[0].write(f"**{row['name']}** — {row['ip']} — {row['vendor']}")
        pick = cols[1].selectbox('Class', ASSET_CLASSES, key=f'class_{idx}')
        if cols[2].button('Submit', key=f'submit_{idx}'):
            st.session_state['asset_assignments'][row['name']] = pick
            st.write('Recorded.')

    if st.button('Show scoring'):
        assignments = st.session_state.get('asset_assignments', {})
        results = []
        for _,row in df.iterrows():
            assigned = assignments.get(row['name'], 'Unassigned')
            correct = assigned == row.get('expected','Unknown')
            results.append({'name':row['name'],'assigned':assigned,'correct':correct})
        dfr = pd.DataFrame(results)
        acc = dfr['correct'].mean()*100 if len(dfr)>0 else 0.0
        st.metric('Classification accuracy', f"{acc:.1f}%")
        st.dataframe(dfr)
        if user_context:
            try:
                db.save_progress(user_context['user_id'], 'Asset Discovery & Classification Lab', acc, {'results':results})
                st.success('Progress saved.')
            except Exception as e:
                st.error(f'Failed to save progress: {e}')
