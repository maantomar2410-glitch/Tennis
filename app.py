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
    p1=current_match['player1']
    p2=current_match['player2']
    server_choice = current_match['server']

    if server_choice == 'player1':
        current_match['server'] = current_match['player1']
    elif server_choice == 'player2':
        current_match['server'] = current_match['player2']

    server=current_match['server']

    conn=sqlite3.connect('tennis.db')  
    cursor=conn.cursor()

    def count(shot_type,player):
        cursor.execute("SELECT COUNT(*) FROM shots WHERE shot_type=? AND player=?", (shot_type, player))
        return cursor.fetchone()[0]

    stats={"p1_Aces": count("Ace",p1), "p2_Aces": count("Ace",p2), 'p1_fh_err': count('Forehand_error', p1),
        'p2_fh_err': count('Forehand_error', p2),
        'p1_bh_err': count('Backhand_error', p1),
        'p2_bh_err': count('Backhand_error', p2),
        "p1_serve_in": count("Serve_in",p1),"p1_serve_out": count("Serve_out",p1),
        "p2_serve_in": count("Serve_in",p2),"p2_serve_out": count("Serve_out",p2),}}

    conn.close()
    return render_template('home.html', p1=p1, p2=p2, server=server,stats=stats)
    

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

@app.route('/undo', methods=['POST'])
def undo():
    conn=sqlite3.connect('tennis.db')  
    cursor=conn.cursor()
    cursor.execute("DELETE FROM shots WHERE id = (SELECT MAX(id) FROM shots)")
    conn.commit()
    conn.close()

    return redirect('/track')


if __name__ == '__main__':
    app.run(debug=True)
