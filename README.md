# Beaglebone Setup Notes

## TODO:

~~1. Scaffold Project~~

~~2. Get Cfg's used into Git~~

~~3. Get commands used into README~~

~~4. Write and add VPN cfg and random selector script~~

5. Put together Metor based interface app

6. Figure out NFS connections to file server

7. Get cron setup to rotate VPN every 6 hours

8. Refactor, throw one away, make another

## Project Overview

The goal of this project is to build a headless bittorrent box using a Beaglebone Black using the transmission-daemon web interface.

Transmission will beconfigured to bind to two network interaces. Since the Beaglebone only has a single Ethernet port we will utilize an alias to support the second IP.

One interface will serve the transmission web UI, and the other will be used to connect to a VPN over which transfer the actual bittorrent data will be transferred.

For the operating system we used the Debian 8.2 image found [here](http://beagleboard.org/latest-images).

Just download the file, decompress it, and write it to a microSD card
## OS Installation

Download the OS image:

    curl -L -O http://builds.beagleboard.org/images/master/08132bf0d0cb284d1148c5d329fe3c8e1aaee44d/bone-debian-8.2-tester-2gb-armhf-2015-11-12-2gb.img.xz

Decompress the file:

    unxz bone-debian-8.2-tester-2gb-armhf-2015-11-12-2gb.img.xz

Determine the device name of your SD card. On my mac it was /dev/disk2.

    sudo dd if=bone-debian-8.2-tester-2gb-armhf-2015-11-12-2gb.img of=/dev/disk2 bs=1m


After the image is written to the microsd card insert it into the microsd slot on the Beaglebone. Boot from the SD card by holding the button on the board nearest the card slot and connecting the power.

Let go of the button after the LEDs stop flashing.

Wait for the board to boot up. If it's connected to ethernet it should automatically configure its network interface with DHCP, and SSH will start automatically.

You should be able to SSH to the device with the username `debian` and password `temppwd`.

Once logged in edit the `/boot/uEnv.txt` file. Uncomment the following line:

    cmdline=init=/opt/scripts/tools/eMMC/init-eMMC-flasher-v3.sh

Save the file and reboot the board. The LEDS will flash as the operating system is written to eMMC. After about 30 minutes the lights will stop flashing. At this point you can power off the board, remove the SD card, and boot from the operating system on the eMMC.

If you want you can repartiation and reformat your SD card and mount it as a separate drive.

For our case we mounted a 32G microSD card to `/var`.

## OS Configuration

You should probably do some things like disable the default `debian` user, create your own user accounts, and do some basic security configuration. I'll leave it to you to figure out how to do all of that.

By default SSH will display a banner when you connect with the following information:

    Debian GNU/Linux 8

    BeagleBoard.org Debian Image 2015-11-12

    Support/FAQ: http://elinux.org/Beagleboard:BeagleBoneBlack_Debian

    default username:password is [debian:temppwd]

You can disable this banner by editing the SSHd config file at `/etc/ssh/sshd_config` and commenting out the following line:

    Banner /etc/issue.net

## Transmission Installation

Install the `transmission-daemon` package:

    sudo apt-get install transmission-daemon

We used the guide found [here](abyrne.me/setting-up-a-transmission-web-interface-on-a-headless-ubuntu-server/) to configure the service. The configuration file is found at `/etc/transmission-daemon/settings.json`. An example can be found in this repository.

The following commands will disable the built-in Beaglebone web services so that Transmission can run on port 80. You should reboot or use `systemctl stop` to make sure the service aren't running:

    sudo systemctl disable cloud9.service
    sudo systemctl disable gateone.service
    sudo systemctl disable bonescript.service
    sudo systemctl disable bonescript.socket
    sudo systemctl disable bonescript-autorun.service

The following command is required to let the transmission service bind to port 80:

    sudo setcap cap_net_bind_service+ep /usr/bin/transmission-daemon

Start transmission:

    sudo systemctl start transmission-daemon.service

Make sure the service is configured to start at boot:

    sudo systemctl enable transmission-daemon.service
