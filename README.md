# SPACE RACE

A game made in  PyGame for ISS 2020

<img src="./Misc/SpaceRace.gif" width="300px" />

Here are the specifications of the game:
 
 1) There are two players in the game, starting at opposite ends of the screen
 2) The game arena has several partitions made by some **Dock Sites**
 3) The player is safe when he is on one of these **Dock Sites**
 4) There are two type of obstacles:
    - Static Obstacles (**Black Holes**)
    - Moving Obstacles (**Asteroids**)
 5) Player gets 5 points on crossing a Static obstacle and 10 points for a
    Moving Obstacle
 6)  Each player has his own set of movement buttons, i.e:
     - **Arrow** keys for Player 1
     - **WASD** keys for Player 2
 7) The speed of the moving obstacles for each player is a function of which
    level they are currently on
 8) Each player's score is calculated based on the number of obstacles they
    have crossed and they get a special time based score bonus on completing a
    round.
 9) Finally, the player who completes the three levels of the game in the
    fewest turns is the winner. If the number of turns taken happen to be
    equal, then the players' scores are compared as a method of breaking the
    tie.
 10) Game configuration data is stored in `game_config.cnf`. Due to
     modularity of the code, features of the game like number of levels, player
     speed, game speed, etc. can easily be modified by changing its value in
     the configuration file
 
##### That's all for the Readme. Now go on and enjoy the game!
