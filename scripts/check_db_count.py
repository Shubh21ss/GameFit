import sqlite3

db='data/gamefit.db'
conn=sqlite3.connect(db)
cur=conn.cursor()
try:
    cur.execute("SELECT COUNT(*) FROM games")
    n=cur.fetchone()[0]
    print('games_in_db=',n)
except Exception as e:
    print('error',e)
finally:
    conn.close()
