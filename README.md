# ICS Training Streamlit App (Auth + Persistence + PDF)

This upgraded project adds:
- User authentication (SQLite + bcrypt)
- User progress persistence (SQLite)
- PDF export of user reports (reportlab)

Run locally:
1. Create a virtualenv
2. pip install -r requirements.txt
3. streamlit run app.py

Default admin user will be created on first run: username `admin`, password `adminpass`
(you should change this in production).
