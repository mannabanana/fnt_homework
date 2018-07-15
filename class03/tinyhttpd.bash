#!/bin/bash
CHECK=($(lsof | awk '$1 ~ /^httpd$/' | wc -l))
if [ $CHECK -eq 0 ]
then
cd /home/user14/homework/materials/class03/src/tinyhttpd/tinyhttpd/
if [ ! -f /root/httpd_start.log ]
then
touch /root/httpd_start.log
fi
echo `date '+%d-%m-%Y %H:%M:%S'` "httpd was not running, starting..." >> /root/httpd_start.log
./httpd
else
echo "httpd is already running"
fi