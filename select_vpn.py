#!/usr/bin/env python
import sys
import os
import random
import subprocess
import optparse

# Default options global variable
_default_config_dir = os.path.abspath('.')
_default_vpn_userfile = os.path.abspath("./vpn_u.conf")
_default_openvpn_bin = '/usr/sbin/openvpn'


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

    parser.add_option("--openvpn", action="store",
                      help="Location of the OpenVPN binary. Default: {0}".format(_default_openvpn_bin))

    opts, _ = parser.parse_args(args)

    # Set the defaults
    if not opts.configdir:
        opts.configdir = _default_config_dir
    if not opts.userfile:
        opts.userfile = _default_vpn_userfile
    if not opts.openvpn:
        opts.openvpn = _default_openvpn_bin

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

    return config


def start_vpn(openvpn, config, userfile):
    """
    Start OpenVPN using the given openvpn configuration file and VPN userfile.

    :return: None
    """
    openvpn_cmd = [openvpn, '--config', config, '--auth-user-pass', userfile]
    subprocess.Popen(openvpn_cmd)


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

    # Get the config to use for openvpn
    config = get_random_config(opts.configdir)

    # Start OpenVPN
    start_vpn(opts.openvpn, config, opts.userfile)


if __name__ == "__main__":
    main()
