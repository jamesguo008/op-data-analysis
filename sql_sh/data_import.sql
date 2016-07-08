-----------------------------------import csv file from phpmyadmin-----------------------------------
load data infile "/home/sdcm/user_sessions.csv" into table user_sessions fields terminated by ',' enclosed by '"' lines terminated by '\n';

-----------------------------------import file from mysql "select into outfile" or hsv(untested)-----------------------------------
load data infile "/home/sdcm/user_sessions.csv" into table user_sessions;

----------------------------------- import file from hive into mysql database without sqoop ----------------------------
load data infile '/home/sdcm/labs/op-data-analysis/online-stats-20151001-20160704.tsv' into table wifi_auth_online_stats fields terminated by '\t' lines terminated by '\n' (@col1, @col2, @col3, @col4, @col5) set gw_id = @col1, mac = @col2, duration = @col3, file_date = @col4, file_time = @col5;