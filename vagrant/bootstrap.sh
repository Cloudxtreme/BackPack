#!/bin/bash

HOST="`hostname`"
SERVHOST="serv"
SERVIP="172.25.0.2"
CLIENTS=("172.25.0.3" "172.25.0.4" "172.25.0.5")
REPO="epel-release-6-8.noarch.rpm"
PREDEST="root@"
USRJOHN="client1"

if [ "${USRJOHN}" == "${HOST}" ]
then
	result=`cat /etc/passwd | grep john | wc -l`
	echo "-----Adding user john-----"
	if [ $result -eq 0 ]
	then
		u="john"
		p="!10v3p3r1"
		useradd "$u"
		echo "$p" | passwd "$u" --stdin
		mkdir /home/john/pr0n
		fallocate -l 15M /home/john/pr0n/p3rl-gone-wild
		fallocate -l 50M /home/john/pr0n/perl3QuickAndDirty
	fi
fi
exit

cd /var/www/
sudo rpm -q epel-release
result=$?
if [ $result -eq 1 ]
then
	echo "-----installing unzip-----"
	yum install -y unzip
	echo "-----adding epel-release repo-----"
	if [ ! -e "/var/www/${REPO}" ]
	then 
		sudo wget "http://download.fedoraproject.org/pub/epel/6/x86_64/${REPO}" 
	fi
	cp "/var/www/${REPO}" "/usr/local/src/${REPO}" 
	cd /usr/local/src/
	sudo rpm -ivh "/usr/local/src/${REPO}"
	echo "-----installing  duplicity and necessary tools-----"
	sudo yum install -y duplicity rsync gpg python python-devel python-pip sshpass bcrypt

	echo "-----installing Google Data-----"
	cd /var/www
	if [ ! -e "/var/www/gdata-2.0.17/" ]
	then 
		if [ ! -e "/var/www/gdata-2.0.17.zip" ]
		then
			wget http://gdata-python-client.googlecode.com/files/gdata-2.0.17.zip
		fi
		unzip gdata-2.0.17.zip
	fi
	cd gdata*
	python setup.py install
fi

if [ "${HOST}" == "${SERVHOST}" ]
then 
	if [ ! -e "/root/.ssh/id_rsa" ]
	then
		echo "-----starting ssh permissions configuration-----"
		if [ ! -d "/root/.ssh/" ]
		then
			mkdir /root/.ssh
			touch /root/.ssh/known_hosts
		fi
		cd /root/.ssh
		ssh-keygen -f id_rsa -t rsa -N ''
		sudo yum install -y sshpass
	fi
	
	for i in "${CLIENTS[@]}"
	do
		result=`cat /root/.ssh/known_hosts | grep $i | wc -l`
		if [ result -eq 0 ]
		then
			ssh-keyscan $i >> /root/.ssh/known_hosts
			sshpass -p 'vagrant' ssh-copy-id -i /root/.ssh/id_rsa ${PREDEST}${i} 
		fi
	done
fi
echo "-----DONE setting up $HOST-----"
