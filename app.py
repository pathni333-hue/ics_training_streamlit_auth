import streamlit as st
from modules import (
    segmentation,
    asset_lab,
    risk_workshop,
    threat_mapping,
    incident_response,
    hygiene_dashboard
)
import db, report, os

st.set_page_config(page_title="OT/ICS Training Platform (Auth)", layout="wide")

# Initialize database safely
try:
    db.init_db()
except Exception as e:
    st.error(f"Database initialization failed: {e}")

def login_page():
    st.header('Login')
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')
    col1, col2 = st.columns(2)

    # track login/register outcome messages using session state
    if 'login_message' not in st.session_state:
        st.session_state['login_message'] = None

    with col1:
        if st.button('Login'):
            uid = db.verify_user(username, password)
            if uid:
                st.session_state['user'] = {'id': uid, 'username': username}
                st.session_state['login_message'] = ('success', 'Logged in.')
                st.experimental_rerun()
            else:
                st.session_state['login_message'] = ('error', 'Invalid credentials.')

    with col2:
        if st.button('Register'):
            ok = db.add_user(username, password)
            if ok:
                st.session_state['login_message'] = ('success', 'User registered. You can now login.')
            else:
                st.session_state['login_message'] = ('error', 'Registration failed (user may already exist).')

    msg = st.session_state.get('login_message')
    if msg:
        getattr(st, msg[0])(msg[1])

def logout():
    if 'user' in st.session_state:
        del st.session_state['user']
    st.experimental_rerun()

def main_app():
    user = st.session_state.get('user')
    if not user:
        st.experimental_rerun()
        return

    st.sidebar.title(f"User: {user['username']}")
    if st.sidebar.button('Logout'):
        logout()

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
        try:
            prog = db.get_progress(user['id'])
            st.subheader('My Progress')
            st.dataframe([
                {'module': p['module'], 'score': p['score'], 'timestamp': p['timestamp']}
                for p in prog
            ])

            if st.button('Download My Report (PDF)'):
                out_dir = os.path.join('data', 'reports')
                os.makedirs(out_dir, exist_ok=True)
                out_path = os.path.join(out_dir, f"report_{user['username']}.pdf")
                report.generate_user_report(user['username'], prog, out_path)
                with open(out_path, 'rb') as f:
                    st.download_button('Click to download PDF', f, file_name=os.path.basename(out_path))
        except Exception as e:
            st.error(f"Could not load progress: {e}")

    st.sidebar.markdown('---')
    st.sidebar.markdown('Resources')
    st.sidebar.markdown('- Example datasets are in the `data/` folder.')
    st.sidebar.markdown('- Expand modules in `modules/` to customise content.')

    # Safely call module.app
    if hasattr(module, 'app') and callable(module.app):
        module.app(user_context={'user_id': user['id'], 'username': user['username']})
    else:
        st.error(f"Module '{choice}' does not have an 'app(user_context)' function.")

if 'user' not in st.session_state:
    login_page()
else:
    main_app()

