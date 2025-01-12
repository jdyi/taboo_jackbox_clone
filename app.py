from flask import Flask, request
from flask import render_template
from flask_socketio import SocketIO, emit
import json
import game
from flask_simplelogin import SimpleLogin, login_required


app = Flask(__name__)
SimpleLogin(app)
app.config['SECRET_KEY'] = '8f4eed1c-43fa-40c9-a979-af5f4757cc86'
socketio = SocketIO(app, async_mode="eventlet", async_handlers=True)
ga = game.Game()

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


def send_prompt_to_user(data):
    emit("update_current_prompt", json.dumps(data), room=data["recipient"])
    # socketio.sleep(0)

def send_new_prompt_to_user(data):
    emit("update_current_prompt", json.dumps(data), room=data["recipient"])
    emit("change_player_view_new_word", "player_prompt_answer", room=data["recipient"])
    # socketio.sleep(0)

def send_word_to_user(data):
    emit("update_current_word", json.dumps(data), room=data["recipient"])
    # socketio.sleep(0)

def send_wait_screen_to_user(data):
    emit("change_player_view", "player_wait", room=data["recipient"])
    # socketio.sleep(0)

def send_guess_screen_to_user(data):
    emit("change_player_view", "player_guess", room=data["recipient"])
    # socketio.sleep(0)

def send_word_play_screen_to_user(data):
    emit("change_player_view", "player_prompt_answer", room=data["recipient"])
    # socketio.sleep(0)

def thread_handling():
    while False:
        socketio.sleep(0)
        socketio.emit("server_display_debug_msg", "ping pong", broadcast=True)
        socketio.sleep(0)
        #print("calling")
    
    


def send_prompt_with_vote_options(data):

    print(ga.main_screen_sid, "send_prompt_with_vote_options", json.dumps(data))

    # eventlet.sleep(0)
    
    emit("server_display_debug_msg", "Ich bin eine Nachricht", room=ga.main_screen_sid)
    # socketio.sleep(0)
    # eventlet.sleep(0)

    emit("server_update_prompt_with_vote_options", json.dumps(data), room=ga.main_screen_sid)
    # socketio.sleep(0)
    # eventlet.sleep(0)

    recipients = data["recipients"]

    for sid in recipients:
        # eventlet.sleep(0)
        emit("update_current_prompt_with_vote_options",
             json.dumps(data), room=sid)
        socketio.sleep(0)
        # eventlet.sleep(0)
        emit("change_player_view", "player_vote_prompt", room=sid)
        socketio.sleep(0)
        #ventlet.sleep(0)


def overwrite_player_name(data):
    print(data)
    sid = data["sid"]
    # eventlet.sleep(0)
    emit("overwrite_player_name", data["new_player_name"], room=sid)
    # socketio.sleep(0)


def server_add_player(name):
    print(name, ga.main_screen_sid, "WHAAAAAAAAAAAAAAAAAAAH")
    # eventlet.sleep(0)
    emit("server_add_player", name, room=ga.main_screen_sid)
    # socketio.sleep(0)


def server_player_has_submitted_answer(name):
    # eventlet.sleep(0)
    
    emit("server_player_has_submitted_answer", name, room=ga.main_screen_sid)
    # socketio.sleep(0)


def server_everybody_has_given_answer(msg):
    # print("EVERYBODDDDYYYY")
    # eventlet.sleep(0)
    
    emit("server_everybody_has_given_answer",
         "nothing", room=ga.main_screen_sid)
    # socketio.sleep(0)
    # eventlet.sleep(0)


def server_update_results(data):
    # eventlet.sleep(0)
    emit("server_update_results", json.dumps(data), room=ga.main_screen_sid)
    # socketio.sleep(0)
    # eventlet.sleep(0)


def server_show_scoreboard(data):
    print(data)
    print(json.dumps(data))
    # eventlet.sleep(0)
    emit("server_show_scoreboard", json.dumps(data), room=ga.main_screen_sid)
    # socketio.sleep(0)
    # eventlet.sleep(0)


def server_show_end_game_scoreboard(data):
    print(data)
    print(json.dumps(data))
    # eventlet.sleep(0)
    emit("server_show_end_game_scoreboard", json.dumps(data), room=ga.main_screen_sid)
    # socketio.sleep(0)
    # eventlet.sleep(0)


def server_switch_player(data):
    # eventlet.sleep(0)
    sid = data["sid"]
    emit("server_switch_player", room=ga.main_screen_sid)
    # socketio.sleep(0)
    emit("change_player_view", "player_pre_turn", room=sid)
    # eventlet.sleep(0)


def server_set_player_team(data):
    # eventlet.sleep(0)
    emit("server_set_player_team", json.dumps(data), room=ga.main_screen_sid)
    # socketio.sleep(0)
    # eventlet.sleep(0)


def server_check_each_player_has_team():
    # eventlet.sleep(0)
    emit("server_check_each_player_has_team", room=ga.main_screen_sid)
    # socketio.sleep(0)
    # eventlet.sleep(0)


