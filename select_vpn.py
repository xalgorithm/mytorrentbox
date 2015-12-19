import random
import os
import subprocess

mycfg = ""

def get_cfg():
    global mycfg
    # getpath
    path = os.getcwd() #get the current directory
    #create an array of files
    dirs = os.listdir( path )
    # pick a config at random
    mycfg = str(random.choice(dirs))


#Start the VPN
def start_vpn():
    openvpn_cmd = ['sudo', 'openvpn', '--config', mycfg, '--auth-user-pass', 'vpn_u.conf']
    subprocess.Popen(openvpn_cmd)


#main ties it all together
def main() :
    get_cfg()
    start_vpn()

if __name__ == "__main__" :
    main()
