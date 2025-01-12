import player
import random
import event_emitter as events
import time
import sched
import threading
from random_word import RandomWords
import db
import eventlet

r = RandomWords()
s = sched.scheduler(time.time, time.sleep)
em = events.EventEmitter()

testMode = False


class Game:
    max_players = 8
    prompts_to_play = 0
    main_screen_sid = None
    # player_id start with 1
    connected_players = []
    # prompts start with 0
    prompts = []
    prompt_assignments = []

    answer_counter = 0

    current_player_count = 0

    
    turn_order = []
    current_player = None
    rounds = 3

    prompt_answers = {}

    events_thread = None
    prompt_vote_loop_thread = None
    i_am_listening = False
    waiting_for_user_input = False

    # -1 unstarted, 0 = wait for more player, 1 = wait for player input, 2 = showing prompt, 3 = showing prompt + voting result
    game_state = -1

    def __init__(self):
        self.events_thread = threading.Thread(None, self.events_handler)
        self.events_thread.start()

    def reset(self):
        self.max_players = 8
        self.prompts_to_play = 0

        self.connected_players = []

        self.prompts = []
        self.prompt_assignments = []

        self.answer_counter = 0

        self.prompt_answers = {}

    def start_event_listener(self):
        print("Now listening for internal events")

    def countdown_function(self, seconds):
        countdown = seconds

        while countdown > 0:
            time.sleep(1)
            countdown -= 1
            print(countdown)
        em.emit("start_prompt_vote_loop", "dummy_message")

    def events_handler(self):
        self.i_am_listening = True
        # events

        em.on("player_connect", self.add_connected_player)
        em.on("start_game", self.start_game)
        em.on("debug_msg", self.print_debug)
        em.on("player_answer", self.add_player_answer)
        em.on("player_skip", self.send_new_prompts_to_players_after_skip)
        em.on("player_success", self.send_new_prompts_to_players_after_success)
        em.on("player_vote", self.add_player_vote)
        em.on("change_game_state", self.set_game_state)
        em.on("start_waiting_for_players", self.start_waiting_for_players)
        em.on("start_prompt_vote_loop", self.start_prompt_vote_loop)
        em.on("switch_to_next_player", self.switch_to_next_player)
        em.on("player_team", self.set_player_teams)
        em.on("check_correct_number_of_players_on_teams", self.check_correct_number_of_players_on_teams)
        em.on("send_prompts_to_players", self.send_prompts_to_players)
        em.on("change_screen_to_words_for_players", self.change_screen_to_words_for_players)

        while True:
            if self.waiting_for_user_input == True:
                pass
                # print("i am waiting for user input")

    def start_prompt_vote_loop_thread(self):
        self.prompt_vote_loop_thread = threading.Thread(
            None, self.start_prompt_vote_loop)
        self.prompt_vote_loop_thread.start()

    def get_player_id_from_name(self, name):
        for player in self.connected_players:
            if player.player_name == name:
                return player.player_id

    def get_player_sid_from_name(self, name):
        for player in self.connected_players:
            if player.player_name == name:
                return player.player_sid

    def get_player_from_sid(self, sid):
        for player in self.connected_players:
            if player.player_sid == sid:
                return player

    def change_screen_to_words_for_players(self):
        print("This is player", self.current_player.player_name)
        sid = self.current_player.player_sid
        # send taboo word screen to current player
        em.emit("word_play_screen_to_user", {"recipient": sid})
        em.emit("show_skip_and_success_to_user", {"recipient": sid})
        for word_to_player in self.connected_players:
            # send taboo word screen to players not on same team as current player
            if word_to_player.player_team != self.current_player.player_team:
                em.emit("word_play_screen_to_user", {"recipient": word_to_player.player_sid})
                em.emit("hide_skip_and_success_to_user", {"recipient": word_to_player.player_sid})

            # send guess screen to players on same team as current player
            elif word_to_player.player_team == self.current_player.player_team and word_to_player.player_sid != self.current_player.player_sid:
                em.emit("guess_screen_to_user", {"recipient": word_to_player.player_sid})

    def send_prompts_to_players(self):
        prompt_to_send = self.select_word_to_play()[0]
        print("This is prompt_to_send", prompt_to_send)
        taboo_words = db.get_specific_taboo_words(prompt_to_send)
        print("This is player", self.current_player.player_name)
        sid = self.current_player.player_sid
        # send taboo words to current player
        em.emit("prompt_to_user", {
                "prompt_text": prompt_to_send, "recipient": sid, "prompt_id": 0, "taboo_words": taboo_words})
        for word_to_player in self.connected_players:
            # send taboo words to players not on same team as current player
            if word_to_player.player_team != self.current_player.player_team:
                em.emit("prompt_to_user", {
                        "prompt_text": prompt_to_send, "recipient": word_to_player.player_sid, "prompt_id": 0, "taboo_words": taboo_words})

            # send guess screen to players on same team as current player
            elif word_to_player.player_team == self.current_player.player_team and word_to_player.player_sid != self.current_player.player_sid:
                em.emit("guess_screen_to_user", {"recipient": word_to_player.player_sid})
                

