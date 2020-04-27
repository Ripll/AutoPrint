PROJECT := $(notdir $(CURDIR))
VERSION := 0.1
IP := $(shell hostname -I | rev | cut -c 2- | rev)


# =================================================================================================
# Base
# =================================================================================================

default:help

help:
	@echo "Telegram: @Ripll_24"



# =================================================================================================
# Development
# =================================================================================================

certs:
	openssl genrsa -out webhook.key 2048
	openssl req -new -x509 -days 3650 -key webhook.key -out webhook.cert -subj "/C=GB/ST=London/L=London/O=Global Security/OU=IT Department/CN=${IP}"


start:
	systemctl start ${PROJECT}.service

restart:
	systemctl restart ${PROJECT}.service

stop:
	systemctl stop ${PROJECT}.service

install:
	apt update
	apt -y upgrade
	apt install -y python3.8 python3.8-dev python3-pip libpython3.8-dev mongodb
	apt install -y gconf-service libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxss1 libxtst6 libappindicator1 libnss3 libasound2 libatk1.0-0 libc6 ca-certificates fonts-liberation lsb-release xdg-utils wget
	$(MAKE) certs
	python3.8 -m pip install --upgrade pip
	python3.8 -m pip install -r requirements.txt
	printf '[Unit]\nDescription = ${PROJECT}\nAfter = network.target\n\n\n[Service]\nPermissionsStartOnly = true\nPIDFile = /run/${PROJECT}/${PROJECT}.pid\nUser = root\nGroup = root\nWorkingDirectory =  $(shell pwd)\nExecStartPre = /bin/mkdir /run/${PROJECT}\nExecStartPre = /bin/chown -R root:root /run/${PROJECT}\nExecStart = /usr/bin/env  python3.8 ./webhook.py\nExecReload = /bin/kill -s HUP $MAINPID\nExecStop = /bin/kill -s TERM $MAINPID\nExecStopPost = /bin/rm -rf /run/${PROJECT}\nPrivateTmp = true\nRemainAfterExit=no\nRestart=on-failure\nRestartSec=5s\n\n[Install]\nWantedBy = multi-user.target' > /etc/systemd/system/${PROJECT}.service
	systemctl enable ${PROJECT}.service
	$(MAKE) start