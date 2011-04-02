import sqlite3
import random
from flask import Flask, render_template, request, redirect, g

app = Flask(__name__)

DATABASE = 'raffle.db'


@app.before_request
def before_request():
    """Connects to the database on each request"""
    g.db = sqlite3.connect(DATABASE)


@app.after_request
def after_request(response):
    """Close the db connection."""
    g.db.close()
    return response


@app.route('/')
def pick_user():
    """Picks a random participant that hasn't yet won a prize."""
    users = g.db.execute("""SELECT participants.id, participants.name
        FROM participants
        LEFT OUTER JOIN winners
        ON winners.participant_id = participants.id
        WHERE winners.participant_id IS NULL""").fetchall()

    user = random.choice(users)
    return render_template('winner.html', id=user[0], name=user[1])


@app.route('/add_winner', methods=('POST',))
def add_winner():
    """Records the prize that a participant won."""
    user_id = int(request.form['user_id'])
    prize = request.form['prize']
    with g.db:
        g.db.execute("""INSERT INTO winners(participant_id, prize_name)
            VALUES (?, ?)""", (user_id, prize))

    username = g.db.execute("""SELECT name
        FROM participants
        WHERE id=?""", (user_id,)).fetchone()

    return render_template('winner_added.html', name=username[0], prize=prize)


@app.route('/winners')
def winners():
    """Lists all raffle winners, and what they won."""
    winners = g.db.execute("""SELECT participants.name, winners.prize_name
        FROM participants
        INNER JOIN winners
        ON participants.id = winners.participant_id""").fetchall()

    return render_template('winners_list.html', winners=winners)


def build_db():
    """Builds the database if necessary."""
    db = sqlite3.connect('raffle.db')
    try:
        db.execute('SELECT 1 FROM participants')
    except sqlite3.OperationalError:
        with db:
            db.execute("""CREATE TABLE participants (
                id INTEGER PRIMARY KEY, name text
            )""")

            db.execute("""CREATE TABLE winners (
                    participant_id INTEGER,
                    prize_name TEXT,
                    FOREIGN KEY(participant_id) REFERENCES participants(id)
                )""")

            with open('data.txt', 'r') as data:
                users = set()
                for line in data.xreadlines():
                    users.add(line.strip())

                for user in users:
                    db.execute("""INSERT INTO participants(name)
                        VALUES (?)""", (user,))

        db.close()


if __name__ == '__main__':
    build_db()
    app.debug = True
    app.run()
