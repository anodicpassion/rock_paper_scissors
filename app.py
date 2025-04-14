from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
from collections import defaultdict

app = Flask(__name__)
socketio = SocketIO(app)

# Store game states
players = []
choices = {}
restart_votes = set()
has_game_end = "0"

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def handle_join():
    if len(players) >= 2:
        emit('full', room=request.sid)
        return
    players.append(request.sid)
    join_room("game")
    emit('waiting', broadcast=True)
    if len(players) == 2:
        # emit('start', broadcast=True)
    
        
        emit('start', broadcast=True)
    

@socketio.on('choice')
def handle_choice(data):
    # global score
    choices[request.sid] = data['choice']
    if len(choices) == 2:
        sid1, sid2 = list(choices.keys())
        result = get_result(choices[sid1], choices[sid2])
       
        
        socketio.emit('result', {
            sid1: result[0],
            sid2: result[1],
            'choice1': choices[sid1],
            'choice2': choices[sid2],
            'has_game_end': has_game_end
        }, room="game")
        choices.clear()

@socketio.on("game_end")
def game_end(arg):
    emit('loose', broadcast=True)
    # socketio.emit('loose', room="game")
    

@socketio.on('restart')
def handle_restart():
    restart_votes.add(request.sid)
    if len(restart_votes) == 2:
        restart_votes.clear()
        socketio.emit('start', room="game")

@socketio.on('soft_restart')
def handle_restart():
    restart_votes.add(request.sid)
    if len(restart_votes) == 2:
        restart_votes.clear()
        socketio.emit('soft_start', room="game")

def get_result(choice1, choice2):
    if choice1 == choice2:
        return 'Draw', 'Draw'
    wins = {'rock': 'scissors', 'scissors': 'paper', 'paper': 'rock'}
    if wins[choice1] == choice2:
        return 'Win', 'Lose'
    else:
        return 'Lose', 'Win'

@socketio.on('disconnect')
def handle_disconnect():
    # global score
    score = {}
    if request.sid in players:
        players.remove(request.sid)
    if request.sid in choices:
        choices.pop(request.sid)
    if request.sid in restart_votes:
        restart_votes.remove(request.sid)
    socketio.emit('waiting', room="game")

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5555)