#!/bin/bash
currentDir=$(pwd)
currentFolder=${PWD##*/} 

if [ "$EUID" -ne 0 ]; then
  echo -e "\n Please run with sudo.\n"
  exit 1
fi


sudo python3 $currentDir/bot.py > botlog.txt