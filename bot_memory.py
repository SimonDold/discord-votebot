import sqlite3
import os

db_file = 'voteBot/data/voteBot.db'
conn = sqlite3.connect(db_file)
abs_path = os.path.abspath(db_file)
cursor = conn.cursor()

UPCOMING_DATE = "UPCOMING_DATE"
NEXT_DATE = "NEXT_DATE"
UPCOMING_PAPER = "UPCOMING_PAPER"


def get_suggestions_table():
    with conn:
        cursor.execute("SELECT * FROM suggestions")
        return cursor.fetchall()

def get_in_claims_table():
    with conn:
        cursor.execute("SELECT * FROM in_claims")
        return cursor.fetchall()

def get_user_in_claim(user):
    with conn:
        query = "SELECT claim FROM in_claims WHERE user = ?"
        cursor.execute(query, (user,))
        [(r,)] = cursor.fetchall()
        return r


def get_marking_users(paper):
    with conn:
        query = "SELECT user FROM marks WHERE paper = ?"
        cursor.execute(query, (paper,))
        return cursor.fetchall()


def get_user_votes_table(user):
    with conn:
        query = "SELECT * FROM suggestions WHERE user = ?"
        cursor.execute(query, (user,))
        return cursor.fetchall()


def get_marks_table():
    with conn:
        cursor.execute("SELECT * FROM marks")
        return cursor.fetchall()

def get_admins_table():
    with conn:
        cursor.execute("SELECT * FROM admins")
        return cursor.fetchall()


def update_suggestions(paper, user, reaction): # from chatGPT 3
    # Connect to the SQLite database
    paper = str(paper)
    reaction = str(reaction)
    print("Update suggestions DB")

    # SQL statements with placeholders
    insert_query = """
        INSERT INTO suggestions (paper, user, reaction)
        SELECT ?, ?, ?
        WHERE NOT EXISTS (
            SELECT 1 FROM suggestions WHERE paper = ? AND user = ?
        )
    """

    update_query = """
        UPDATE suggestions
        SET reaction = ?
        WHERE paper = ? AND user = ?
    """

    # -- Insert a new row if it doesn't exist
    insert_query_claims = """
                INSERT INTO in_claims (user, claim)
                SELECT ?, ?
                WHERE NOT EXISTS (
                    SELECT 1 FROM in_claims WHERE user = ?
                )
            """

    # Execute the INSERT statement with parameters
    cursor.execute(insert_query, (paper, user, reaction, paper, user))

    # Execute the UPDATE statement with parameters
    cursor.execute(update_query, (reaction, paper, user))

    cursor.execute(insert_query_claims, (user, "uk", user))

    # Commit the changes
    conn.commit()

def update_marks(paper, user, mark=True):
    # Connect to the SQLite database
    paper = str(paper)
    print("Update marks DB")

    # SQL statements with placeholders
    insert_query = """
        INSERT INTO marks (paper, user)
        SELECT ?, ?
        WHERE NOT EXISTS (
            SELECT 1 FROM marks WHERE paper = ? AND user = ?
        )
    """
    delete_query = """
                DELETE FROM marks
                WHERE paper = ? AND user = ?
            """
    if mark:
        cursor.execute(insert_query, (paper, user, paper, user))
        print(f"mark {paper}, {user} addded")
    else:
        cursor.execute(delete_query, (paper, user))
        print(f"mark {paper}, {user} removed")

    # Commit the changes
    conn.commit()


def update_admins(user, add=True):
    # Connect to the SQLite database
    user = int(user)
    print(f"Update admins DB with {user}")

    # SQL statements with placeholders
    insert_query = """
        INSERT INTO admins (user)
        SELECT ?
        WHERE NOT EXISTS (
            SELECT 1 FROM admins WHERE user = ?
        )
    """
    delete_query = """
                DELETE FROM admins
                WHERE user = ?
            """
    if add:
        cursor.execute(insert_query, (user, user))
        print(f"admin {user} added")
    else:
        cursor.execute(delete_query, (user,))
        print(f"admin {user} removed")

    # Commit the changes
    conn.commit()

