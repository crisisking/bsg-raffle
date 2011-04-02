import os
import sqlite3
import random
from flask import Flask, render_template, request, redirect

sqlite3.register_adapter

app = Flask(__name__)




@app.route('/')
def pick_user():
    DB = sqlite3.connect('raffle.db')
    results = DB.execute('SELECT id, name FROM participants WHERE id NOT IN (SELECT participant_id FROM winners)')
    users = results.fetchall()
    DB.close()
    user = random.choice(users)
    return render_template('winner.html', id=user[0], name=user[1])
    

@app.route('/add_winner', methods=('POST',))
def add_winner():
    DB = sqlite3.connect('raffle.db')
    user_id = int(request.form['user_id'])
    prize = request.form['prize']
    with DB:
        DB.execute("INSERT INTO winners(participant_id, prize_name) values (?, ?)", [user_id, prize])
        
    DB.close()
    return redirect('/')
    
@app.route('/winners')
def winners():
    DB = sqlite3.connect('raffle.db')
    winners = DB.execute("SELECT participants.name, winners.prize_name FROM participants INNER JOIN winners ON participants.id = winners.participant_id").fetchall()
    response = '<ul><li>'
    response += '<li>'.join([winner[0] + ': ' + winner[1] for winner in winners])
    return response

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