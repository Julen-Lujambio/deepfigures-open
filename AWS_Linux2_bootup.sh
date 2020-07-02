#!/bin/bash

# Side note by adding the -y you are auto answering yes
# when program would usually ask if it should install or not

# General set up for linux 2 vm ---------------------------------

# Elevate to admin privileges to run everything as root user

# update the yum
sudo yum update -y
# install python 3.7
sudo yum install -y python37
# install git to clone repos
sudo yum install git -y

# Set up required to run pdffigures2 -----------------------------------------

# install java 8 
sudo yum install java-1.8.0-openjdk-devel -y
# install scala 2.13.0
sudo wget http://downloads.typesafe.com/scala/2.13.0/scala-2.13.0.tgz
tar -xzvf scala-2.13.0.tgz
sudo rm -rf scala-2.13.0.tgz
export SCALA_HOME=/home/ec2-user/scala-2.13.0
export PATH=$PATH:/home/ec2-user/scala-2.13.0/bin
# install sbt
sudo curl https://bintray.com/sbt/rpm/rpm | sudo tee /etc/yum.repos.d/bintray-sbt-rpm.repo
sudo yum install sbt -y

# Set up needed for deepfigures ---------------------------------------------

# install pip
sudo curl -O https://bootstrap.pypa.io/get-pip.py
sudo python3.7 get-pip.py --user
# install click module that is needed for manage.py in deepfigures
sudo python3.7 -m pip install click
sudo python3.7 -m pip install scikit-image
sudo pip3 install scikit-image
sudo pip3 install click
# install docker -- vm that runs nueral network to extract figures
sudo amazon-linux-extras install docker -y
service docker start
# may need to reboot instance to have this enabled
sudo usermod -a -G docker ec2-user 

# Getting deepfigures downloaded and ready to run -------------------------

# make a git directory and enter it 
sudo mkdir git # the name is subject to change......
cd git
# clone edited deepfigures into git
sudo git clone https://github.com/Julen-Lujambio/deepfigures_open.git
cd deepfigures_open
# downloads the weights for nueral network
sudo curl -O https://s3-us-west-2.amazonaws.com/ai2-s2-research-public/deepfigures/weights.tar.gz
sudo tar -xvf weights.tar.gz
# compiling the .jar file for deepfigures
sudo git clone https://github.com/allenai/pdffigures2
cd pdffigures2
sudo sbt assembly
sudo mv target/scala-2.12/pdffigures2-assembly-0.1.0.jar ../bin
cd ..
sudo rm -rf pdffigures2

# Install modules for web scrapper
sudo pip3 install pandas
sudo pip3 install requests
sudo pip3 install bs4

# SET UP is complete now and deepfigure should run -----------------------------
cd ../../
sudo mv git home/ec2-user
cd home/ec2-user

sudo touch DONE.txt