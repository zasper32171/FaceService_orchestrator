SET @query = CONCAT('CREATE USER "', @DB_USER, '"@"%" IDENTIFIED BY "', @DB_PASSWD, '";');
PREPARE stmt FROM @query; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @query = CONCAT('GRANT ALL PRIVILEGES ON *.* TO "', @DB_USER, '"@"%";');
PREPARE stmt FROM @query; EXECUTE stmt; DEALLOCATE PREPARE stmt;

FLUSH PRIVILEGES;

CREATE DATABASE reports;
USE reports;

CREATE TABLE `packet_info` (
  `timestamp` double NOT NULL,
  `session_id` int(11) NOT NULL,
  `handler_id` int(11) NOT NULL,
  `sequence` int(11) NOT NULL,
  `event` varchar(45) NOT NULL,
  `size` int(11) DEFAULT NULL,
  PRIMARY KEY (`timestamp`,`session_id`,`handler_id`,`sequence`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `proc_info` (
  `timestamp` double NOT NULL,
  `session_id` int(11) NOT NULL,
  `handler_id` int(11) NOT NULL,
  `cpu_util` float DEFAULT NULL,
  `mem_util` float DEFAULT NULL,
  `gpu_util` int(11) DEFAULT NULL,
  `gpu_mem_util` int(11) DEFAULT NULL,
  PRIMARY KEY (`timestamp`,`session_id`,`handler_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `sys_info` (
  `timestamp` double NOT NULL,
  `node_id` int(11) NOT NULL,
  `cpu_util` float DEFAULT NULL,
  `mem_total` int(11) DEFAULT NULL,
  `mem_util` float DEFAULT NULL,
  `gpu_util` int(11) DEFAULT NULL,
  `gpu_mem_util` int(11) DEFAULT NULL,
  `gpu_clock` int(11) DEFAULT NULL,
  `gpu_power` int(11) DEFAULT NULL,
  PRIMARY KEY (`timestamp`,`node_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
