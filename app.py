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
DEUCE=False
TIEBRAKE=False
tie_p1=0
tie_p2=0
p1_gs=0
p2_gs=0
p1_gc=0
p2_gc=0
p1_set=0
p2_set=0
set_history=[]


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

points_won=["Ace", "W_FH", "W_BH", "W_FH_approach", "W_BH_approach",
            "W_FH_volley", "W_BH_volley", "W_overhead", "W_FH_misc", "W_BH_misc",
            "Return_FH_winner", "Return_BH_winner"]

point_neutral = ["Serve_in", "Return_in"] 

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

    def serve_pc(p):
        sin=detailed['Serve_in'][p]+detailed['Ace'][p]
        so=detailed['Serve_fault'][p]+detailed['Double_fault'][p]
        total=sin+so
        return round(sin / total * 100, 1) if total > 0 else 0

    def total_UE(p):
        return sum(detailed[st][p] for st in SHOT_TYPES if st.startswith('UE_'))

    def total_FE(p):
        return sum(detailed[st][p] for st in SHOT_TYPES if st.startswith('FE_'))

    def total_W(p):
        return sum(detailed[st][p] for st in SHOT_TYPES if st.startswith('W_'))

    summary={'p1_Aces': detailed['Ace']['p1'], 'p2_Aces': detailed['Ace']['p2'],
             'p1_Double_Fault': detailed['Double_fault']['p1'], 'p2_Double_Fault': detailed['Double_fault']['p2'],
             'p1_Serve_in': serve_pc('p1'), 'p2_Serve_in': serve_pc('p2'),
             'p1_UE': total_UE('p1'), 'p2_UE': total_UE('p2'),
             'p1_FE': total_FE('p1'), 'p2_FE': total_FE('p2'),
             'p1_W': total_W('p1'), 'p2_W': total_W('p2')}

    return summary, detailed


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

    summary,detailed=get_all_stats(p1, p2)
    player1_score=[p1_set,p1_gc,p1_gs]
    player2_score=[p2_set,p2_gc,p2_gs]


    return render_template('home.html', p1=p1, p2=p2, server=server, stats=summary, p1_score=player1_score, p2_score=player2_score, tie_p1=tie_p1, tie_p2=tie_p2,set_history=set_history)
    

def update_score(shot, player):
    global p1_gs, p2_gs, p1_gc, p2_gc, p1_set, p2_set, DEUCE, TIEBRAKE, tie_p1, tie_p2 

    p1name = current_match['player1']

    if shot in point_neutral:
        return  

    if shot in points_won:
        winner = player
    else:
        winner = current_match['player2'] if player == p1name else p1name

    if TIEBRAKE:
        if winner == p1name:
            tie_p1 += 1
        else:
            tie_p2 += 1

        if tie_p1 >= 7 and tie_p1 - tie_p2 >= 2:
            p1_set += 1
            set_history.append([p1_gc, p2_gc])
            tie_p1 = tie_p2 = 0
            p1_gc = p2_gc = 0
            
            TIEBRAKE = False
        elif tie_p2 >= 7 and tie_p2 - tie_p1 >= 2:
            p2_set += 1
            set_history.append([p1_gc, p2_gc])
            tie_p1 = tie_p2 = 0
            p1_gc = p2_gc = 0
            TIEBRAKE = False
        return      

    if DEUCE:
        if winner == p1name:
            if p1_gs == 4:                # P1 had advantage → win game
                p1_gc += 1
                p1_gs = p2_gs = 0
                DEUCE = False
            elif p2_gs == 4:              # P2 had adv, P1 wins → back to deuce
                p1_gs = p2_gs = 3
            else:                         # from deuce → P1 advantage
                p1_gs = 4
        else:
            if p2_gs == 4:                # P2 had advantage → win game
                p2_gc += 1
                p1_gs = p2_gs = 0
                DEUCE = False
            elif p1_gs == 4:              # P1 had adv, P2 wins → back to deuce
                p1_gs = p2_gs = 3
            else:                         # from deuce → P2 advantage
                p2_gs = 4

    else:
        if winner == p1name:
            if p1_gs == 3 and p2_gs < 3:  # at 40, opponent below → win game
                p1_gc += 1
                p1_gs = p2_gs = 0
            else:
                p1_gs += 1
        else:
            if p2_gs == 3 and p1_gs < 3:
                p2_gc += 1
                p1_gs = p2_gs = 0
            else:
                p2_gs += 1

        if p1_gs == 3 and p2_gs == 3:
            DEUCE = True

    # ===== GAMES → SETS =====
    if p1_gc >= 6 and p1_gc - p2_gc >= 2:
        p1_set += 1
        set_history.append([p1_gc, p2_gc])
        p1_gc = p2_gc = 0
    if p2_gc >= 6 and p2_gc - p1_gc >= 2:
        p2_set += 1
        set_history.append([p1_gc, p2_gc])
        p1_gc = p2_gc = 0

    if p1_gc == 6 and p2_gc == 6:
        TIEBRAKE = True
    return [p1_gs, p2_gs, p1_gc, p2_gc, p1_set, p2_set,tie_p1, tie_p2]


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
    update_score(shot, player)  # Update the score based on the shot and player
    
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
