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

SHOT_TYPES = [
    'Ace', 'Serve_in', 'Serve_fault', 'Double_fault',
    'UE_FH', 'UE_BH', 'UE_FH_approach', 'UE_BH_approach',
    'UE_FH_volley', 'UE_BH_volley', 'UE_overhead', 'UE_FH_misc', 'UE_BH_misc',
    'FE_FH', 'FE_BH', 'FE_FH_approach', 'FE_BH_approach',
    'FE_FH_volley', 'FE_BH_volley', 'FE_overhead', 'FE_FH_misc', 'FE_BH_misc',
    'W_FH', 'W_BH', 'W_FH_approach', 'W_BH_approach',
    'W_FH_volley', 'W_BH_volley', 'W_overhead', 'W_FH_misc', 'W_BH_misc',
    'Return_FH_winner', 'Return_BH_winner', 'Return_FH_error', 'Return_BH_error',
]

def get_all_stats(p1, p2):
    conn = sqlite3.connect('tennis.db')
    cursor = conn.cursor()

    def count_exact(shot_type, player):
        cursor.execute("SELECT COUNT(*) FROM shots WHERE shot_type = ? AND player = ?",
                       (shot_type, player))
        return cursor.fetchone()[0]

    
    detailed = {}
    for st in SHOT_TYPES:
        detailed[st] = {'p1': count_exact(st, p1), 'p2': count_exact(st, p2)}

    conn.close()
    return detailed

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

    stats=get_all_stats(p1, p2)

    return render_template('home.html', p1=p1, p2=p2, server=server, stats=stats)
    

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

@app.route('/report')
def report():
    stats=get_all_stats(current_match['player1'], current_match['player2'])
    p1=current_match['player1']
    p2=current_match['player2']
    server=current_match['server']

    return render_template('report.html', p1=p1, p2=p2, server=server, stats=stats)

if __name__ == '__main__':
    app.run(debug=True)
