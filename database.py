import sqlite3

def init_db():
    """Initializes the database and creates the required tables."""
    conn = sqlite3.connect('car_insurance.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('policyholder', 'assessor'))
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS claims (
            claim_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            vehicle_make TEXT,
            vehicle_model TEXT,
            vehicle_year INTEGER,
            brand_tier TEXT,
            image_path TEXT,
            estimated_cost REAL,
            status TEXT DEFAULT 'Pending Review',
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Seed default admin if missing
    cursor.execute("SELECT id FROM users WHERE role = 'assessor'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ('admin', 'admin123', 'assessor')
        )

    conn.commit()
    conn.close()

def verify_user(username, password, role):
    """Verifies credentials against the database."""
    conn = sqlite3.connect('car_insurance.db')
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, username FROM users WHERE username=? AND password=? AND role=?', 
        (username, password, role)
    )
    user = cursor.fetchone()
    conn.close()
    return user

def register_user(username, password, role):
    """Registers a new user into the database."""
    conn = sqlite3.connect('car_insurance.db')
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO users (username, password, role) VALUES (?, ?, ?)', 
            (username, password, role)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def add_claim(user_id, vehicle_make, vehicle_model, vehicle_year, brand_tier, image_path, estimated_cost):
    """Inserts a new claim record into the claims table."""
    conn = sqlite3.connect('car_insurance.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO claims (user_id, vehicle_make, vehicle_model, vehicle_year, brand_tier, image_path, estimated_cost)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, vehicle_make, vehicle_model, vehicle_year, brand_tier, image_path, estimated_cost))
    conn.commit()
    conn.close()

def get_user_claims(user_id):
    """Retrieves all claims submitted by a specific policyholder."""
    conn = sqlite3.connect('car_insurance.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT claim_id, vehicle_make, vehicle_model, vehicle_year, brand_tier, estimated_cost, status, image_path
        FROM claims WHERE user_id=? ORDER BY claim_id DESC
    ''', (user_id,))
    claims = cursor.fetchall()
    conn.close()
    return claims

def get_all_claims():
    """Retrieves all claims for assessor review along with policyholder usernames."""
    conn = sqlite3.connect('car_insurance.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.claim_id, u.username, c.vehicle_make, c.vehicle_model, c.vehicle_year, 
               c.brand_tier, c.estimated_cost, c.status, c.image_path
        FROM claims c
        JOIN users u ON c.user_id = u.id
        ORDER BY c.claim_id DESC
    ''')
    claims = cursor.fetchall()
    conn.close()
    return claims

def update_claim_status(claim_id, status, new_cost=None):
    """Updates status and optionally overrides the estimated cost for a claim."""
    conn = sqlite3.connect('car_insurance.db')
    cursor = conn.cursor()
    if new_cost is not None:
        cursor.execute(
            'UPDATE claims SET status=?, estimated_cost=? WHERE claim_id=?',
            (status, new_cost, claim_id)
        )
    else:
        cursor.execute(
            'UPDATE claims SET status=? WHERE claim_id=?',
            (status, claim_id)
        )
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()