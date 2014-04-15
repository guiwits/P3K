#!/usr/bin/python
from threading import Thread
import subprocess
from Queue import Queue
import time
import datetime;
import socket;
import smtplib;
import os
import getopt
import sys
from email.MIMEText import MIMEText;

CS1PVT = "xxx.xxx.xxx.xxx"
CS2PVT = "xxx.xxx.xxx.xxx"
CS3PVT = "xxx.xxx.xxx.xxx"
CS4PVT = "xxx.xxx.xxx.xxx"

CS1PUB = "xxx.xxx.xxx.xxx"
CS2PUB = "xxx.xxx.xxx.xxx"
CS3PUB = "xxx.xxx.xxx.xxx"
CS4PUB = "xxx.xxx.xxx.xxx"

pvt_ips = [CS1PVT, CS2PVT, CS3PVT, CS4PVT]
pub_ips = [CS1PUB, CS2PUB, CS3PUB, CS4PUB]

ips = {'host1_pvt' : 'xxx.xxx.xxx.xxx',  'host2_pvt' : 'xxx.xxx.xxx.xxx',
       'host3_pvt' : 'xxx.xxx.xxx.xxx',  'host4_pvt' : 'xxx.xxx.xxx.xxx',
       'host1'     : 'xxx.xxx.xxx.xxx', 'host2'      : 'xxx.xxx.xxx.xxx',
       'host3'     : 'xxx.xxx.xxx.xxx', 'host4'      : 'xxx.xxx.xxx.xxx'}


hosts = {'xxx.xxx.xxx.xxx' : 'host1_pvt', 'xxx.xxx.xxx.xxx' : 'host2_pvt',
         'xxx.xxx.xxx.xxx' : 'host3_pvt', 'xxx.xxx.xxx.xxx' : 'host4_pvt',
         'xxx.xxx.xxx.xxx' : 'host1', 'xxx.xxx.xxx.xxx'     : 'host2',
         'xxx.xxx.xxx.xxx' : 'host3', 'xxx.xxx.xxx.xxx'     : 'host4'}

netmon_start       = "/home/steve/comserv/bin/run_netmon"
netmon_restart     = "/home/steve/comserv/bin/netmon -r"
netmon_start_all   = "/home/steve/comserv/bin/netmon -s"
netmon_terminate   = "/home/steve/comserv/bin/netmon -t"
snw_restart        = "/home/steve/utils/snw/snwctl.sh restart"

### Calls the systems' ping command for initial check ###
def PingServer (server_ip):
    ip = server_ip
    print "Pinging hostname %s [IP %s]." % ((GetHostname (ip)), ip)
    ret = subprocess.call ("/bin/ping -c 5 %s" % ip, shell = True, 
              stdout = open ('/dev/null', 'w'), stderr = subprocess.STDOUT)

    if ret != 0: 
        return GetHostname (ip) 
    else: 
        return 0
### END PingServer ###

### Ping the specific server again as it prepares to take over.  ###
### This is done over a time interval in case the server comes   ###
### back on-line for whatever reason. We don't want the machines ###
### fighting to take control. Not good for the Q330's.           ###
def PingServerAgain (ip):
    ret = subprocess.call ("/bin/ping -c 5 %s" % ip, shell = True,
              stdout = open ('/dev/null', 'w'), stderr = subprocess.STDOUT)
    return ret
### END PingServerAgain ###

