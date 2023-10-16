import sqlite3
import os

db_file = 'voteBot/data/voteBot.db'
conn = sqlite3.connect(db_file)
abs_path = os.path.abspath(db_file)
cursor = conn.cursor()

UPCOMING_DATE = "UPCOMING_DATE"
NEXT_DATE = "NEXT_DATE"
UPCOMING_PAPER = "UPCOMING_PAPER"



def get_marking_users(paper):
    with conn:
        query = "SELECT user FROM marks WHERE paper = ?"
        cursor.execute(query, (paper,))
        return cursor.fetchall()

def get_marks_table():
    with conn:
        cursor.execute("SELECT * FROM marks")
        return cursor.fetchall()

def get_admins_table():
    with conn:
        cursor.execute("SELECT * FROM admins")
        return cursor.fetchall()


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


def init(admin_id):
    print("DB created")

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS marks (
                paper TEXT,
                user INT
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




