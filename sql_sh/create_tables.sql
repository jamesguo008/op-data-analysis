CREATE TABLE `time_user_privileges` (
  `time_user_privilege_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `time` datetime NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `privilege_level` int(11) NOT NULL,
  PRIMARY KEY (`time_user_privilege_id`),
  UNIQUE KEY `time_user_privilege_id` (`time_user_privilege_id`),
  UNIQUE KEY `unique_index` (`time`,`user_id`,`privilege_level`),
  KEY `time` (`time`),
  KEY `user_id` (`user_id`),
  KEY `privilege_level` (`privilege_level`)
) ENGINE=InnoDB AUTO_INCREMENT=1170796 DEFAULT CHARSET=utf8;

CREATE TABLE `user_latest_deadlines` (
  `user_latest_deadline_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) NOT NULL,
  `wifi_user_action_log_id` bigint(20) NOT NULL,
  `privilege_level` int(11) NOT NULL,
  `deadline` datetime NOT NULL,
  PRIMARY KEY (`user_latest_deadline_id`),
  UNIQUE KEY `user_latest_deadline_id` (`user_latest_deadline_id`),
  UNIQUE KEY `unique_index` (`user_id`,`privilege_level`),
  KEY `user_id` (`user_id`),
  KEY `wifi_user_action_log_id` (`wifi_user_action_log_id`),
  KEY `privilege_level` (`privilege_level`)
) ENGINE=InnoDB AUTO_INCREMENT=77487 DEFAULT CHARSET=utf8;



insert into mac_user_relations (mac, user_id) select distinct mac, user_id from user_sessions;