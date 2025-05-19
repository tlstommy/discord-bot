#!/bin/bash

currentDir=$(dirname "$PWD")
currentWorkingDir=$(pwd)
currentFolder=${PWD##*/} 

if [ "$EUID" -ne 0 ]; then
  echo -e "\n[ERROR]:  Please run with sudo.\n"
  exit 1
fi


if grep -Fxq "exit 0" /etc/rc.local; then
  sudo sed -i "/exit 0/i cd $currentWorkingDir && sudo bash $currentWorkingDir/scripts/start.sh > $currentWorkingDir/piink-log.txt 2>&1 &" /etc/rc.local
fi



sudo pip install -r $currentWorkingDir/requirements.txt --break-system-packages
