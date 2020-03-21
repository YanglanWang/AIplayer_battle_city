# battle-city

![game home screen](/images/screens/01.png)

forked from
* [softpedia.com](http://linux.softpedia.com/get/GAMES-ENTERTAINMENT/Arcade/BattleCity-Tanks-59571.shtml)
* [code.google.com](https://code.google.com/archive/p/battle-city-tanks/)

## Keys and arguments

### Controls
- Player 1: * movement: up/left/down/right * fire: space
- Player 2: * movement: w/d/s/a * fire: f

### Fullscreen
You can start the game in fullscreen mode by passing the "-f" argument

### Quitting
Pressing the "q" key will quit the game

## Things that are different from original
There are number of differences from original BattleCity.: * Copyright symbol © on intro screen is made up from "(c)". This is because font doesn't support © and I didn't want to put an image instead. * Ice terrain doesn't do anything. it acts like empty space. This is because I don't really know what supposed to happen. Hopefully this will be fixed * The are some missing sounds and I couldn't get that only one sound can be played simultaneously, pausing other and then resuming on finishing. So my BattleCity has only basic sound support, which can be toggled during gameplay with "m" * There is no "Stage X" screen before each stage * Power-ups are dropped randomly. I would even say too randomly, 'cause they are not alyaws accessible (e.g. in the middle of water) * If enemy is spawned during timefreeze, he also should be paused * Brick destruction is different: this game has static big block which is divided into 4 smaller static blocks. Original has smaller blocks whose destruction amount depends on which side bullet came from

## Known bugs
sometimes tanks can get stuck: between some specific terrain or with each other

## System requirements
* Python
* pygame

## Launch
`python tanks.py` from command line
