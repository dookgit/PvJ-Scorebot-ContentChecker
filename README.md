# PvJ-Scorebot-ContentChecker
A service content checker solution for use with PvJ Scorebot

### Overview ###
ProsVJoes is an AWESOME CTF, where teams have to kick out an embedded Red Team out of their servers, as well as defend againest other Blue Teams AND attack those same Blue Teams.
The heart of PvJCTF is the scoreboard AKA Scorebot (https://github.com/iDigitalFlame/scorebot-core/tree/v3) this helps in showing what servers teams have, what services need to be kept running, any "beacons/flares" that are sent from the Red Team or opposing Blue Teams and also importantly keep the game score going.  No scores...no game.

The same scoreboard is used in the RvBCTF (https://rvbctf.com) which i run from time to time.

### Problem ###
In my testing the Scorebot "health and wellbeing" checker has a few issues, and i could never get it fully working.
It's meant to talk to the Scorebot API to get a "job" which is basically, go check web01 server for blue team 3 on port 80, and make sure it's listening, and has the content we expect.

The health and wellbeing definately checks to see if the ports are open or not, but i could never get it to perform the "content" checks successfully.

### My solution ###
After looking around i came across a similar CTF scoreboard called ScoringEngine (https://github.com/scoringengine/scoringengine) this doesn't have the same "gamification" as Scorebot in my opinion, and it also lacks the "beacons/flares" which is one of the best parts of PvJ.  But, it's service content checker is AWESOME! and is very modular, so new checks for new services could be created and added.
It also can output the results of these checks in JSON format, which makes it great to be parsed by script.

The attached script (MonitorScript.py) connects the 2 systems together, so it can get a job from Scorebot, then check the corresponding host and port for that job, againest the same one being monitored by ScoringEngine, and return the result.

### Prep ###
This guide assume you have got a working Scorebot scoreboard, an access token for the MonitorScript to use, and a game with associated hosts and services.
