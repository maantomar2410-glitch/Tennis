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



@app.route('/start ', methods=['POST'])
def start():
    player1=request.form['player1']
    player2=request.form['player2']





@app.route('/')
def home():
    conn = sqlite3.connect('tennis.db')
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM shots WHERE shot_type = 'forehand_error'")
    forehand_errors = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM shots WHERE shot_type = 'backhand_error'")
    backhand_errors = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM shots WHERE shot_type = 'serve_in'")
    serves_in = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM shots WHERE shot_type = 'serve_out'")
    serves_out = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM shots WHERE shot_type = 'ace'")
    aces = cursor.fetchone()[0]

    conn.close()

    total = forehand_errors + backhand_errors

    return render_template("home.html",
                           fh=forehand_errors,
                           bh=backhand_errors,
                           serves_in=serves_in,
                           serves_out=serves_out,
                           aces=aces,
                           total=total)

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
