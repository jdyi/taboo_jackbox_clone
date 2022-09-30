let socket

function socket_events() {

    socket.on("server_add_player", function(player_name) {

        add_player(player_name)

    });

    socket.on("server_assign_current_player", function(player_name) {

        assign_current_player(player_name)

    });

    socket.on("server_player_has_submitted_answer", function(player_name) {

        make_player_appear_with_background_color(player_name)

    });

    socket.on("server_everybody_has_given_answer", function(msg) {

        console.log("All players have given answers")

        all_answers_given = true

    });

    socket.on("server_add_points_to_scoreboard", function(data) {

        let score_object = JSON.parse(data)

        console.log(score_object)
        
        p_name = score_object["player_name"]
        p_score = score_object["player_score"]

        console.log("Add point after success to scoreboard")

        add_points_to_scoreboard(p_name, p_score)

    });

    socket.on("server_update_prompt_with_vote_options", function(data) {

        console.log("HIER BIN ICHHHHHHHHH")

        let prompt_object = JSON.parse(data)

        console.log("server_update_prompt_with_vote_options", prompt_object)

        current_prompt = prompt_object["prompt_text"]
        current_options = prompt_object["vote_options"]
        vote_countdown = prompt_object["time_to_vote"]
        start_vote_countdown(vote_countdown)
        set_active_screen("server_prompt")


    });

    socket.on("server_update_results", function(data) {

        voting_period_ended = true

        let results_object = JSON.parse(data)

        console.log(results_object)

        update_results(results_object)

        set_active_screen("server_prompt_with_results")


    });

    socket.on("server_show_scoreboard", function(data) {

        let scores_object = JSON.parse(data)

        console.log("server_show_scoreboard ", data)

        console.log("scores_object ", scores_object)

        current_scores = scores_object

        update_scoreboard()

    });

    socket.on("server_show_end_game_scoreboard", function(data) {

        let scores_object = JSON.parse(data)

        console.log("server_show_end_game_scoreboard ", data)

        console.log("scores_object ", scores_object)

        end_game_scores = scores_object

        update_end_game_scoreboard()

    });

    socket.on("server_end_game", function(data) {

        end_game()

    });

    socket.on("set_ready_button_pressed_true", function() {
        
        ready_button_pressed = true

    });

    socket.on("server_switch_player", function() {
        
        start_pre_turn_countdown(15)
        
        // start_prompt_answer_countdown(90)

    });

    socket.on("server_start_prompt_answer_countdown", function() {
        
        // start_pre_turn_countdown(15)
        
        start_prompt_answer_countdown(18)

    });

    socket.on("server_set_player_team", function(data) {
        
        let player_team_object = JSON.parse(data)

        console.log(player_team_object)
        
        p_team = player_team_object["player_team"].toLowerCase()
        p_name = player_team_object["player_name"]

        
        console.log(p_team)
        console.log(p_name)

        set_player_team(p_name, p_team)

    });

    socket.on("server_start_game_succesful", function(state) {

        if (state == 1) {
            // start game
            start_new_game()
        } else {
            // show message not enough players
            console.log("Please have 4 or more players connected")
        }


    });

    socket.on("disconnect", function(msg) {
        set_active_screen("server_start")
        console.log("Disconnected from Server")
    });

    socket.on("server_display_debug_msg", function(msg) {
        console.log("debug msg:", msg)
    });

    socket.on("server_check_each_player_has_team", function() {
        check_each_player_has_team_true()
    });

    socket.on("server_check_correct_number_of_players_on_teams", function() {
        check_correct_number_of_players_on_teams_true()
    });

}

function connect_to_socket(address) {

    socket = io.connect(address);

    socket.emit("server_connect")

    socket_events()

}

function start_game() {

    socket.emit("start_game")


}

function start_vote_loop() {

    socket.emit("start_vote_loop")


}

function switch_to_next_player() {

    socket.emit("switch_to_next_player")


}

function change_player_view_to_words() {

    socket.emit("change_player_view_to_words")


}

async function check_correct_number_of_players_on_teams() {

    socket.emit("check_correct_number_of_players_on_teams")


}

function send_prompts_to_players() {

    socket.emit("send_prompts_to_players")

}

function send_server_start_turn_button(o_id, p_id, p_name) {
    let object_to_send = {
        option_id: o_id,
        prompt_id: p_id,
        player_name: p_name
    }

    console.log(object_to_send)

    socket.emit("player_start_turn_button", JSON.stringify(object_to_send))
}

function restart_game() {

    socket.emit("server_restart_game")

}