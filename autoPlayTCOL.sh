#!/bin/bash

export FOLDER_TCOL=`date "+%m-%d-%A-%B-%Y"`

echo "Playing $FOLDER_TCOL"

# log start and end of playing  (which folder) using wget to url on infiniterecursion

#configure vlc to :
# not show osd
# go fullscreen
# floating on top
# not check updates
# try to loop endless through list of files

# Adapt these paths to production mac-mini etc
/Applications/MacPorts/VLC.app/Contents/MacOS/VLC --loop --no-osd --fullscreen --video-on-top --no-video-title-on-show /Volumes/TCOL_daily_log_0/$FOLDER_TCOL/*.mov


