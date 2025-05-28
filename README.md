## Amethyx - A game that runs in terminal for bored developers

Simply clone the repo and run play.py

The game will then start executing.
The goal is simple: 
 - coordinate the rover "[R]" to the sample "[S]" and drop the sample off at the base "[B]"

 You do this by writing code. The language is super simple:

 There is a catch though, memory onboard and bandwith in space is limited.
 
 Each character in your code is 8 bytes. 
 Before your code executes it will check its size and if it's too large, you'll have to re-write it more efficiently.

The rover also has a battery which you need to maintain. 
Each isntruction drains the battery by 2% so it is crucial to be efficient, and incldue some charging stations on the way. 


```
mvn # move noth
mve # move east
mvw # move west
mvs # move south
clt # collect sample
drp # drop sample
obs # observe current terrain
```

The game can also execute a for loop, which looks like this:
```
for 4 >> mve # it will execute four eastward movement
```
You can also combine steps in a for loop like this:
```
for 4 >> mve, mvw # it will go east, west and repeat 3 more times.
```
If statements are also possible, which may look like this:
```
if mve == # then mvs else mve
```
This way, if the move to east runs into a wall [#], it will go south. If safe, it will simply execute to east.

# The general blocks in the game:

### [X] - Standard terrain
### [R] - Rover
### [S] - Sample drilling area
### [B] - Starbase. Sample needs to be returned here and the rover before the next mission
### [?] - Unmapped territory, can result in some battery boost or battery drain when unlucky
### [@] - Fast charging station
##### more to come with further updates.

The game is early development mode, and only includes two maps in maps.py
You can freely add more custom maps, and the game will automatically increment as you play.

Enjoy

