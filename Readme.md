# battle-city auto test

![game home screen](/images/screens/01.png)

forked from
* [softpedia.com](http://linux.softpedia.com/get/GAMES-ENTERTAINMENT/Arcade/BattleCity-Tanks-59571.shtml)
* [code.google.com](https://code.google.com/archive/p/battle-city-tanks/)

This is the auto test script in playing with battle-city. The original game script is forked from https://github.com/shinima/battle-city.git.
From the convenience of editing in original game script--tanks.py, my test didn't change this file by using threading.
## Keys and arguments

### Controls in original game
- Player 1: * movement: up/left/down/right * fire: space
- Player 2: * movement: w/d/s/a * fire: f

- Press "-f" to start the game in fullscreen mode
- Press the "q" key will quit the game
![gorithm charflow](https://www.lucidchart.com/invitations/accept/c0209e27-c222-4841-a673-831b8313cc2b)
## Algorithm

- One player mode:



- Two players mode


## Known bugs
sometimes tanks can get stuck: between some specific terrain or with each other

## System requirements
* Python 2.7
* pygame
* math
* heapq
* os
* logging
* threading
* time
* TKinter

## Launch
`python ui.py` from command line, in AI-battle-city ui, choose stage and number of players, and then enter play.
