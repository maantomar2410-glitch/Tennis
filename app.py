from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect('tennis.db')       
    cursor = conn.cursor()                     
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shot_type TEXT NOT NULL)
    ''')
    conn.commit()                             
    conn.close()                               

init_db()   

stats = {
    "forehand_errors": 0,
    "backhand_errors": 0,
    "serves_in": 0,
    "serves_out": 0,
    "aces": 0
}

@app.route('/')
def home():
    total = stats["forehand_errors"] + stats["backhand_errors"]
    return render_template("home.html", stats=stats, total=total , aces=stats["aces"])


@app.route('/log', methods=['POST'])
def log_shot():
    shot = request.form['shot']         

    conn = sqlite3.connect('tennis.db')  
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO shots (shot_type) VALUES (?)",   
        (shot,)
    )
    conn.commit()                        
    conn.close()                         

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
