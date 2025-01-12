let socket
let my_ip


function socket_events() {

    socket.on("change_player_view", function(msg) {

        set_active_screen(msg)

    });

    socket.on("change_player_view_new_word", function(msg) {

        change_active_screen(msg)

    });

    socket.on("hide_skip_and_success_to_user", function(msg) {

        hide_skip_and_success()

    });

    socket.on("show_skip_and_success_to_user", function(msg) {

        show_skip_and_success()

    });


    socket.on("update_current_prompt", function(data) {

        let prompt_object = JSON.parse(data)

        current_prompt = prompt_object["prompt_text"]
        current_prompt_id = prompt_object["prompt_id"]
        current_taboo_words = prompt_object["taboo_words"]

    });

    socket.on("update_current_prompt_with_vote_options", function(data) {

        let prompt_object = JSON.parse(data)

        console.log(prompt_object)

        current_prompt = prompt_object["prompt_text"]
        current_prompt_id = prompt_object["prompt_id"]
        current_options = prompt_object["vote_options"]

    });

    socket.on("overwrite_player_name", function(new_name) {

        my_player_name = new_name
        update_displayed_player_name()
        console.log("Overwritten username")
    });

    socket.on("disconnect", function(msg) {
        set_active_screen("player_wait")
        console.log("Disconnected from Server")
    });

    socket.on("player_restart", function(msg) {
        console.log("player_restart")
        reset_values()
        set_active_screen("player_connect")
        console.log("Server has restarted the game, please connect again")
    });

    socket.on("server_display_debug_msg", function(msg) {
        console.log("debug msg:", msg)
    });

}


function connect_to_socket(address, player_name) {
    console.log(player_name, " connecting...")
    socket = io.connect(address);
    socket.on('connect', function() {
        //my_ip = socket.handshake.address.address



        socket.send('User has connected!');
    });

    socket.on("everybody", function(msg) {

        console.log(msg)

    });

    socket_events()

    // dummy ip, ip check for reconnect for the future
    send_player(player_name, "127.0.0.1")

}

function send_player(name, ip) {

    let object_to_send = {
        player_name: name,
        player_ip: ip
    }

    console.log(object_to_send)

    socket.emit("player_connect", JSON.stringify(object_to_send))

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

function send_prompt_answer(answer, p_id, p_name) {

    let object_to_send = {
        prompt_answer: answer,
        prompt_id: p_id,
        player_name: p_name
    }

    console.log(object_to_send)

    socket.emit("prompt_answer", JSON.stringify(object_to_send))
}

function send_player_skip(o_id, p_id, p_name) {
    let object_to_send = {
        option_id: o_id,
        prompt_id: p_id,
        player_name: p_name
    }

    console.log(object_to_send)

    socket.emit("player_skip", JSON.stringify(object_to_send))
}

function send_player_success(o_id, p_id, p_name) {
    let object_to_send = {
        option_id: o_id,
        prompt_id: p_id,
        player_name: p_name
    }

    console.log(object_to_send)

    socket.emit("player_success", JSON.stringify(object_to_send))
}

function send_player_start_turn_button(o_id, p_id, p_name) {
    let object_to_send = {
        option_id: o_id,
        prompt_id: p_id,
        player_name: p_name
    }

    console.log(object_to_send)

    socket.emit("player_start_turn_button", JSON.stringify(object_to_send))
}

function send_player_team_button(p_team, p_name) {
    let object_to_send = {
        player_team: p_team,
        player_name: p_name
    }

    console.log(object_to_send)

    socket.emit("player_team_button", JSON.stringify(object_to_send))
}

function send_player_vote(o_id, p_id, p_name) {
    let object_to_send = {
        option_id: o_id,
        prompt_id: p_id,
        player_name: p_name
    }

    console.log(object_to_send)

    socket.emit("player_vote", JSON.stringify(object_to_send))
}