#    def send_prompts_to_players(self):
#        for index, player_id_list in enumerate(self.prompt_assignments):
#            prompt_to_send = self.prompts[index]
#            print("This is prompt_to_send", prompt_to_send)
#            print("This is index", index)
#            taboo_words = db.get_specific_taboo_words(prompt_to_send)
#            for player in player_id_list:
#                print("This is player", player)
#                print("This is connectedplayer indexed", self.connected_players[player-1])
#                sid = self.connected_players[player-1].player_sid
#                em.emit("prompt_to_user", {
#                        "prompt_text": prompt_to_send, "recipient": sid, "prompt_id": index, "taboo_words": taboo_words})

    def send_new_prompts_to_players_after_skip(self):
        prompt_to_send = self.select_word_to_play()[0]
        print("This is prompt_to_send", prompt_to_send)
        taboo_words = db.get_specific_taboo_words(prompt_to_send)
        sid = self.current_player.player_sid
        # send taboo words to current player
        em.emit("new_prompt_to_user", {
                "prompt_text": prompt_to_send, "recipient": sid, "prompt_id": 0, "taboo_words": taboo_words})
        for word_to_player in self.connected_players:
            # send taboo words to players not on same team as current player
            if word_to_player.player_team != self.current_player.player_team:
                em.emit("new_prompt_to_user", {
                        "prompt_text": prompt_to_send, "recipient": word_to_player.player_sid, "prompt_id": 0, "taboo_words": taboo_words})


    def send_new_prompts_to_players_after_success(self):
        prompt_to_send = self.select_word_to_play()[0]
        print("This is prompt_to_send", prompt_to_send)
        taboo_words = db.get_specific_taboo_words(prompt_to_send)
        sid = self.current_player.player_sid
        # add points because success was pressed
        self.update_points_from_sid(sid, 1)
        # send taboo words to current player
        em.emit("new_prompt_to_user", {
                "prompt_text": prompt_to_send, "recipient": sid, "prompt_id": 0, "taboo_words": taboo_words})
        for word_to_player in self.connected_players:
            # send taboo words to players not on same team as current player
            if word_to_player.player_team != self.current_player.player_team:
                em.emit("new_prompt_to_user", {
                        "prompt_text": prompt_to_send, "recipient": word_to_player.player_sid, "prompt_id": 0, "taboo_words": taboo_words})


    def update_points_from_sid(self, sid, amount):
        for uplayer in self.connected_players:
            if uplayer.player_sid == sid:
                uplayer.add_points(amount)
                em.emit("add_points_to_scoreboard", {"player_name": uplayer.player_name, "player_score": uplayer.player_score})

