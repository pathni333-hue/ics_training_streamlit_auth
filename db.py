import sqlite3, os, time, bcrypt, json
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'app.db')

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash BLOB,
        created_at REAL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        module TEXT,
        score REAL,
        details TEXT,
        timestamp REAL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    conn.commit()
    conn.close()
    # create default admin if no users
    if not get_all_users():
        add_user('admin','adminpass')

def get_conn():
    return sqlite3.connect(DB_PATH)

def add_user(username, password):
    pw = password.encode('utf-8')
    hashed = bcrypt.hashpw(pw, bcrypt.gensalt())
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username,password_hash,created_at) VALUES (?,?,?)', (username, hashed, time.time()))
        conn.commit()
        return True
    except Exception as e:
        return False
    finally:
        conn.close()

def verify_user(username, password):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT id, password_hash FROM users WHERE username=?', (username,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    uid, pw_hash = row[0], row[1]
    try:
        if bcrypt.checkpw(password.encode('utf-8'), pw_hash):
            return uid
    except Exception:
        return None
    return None

def get_user_by_username(username):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT id, username, created_at FROM users WHERE username=?', (username,))
    row = c.fetchone()
    conn.close()
    if row:
        return {'id':row[0],'username':row[1],'created_at':row[2]}
    return None

def get_all_users():
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT id,username FROM users')
    rows = c.fetchall()
    conn.close()
    return [{'id':r[0],'username':r[1]} for r in rows]

def save_progress(user_id, module, score, details):
    conn = get_conn()
    c = conn.cursor()
    c.execute('INSERT INTO progress (user_id,module,score,details,timestamp) VALUES (?,?,?,?,?)',
              (user_id, module, score, json.dumps(details), time.time()))
    conn.commit()
    conn.close()

def get_progress(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT module,score,details,timestamp FROM progress WHERE user_id=? ORDER BY timestamp DESC', (user_id,))
    rows = c.fetchall()
    conn.close()
    return [{'module':r[0],'score':r[1],'details':json.loads(r[2]) if r[2] else {}, 'timestamp':r[3]} for r in rows]
