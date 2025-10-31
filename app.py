import streamlit as st
from modules import segmentation, asset_lab, risk_workshop, threat_mapping, incident_response, hygiene_dashboard
import db, report, os

st.set_page_config(page_title="OT/ICS Training Platform (Auth)", layout="wide")
db.init_db()

def login_page():
    st.header('Login')
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')
    col1, col2 = st.columns(2)
    with col1:
        if st.button('Login'):
            uid = db.verify_user(username, password)
            if uid:
                st.session_state['user'] = {'id':uid,'username':username}
                st.success('Logged in.')
            else:
                st.error('Invalid credentials.')
    with col2:
        if st.button('Register'):
            ok = db.add_user(username, password)
            if ok:
                st.success('User registered. You can now login.')
            else:
                st.error('Registration failed (user may already exist).')

def logout():
    if 'user' in st.session_state:
        del st.session_state['user']

def main_app():
    st.sidebar.title(f"User: {st.session_state['user']['username']}")
    if st.sidebar.button('Logout'):
        logout()
        st.experimental_rerun()

    st.title('OT / ICS Interactive Training Platform (Authenticated)')
    st.markdown('Select a module from the sidebar to begin. Progress will be saved to the database.')

    MODULES = {
        "1 - Network Segmentation Trainer": segmentation,
        "2 - Asset Discovery & Classification Lab": asset_lab,
        "3 - OT Risk Scoring Workshop": risk_workshop,
        "4 - Threat-to-Mitigation Mapping Challenge": threat_mapping,
        "5 - OT Incident Response Simulation": incident_response,
        "6 - OT Cyber Hygiene Assessment Dashboard": hygiene_dashboard
    }

    choice = st.sidebar.radio("Choose module", list(MODULES.keys()))
    module = MODULES[choice]

    st.sidebar.markdown('---')
    if st.sidebar.button('My Progress Dashboard'):
        prog = db.get_progress(st.session_state['user']['id'])
        st.subheader('My Progress')
        st.write('Recent activity:')
        st.dataframe([{'module':p['module'],'score':p['score'],'timestamp':p['timestamp']} for p in prog])
        # PDF export
        if st.button('Download My Report (PDF)'):
            out_dir = os.path.join('data','reports')
            os.makedirs(out_dir, exist_ok=True)
            out_path = os.path.join(out_dir, f"report_{st.session_state['user']['username']}.pdf")
            report.generate_user_report(st.session_state['user']['username'], prog, out_path)
            with open(out_path, 'rb') as f:
                st.download_button('Click to download PDF', f, file_name=os.path.basename(out_path))

    st.sidebar.markdown('---')
    st.sidebar.markdown('**Resources**')
    st.sidebar.markdown('- Example datasets are in the `data/` folder.')
    st.sidebar.markdown('- Expand modules in `modules/` to customise content.')

    # run module app with saving callback available
    module.app(user_context={'user_id': st.session_state['user']['id'], 'username': st.session_state['user']['username']})

if 'user' not in st.session_state:
    login_page()
else:
    main_app()