### A server is down, time for the partner to take over ###
def Takeover (ip):
    print "Trying to ping hostname %s [IP %s] again in 60 seconds." % ((GetHostname (ip)), ip)
    time.sleep (60) # Give machine a minute to ping again. Afer that, take over.
    ret = PingServerAgain (ip)
    if ret == 0:
        print "Hostname %s [IP %s] is alive. Aborting takeover" % ((GetHostname (ip)), ip)
        return
    else:
        print "Hostname %s [IP %s] is still down. Taking over stations" % ((GetHostname (ip)), ip)
        # Check to see if we have already taken over, if yes, quit otherwise proceed #
        if HaveTakenOver (GetHostname (ip)) == True:
            print "Already have taken over host %s. Exiting." % (GetHostname (ip))
            return 
    
    text = '%s can\'t ping hostname: %s. Taking over now' % (socket.gethostname(), GetHostname (ip))
    SendMail (text, ip)
	
    if (GetHostname (ip)) == 'host1' or (GetHostname (ip)) == 'host1_pvt':
        CreateStationsFile ("host1")
        RestartNetmonService ()
    elif (GetHostname (ip)) == 'host2' or (GetHostname (ip)) == 'host2_pvt':
        CreateStationsFile ("host2")
        RestartNetmonService ()
    elif (GetHostname (ip)) == 'host3' or (GetHostname (ip)) == 'host3_pvt':
        CreateStationsFile ("host3")
        RestartNetmonService ()
    elif (GetHostname (ip)) == 'host4' or (GetHostname (ip)) == 'host4_pvt':
        CreateStationsFile ("host4")
        RestartNetmonService ()
    else:
        print "ERROR: Unable to fine ip [%s]. Aborting." % ip
### END Takeover ###

### A method to make sure that machine taking over stations is actually ok ###
### to do so. We are tyring to prevent the case that the reason pings fail ###
### aren't because the pinging machine is offline.                         ###
def amIOk ():
    google = "www.google.com";
    yahoo  = "www.yahoo.com";
    unix1  = "host1.pvt.scsn.org";
    unix2  = "host2.pvt.scsn.org";
    print "Pinging google."
    googlerc = subprocess.call ("/bin/ping -c 5 %s" % google, shell = True,
               stdout = open   ('/dev/null', 'w'), stderr = subprocess.STDOUT)
    print "Pinging yahoo."
    yahoorc  = subprocess.call ("/bin/ping -c 5 %s" % yahoo, shell = True,
               stdout = open   ('/dev/null', 'w'), stderr = subprocess.STDOUT)
    print "Pinging host1."
    unix1rc  = subprocess.call ("/bin/ping -c 5 %s" % host1, shell = True,
               stdout = open   ('/dev/null', 'w'), stderr = subprocess.STDOUT)
    print "Pinging host2."
    unix2rc  = subprocess.call ("/bin/ping -c 5 %s" % host2, shell = True,
               stdout = open   ('/dev/null', 'w'), stderr = subprocess.STDOUT)

    ### If more than 3 are successful, we are ok ###
    if (googlerc == 0  and yahoorc == 0 and
        host1rc  == 0  and host2rc == 0):
        print "Able to ping every server.\n"
        return 0
    elif (googlerc == 0 and host1rc == 0  and host2rc == 0):
        return 0
    elif (yahoorc == 0  and host1rc == 0  and host2rc == 0):
        return 0
    elif (yahoorc == 0  and googlerc == 0 and hostrc == 0):
        return 0
    elif (yahoorc == 0  and googlerc == 0 and host2rc == 0):
        return 0
    else:
        return 1
### End amIOk ###

### Takes an IP address and returns the server name ###
def GetHostname (ip):
    return hosts [ip]
### END GetHostname ###

### Takes a hostname and returns its IP address ###
def GetIpAddr (host): 
    print host
    return ips [host]
### END GetIpAddr ###

### Look to see if netmon, qmaserv, and cs2mcast procs are running ###
def CheckServices (hostname):
    searchString = 'ssh %s ls' % (hostname)
    print "Search string is %s" % (searchString)
    return NumberOfProcesses
### END CheckServices ###