#    def send_new_prompts_to_players_after_skip(self):
#        for index, player_id_list in enumerate(self.prompt_assignments):
#            prompt_to_send = self.prompts[index]
#            print("I am sending new prompt", prompt_to_send)
#            taboo_words = db.get_specific_taboo_words(prompt_to_send)
#            for player in player_id_list:
#                sid = self.connected_players[player-1].player_sid
#                em.emit("prompt_to_user", {
#                        "prompt_text": prompt_to_send, "recipient": sid, "prompt_id": index, "taboo_words": taboo_words})

    def calc_points_for_prompt(self, prompt_id):
      #  print(self.prompts[prompt_id])
       # print(self.prompt_answers[prompt_id][0]["voters"])

        overall_voters_amount = 0

        for answer in self.prompt_answers[prompt_id]:
            # print(answer["voters"])
            overall_voters_amount += len(answer["voters"])

            if (overall_voters_amount == 0):
                overall_voters_amount = 1

       # print(overall_voters_amount)

        for answer in self.prompt_answers[prompt_id]:
            author_id = answer["author"]
            amount_of_votes = len(answer["voters"])

            calc_points = round(
                (amount_of_votes / overall_voters_amount) * 100)

            self.connected_players[author_id-1].add_points(calc_points)
            print(
                self.connected_players[author_id-1].player_name, "gets", calc_points, "points.")

        # self.print_connected_player()

    def get_assigned_prompt_id(self, player_id):

        result_prompt_id = None

        for prompt_id, assignments in enumerate(self.prompt_assignments):
            for players in assignments:
                if (players == player_id):
                    result_prompt_id = prompt_id

        return result_prompt_id

    def set_game_state(self, state_id):
        self.game_state = state_id
        print("Game State: ", self.game_state)

        if (self.game_state == 4):
            print("GAME OVER!")
            self.print_connected_player()
            em.emit("change_game_state", -1)

    def all_players_have_given_answer(self):

        if (self.answer_counter == len(self.connected_players)):
            return True
        else:
            return False

    def add_player_answer(self, answer):
        # answer: player_id, prompt_id, submitted_answer
        # EXAMPLE {"player_id": 1, "prompt_id": 1, "answer": "Creative Answer"
        answer_object = {
            "answer": answer["answer"], "author": answer["player_id"], "voters": [], "points": -1}
        self.prompt_answers[answer["prompt_id"]].append(answer_object)

        em.emit("server_player_has_submitted_answer",
                self.connected_players[answer["player_id"]-1].player_name)

        self.answer_counter += 1

        if (self.all_players_have_given_answer()):
            # working
            em.emit("server_everybody_has_given_answer", "nothing")

        print(self.prompt_answers)

    def add_player_vote(self, vote):
       # {"player_id": 0, "prompt_id": 1, "voted_for": 0}
        print("add_player_vote", vote)
        self.prompt_answers[vote["prompt_id"]][vote["voted_for"]]["voters"].append(
            vote["player_id"])

    def print_debug(self):
        print("debug msg")

    def add_connected_player(self, name, sid):
        # TO DO check if SID is already stored
        print("Adding connected player...")
        if (self.game_state == 0 and (len(self.connected_players) <= (self.max_players-1))):

            # check if name is in use, if yes, attach "_"
            for p in self.connected_players:
                if p.player_name == name:
                    name = name + "_"
                    em.emit("overwrite_player_name", {
                            "new_player_name": name, "sid": sid})

            print("Test1")
            self.connected_players.append(player.Player(name, sid))
            print("Test2")

            # set player id
            self.connected_players[len(
                self.connected_players)-1].player_id = len(self.connected_players)

            # add to main screen
            em.emit("server_add_player", name)

            print("New Player:", name)
            self.print_connected_player()
        else:
            print("No new players are allowed")
            # TO DO send message to players and reset their view

    def print_connected_player(self):
        for p in self.connected_players:
            print(p.player_id, p.player_name, p.player_score, p.player_sid)


