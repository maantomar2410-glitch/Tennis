from flask import Flask, render_template, request, redirect

app = Flask(__name__)


stats = {
    "forehand_errors": 0,
    "backhand_errors": 0,
    "serves_in": 0,
    "serves_out": 0,
    "Aces": 0
}

@app.route('/')
def home():
    total = stats["forehand_errors"] + stats["backhand_errors"]
    winners=stats["Aces"]
    return render_template("home.html", stats=stats, total=total,winners=winners)

@app.route('/log', methods=['POST'])
def log_shot():
    shot = request.form['shot']       
    if shot == 'forehand_error':
        stats["forehand_errors"] += 1
    elif shot == 'backhand_error':
        stats["backhand_errors"] += 1
    elif shot == 'serve_in':
        stats["serves_in"] += 1
    elif shot == 'serve_out':
        stats["serves_out"] += 1
    elif shot=="Aces":
        stats["Aces"] += 1
    return redirect('/')              

if __name__ == '__main__':
    app.run(debug=True)