### Create a new stations.ini file based upon which host's stations are being taken over ###
def CreateStationsFile (hostname):
    print "Setting up stations.ini file to take over stations from host %s" % hostname
    cmd = subprocess.Popen (["hostname", "-s"], stdout = subprocess.PIPE)
    localHostname = cmd.stdout.read()

    ### copy stations.ini file to a backup, cat new group + old backup group ###
    os.system ('cp /home/steve/comserv/etc/stations.ini /home/steve/comserv/etc/stations.ini.takeover')

    ### Write the new @include to the stations.ini file for the host to takeover ###
    if hostname == "host1":
        os.system ('echo "@/home/steve/comserv/etc/stations_1.ini" >> /home/steve/comserv/etc/stations.ini')
    elif hostname == "host2":
        os.system ('echo "@/home/steve/comserv/etc/stations_2.ini" >> /home/steve/comserv/etc/stations.ini')
    elif hostname == "host3":
        os.system ('echo "@/home/steve/comserv/etc/stations_3.ini" >> /home/steve/comserv/etc/stations.ini')
    elif hostname == "host4":
	    os.system ('echo "@/home/steve/comserv/etc/stations_4.ini" >> /home/steve/comserv/etc/stations.ini')
    else:
        print "ERROR: hostname not recognized. Aborting." 
        return -1

    return 0
### END CreateStationsFile ###
    
### Restart the netmon service on the localhost ###ss
def RestartNetmonService ():
    print "Restarting the netmon service with command %s." % (netmon_restart)
    ### check to see if netmon is running. If it is, restart it. If not, start it. ###
    pipe = subprocess.Popen ("ps aux | grep netmon | grep -v grep | awk '{print $2}'", 
                             shell=True, stdout=subprocess.PIPE).stdout
    netmonPid = pipe.read()

    if netmonPid == '':
        print "netmon not running. Starting it"
        StartNetmon()
    else:
        print "netmon is running with pid", netmonPid
        os.system (netmon_restart)  # adds stations ==> netmon -r 
        time.sleep (15)
        os.system (netmon_start_all)  # adds stations ==> netmon -s
       
    ###SNWRestart()
    return
### END RestartNetmonService ###

### Start/Restart the SNW agents ###
def SNWRestart():
    os.system (snw_restart)
### END SNWRestart ###

### Terminates the netmon service on the machine we're taking over ###
def TerminateNetmonService():
    counter = 0
    os.system (netmon_terminate)
    while (os.system ('ps aux | grep qmaserv | grep -v grep | wc -l')) != 0:
        counter = counter + 1
        print "qmaserv still running. Waiting for it to stop"
        time.sleep (10)
        if counter == 25:
            print "Counter has reached its patience limit. Killing off processes."
            for i in (os.system ("ps aux | grep qmaserv | grep -v grep | awk '{print $2}'")):
                try:
                    os.kill (int (i), 9)
                    raise Exception ("""wasn't able to kill the process.""")
                except OSError as ex:
                    continue

    ### get PID of netmon to kill it ###
    pipe = subprocess.Popen ("ps aux | grep netmon | grep -v grep | awk '{print $2}'", 
                              shell=True, stdout=subprocess.PIPE).stdout
    pid = pipe.read()
    print "PID of netmon is", pid
    try:
        os.kill (int (pid), 9)
        raise Exception ("""wasn't able to kill the process.""")
    except OSError as ex:
        print "Unable to kill the PID os netmon."
    
    return
### END TerminateNetmonService ###

### Kill off netmon and restart it after the correct stations.ini file has been constructed ###
def StartNetmon():
    print "Starting netmon with command %s" % (netmon_start)
    os.system (netmon_start)
    time.sleep (10)
    os.system (netmon_start_all)  # adds stations to netmon but doesn't start (when runnable)
    return
### END StartNetmon ###

### Mail off a message when a system is going to be taken over ###
def SendMail (message, ip):
    server_ip = ip
    mail_message = message
    now = datetime.datetime.now();
    sender = sender = 'rtem@%s' % socket.gethostname()
    recipients = ['name1@host', 'name2@host', 'name3@host', 'name3@host']
    msg = MIMEText (mail_message);
    msg['Subject'] = '%s can\'t ping host %s at time: %s' % (socket.gethostname(), GetHostname (server_ip), now)
    msg['From'] = sender
    msg['To'] = ", ".join(recipients)
    s = smtplib.SMTP('localhost')
    s.sendmail(sender, recipients, msg.as_string())
    s.quit()
    return
