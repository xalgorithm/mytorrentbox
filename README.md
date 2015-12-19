# Beaglebone Setup Notes

The Debian 8.2 image found [here](http://beagleboard.org/latest-images) was used to configure the OS of the Beaglebone
Black.

Download the file, decompress it, and write it to a microSD card:

    curl -L -O http://builds.beagleboard.org/images/master/08132bf0d0cb284d1148c5d329fe3c8e1aaee44d/bone-debian-8.2-tester-2gb-armhf-2015-11-12-2gb.img.xz

    unxz bone-debian-8.2-tester-2gb-armhf-2015-11-12-2gb.img.xz

    sudo dd if=bone-debian-8.2-tester-2gb-armhf-2015-11-12-2gb.img of=${sdcard_device}

## OS Installation

After the image is written to the microsd card insert it into the microsd slot on the Beaglebone. Boot from the SD card by holding the button on the board nearest the card slot and connecting the power.

Let go of the button after the LEDs stop flashing.

Wait for the board to boot up. If it's connected to ethernet it should automatically configure its network interface with DHCP, and SSH will start automatically.

You should be able to SSH to the device with the username `debian` and password `temppwd`.

Once logged in edit the `/boot/uEnv.txt` file. Uncomment the following line:

    cmdline=init=/opt/scripts/tools/eMMC/init-eMMC-flasher-v3.sh

Save the file and reboot the board. The LEDS will flash as the operating system is written to eMMC. After about 30 minutes the lights will stop flashing. At this point you can power off the board, remove the SD card, and boot from the operating system on the eMMC.

If you want you can repartiation and reformat your SD card and mount it as a separate drive.

For our case we mounted a 32G microSD card to `/var`.

## Transmission Installation

Install the `transmission-daemon` package:

    sudo apt-get install transmission-daemon

We used the guide found [here](abyrne.me/setting-up-a-transmission-web-interface-on-a-headless-ubuntu-server/) to configure the service. The configuration file is found at `/etc/transmission-daemon/settings.json`. An example can be found in this repository.

The following commands will disable the built-in Beaglebone web services so that Transmission can run on port 80:

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
