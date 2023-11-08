import mysql.connector

dbconfig = mysql.connector.connect(
    host="localhost", user="root", password="", database="db_todo"
)

db = dbconfig.cursor(buffered=True)
table = "todo_item"


def add_todo(title, date_time, created_date):
    q = f"INSERT INTO {table} (title, reminder_date, created_date) VALUES ('{title}', '{date_time}', '{created_date}')"
    print(q)
    db.execute(q)
    print(f"CREATED {title}")

    dbconfig.commit()


def get_all_todo():
    q = f"SELECT * FROM todo_item ORDER BY reminder_date"
    db.execute(q)
    return db.fetchall()


def get_one_todo(id):
    q = f"SELECT * FROM todo_item WHERE id={id}"
    db.execute(q)
    return db.fetchone()


def edit_todo(id, new_title, reminder_date, note):
    q = f"UPDATE {table} SET title = '{new_title}', reminder_date = '{reminder_date}', note = '{note}' WHERE id = {id};"
    db.execute(q)
    dbconfig.commit()
    print(f"EDITED id {id} to {new_title}")


def delete_todo(id):
    q = f"DELETE FROM {table} WHERE id={id};"
    print(q)
    db.execute(q)
    dbconfig.commit()
    print(f"DELETED id {id}")


# The DATETIME type is used for values that contain both date and time parts.
# MySQL retrieves and displays DATETIME values in 'YYYY-MM-DD hh:mm:ss' format.
# The supported range is '1000-01-01 00:00:00' to '9999-12-31 23:59:59'.
