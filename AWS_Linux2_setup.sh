#!/bin/bash

# Side note by adding the -y you are auto answering yes
# when program would usually ask if it should install or not

# General set up for linux 2 vm ---------------------------------

# Elevate to admin privileges to run everything as root user
sudo su
# update the yum
yum update -y
# install python 3.7
yum install -y python37
# install git to clone repos
yum install git -y

# Set up required to run pdffigures2 -----------------------------------------

# install java 8 
yum install java-1.8.0-openjdk-devel -y
# install scala 2.13.0
wget http://downloads.typesafe.com/scala/2.13.0/scala-2.13.0.tgz
tar -xzvf scala-2.13.0.tgz
rm -rf scala-2.13.0.tgz
export SCALA_HOME=/home/ec2-user/scala-2.13.0
export PATH=$PATH:/home/ec2-user/scala-2.13.0/bin
# install sbt
curl https://bintray.com/sbt/rpm/rpm | sudo tee /etc/yum.repos.d/bintray-sbt-rpm.repo
sudo yum install sbt -y

# Set up needed for deepfigures ---------------------------------------------

# install pip
curl -O https://bootstrap.pypa.io/get-pip.py
python3.7 get-pip.py --user
# install click module that is needed for manage.py in deepfigures
python3.7 -m pip install click
python3.7 -m pip install scikit-image
pip3 install scikit-image
pip3 install click
# install docker -- vm that runs nueral network to extract figures
amazon-linux-extras install docker -y
service docker start
# may need to reboot instance to have this enabled
usermod -a -G docker ec2-user 

# Getting deepfigures downloaded and ready to run -------------------------

# make a git directory and enter it 
mkdir git # the name is subject to change......
cd git
# clone edited deepfigures into git
git clone https://github.com/Julen-Lujambio/deepfigures_open.git
cd deepfigures_open
# downloads the weights for nueral network
curl -O https://s3-us-west-2.amazonaws.com/ai2-s2-research-public/deepfigures/weights.tar.gz
tar -xvf weights.tar.gz
# compiling the .jar file for deepfigures
git clone https://github.com/allenai/pdffigures2
cd pdffigures2
sbt assembly
mv target/scala-2.12/pdffigures2-assembly-0.1.0.jar ../bin
cd ..
rm -rf pdffigures2

# Install modules for web scrapper
pip3 install pandas
pip3 install requests
pip3 install bs4

# SET UP is complete now and deepfigure should run -----------------------------
cd ../../
mv git home/ec2-user
cd home/ec2-user


touch DONE.txt