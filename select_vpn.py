#!/usr/bin/env python
import sys
import os
import random
import subprocess
import optparse
import signal
import json
from time import sleep

# Default options global variable
_default_config_dir = os.path.abspath('.')
_default_vpn_userfile = os.path.abspath("./vpn_u.conf")
_default_openvpn_bin = '/usr/sbin/openvpn'
_default_cacert = os.path.abspath("./ca.crt")
_default_pidfile = '/var/run/openvpn/torrentbox_vpn.pid'
_default_transmission_config = '/etc/transmission-daemon/settings.json'


def parse_command_line(args=None):
    """
    Parse options from the command line.

    :param args: Args passed to the script from the command line
    :return: The "opts" portion of the out put from the OptionParser.parse_args() method.
    """
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage=usage)

    parser.add_option("-c", "--configdir", action="store",
                      help=("Directory of OpenVPN configuration files to use.\n"
                            "Default: {0}".format(_default_config_dir)))

    parser.add_option("-u", "--userfile", action="store",
                      help=("Configuration File containing OpenVPN authentication credentials\n"
                            "Default: {0}".format(_default_vpn_userfile)))

    parser.add_option("--cacert", action="store",
                      help="Location of the VPN provider's CA Cert. Default: {0}".format(_default_cacert))

    parser.add_option("--openvpn", action="store",
                      help="Location of the OpenVPN binary. Default: {0}".format(_default_openvpn_bin))

    parser.add_option("-p", "--pidfile", action="store",
                      help="Location of the openvpn PID file. Default: {0}".format(_default_pidfile))

    parser.add_option("-t", "--transmission_config", action="store",
                      help=("Location of the transmission-daemon settings.json file. "
                            "Default: {0}".format(_default_transmission_config)))

    opts, _ = parser.parse_args(args)

    # Set the defaults
    if not opts.configdir:
        opts.configdir = _default_config_dir
    if not opts.userfile:
        opts.userfile = _default_vpn_userfile
    if not opts.openvpn:
        opts.openvpn = _default_openvpn_bin
    if not opts.cacert:
        opts.cacert = _default_cacert
    if not opts.pidfile:
        opts.pidfile = _default_pidfile
    if not opts.transmission_config:
        opts.transmission_config = _default_transmission_config

    return opts


def get_random_config(directory=None):
    """
    Returns a random openvpn configuration file from the given directory.

    :param directory: The directory from which to pull a random VPN config file.
    :return: The path to the randomly chosen VPN configuration file.
    """
    # Get all of the files in the config directory
    files = os.listdir(directory)

    # Filter out only '.ovpn' files
    ovpn_files = []
    for f in files:
        if '.ovpn' in f:
            ovpn_files.append(f)

    # pick a config at random
    config = str(random.choice(ovpn_files))

    return "{0}/{1}".format(directory, config)


def start_vpn(openvpn, config, userfile, cacert):
    """
    Start OpenVPN using the given openvpn configuration file and VPN userfile.

    :param openvpn: Location of openvpn binary.
    :param config: Location of the openvpn config file to use.
    :param userfile: Location of the openvpn credentials to use.
    :param cacert: Location of the CA cert for the VPN provider
    :return: Dictionary containing OpenVPN PID and local VPN connection IP address. None if OpenVPN connect fails.
    """

    openvpn_cmd = [openvpn, '--config', config, '--auth-user-pass', userfile, '--ca', cacert]
    proc = subprocess.Popen(openvpn_cmd, stdout=subprocess.PIPE)

    # Wait a few seconds for OpenVPN to finish connecting
    sleep(30)

    stdout = proc.stdout.read()
    print stdout
    for line in stdout:
        if '/sbin/ip addr add dev' in line:
            vpn_ip = line.split(' ')[11]

    return {'pid': proc.pid, 'ip': vpn_ip}


def update_transmission_config(config_file, ip):
    """
    Update the configuration settings.json for transmission-daemon with the local VPN connection IP address.

    this will ensure that transmission-daemon binds its bittorrent traffic to the VPN link.

    :param config_file: Location of the Transmission daemon config file.
    :param ip: IP Address of the local VPN link to add to the config file.
    :return:
    """
    with open(config_file, 'w') as settings_json:
        data = json.loads(settings_json.read())

        data['bind-address-ipv4'] = str(ip)

        json.dumps(data, settings_json, indent=4)


def main():
    """
    Main method. Check the environment to make sure it's sane first, and then try to bring up a VPN link with
    a random config file from the VPN configs directory.

    :return: None
    """
    opts = parse_command_line()

    # Script should run as root.
    if os.getuid() != 0:
        print "This script must be run as an administrator."
        sys.exit(1)

    # Fail if OpenVPN is not found.
    if not os.path.isfile(opts.openvpn):
        print "OpenVPN not found at {0} - make sure OpenVPN is installed on this machine.".format(opts.openvpn)
        sys.exit(1)

    # Check for an existing PID file. If one exists read the PID from it, and kill the old VPN connection.
    if os.path.isfile(opts.pidfile):
        pid = open(opts.pidfile, 'r').read()

        try:
            print "Stopping old OpenVPN session..."
            os.kill(pid, signal.SIGINT)
        except OSError, e:
            print "A PID file exists, but the PID could not be killed. Opening new VPN connection anyway."
            print e.message

    # Get the config to use for openvpn
    config = get_random_config(opts.configdir)

    # Start OpenVPN
    vpn = start_vpn(opts.openvpn, config, opts.userfile, opts.cacert)

    # Check if OpenVPN connected successfully.
    if vpn:
        # Write PID file with new PID.
        pid_file = open(opts.pidfile, 'w')
        pid_file.write(vpn['pid'])

        update_transmission_config(opts.transmission_config, vpn['ip'])
    else:
        print "OpenVPN connection failed. Quitting."
        sys.exit(1)




if __name__ == "__main__":
    main()