def server_check_correct_number_of_players_on_teams():
    # eventlet.sleep(0)
    emit("server_check_correct_number_of_players_on_teams", room=ga.main_screen_sid)
    # socketio.sleep(0)
    # eventlet.sleep(0)


def send_server_assign_current_player(data):
    # eventlet.sleep(0)
    emit("server_assign_current_player", data["player_name"], room=ga.main_screen_sid)
    # socketio.sleep(0)
    # eventlet.sleep(0)


def send_hide_skip_and_success_to_user(data):
    # eventlet.sleep(0)
    sid = data["recipient"]
    emit("hide_skip_and_success_to_user", room=sid)
    # socketio.sleep(0)
    # eventlet.sleep(0)


def send_show_skip_and_success_to_user(data):
    # eventlet.sleep(0)
    sid = data["recipient"]
    emit("show_skip_and_success_to_user", room=sid)
    # socketio.sleep(0)
    # eventlet.sleep(0)


def send_add_points_to_scoreboard(data):
    # eventlet.sleep(0)
    emit("server_add_points_to_scoreboard", json.dumps(data), room=ga.main_screen_sid)
    # socketio.sleep(0)
    # eventlet.sleep(0)


def end_game():
    # eventlet.sleep(0)
    emit("server_end_game", room=ga.main_screen_sid)
    # socketio.sleep(0)
    emit("change_player_view", "player_wait", broadcast=True)
    # eventlet.sleep(0)



game.em.on("prompt_to_user", send_prompt_to_user)
game.em.on("new_prompt_to_user", send_new_prompt_to_user)
game.em.on("word_to_user", send_word_to_user)
game.em.on("send_prompt_with_vote_option", send_prompt_with_vote_options)
game.em.on("overwrite_player_name", overwrite_player_name)
game.em.on("server_add_player", server_add_player)
game.em.on("server_player_has_submitted_answer",
           server_player_has_submitted_answer)
game.em.on("server_everybody_has_given_answer",
           server_everybody_has_given_answer)
game.em.on("server_update_results", server_update_results)
game.em.on("server_show_scoreboard", server_show_scoreboard)
game.em.on("server_show_end_game_scoreboard", server_show_end_game_scoreboard)
game.em.on("server_switch_player", server_switch_player)
game.em.on("server_set_player_team", server_set_player_team)
game.em.on("server_check_each_player_has_team", server_check_each_player_has_team)
game.em.on("server_check_correct_number_of_players_on_teams", server_check_correct_number_of_players_on_teams)
game.em.on("wait_screen_to_user", send_wait_screen_to_user)
game.em.on("guess_screen_to_user", send_guess_screen_to_user)
game.em.on("word_play_screen_to_user", send_word_play_screen_to_user)
game.em.on("server_assign_current_player", send_server_assign_current_player)
game.em.on("hide_skip_and_success_to_user", send_hide_skip_and_success_to_user)
game.em.on("show_skip_and_success_to_user", send_show_skip_and_success_to_user)
game.em.on("add_points_to_scoreboard", send_add_points_to_scoreboard)
game.em.on("end_game", end_game)


@socketio.on("player_connect")
def handle_player_connect(json_string):
    # eventlet.sleep(0)
    print("Connecting a player...")

    data = json.loads(json_string)
    print(data["player_name"])
    game.em.emit("player_connect", data["player_name"], request.sid)
    # eventlet.sleep(0)
    print(data["player_name"], "connected successfully in app.py")


@socketio.on("start_game")
def handle_game_start():
    
    if (len(ga.connected_players) > 0):
        # eventlet.sleep(0)
        emit("server_start_game_succesful", 1, room=ga.main_screen_sid)
        # socketio.sleep(0)
        # eventlet.sleep(0)
        game.em.emit("start_game")
        #emit("everybody", "Nachricht an alle",broadcast=True)
        # eventlet.sleep(0)
        # emit("change_player_view", "player_prompt_answer", broadcast=True)
        game.em.emit("change_screen_to_words_for_players")
        # socketio.sleep(0)
        # eventlet.sleep(0)
    else:
        # eventlet.sleep(0)
        emit("server_start_game_succesful", 0, room=ga.main_screen_sid)
        # socketio.sleep(0)
        # eventlet.sleep(0)


@socketio.on("start_vote_loop")
def handle_start_of_vote_loop():
    # eventlet.sleep(0)
    game.em.emit("start_prompt_vote_loop")
    # eventlet.sleep(0)


@socketio.on("switch_to_next_player")
def handle_switch_to_next_player():
    # eventlet.sleep(0)
    game.em.emit("switch_to_next_player")
    # eventlet.sleep(0)


@socketio.on("check_correct_number_of_players_on_teams")
def handle_check_correct_number_of_players_on_teams():
    # eventlet.sleep(0)
    game.em.emit("check_correct_number_of_players_on_teams")
    # eventlet.sleep(0)


