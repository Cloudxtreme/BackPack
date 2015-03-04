#!/bin/bash

HOST="`hostname`"
SERVHOST="serv"
SERVIP="172.25.0.2"
CLIENTS=("172.25.0.3" "172.25.0.4" "172.25.0.5")
REPO="epel-release-6-8.noarch.rpm"
PREDEST="root@"

echo "-----starting duplicity install-----"
if [ ! -e "/var/www/${REPO}" ]
then 
	cd /var/www/
	sudo wget "http://download.fedoraproject.org/pub/epel/6/x86_64/${REPO}" 
fi
cp "/var/www/${REPO}" "/usr/local/src/${REPO}" 
cd /usr/local/src/
sudo rpm -ivh "/usr/local/src/${REPO}"

sudo yum install -y duplicity rsync gpg python python-devel python-pip sshpass unzip

if [ ! -e "/var/www/gdata-2.0.17/" ]
then 
	cd /var/www
	if [ ! -e "/var/www/gdata-2.0.17.zip" ]
	then
		wget http://gdata-python-client.googlecode.com/files/gdata-2.0.17.zip
	fi
	unzip gdata-2.0.17.zip
	cd gdata*
	python setup.py install
fi
echo "-----finished duplicity install-----"

if [ "${HOST}" == "${SERVHOST}" ]
then 
	echo "-----starting ssh permitions-----"

	if [ ! -e "/root/.ssh/id_rsa" ]
	then
		if [ ! -d "/root/.ssh/" ]
		then
			mkdir /root/.ssh
		fi
		cd /root/.ssh
		ssh-keygen -f id_rsa -t rsa -N ''
		sudo yum install -y sshpass
	fi

	if [ -e "/root/.bashrc" ]
	then
		mv /root/.bashrc /root/.bashrc.bak
	fi
	
	for i in "${CLIENTS[@]}"
	do
		ssh-keyscan $i >> /root/.ssh/known_hosts
		sshpass -p 'vagrant' ssh-copy-id -i /root/.ssh/id_rsa ${PREDEST}${i} 
	done
	mv /root/.bashrc.bak /root/.bashrc
	echo "-----finished ssh permitions-----"
fi
