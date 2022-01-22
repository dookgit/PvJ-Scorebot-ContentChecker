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

### Setup ###
This guide assume you have got a working Scorebot scoreboard, an access token for the MonitorScript to use, and a game with associated hosts and services.

A server running ScoringEngine (https://github.com/scoringengine/scoringengine) should be deployed. Running the Docker version seemed to run really well, and removes the majority of the dependency checks required.

ScoringEngine takes it's config, and what servers to monitor from a YAML file named competiion.yaml.  If you ever need to update this file (e.g with new servers otr a change to an existing one) just update this file, issue a **make rebuild-new** which will redeploy the docker containers with the new YAML file.
This will also "restart" the game within ScoringEngine, but as we're not using it for the game, and just for something to monitor services, it's not a problem.

In this repo is an example competition.yaml file, which contains a load of servers which have been used in RvBCTF before, and shows the possible service checks that could be used.

For this solution, there are no seperate "teams" defined within ScoringEngine, all servers and servers are defined under the team named "MonitoredServices".  The only way to differentiate between which servers are for which team, is from the FQDN for each host (e.g web01.bt1.rvb.ctf vs web01.bt4.rvb.ctf)

There are heaps of comments in the YAML file, which gives further details on the checks being performed, and ScoringWEngine has some great doco (https://scoringengine.readthedocs.io/)

The MonitorScript.py can be run on the same server as ScoringEngine, and makes sense to run it here too, so the whole server can act as a "Monitoring Server".
It could even be that you could run multiple MonitorServers with the same config, but these servers could be located in different networks (subnets).

So imagine if all the Blue Teams players were on 4 seperate subnets (10.1.10.0/24, 10.1.20.0/24, 10.1.30.0/24 and 10.1.40.0/24).  If you can also deploy a Monitoring Server in this same subnet, then the contect checks would be coming from the same subnet as players.  If an opposing team blocks all traffic from another teams subnet....the Monitoring Server would not be able to check that teams services, and would then mark them as offline. (That sentence didn't make much sense, but....you get the idea.  multiple Monitoring Servers could be deployed, so teams don't know which is a Monitoring Server and what is a legit player)

The MonitorScript.py performs the following actions:

- Connects to Scorebot API .(using it's Access Token)
- Gets a "job" from the Scorebot API.
- Parses the job information, taking out the host FQDN, service (port)  and job ID.
- First it checks that host FQDN and port, to make sure it is listening OK.
- If the port on the host isn't listening, it then responds back to Scorebot API for the job ID, stating that server is in "timeout", (which means off/not listening) (This would then make Scorebot mark the service as Red)
- If the port is open, then it continues on and connects to ScoringEngine, and the JSON output of checked services.
- Parses this JSON to find the matching host FQDN, then find the matching port for that host, an finally gets the status of the service.  Status is basically "Are you responding to how i expect you too" or "Do you have the content on you i expect to see"..
- If the status is not valid (Not the right content) then it then responds back to Scorebot API for the job ID, stating that server is in "invalid". (This would then make Scorebot mark the service as Yellow)
- If the status is good (The correct content we expect) then it then responds back to Scorebot API for the job ID, stating that server is in "pass". (This would then make Scorebot mark the service as Green)
- Then waits for 5 seconds before trying again to get a new job.

If MonitorScript gets a 204 response when connecting to the ScoreBot API, this means there is no job todo, so it waits 5 seconds then tries again.
