import sqlite3
import random
from flask import Flask, render_template, request, redirect, g

app = Flask(__name__)

DATABASE = 'raffle.db'

@app.before_request
def before_request():
    g.db = sqlite3.connect(DATABASE)
    
@app.after_request
def after_request(response):
    g.db.close()
    return response

@app.route('/')
def pick_user():
    users = g.db.execute('SELECT id, name FROM participants WHERE id NOT IN (SELECT participant_id FROM winners)').fetchall()
    user = random.choice(users)
    return render_template('winner.html', id=user[0], name=user[1])
    

@app.route('/add_winner', methods=('POST',))
def add_winner():
    user_id = int(request.form['user_id'])
    prize = request.form['prize']
    with g.db:
        g.db.execute("INSERT INTO winners(participant_id, prize_name) values (?, ?)", [user_id, prize])
    
    username = g.db.execute('SELECT name FROM participants WHERE id=?', (user_id,)).fetchone()
    return render_template('winner_added.html', name=username[0], prize=prize)
    
@app.route('/winners')
def winners():
    winners = g.db.execute("SELECT participants.name, winners.prize_name FROM participants INNER JOIN winners ON participants.id = winners.participant_id").fetchall()
    return render_template('winners_list.html', winners=winners)

def build_db():
    DB = sqlite3.connect('raffle.db')
    try:
        DB.execute('SELECT 1 FROM participants')
    except sqlite3.OperationalError:
        with DB:
            DB.execute('CREATE TABLE participants (id INTEGER PRIMARY KEY, name text)')
            DB.execute("""CREATE TABLE winners (
                    participant_id INTEGER, 
                    prize_name TEXT,
                    FOREIGN KEY(participant_id) REFERENCES participants(id)
                )""")
            
            with open('data.txt', 'r') as data:
                users = set()
                for line in data.xreadlines():
                    users.add(line.strip())
                
                for user in users:
                    DB.execute('INSERT INTO participants(name) values (?)', (user,))
        DB.close()
if __name__ == '__main__':
    build_db()
    app.debug = True
    app.run()