#    def assign_players_to_prompts(self):
#
#        p_a = [None] * len(self.prompts)
#        player_index = len(self.connected_players)
#        i = 0
#        while i < len(self.prompts):
#
#            p_list = []
#
#            # clean up
#            p_list.append(player_index)
#            player_index = player_index - 1
#            p_list.append(player_index)
#            player_index = player_index - 1
#
#            if player_index == 1:
#                p_list.append(player_index)
#                player_index = player_index - 1
#
#            p_a[i] = p_list
#            i = i + 1
#
#        self.prompt_assignments = p_a

    def assign_players_to_prompts(self):

        p_a = [None] * len(self.prompts)
        player_index = len(self.connected_players)
        i = 0
        while i < len(self.prompts):

            p_list = []

            # clean up
            p_list.append(player_index)
            player_index = player_index - 1
            p_list.append(player_index)
            player_index = player_index - 1

            if player_index == 1:
                p_list.append(player_index)
                player_index = player_index - 1

            p_a[i] = p_list
            i = i + 1
        
        print(p_a)
        self.prompt_assignments = p_a

    def calc_prompts_amount(self, player_amount):
        if player_amount % 2 == 1:
            player_amount = player_amount - 1

        return int(player_amount / 2)

    def select_prompts(self):
        allPrompts = db.get_prompts_by_usages(4, True)
        random.shuffle(allPrompts)
        return allPrompts[:self.prompts_to_play]

    def select_words(self):
        words = db.get_words(4)
        random.shuffle(words)
        return words[:self.prompts_to_play]
    
    def select_word_to_play(self):
        words = db.get_words_no_limit()
        random.shuffle(words)
        return words[:1]

    def start_waiting_for_players(self):
        # NEW GAME
        em.emit("change_game_state", 0)

        # let the players connect
        if (testMode):
            for n in range(1, random.randint(8, 8)):
                em.emit("player_connect", get_random_name())

        # time.sleep(20)

    def start_countdown(self, seconds):

        countdown_thread = threading.Thread(
            target=self.countdown_function, args=(seconds,))
        countdown_thread.start()

    def start_game(self):
        em.emit("change_game_state", 1)
        
        em.emit("server_show_scoreboard", self.get_scoreboard())

        self.prompts_to_play = self.calc_prompts_amount(
            len(self.connected_players))
        self.prompts = self.select_words()

        # make prompt_answers as big as prompts
        self.prompt_answers = [[]] * len(self.prompts)

        for i in range(0, len(self.prompt_answers)):
            self.prompt_answers[i] = []

        self.get_player_order()

        # get turn order and assign the first player
        self.current_player = self.get_player_from_sid(self.turn_order[self.current_player_count].get("player_sid"))
        em.emit("server_assign_current_player", {"player_name": self.current_player.player_name})
        print("this is the current player ", self.current_player.player_sid)
        print("this is the turn order ", self.turn_order)

        # self.assign_players_to_prompts()

        # send taboo words to users
        self.send_prompts_to_players()

        # wait for XX seconds

        # simulated player answers

        if (testMode):
            for player in self.connected_players:
                for_which_prompt = self.get_assigned_prompt_id(
                    player.player_id)
                em.emit("player_answer", {
                        "player_id": player.player_id, "prompt_id": for_which_prompt, "answer": r.get_random_word()})

        print(self.prompt_answers)

        # self.start_countdown(15)

        # wait for user input
        # self.start_waiting_for_input(1)

        # simulate user input

        # print("los gehts mit prompts")

    def start_turn_loop(self):
        em.emit("change_game_state", 1)

        self.prompts_to_play = self.calc_prompts_amount(
            len(self.connected_players))
        self.prompts = self.select_words()

        # make prompt_answers as big as prompts
        self.prompt_answers = [[]] * len(self.prompts)

        for i in range(0, len(self.prompt_answers)):
            self.prompt_answers[i] = []

        self.assign_players_to_prompts()

        # send taboo words to users
        self.send_prompts_to_players()

        # wait for XX seconds

        # simulated player answers

        if (testMode):
            for player in self.connected_players:
                for_which_prompt = self.get_assigned_prompt_id(
                    player.player_id)
                em.emit("player_answer", {
                        "player_id": player.player_id, "prompt_id": for_which_prompt, "answer": r.get_random_word()})

        print(self.prompt_answers)

    def player_id_to_name(self, player_id):
        return self.connected_players[player_id-1].player_name

    def everybody_voted_for_prompt(self, prompt_id):
        player_amount = len(self.connected_players)
        answers_amount = len(self.prompt_answers[prompt_id])
        votes_amount = 0
        for answer in self.prompt_answers[prompt_id]:
            votes_amount += len(answer["voters"])

        if (votes_amount == (player_amount-answers_amount)):
            return True
        else:
            return False

    def switch_to_next_player(self):
        # if self.current_player_count == len(self.turn_order) - 1:
        if self.current_player_count == len(self.connected_players) - 1:
            em.emit("server_show_end_game_scoreboard", self.get_scoreboard())
            em.emit("end_game")
            print("All turns have been completed. Ending game!")
        else:
            self.current_player_count += 1
            self.current_player = self.get_player_from_sid(self.turn_order[self.current_player_count].get("player_sid"))
            em.emit("server_assign_current_player", {"player_name": self.current_player.player_name})
            for player in self.connected_players:
                if player.player_sid == self.current_player.player_sid:
                    em.emit("server_switch_player", {"sid": player.player_sid})
                else:
                    em.emit("wait_screen_to_user", {"recipient": player.player_sid})

    def start_prompt_vote_loop(self):
        em.emit("change_game_state", 2)

        for prompt_id, prompt in enumerate(self.prompts):
            print("Prompt:", prompt)

            options_list = []
            options_amount = 0
            for answer in self.prompt_answers[prompt_id]:
                print("Option:", answer["answer"])
                options_amount += 1
                options_list.append(answer["answer"])

            players_who_can_vote = []

            for player in self.connected_players:
                if prompt_id == self.get_assigned_prompt_id(player.player_id):
                    pass
                else:
                    players_who_can_vote.append(player.player_sid)

            time_to_vote = 15

            prompt_with_vote_options = {
                "prompt_text": self.prompts[prompt_id],
                "prompt_id": prompt_id,
                "vote_options": options_list,
                "recipients": players_who_can_vote,
                "time_to_vote": time_to_vote
            }

            # check who can vote for this
            em.emit("send_prompt_with_vote_option", prompt_with_vote_options)

            # user votes

            if (testMode):
                for player in self.connected_players:
                    player_id = player.player_id

                    if (prompt_id == self.get_assigned_prompt_id(player_id)):
                        pass
                    else:
                        i_vote_for = random.randint(0, options_amount-1)-1
                        em.emit("player_vote", {
                                "player_id": player_id, "prompt_id": prompt_id, "voted_for": i_vote_for})

            # time.sleep(time_to_vote+1)

            # check for votes given

            vote_countdown = time_to_vote

            while (vote_countdown > 0):
                print(vote_countdown)

                if(self.everybody_voted_for_prompt(prompt_id)):
                    break

                eventlet.sleep(1)
                vote_countdown -= 1

            em.emit("change_game_state", 3)

            self.calc_points_for_prompt(prompt_id)

            print("Prompt:", prompt)

            data_to_display_on_main_screen = {

            }

            data_counter = 0

            for answer in self.prompt_answers[prompt_id]:

                voters_string = ""

                for index, voter_id in enumerate(answer["voters"]):
                    voters_string += self.player_id_to_name(voter_id)
                    if (index+1 == len(answer["voters"])):
                        pass
                    else:
                        voters_string += ", "

                data_to_add = {
                    "answer": answer["answer"],
                    "author": self.player_id_to_name(answer["author"]),
                    "voters": voters_string,
                    # TO DO show added points, not overall
                    "points": self.connected_players[answer["author"]-1].player_score
                }

                data_to_display_on_main_screen[str(data_counter)] = data_to_add
                data_counter += 1

                print("Option:", answer["answer"], "|",
                      "Votes: ", len(answer["voters"]))

            # for display need: author, voters, points
            print(data_to_display_on_main_screen)
            em.emit("server_update_results", data_to_display_on_main_screen)

            # wait 7 seconds, to begin next iteration, to show results on main screen
            eventlet.sleep(7)

            if (prompt_id == len(self.prompts)-1):
                em.emit("change_game_state", 4)
                em.emit("server_show_scoreboard", self.get_scoreboard())
            else:
                em.emit("change_game_state", 2)

    def get_scoreboard(self):
        object_to_build = {}
        for player in self.connected_players:
            object_to_build[player.player_name] = player.player_score

        return object_to_build

    def start_waiting_for_input(self, countdown_time):
        self.waiting_for_user_input = True
        print("cD start")

        # wait xx second
        time.sleep(countdown_time)

        self.waiting_for_user_input = False
        print("cD stop")

    def get_players_on_specific_team(self, team):
        players_on_team = []
        for player in self.connected_players:
            if player.player_team == team:
                players_on_team.append(player)

        return players_on_team

    def get_player_order(self):
        red_team_list = self.get_players_on_specific_team("red")
        blue_team_list = self.get_players_on_specific_team("blue")
        green_team_list = self.get_players_on_specific_team("green")
        yellow_team_list = self.get_players_on_specific_team("yellow")
        cnt=1
        for p in red_team_list:
            self.turn_order.append({"player_sid": p.player_sid, 
                                    "player_name": p.player_name, 
                                    "turn_order": cnt, 
                                    "team":"red"})
            cnt+=1
        cnt=1
        for pb in blue_team_list:
            self.turn_order.append({"player_sid": pb.player_sid, 
                                    "player_name": pb.player_name, 
                                    "turn_order": cnt, 
                                    "team":"blue"})
            cnt+=1
        cnt=1
        for pg in green_team_list:
            self.turn_order.append({"player_sid": pg.player_sid, 
                                    "player_name": pg.player_name, 
                                    "turn_order": cnt, 
                                    "team":"green"})
            cnt+=1
        cnt=1
        for py in yellow_team_list:
            self.turn_order.append({"player_sid": py.player_sid, 
                                    "player_name": py.player_name, 
                                    "turn_order": cnt, 
                                    "team":"yellow"})
            cnt+=1
        cnt=1

        # sort list of players by turn and then team. Example: player 1 red goes first,
        # player blue 1 goes second, player 2 red goes third and player 2 blue goes fourth
        self.turn_order = sorted(self.turn_order, key = lambda player: (player['turn_order'], player['team'])) * self.rounds

        print(self.turn_order)

    def set_player_teams(self, team):
        # {"player_name": 0, "player_team": 1, "voted_for": 0}
        print("set_player_teams", team)
        for player in self.connected_players:
            if player.player_sid == team["player_sid"]:
                player.player_team = team["player_team"]
                em.emit("server_set_player_team", team)

    def check_correct_number_of_players_on_teams(self):
        red_cnt = 0
        blue_cnt = 0
        green_cnt = 0
        yellow_cnt = 0
        print("check_correct_number_of_players_on_teams")
        for player in self.connected_players:
            if player.player_team == "red":
                red_cnt+=1
            elif player.player_team == "blue":
                blue_cnt+=1
            elif player.player_team == "green":
                green_cnt+=1
            elif player.player_team == "yellow":
                yellow_cnt+=1
        if sum([red_cnt, blue_cnt, green_cnt, yellow_cnt]) == len(self.connected_players):
            print("sum boolean has passed")
            em.emit("server_check_each_player_has_team")
        if (red_cnt >= 2 or red_cnt == 0) and (blue_cnt >= 2 or blue_cnt == 0) and (green_cnt >= 2 or green_cnt == 0) and (yellow_cnt >= 2 or yellow_cnt == 0):
            print("cnt booleans have passed")
            em.emit("server_check_correct_number_of_players_on_teams")
        





