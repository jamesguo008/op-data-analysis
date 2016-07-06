-----------------------------------import csv file from phpmyadmin-----------------------------------
load data infile "/home/sdcm/user_sessions.csv" into table user_sessions fields terminated by ',' enclosed by '"' lines terminated by '\n';

-----------------------------------import file from mysql "select into outfile" or hsv(untested)-----------------------------------
load data infile "/home/sdcm/user_sessions.csv" into table user_sessions;