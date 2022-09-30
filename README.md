# taboo-game
A Jackbox-style game of Taboo. Players connect with their phones using the given url and play along with the main screen.

To play:
- change the ip address in player_main.js and server_main.js to your own
- run app.py
- (optional) if you want to play this over the Internet and not in your local network, then you need to forward the port 25565 in your router's settings
- set up the main screen by going to <your_ip>:25565/main_screen (user: admin, password: secret) in your browser
- Every player can connect by going to <your_ip>:25565/play in a browser

4-8 players, 3 rounds only.

Technologies used: Flask with Flask-Socket.IO on Server Side, Vanilla JavaScript on Client side, Python for the app and backend, and SQLite3 for database.