sampleNames = ["Jene",
               "Chase",
               "Chester",
               "Linda",
               "Amal",
               "Jaqueline",
               "Adaline",
               "Eldridge",
               "Shirley",
               "Ronni",
               "Brendan",
               "Sheba",
               "Arden",
               "Herbert",
               "Lona",
               "Judson",
               "Brandi",
               "Mee",
               "Francine",
               "Joeann"]


def get_random_name():
    return random.choice(sampleNames)


def read_prompts_into_list(filename):
    lineList = [line.rstrip('\n') for line in open(filename)]
    return lineList
    # for l in lineList:
    # print(l)


#tGame = Game()

""" while tGame.i_am_listening == False:
    print("not ready yet")

# add random test players
for n in range(1, random.randint(9, 9)):
    em.emit("player_connect", get_random_name())

tGame.print_connected_player()

def waiting():
    while True:
     if tGame.waiting_for_user_input:
         print("is true")

fakeThread = threading.Thread(None, waiting) """
# fakeThread.start()

# em.emit("start_waiting_for_players")
#em.emit("player_answer", {"player_id": 1, "prompt_id": 1, "answer": "Creative Answer"})
#em.emit("player_vote", {"player_id": 0, "prompt_id": 1, "voted_for": 0})

# add random answers

""" for player in tGame.connected_players:
    for_which_prompt = tGame.get_assigned_prompt_id(player.player_id)
    em.emit("player_answer", {"player_id": player.player_id, "prompt_id": for_which_prompt, "answer": r.get_random_word()})

# print(r.get_random_word())

#print(tGame.get_assigned_prompt_id(4))

#add random vote

for player in tGame.connected_players:
    id_of_my_prompt = for_which_prompt = tGame.get_assigned_prompt_id(player.player_id)

    for index, prompt in enumerate(tGame.prompt_assignments):
        if (index == id_of_my_prompt):
            pass
        else:
            vote_options = len(tGame.prompt_assignments[index])
            i_vote_for = random.randint(0, vote_options-1)-1
            em.emit("player_vote", {"player_id": player.player_id, "prompt_id": index, "voted_for": i_vote_for})


print (tGame.prompt_answers)

for index, prompt in enumerate(tGame.prompts):
    tGame.calc_points_for_prompt(index)

tGame.print_connected_player() """
