-----------------------------------session ids-----------------------------------

CREATE TABLE `tmp_user_max_non_public_session_ids` (
  `user_id` bigint(20) DEFAULT NULL,
  `user_session_id` bigint(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

insert into tmp_user_max_non_public_session_ids
select user_id,max(user_session_id)
from user_sessions
where gw_id <> 'PUBLIC' and gw_id not like '100-%' and gw_id not like '000-%'
group by user_id;

-----------------------------------user account-----------------------------------

CREATE TABLE `tmp_user_accounts` (
  `user_id` bigint,
  `gw_id` varchar(30) DEFAULT NULL,
  `session_created_at` datetime DEFAULT NULL,
  `account_name` varchar(30) DEFAULT NULL,
  `start_time` datetime DEFAULT NULL,
  `next_use_time` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

insert into tmp_user_accounts
select v1.*,gcp.account_name,gcp.start_time,gcp.next_use_time from
(select a.user_id,b.gw_id,b.created_at from tmp_user_max_non_public_session_ids a left join user_sessions b on a.user_session_id=b.user_session_id) v1
left join gw_change_points gcp
on v1.created_at between gcp.start_time and gcp.next_use_time and v1.gw_id=gcp.gw_id

-----------------------------------final get user factory relation-----------------------------------

CREATE TABLE `user_factory_from_last_non_public` (
  `user_id` bigint,
  `gw_id` varchar(30) DEFAULT NULL,
  `account_name` varchar(200) DEFAULT NULL,
  `factory_sequence_id` varchar(200) NOT NULL,
  `name` varchar(200) NOT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

insert into user_factory_from_last_non_public
select ua.user_id,ua.gw_id,ua.account_name,dfr.factory_sequence_id,dfr.name
from tmp_user_accounts ua
left join device_factory_relations dfr
on dfr.device_sequence_id=ua.account_name;