@socketio.on("change_player_view_to_words")
def handle_change_player_view_to_words():
    # eventlet.sleep(0)
    # emit("change_player_view", "player_prompt_answer", broadcast=True)
    game.em.emit("change_screen_to_words_for_players")
    game.em.emit("player_skip")
    # eventlet.sleep(0)


@socketio.on("prompt_answer")
def handle_prompt_answer(data):
    #{'prompt_answer': 'sdfdsfsfd', 'prompt_id': 0, 'player_name': 'b'}
    prompt_data = json.loads(data)
    # eventlet.sleep(0)
    data_for_function = {"player_id": ga.get_player_id_from_name(prompt_data["player_name"]),
                         "prompt_id": prompt_data["prompt_id"],
                         "answer": prompt_data["prompt_answer"]}

    # eventlet.sleep(0)


@socketio.on("player_vote")
def handle_player_vote(data):
     # {"player_id": 0, "prompt_id": 1, "voted_for": 0}
    # eventlet.sleep(0)
    vote_data = json.loads(data)

    data_for_function = {"player_id": ga.get_player_id_from_name(vote_data["player_name"]),
                         "prompt_id": vote_data["prompt_id"],
                         "voted_for": vote_data["option_id"]}
    print("player_vote", data_for_function)
    # eventlet.sleep(0)
    game.em.emit("player_vote", data_for_function)
    # eventlet.sleep(0)

@socketio.on("player_skip")
def handle_player_skip(data):
     # {"player_id": 0, "prompt_id": 1, "voted_for": 0}
    # eventlet.sleep(0)
    skip_data = json.loads(data)

    data_for_function = {"player_id": ga.get_player_id_from_name(skip_data["player_name"]),
                         "prompt_id": skip_data["prompt_id"],
                         "voted_for": skip_data["option_id"]}
    print("player_skip", data_for_function)
    # eventlet.sleep(0)
    # game.em.emit("player_skip", data_for_function)
    game.em.emit("player_skip")
    # eventlet.sleep(0)

@socketio.on("player_success")
def handle_player_success(data):
     # {"player_id": 0, "prompt_id": 1, "voted_for": 0}
    # eventlet.sleep(0)
    success_data = json.loads(data)

    data_for_function = {"player_id": ga.get_player_id_from_name(success_data["player_name"]),
                         "prompt_id": success_data["prompt_id"],
                         "voted_for": success_data["option_id"]}
    print("player_success", data_for_function)
    # eventlet.sleep(0)
    game.em.emit("player_success")
    # eventlet.sleep(0)


@socketio.on("player_start_turn_button")
def handle_player_start_turn_button(data):
     # {"player_id": 0, "prompt_id": 1, "voted_for": 0}
    # eventlet.sleep(0)
    skip_data = json.loads(data)

    data_for_function = {"player_id": ga.get_player_id_from_name(skip_data["player_name"]),
                         "prompt_id": skip_data["prompt_id"],
                         "voted_for": skip_data["option_id"]}
    print("player_skip", data_for_function)
    # eventlet.sleep(0)
    game.em.emit("change_screen_to_words_for_players")
    game.em.emit("player_skip")
    # game.em.emit("player_skip", data_for_function)
    emit("set_ready_button_pressed_true", room=ga.main_screen_sid)
    # eventlet.sleep(0)


@socketio.on("send_prompts_to_players")
def handle_send_prompts_to_players():
    # eventlet.sleep(0)
    game.em.emit("send_prompts_to_players")
    # game.em.emit("player_skip", data_for_function)
    # eventlet.sleep(0)


@socketio.on("player_team_button")
def handle_player_team_button(data):
     # {"player_id": 0, "prompt_id": 1, "voted_for": 0}
    # eventlet.sleep(0)
    team_data = json.loads(data)

    data_for_function = {"player_sid": ga.get_player_sid_from_name(team_data["player_name"]),
                         "player_name": team_data["player_name"],
                         "player_team": team_data["player_team"]}
    print("player team", data_for_function)
    # eventlet.sleep(0)
    game.em.emit("player_team", data_for_function)
    # eventlet.sleep(0)


@socketio.on("server_connect")
def handle_server_connect():
    # eventlet.sleep(0)
    socketio.start_background_task(target=thread_handling)
    game.em.emit("start_waiting_for_players")

    ga.main_screen_sid = request.sid

    print("Main Screen has connected",
          ga.main_screen_sid, "WHAAAAAAAAAAAAAAAAAAAAAH")
    # eventlet.sleep(0)


@socketio.on("server_restart_game")
def handle_server_game_restart():
    # eventlet.sleep(0)
    print("Restart pressed")
    ga.reset()
    game.em.emit("start_waiting_for_players")
    emit("player_restart", "nothing", broadcast=True)
    # socketio.sleep(0)
    # eventlet.sleep(0)


@app.route("/play/")
def player_view():
    return render_template("player.html")


@app.route("/main_screen")
@login_required(username="admin")
def main_screen_view():
    return render_template("server.html")


if __name__ == '__main__':
    # socketio.run(app, host="0.0.0.0", port=25565) # external
    socketio.run(app, host="127.0.0.1", port=25565) # local
