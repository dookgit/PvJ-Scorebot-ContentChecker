# dooks Janky AF python script for connecting Scorebot to ScoringEngine
# Check https://github.com/dookgit/PvJ-Scorebot-ContentChecker/ for updates

# Version 3 - Initial release (After using in RvBCTF)

# Import the required modules.
from typing import final
import requests, json, socket, logging, time
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Server IP's
scoreboardaddress = "http://10.10.10.10:4000/api/job"
monitoraddress = "https://10.x.x.x/api/overview/data"
# Logging configuration
logging.basicConfig(filename="MonitorScript.log", level=logging.INFO)

def main():
    # Send a GET request to the scoreboard to get a job.
    scoreboard_request = requests.get(scoreboardaddress, headers={'SBE-AUTH' : '354787eb-0b6e-4a38-8db5-d8ac753cfdca'})
    # If status code is 204, then ignore.
    if (scoreboard_request.status_code) == 204:
        logging.info(" **********************************")
        logging.info(" Status 204 - No hosts available (No jobs todo)")
        # Sleep for 5 secs, then restart
        time.sleep(5)
    # Else if status code is 201, continue on.
    elif (scoreboard_request.status_code) == 201:
        serviceresponse = ""
        fullresponsetosend = ""
        # Added by dook 21/12/2021
        sendresult = ""
        servicenum = 0
        logging.info(" **********************************")
        # Convert the request response into JSON format, from byte format.
        json_request = json.loads(scoreboard_request.content)
        # Sets the "fqdn" value from the response into a variable.
        hosttocheck_fqdn = json_request['host']['fqdn']
        # Strips out the "services" section from the response.
        services = json_request['host']['services']
        numofservicestocheck = len(services)
        hosttocheck_job_id = json_request['id']
        logging.info(" Status 201 - Got a job! - " + str(hosttocheck_job_id) + ".")
        for servicetocheck in services:
            servicenum += 1
            # Sets the "port" value from the response into a variable.
            hosttocheck_port = servicetocheck['port']
            # Sets the "id"(job id) value from the response into a variable.
            logging.info(" " + str(hosttocheck_job_id) + " - Checking " + str(hosttocheck_fqdn) + " on port " + str(hosttocheck_port) + ".")
            # Create a socket connection.
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Set a socket timeout (reduces issues).
            sock.settimeout(2)
            # Make a connection to the host on the port.
            result = sock.connect_ex((hosttocheck_fqdn,hosttocheck_port))
            # If the port is open, then continue on.
            if result == 0:
                # Send a GET request to the infra monitor to get all the service statuses(They all get returned).
                monitor_request = requests.get(monitoraddress, verify=False)
                # Convert the request response into JSON format, from string format.
                monitor_json_request = json.loads(monitor_request.content)
                # Stripe out the first value, which in testing was "TestTeam1".
                minus_testteam1 = monitor_json_request['MonitoredServices']
                # Start a for loop, for each check returned.
                for key in minus_testteam1:
                    # Extract the specific check details.
                    specific_check = minus_testteam1[key]
                    # Start a for loop for the specific check, to extract each item.
                    for key, value in specific_check.items():
                        # If the key is "host" then set the value into a variable.
                        if key == "host":
                            host = value
                        # If the key is "port" then set the value into a variable.
                        elif key == "port":
                            port = value
                        # If the key is "passing" then set the value into a variable.
                        elif key == "passing":
                            servicestatus = value
                    # If the value of host matches the host we are checking, start this if statement.
                    if host == hosttocheck_fqdn:
                        # If the value of port matches the port we are checking, start this if statement.
                        # Doing these 2 if statements, ensures we are just working with the host in question.
                        if port == hosttocheck_port:
                            # If the value of servicestatus is False, then set the variable to be "invalid".
                            # "invalid" means the service is working, but the it's not getting the content it i expecting.
                            if servicestatus == False:
                                sendresult = "invalid"
                                logging.info(" " + str(hosttocheck_job_id) + " Port is open, but content does not match.")
                            # If the value of servicestatus if True, then set the variable to be "pass".
                            # "pass" means the servcice is working, and the it does get the content it is expecting.
                            elif servicestatus == True:
                                sendresult = "pass"
                                logging.info(" " + str(hosttocheck_job_id) + " Port is open, and content matches.")
            # Else if the port is closed, set the value of sendresult to "timeout" and servicestatus to nothing (Not needed, but needs to be set)
            else:
                sendresult = "timeout"
                servicestatus = ""
                logging.info(" " + str(hosttocheck_job_id) + " Port is closed.")
            #dookupdate
            serviceresponse = '{"status": "' + str(sendresult) + '", "application": "http", "content": null, "protocol": "tcp", "port": ' + str(hosttocheck_port) + '}'
            fullresponsetosend+=serviceresponse
            if servicenum != len(services):
                seperator = ", "
                fullresponsetosend+=seperator
        starter = ('{"host": {"services": [')
        ender = ('], "ping_sent": 5, "ping_respond": 5}, "id": ' + str (hosttocheck_job_id) + '}')
        finalresponse = ""
        finalresponse+=starter
        finalresponse+=fullresponsetosend
        finalresponse+=ender
        finalresponse_json = json.loads(finalresponse)
        # Convert the request response into JSON format, from string format.
        # Send the response to the job as a POST request to the scoreboard.
        logging.info(" " + str(hosttocheck_job_id) + " Submitting response to job.")
        response = requests.post(scoreboardaddress, headers={'SBE-AUTH' : '354787eb-0b6e-4a38-8db5-d8ac753cfdca'}, json=finalresponse_json)
        logging.info(" " + str(hosttocheck_job_id) + " Response from scoreboard. - " + str(response.content) + ".")
    # Sleep for 5 secs, then restart
    time.sleep(5)

while True:
    main()
