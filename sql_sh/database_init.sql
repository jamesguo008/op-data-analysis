Create DATABASE op_data_analysis default charset utf8;
grant all privileges on op_data_analysis.* to op_data_analysis@localhost identified by 'op_data_analysis';flush privileges;
grant all privileges on op_data_analysis.* to op_data_analysis@'%' identified by 'op_data_analysis';flush privileges;

CREATE TABLE `user_sessions` (
  `user_session_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '主键',
  `user_id` bigint(20) unsigned NOT NULL,
  `gw_id` varchar(40) COLLATE utf8_unicode_ci DEFAULT NULL,
  `mac` varchar(40) COLLATE utf8_unicode_ci NOT NULL COMMENT '本次登录的mac地址',
  `access_token` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `grant_type` varchar(40) COLLATE utf8_unicode_ci NOT NULL,
  `scope` varchar(160) COLLATE utf8_unicode_ci DEFAULT NULL,
  `ip` varchar(40) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '本次登录的ip地址',
  `agent` varchar(80) COLLATE utf8_unicode_ci DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `expired_at` datetime NOT NULL COMMENT '会话过期时间',
  `revoked_at` datetime DEFAULT NULL COMMENT '会话主动断开时间',
  `status` tinyint(4) NOT NULL COMMENT '会话状态。1-有效',
  `redirect_url` varchar(2000) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`user_session_id`),
  UNIQUE KEY `access_token` (`access_token`),
  KEY `user_id` (`user_id`),
  KEY `mac` (`mac`),
  KEY `gw_id` (`gw_id`),
  KEY `status` (`status`)
) ENGINE=InnoDB AUTO_INCREMENT=3076783 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='用户会话信息'

CREATE TABLE `device_factory_relations` (
  `name` varchar(200) NOT NULL,
  `factory_sequence_id` varchar(200) NOT NULL,
  `device_sequence_id` varchar(200) NOT NULL,
  `site_name` varchar(200) NOT NULL,
  KEY `factory_sequence_id` (`factory_sequence_id`),
  KEY `device_sequence_id` (`device_sequence_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `gw_change_points` (
  `gw_change_point_id` int(11) NOT NULL,
  `version` int(11) NOT NULL,
  `gw_id` varchar(30) DEFAULT NULL,
  `account_name` varchar(30) DEFAULT NULL,
  `start_time` datetime DEFAULT NULL,
  `end_time` datetime DEFAULT NULL,
  `next_use_time` datetime DEFAULT NULL,
  `ralation_effective` int(11) DEFAULT NULL,
  `device_id` int(11) DEFAULT NULL,
  `create_time` datetime DEFAULT NULL,
  `modify_time` datetime DEFAULT NULL,
  `creator` int(11) DEFAULT NULL,
  `deleted` int(11) DEFAULT NULL,
  PRIMARY KEY (`gw_change_point_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;