def count_mark_conflicts(paper):
    print(f"check DB for mark conflict with {paper}")
    query = """
                    SELECT COUNT(*) 
                    FROM marks 
                    JOIN in_claims on marks.user=in_claims.user 
                    WHERE paper=? AND claim = ?
                """

    cursor.execute(query, (paper, "out"))

    # Fetch the result
    result = cursor.fetchone()

    return result[0]

def remove_suggestions(paper):
    print(f"remove paper '{paper}' from DB")
    delete_query = """
            DELETE FROM suggestions
            WHERE paper = ?
        """
    cursor.execute(delete_query, (paper,))
    conn.commit()

def purge_in_claims():
    print(f"purge in_claims")
    delete_query = """
                DELETE FROM in_claims
                WHERE 1 = 1
            """
    cursor.execute(delete_query, ())
    conn.commit()

def remove_user(user):
    print(f"remove user '{user}' from DB")
    delete_query = """
            DELETE FROM suggestions
            WHERE user = ?
        """
    cursor.execute(delete_query, (user,))
    conn.commit()
    delete_query = """
                DELETE FROM in_claims
                WHERE user = ?
            """
    cursor.execute(delete_query, (user,))
    conn.commit()
    delete_query = """
                    DELETE FROM marks
                    WHERE user = ?
                """
    cursor.execute(delete_query, (user,))
    conn.commit()

def update_in_claims(user, claim):
    #in_claims[str(user)] = claim
    claim = str(claim)
    print("Update in_claims DB")
    # SQL statements with placeholders
    insert_query = """
            INSERT INTO in_claims (user, claim)
            SELECT ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM in_claims WHERE user = ?
            )
        """

    update_query = """
            UPDATE in_claims
            SET claim = ?
            WHERE user = ?
        """

    # Execute the INSERT statement with parameters
    cursor.execute(insert_query, (user, claim, user))

    # Execute the UPDATE statement with parameters
    cursor.execute(update_query, (claim, user))
    conn.commit()


def init(admin_id):
    print("DB created")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS suggestions (
            paper TEXT,
            user INT,
            reaction TEXT
        )
        ''')

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS marks (
                paper TEXT,
                user INT
            )
            ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS in_claims (
        user INT,
        claim TEXT
    )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS info (
            info_key TEXT,
            info_value TEXT
        )
        ''')

    # -- Insert a new row if it doesn't exist
    insert_query = """
                    INSERT INTO info (info_key, info_value)
                    SELECT ?, ?
                    WHERE NOT EXISTS (
                        SELECT 1 FROM info WHERE info_key = ?
                    )
                """

    cursor.execute(insert_query, (UPCOMING_DATE, "N/A", UPCOMING_DATE))
    cursor.execute(insert_query, (NEXT_DATE, "N/A", NEXT_DATE))
    cursor.execute(insert_query, (UPCOMING_PAPER, "N/A", UPCOMING_PAPER))

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            user INT
        )
        ''')

    update_admins(admin_id, add=True)

def get_info(info_key):
    print("getting info from DB")
    with conn:
        print("define DB query")

        query = "SELECT info_value FROM info WHERE info_key = ?"
        cursor.execute(query, (info_key,))
        print("DB check executed")
        [(r,)] = cursor.fetchall()
        return r


def set_info(info_key, info_value):
    insert_query = """
                INSERT INTO info (info_key, info_value)
                SELECT ?, ?
                WHERE NOT EXISTS (
                    SELECT 1 FROM info WHERE info_key = ?
                )
            """

    update_query = """
                UPDATE info
                SET info_value = ?
                WHERE info_key = ?
            """

    # Execute the INSERT statement with parameters
    cursor.execute(insert_query, (info_key, info_value, info_key))

    # Execute the UPDATE statement with parameters
    cursor.execute(update_query, (info_value, info_key))
    conn.commit()


def db_count(paper, reaction, claim):
    query = """
                SELECT COUNT(*) 
                FROM suggestions 
                JOIN in_claims on suggestions.user=in_claims.user 
                WHERE paper=? AND reaction = ? AND claim = ?
            """

    cursor.execute(query, (paper, reaction, claim))

    # Fetch the result
    result = cursor.fetchone()

    return result[0]

def get_papers():
    cursor.execute("SELECT DISTINCT paper FROM suggestions")
    papers = cursor.fetchall()
    print(f"SELECT DISTINCT paper FROM suggestions\n{papers}")
    return papers

