from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect('tennis.db')       
    cursor = conn.cursor()                     
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shot_type TEXT NOT NULL,
            player TEXT NOT NULL

        )
    ''')
    conn.commit()                             
    conn.close()                               

init_db()  



current_match = {}

@app.route('/')
def setup():
    return render_template('setup.html')

@app.route('/start', methods=['POST'])
def start():
    current_match['player1'] = request.form['player1']
    current_match['player2'] = request.form['player2']
    current_match['server'] = request.form['server']
    return redirect('/track')

@app.route('/track')
def track():                              
    return render_template('home.html', p1=current_match['player1'], p2=current_match['player2'], server=current_match['server'])
    

@app.route('/log', methods=['POST'])
def log_shot():
    shot = request.form['shot']          
    player = request.form['player']      

    conn = sqlite3.connect('tennis.db')  
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO shots (shot_type, player) VALUES (?, ?)",   
        (shot, player)
    )
    conn.commit()                        
    conn.close()                         

    return redirect('/track')


if __name__ == '__main__':
    app.run(debug=True)