### END SendMail ###

### Check if the downed server(s) have already been taken over ###
def HaveTakenOver (station):
    f = open('/etc/stations.ini', 'r')
    lines = f.read().splitlines()
    f.close()
    for line in lines:
        if line == "@/home/steve/comserv/etc/stations_1.ini" and station == "host1":
            return True
        if line == "@/home/steve/comserv/etc/stations_2.ini" and station == "host2":
            return True
        if line == "@/home/steve/comserv/etc/stations_3.ini" and station == "host3":
            return True
        if line == "@/home/steve/comserv/etc/stations_4.ini" and station == "host4":
            return True
    return False
    
### Displays the usage to the user upon -h flag or error ###
def Usage():
    print "This script either runs automatically and watches certain machines"
    print "for processes and network connectivity before it takes over certain"
    print "groups of stations or it is run manually by giving it a group of stations"
    print "to takeover. Options are: [host1, host2, host3, host4]."
    print "Usage: python takeover.py  --OR-- python takeover.py -s [hostX]." 
### END Usage ###

### Main ... ###
def Main():
    try:
        opts, args = getopt.getopt (sys.argv[1:], "hs:v", ["help", "stations="])
    except getopt.GetoptError, err:
        print str (err) # will print something like "option -s not recognized"
        Usage ()
        sys.exit (2)

    stations  = None
    verbose   = False
    hostname  = subprocess.Popen (["hostname", "-s"], stdout = subprocess.PIPE)
    localhost = hostname.stdout.read().rstrip('\n')

    for o, s in opts:
        if o == "-v":
            verbose = True
        elif o in ("-h", "--help"):
            Usage ()
            sys.exit ()
        elif o in ("-s", "--stations"):
            stations = s
            print "Manually taking over stations %s.\n" % str (stations)
        else:
            assert False, "unhandled option"

    if stations != None:
        print "Command line argument given: %s" % (stations)
        for item in hosts:
            if hosts[item] == stations:
                ip = item
        Takeover (ip)
    else:
        print "*** Checking host cluster private interface ***"
        for server_ip in pvt_ips:
            retcode = PingServer (server_ip)
            if (retcode != 0):
                print "Can't ping %s's private interface. Checking public interface on %s" % (retcode, retcode)
                badPrivateHost = retcode
                bph = badPrivateHost[:10]
                pubHost = PingServer (GetIpAddr (bph))
                if (pubHost != 0): 
                    print "Both public and private interfaces are down on host %s." % (bph) 
                    print "Checking to see if I am ok and if I am, I will take over host %s" % (bph)
                    print "if I am the next peer in line to take over."
                    okToTakeover = amIOk() 
                    if (okToTakeover == 0): 
                        print "I am ok to take over host %s. Calling the takeover method." % (bph) 
                        ### Machine hasn't recovered, going to take over the stations ###
                        ### cs 1 <----> cs 2 (primary concern)
                        ### cs 3 <----> cs 4 (primary concern)
                        ### cs 1 <----> cs 3 (secondary concern)
                        ### cs 2 <----> cs 4 (secondary concern)
	                ### cs 1 <----> cs 4 (tertiary concern)
	                ### cs 2 <----> cs 3 (tertiary concern)
                        ################################################################## 
                        print "Hostname is %s" % (localhost)
                        print "Host to takeover is %s" % (bph)

                        # host1 priorities #
                        # Primary is host2 #
                        if localhost == "host1" and bph == "host2": 
                            time.sleep (5) 
                            print "host1 taking over %s" % (bph)
                            Takeover (GetIpAddr (bph))
                        elif localhost == "host1" and bph == "host4": 
                            time.sleep (10) 
                            if (PingServer ((GetIpAddr ('host3'))) == 0):
                                print "host3 pingable. Leaving %s alone." % (bph) 
                            else:
                                print "host1 taking over %s" % (bph)
                                Takeover (GetIpAddr (bph)) 
                        elif localhost == "host1" and bph == "host3": 
                            time.sleep (15) 
                            # ping host2 and host4 to see if they are alive #
                            # to take over                                            #
                            if (PingServer ((GetIpAddr ('host2'))) == 0) or \
                               (PingServer ((GetIpAddr ('host4'))) == 0):
                                print "host2 or host4 are pingable. Leaving %s alone." % (bph) 
                            else:
                                print "host1 taking over %s" % (bph)
                                Takeover (GetIpAddr (bph)) 

                        # host2 priorities #
                        # Primary is host1 #
                        if localhost == "host2" and bph == "host1": 
                            time.sleep (5) 
                            print "host2 taking over %s" % (bph)
                            Takeover (GetIpAddr (bph)) 
                        elif localhost == "host2" and bph == "host3": 
                            time.sleep (10) 
                            if (PingServer ((GetIpAddr ('host4'))) == 0):
                                print "host4 pingable. Leaving %s alone." % (bph)
                            else:
                                print "host2 taking over %s" % (bph)
                                Takeover (GetIpAddr (bph))
                        elif localhost == "host2" and bph == "host4": 
                            time.sleep (15) 
                            if (PingServer ((GetIpAddr ('host1'))) == 0) or \
                               (PingServer ((GetIpAddr ('host3'))) == 0):
                                print "host1 or host3 are pingable. Leaving %s alone." % (bph) 
                            else:
                                print "host2 taking over %s" % (bph)
                                Takeover (GetIpAddr (bph)) 

                        # host3 priorities #
                        # Primary is host4 #
                        if localhost == "host3" and bph == "host4": 
                            time.sleep (5) 
                            print "host3 taking over %s" % (bph)
                            Takeover (GetIpAddr (bph)) 
                        elif localhost == "host3" and bph == "host2": 
                            time.sleep (10) 
                            if (PingServer ((GetIpAddr ('host1'))) == 0):
                                print "host1 pingable. Leaving %s alone." % (bph)
                            else:
                                print "host3 taking over %s" % (bph)
                                Takeover (GetIpAddr (bph))
                        elif localhost == "host3" and bph == "host1": 
                            time.sleep (15) 
                            if (PingServer ((GetIpAddr ('host2'))) == 0) or \
                               (PingServer ((GetIpAddr ('host4'))) == 0):
                                print "host2 or host4 are pingable. Leaving %s alone." % (bph)
                            else:
                                print "host3 taking over %s" % (bph)
                                Takeover (GetIpAddr (bph))
                        # host4 priorities #
                        if localhost == "host4" and bph == "host3": 
                            time.sleep (5) 
                            print "host4 taking over %s" % (bph)
                            Takeover (GetIpAddr (bph)) 
                        elif localhost == "host4" and bph == "host1": 
                            time.sleep (10) 
                            if (PingServer ((GetIpAddr ('host2'))) == 0):
                                print "host2 pingable. Leaving %s alone." % (bph)
                            else:
                                print "host4 taking over %s" % (bph)
                                Takeover (GetIpAddr (bph))
                        elif localhost == "host4" and bph == "host2": 
                            time.sleep (15) 
                            if (PingServer ((GetIpAddr ('host1'))) == 0) or \
                               (PingServer ((GetIpAddr ('host3'))) == 0):
                                print "host1 or host3 are pingable. Leaving %s alone." % (bph)
                            else:
                                print "host4 taking over %s" % (bph)
                                Takeover (GetIpAddr (bph))
                        else: 
                            print "Host %s." % localhost 
                else: 
                    print "I don't seem to be ok. Aborting any type of takeover." 
                    sys.exit (2)
        
    print "Program completed. Exiting."
### END Main ###

if __name__ == "__main__":
    Main()

