from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import random

app = Flask(__name__)
socketio = SocketIO(app)

# Configuration for specific player positions
# Format: {position: player_number}
fixed_positions = {
 2: 20,3:21    # On the 14th click of "Next Bid", select player 14
}

available_players = list(range(1, 37))  # 1 to 36
current_player = None
bidding_data = {}
pick_count = 0  # Track the number of players picked

@app.route('/')
def viewer():
    return render_template('viewer.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@socketio.on('next_player')
def handle_next_player():
    global current_player, pick_count
    pick_count += 1  # Increment pick count

    if not available_players:
        emit('no_players_left', broadcast=True)
        return

    # Check if current position has a fixed player
    if pick_count in fixed_positions and fixed_positions[pick_count] in available_players:
        current_player = fixed_positions[pick_count]
    else:
        current_player = random.choice(available_players)

    available_players.remove(current_player)

    emit('start_spin', {
        'number': current_player,
        'image': f"{current_player}.png",
        'name': f"Player {current_player}"  # Optional
    }, broadcast=True)

@socketio.on('team_bid')
def handle_team_bid(data):
    emit('update_bid', data, broadcast=True)

@socketio.on('sold_player')
def handle_sold(data):
    emit('player_sold', data, broadcast=True)

@socketio.on('unsold_player')
def handle_unsold():
    if current_player:
        available_players.append(current_player)
    emit('reset_bid', broadcast=True)

@socketio.on('undo_bid')
def handle_undo():
    emit('restart_bid', broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)