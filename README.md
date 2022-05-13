# Fun-GIF-orme

A Discord bot to manage the Fun-GIF-orme contest.

Fun-GIF-orme is a timed daily event on discord where GIFs are used to reply to posts in a channel and voted by users using the 🍄 reaction (both configurable in the ini file).

Most votes win!!

# Installation

Please note that after installing the bot, it must be configured with the correct values for `Token` and `Channel` in  fungiforme.ini; you can copy and rename the sample fungiforme.ini.example file to have a basic configuration.  

## Quick Set-up
Clone this repo on target server, create virtualenv, activate and install requirements.

Run fungiforme.py

## Run the bot as a service  

It is recommended to run this bot as a service so as it is always available, to configure the systemd service do the following:

* Clone the repository in your target directory (i.e. /opt/fungiforme)
* Create a virtualenv, activate it and install requirements
``` 
# cd /opt/fungiforme
# python3 -m venv .venv
# source .venv/bin/activate
# pip install -r requirements.txt
```
* Create a fungiforme service user and group, set the homedir to the directory where you cloned fungiforme (i.e. /opt/fungiforme):
```
# groupadd fungiforme
# useradd --system --home-dir "/opt/fungiforme" --user-group \
--groups fungiforme --shell /bin/false fungiforme
```
* Fix permissions on the cloned fungiforme directory:
```
# chown -R fungiforme: /opt/fungiforme
```
* Create a systemd unit file in `/etc/systemd/system/fungiforme.service`
```
[Unit]
Description=Discord fungiforme bot service 
After=network.target

[Service]
User=fungiforme
Group=fungiforme
WorkingDirectory=/opt/fungiforme/
ExecStart=/opt/fungiforme/.venv/bin/python3 /opt/fungiforme/fungiforme.py
Restart=always

[Install]
WantedBy=multi-user.target
```
* Enable and start the bot
```
# systemctl enable fungiforme.service
# systemctl start fungiforme.service
```

