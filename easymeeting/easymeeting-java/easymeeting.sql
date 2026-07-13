/*
 Navicat Premium Data Transfer

 Source Server         : localhost
 Source Server Type    : MySQL
 Source Server Version : 50739 (5.7.39-log)
 Source Host           : localhost:3306
 Source Schema         : easymeeting

 Target Server Type    : MySQL
 Target Server Version : 50739 (5.7.39-log)
 File Encoding         : 65001

 Date: 25/06/2025 10:08:29
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for app_update
-- ----------------------------
DROP TABLE IF EXISTS `app_update`;
CREATE TABLE `app_update`  (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增ID',
  `version` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '版本号',
  `update_desc` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '更新描述',
  `create_time` datetime NULL DEFAULT NULL COMMENT '创建时间',
  `status` tinyint(1) NULL DEFAULT NULL COMMENT '0:未发布 1:灰度发布 2:全网发布',
  `grayscale_uid` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '灰度uid',
  `file_type` tinyint(1) NULL DEFAULT NULL COMMENT '文件类型0:本地文件 1:外链',
  `outer_link` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '外链地址',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `idx_key`(`version`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = 'app发布' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for cmbc_charge_code
-- ----------------------------
DROP TABLE IF EXISTS `cmbc_charge_code`;
CREATE TABLE `cmbc_charge_code`  (
  `charge_code` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '缴款码',
  `app_key` varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '应用唯一标识',
  `user_id` bigint(20) NULL DEFAULT NULL COMMENT '用户ID',
  PRIMARY KEY (`charge_code`, `app_key`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = '民生银行缴款码' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for meeting_chat_message
-- ----------------------------
DROP TABLE IF EXISTS `meeting_chat_message`;
CREATE TABLE `meeting_chat_message`  (
  `message_id` bigint(16) NOT NULL COMMENT '消息ID',
  `meeting_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '会议ID',
  `message_type` tinyint(1) NOT NULL COMMENT '消息类型',
  `message_content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '消息内容',
  `send_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人ID',
  `send_user_nick_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人昵称',
  `send_time` bigint(20) NULL DEFAULT NULL COMMENT '发送时间',
  `receive_type` tinyint(1) NULL DEFAULT NULL COMMENT '0:全员 1:指定接受人',
  `receive_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '接收联系人ID',
  `file_size` bigint(20) NULL DEFAULT NULL COMMENT '文件大小',
  `file_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件名',
  `file_type` tinyint(1) NULL DEFAULT NULL COMMENT '文件类型',
  `file_suffix` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件后缀',
  `status` tinyint(1) NULL DEFAULT 1 COMMENT '状态 0:正在发送 1:已发送',
  PRIMARY KEY (`message_id`) USING BTREE,
  INDEX `idx_meeting_id`(`meeting_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会议聊天信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for meeting_chat_message_01
-- ----------------------------
DROP TABLE IF EXISTS `meeting_chat_message_01`;
CREATE TABLE `meeting_chat_message_01`  (
  `message_id` bigint(16) NOT NULL COMMENT '消息ID',
  `meeting_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '会议ID',
  `message_type` tinyint(1) NOT NULL COMMENT '消息类型',
  `message_content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '消息内容',
  `send_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人ID',
  `send_user_nick_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人昵称',
  `send_time` bigint(20) NULL DEFAULT NULL COMMENT '发送时间',
  `receive_type` tinyint(1) NULL DEFAULT NULL COMMENT '0:全员 1:指定接受人',
  `receive_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '接收联系人ID',
  `file_size` bigint(20) NULL DEFAULT NULL COMMENT '文件大小',
  `file_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件名',
  `file_type` tinyint(1) NULL DEFAULT NULL COMMENT '文件类型',
  `file_suffix` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件后缀',
  `status` tinyint(1) NULL DEFAULT 1 COMMENT '状态 0:正在发送 1:已发送',
  PRIMARY KEY (`message_id`) USING BTREE,
  INDEX `idx_meeting_id`(`meeting_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会议聊天信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for meeting_chat_message_02
-- ----------------------------
DROP TABLE IF EXISTS `meeting_chat_message_02`;
CREATE TABLE `meeting_chat_message_02`  (
  `message_id` bigint(16) NOT NULL COMMENT '消息ID',
  `meeting_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '会议ID',
  `message_type` tinyint(1) NOT NULL COMMENT '消息类型',
  `message_content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '消息内容',
  `send_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人ID',
  `send_user_nick_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人昵称',
  `send_time` bigint(20) NULL DEFAULT NULL COMMENT '发送时间',
  `receive_type` tinyint(1) NULL DEFAULT NULL COMMENT '0:全员 1:指定接受人',
  `receive_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '接收联系人ID',
  `file_size` bigint(20) NULL DEFAULT NULL COMMENT '文件大小',
  `file_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件名',
  `file_type` tinyint(1) NULL DEFAULT NULL COMMENT '文件类型',
  `file_suffix` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件后缀',
  `status` tinyint(1) NULL DEFAULT 1 COMMENT '状态 0:正在发送 1:已发送',
  PRIMARY KEY (`message_id`) USING BTREE,
  INDEX `idx_meeting_id`(`meeting_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会议聊天信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for meeting_chat_message_03
-- ----------------------------
DROP TABLE IF EXISTS `meeting_chat_message_03`;
CREATE TABLE `meeting_chat_message_03`  (
  `message_id` bigint(16) NOT NULL COMMENT '消息ID',
  `meeting_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '会议ID',
  `message_type` tinyint(1) NOT NULL COMMENT '消息类型',
  `message_content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '消息内容',
  `send_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人ID',
  `send_user_nick_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人昵称',
  `send_time` bigint(20) NULL DEFAULT NULL COMMENT '发送时间',
  `receive_type` tinyint(1) NULL DEFAULT NULL COMMENT '0:全员 1:指定接受人',
  `receive_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '接收联系人ID',
  `file_size` bigint(20) NULL DEFAULT NULL COMMENT '文件大小',
  `file_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件名',
  `file_type` tinyint(1) NULL DEFAULT NULL COMMENT '文件类型',
  `file_suffix` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件后缀',
  `status` tinyint(1) NULL DEFAULT 1 COMMENT '状态 0:正在发送 1:已发送',
  PRIMARY KEY (`message_id`) USING BTREE,
  INDEX `idx_meeting_id`(`meeting_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会议聊天信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for meeting_chat_message_04
-- ----------------------------
DROP TABLE IF EXISTS `meeting_chat_message_04`;
CREATE TABLE `meeting_chat_message_04`  (
  `message_id` bigint(16) NOT NULL COMMENT '消息ID',
  `meeting_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '会议ID',
  `message_type` tinyint(1) NOT NULL COMMENT '消息类型',
  `message_content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '消息内容',
  `send_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人ID',
  `send_user_nick_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人昵称',
  `send_time` bigint(20) NULL DEFAULT NULL COMMENT '发送时间',
  `receive_type` tinyint(1) NULL DEFAULT NULL COMMENT '0:全员 1:指定接受人',
  `receive_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '接收联系人ID',
  `file_size` bigint(20) NULL DEFAULT NULL COMMENT '文件大小',
  `file_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件名',
  `file_type` tinyint(1) NULL DEFAULT NULL COMMENT '文件类型',
  `file_suffix` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件后缀',
  `status` tinyint(1) NULL DEFAULT 1 COMMENT '状态 0:正在发送 1:已发送',
  PRIMARY KEY (`message_id`) USING BTREE,
  INDEX `idx_meeting_id`(`meeting_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会议聊天信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for meeting_chat_message_05
-- ----------------------------
DROP TABLE IF EXISTS `meeting_chat_message_05`;
CREATE TABLE `meeting_chat_message_05`  (
  `message_id` bigint(16) NOT NULL COMMENT '消息ID',
  `meeting_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '会议ID',
  `message_type` tinyint(1) NOT NULL COMMENT '消息类型',
  `message_content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '消息内容',
  `send_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人ID',
  `send_user_nick_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人昵称',
  `send_time` bigint(20) NULL DEFAULT NULL COMMENT '发送时间',
  `receive_type` tinyint(1) NULL DEFAULT NULL COMMENT '0:全员 1:指定接受人',
  `receive_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '接收联系人ID',
  `file_size` bigint(20) NULL DEFAULT NULL COMMENT '文件大小',
  `file_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件名',
  `file_type` tinyint(1) NULL DEFAULT NULL COMMENT '文件类型',
  `file_suffix` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件后缀',
  `status` tinyint(1) NULL DEFAULT 1 COMMENT '状态 0:正在发送 1:已发送',
  PRIMARY KEY (`message_id`) USING BTREE,
  INDEX `idx_meeting_id`(`meeting_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会议聊天信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for meeting_chat_message_06
-- ----------------------------
DROP TABLE IF EXISTS `meeting_chat_message_06`;
CREATE TABLE `meeting_chat_message_06`  (
  `message_id` bigint(16) NOT NULL COMMENT '消息ID',
  `meeting_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '会议ID',
  `message_type` tinyint(1) NOT NULL COMMENT '消息类型',
  `message_content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '消息内容',
  `send_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人ID',
  `send_user_nick_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人昵称',
  `send_time` bigint(20) NULL DEFAULT NULL COMMENT '发送时间',
  `receive_type` tinyint(1) NULL DEFAULT NULL COMMENT '0:全员 1:指定接受人',
  `receive_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '接收联系人ID',
  `file_size` bigint(20) NULL DEFAULT NULL COMMENT '文件大小',
  `file_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件名',
  `file_type` tinyint(1) NULL DEFAULT NULL COMMENT '文件类型',
  `file_suffix` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件后缀',
  `status` tinyint(1) NULL DEFAULT 1 COMMENT '状态 0:正在发送 1:已发送',
  PRIMARY KEY (`message_id`) USING BTREE,
  INDEX `idx_meeting_id`(`meeting_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会议聊天信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for meeting_chat_message_07
-- ----------------------------
DROP TABLE IF EXISTS `meeting_chat_message_07`;
CREATE TABLE `meeting_chat_message_07`  (
  `message_id` bigint(16) NOT NULL COMMENT '消息ID',
  `meeting_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '会议ID',
  `message_type` tinyint(1) NOT NULL COMMENT '消息类型',
  `message_content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '消息内容',
  `send_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人ID',
  `send_user_nick_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人昵称',
  `send_time` bigint(20) NULL DEFAULT NULL COMMENT '发送时间',
  `receive_type` tinyint(1) NULL DEFAULT NULL COMMENT '0:全员 1:指定接受人',
  `receive_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '接收联系人ID',
  `file_size` bigint(20) NULL DEFAULT NULL COMMENT '文件大小',
  `file_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件名',
  `file_type` tinyint(1) NULL DEFAULT NULL COMMENT '文件类型',
  `file_suffix` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件后缀',
  `status` tinyint(1) NULL DEFAULT 1 COMMENT '状态 0:正在发送 1:已发送',
  PRIMARY KEY (`message_id`) USING BTREE,
  INDEX `idx_meeting_id`(`meeting_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会议聊天信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for meeting_chat_message_08
-- ----------------------------
DROP TABLE IF EXISTS `meeting_chat_message_08`;
CREATE TABLE `meeting_chat_message_08`  (
  `message_id` bigint(16) NOT NULL COMMENT '消息ID',
  `meeting_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '会议ID',
  `message_type` tinyint(1) NOT NULL COMMENT '消息类型',
  `message_content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '消息内容',
  `send_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人ID',
  `send_user_nick_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人昵称',
  `send_time` bigint(20) NULL DEFAULT NULL COMMENT '发送时间',
  `receive_type` tinyint(1) NULL DEFAULT NULL COMMENT '0:全员 1:指定接受人',
  `receive_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '接收联系人ID',
  `file_size` bigint(20) NULL DEFAULT NULL COMMENT '文件大小',
  `file_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件名',
  `file_type` tinyint(1) NULL DEFAULT NULL COMMENT '文件类型',
  `file_suffix` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件后缀',
  `status` tinyint(1) NULL DEFAULT 1 COMMENT '状态 0:正在发送 1:已发送',
  PRIMARY KEY (`message_id`) USING BTREE,
  INDEX `idx_meeting_id`(`meeting_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会议聊天信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for meeting_chat_message_09
-- ----------------------------
DROP TABLE IF EXISTS `meeting_chat_message_09`;
CREATE TABLE `meeting_chat_message_09`  (
  `message_id` bigint(16) NOT NULL COMMENT '消息ID',
  `meeting_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '会议ID',
  `message_type` tinyint(1) NOT NULL COMMENT '消息类型',
  `message_content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '消息内容',
  `send_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人ID',
  `send_user_nick_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人昵称',
  `send_time` bigint(20) NULL DEFAULT NULL COMMENT '发送时间',
  `receive_type` tinyint(1) NULL DEFAULT NULL COMMENT '0:全员 1:指定接受人',
  `receive_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '接收联系人ID',
  `file_size` bigint(20) NULL DEFAULT NULL COMMENT '文件大小',
  `file_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件名',
  `file_type` tinyint(1) NULL DEFAULT NULL COMMENT '文件类型',
  `file_suffix` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件后缀',
  `status` tinyint(1) NULL DEFAULT 1 COMMENT '状态 0:正在发送 1:已发送',
  PRIMARY KEY (`message_id`) USING BTREE,
  INDEX `idx_meeting_id`(`meeting_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会议聊天信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for meeting_chat_message_10
-- ----------------------------
DROP TABLE IF EXISTS `meeting_chat_message_10`;
CREATE TABLE `meeting_chat_message_10`  (
  `message_id` bigint(16) NOT NULL COMMENT '消息ID',
  `meeting_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '会议ID',
  `message_type` tinyint(1) NOT NULL COMMENT '消息类型',
  `message_content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '消息内容',
  `send_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人ID',
  `send_user_nick_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人昵称',
  `send_time` bigint(20) NULL DEFAULT NULL COMMENT '发送时间',
  `receive_type` tinyint(1) NULL DEFAULT NULL COMMENT '0:全员 1:指定接受人',
  `receive_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '接收联系人ID',
  `file_size` bigint(20) NULL DEFAULT NULL COMMENT '文件大小',
  `file_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件名',
  `file_type` tinyint(1) NULL DEFAULT NULL COMMENT '文件类型',
  `file_suffix` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件后缀',
  `status` tinyint(1) NULL DEFAULT 1 COMMENT '状态 0:正在发送 1:已发送',
  PRIMARY KEY (`message_id`) USING BTREE,
  INDEX `idx_meeting_id`(`meeting_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会议聊天信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for meeting_chat_message_11
-- ----------------------------
DROP TABLE IF EXISTS `meeting_chat_message_11`;
CREATE TABLE `meeting_chat_message_11`  (
  `message_id` bigint(16) NOT NULL COMMENT '消息ID',
  `meeting_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '会议ID',
  `message_type` tinyint(1) NOT NULL COMMENT '消息类型',
  `message_content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '消息内容',
  `send_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人ID',
  `send_user_nick_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人昵称',
  `send_time` bigint(20) NULL DEFAULT NULL COMMENT '发送时间',
  `receive_type` tinyint(1) NULL DEFAULT NULL COMMENT '0:全员 1:指定接受人',
  `receive_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '接收联系人ID',
  `file_size` bigint(20) NULL DEFAULT NULL COMMENT '文件大小',
  `file_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件名',
  `file_type` tinyint(1) NULL DEFAULT NULL COMMENT '文件类型',
  `file_suffix` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件后缀',
  `status` tinyint(1) NULL DEFAULT 1 COMMENT '状态 0:正在发送 1:已发送',
  PRIMARY KEY (`message_id`) USING BTREE,
  INDEX `idx_meeting_id`(`meeting_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会议聊天信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for meeting_chat_message_12
-- ----------------------------
DROP TABLE IF EXISTS `meeting_chat_message_12`;
CREATE TABLE `meeting_chat_message_12`  (
  `message_id` bigint(16) NOT NULL COMMENT '消息ID',
  `meeting_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '会议ID',
  `message_type` tinyint(1) NOT NULL COMMENT '消息类型',
  `message_content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '消息内容',
  `send_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人ID',
  `send_user_nick_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人昵称',
  `send_time` bigint(20) NULL DEFAULT NULL COMMENT '发送时间',
  `receive_type` tinyint(1) NULL DEFAULT NULL COMMENT '0:全员 1:指定接受人',
  `receive_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '接收联系人ID',
  `file_size` bigint(20) NULL DEFAULT NULL COMMENT '文件大小',
  `file_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件名',
  `file_type` tinyint(1) NULL DEFAULT NULL COMMENT '文件类型',
  `file_suffix` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件后缀',
  `status` tinyint(1) NULL DEFAULT 1 COMMENT '状态 0:正在发送 1:已发送',
  PRIMARY KEY (`message_id`) USING BTREE,
  INDEX `idx_meeting_id`(`meeting_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会议聊天信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for meeting_chat_message_13
-- ----------------------------
DROP TABLE IF EXISTS `meeting_chat_message_13`;
CREATE TABLE `meeting_chat_message_13`  (
  `message_id` bigint(16) NOT NULL COMMENT '消息ID',
  `meeting_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '会议ID',
  `message_type` tinyint(1) NOT NULL COMMENT '消息类型',
  `message_content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '消息内容',
  `send_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人ID',
  `send_user_nick_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人昵称',
  `send_time` bigint(20) NULL DEFAULT NULL COMMENT '发送时间',
  `receive_type` tinyint(1) NULL DEFAULT NULL COMMENT '0:全员 1:指定接受人',
  `receive_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '接收联系人ID',
  `file_size` bigint(20) NULL DEFAULT NULL COMMENT '文件大小',
  `file_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件名',
  `file_type` tinyint(1) NULL DEFAULT NULL COMMENT '文件类型',
  `file_suffix` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件后缀',
  `status` tinyint(1) NULL DEFAULT 1 COMMENT '状态 0:正在发送 1:已发送',
  PRIMARY KEY (`message_id`) USING BTREE,
  INDEX `idx_meeting_id`(`meeting_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会议聊天信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for meeting_chat_message_14
-- ----------------------------
DROP TABLE IF EXISTS `meeting_chat_message_14`;
CREATE TABLE `meeting_chat_message_14`  (
  `message_id` bigint(16) NOT NULL COMMENT '消息ID',
  `meeting_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '会议ID',
  `message_type` tinyint(1) NOT NULL COMMENT '消息类型',
  `message_content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '消息内容',
  `send_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人ID',
  `send_user_nick_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人昵称',
  `send_time` bigint(20) NULL DEFAULT NULL COMMENT '发送时间',
  `receive_type` tinyint(1) NULL DEFAULT NULL COMMENT '0:全员 1:指定接受人',
  `receive_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '接收联系人ID',
  `file_size` bigint(20) NULL DEFAULT NULL COMMENT '文件大小',
  `file_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件名',
  `file_type` tinyint(1) NULL DEFAULT NULL COMMENT '文件类型',
  `file_suffix` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件后缀',
  `status` tinyint(1) NULL DEFAULT 1 COMMENT '状态 0:正在发送 1:已发送',
  PRIMARY KEY (`message_id`) USING BTREE,
  INDEX `idx_meeting_id`(`meeting_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会议聊天信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for meeting_chat_message_15
-- ----------------------------
DROP TABLE IF EXISTS `meeting_chat_message_15`;
CREATE TABLE `meeting_chat_message_15`  (
  `message_id` bigint(16) NOT NULL COMMENT '消息ID',
  `meeting_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '会议ID',
  `message_type` tinyint(1) NOT NULL COMMENT '消息类型',
  `message_content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '消息内容',
  `send_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人ID',
  `send_user_nick_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人昵称',
  `send_time` bigint(20) NULL DEFAULT NULL COMMENT '发送时间',
  `receive_type` tinyint(1) NULL DEFAULT NULL COMMENT '0:全员 1:指定接受人',
  `receive_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '接收联系人ID',
  `file_size` bigint(20) NULL DEFAULT NULL COMMENT '文件大小',
  `file_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件名',
  `file_type` tinyint(1) NULL DEFAULT NULL COMMENT '文件类型',
  `file_suffix` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件后缀',
  `status` tinyint(1) NULL DEFAULT 1 COMMENT '状态 0:正在发送 1:已发送',
  PRIMARY KEY (`message_id`) USING BTREE,
  INDEX `idx_meeting_id`(`meeting_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会议聊天信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for meeting_chat_message_16
-- ----------------------------
DROP TABLE IF EXISTS `meeting_chat_message_16`;
CREATE TABLE `meeting_chat_message_16`  (
  `message_id` bigint(16) NOT NULL COMMENT '消息ID',
  `meeting_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '会议ID',
  `message_type` tinyint(1) NOT NULL COMMENT '消息类型',
  `message_content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '消息内容',
  `send_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人ID',
  `send_user_nick_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人昵称',
  `send_time` bigint(20) NULL DEFAULT NULL COMMENT '发送时间',
  `receive_type` tinyint(1) NULL DEFAULT NULL COMMENT '0:全员 1:指定接受人',
  `receive_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '接收联系人ID',
  `file_size` bigint(20) NULL DEFAULT NULL COMMENT '文件大小',
  `file_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件名',
  `file_type` tinyint(1) NULL DEFAULT NULL COMMENT '文件类型',
  `file_suffix` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件后缀',
  `status` tinyint(1) NULL DEFAULT 1 COMMENT '状态 0:正在发送 1:已发送',
  PRIMARY KEY (`message_id`) USING BTREE,
  INDEX `idx_meeting_id`(`meeting_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会议聊天信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for meeting_chat_message_17
-- ----------------------------
DROP TABLE IF EXISTS `meeting_chat_message_17`;
CREATE TABLE `meeting_chat_message_17`  (
  `message_id` bigint(16) NOT NULL COMMENT '消息ID',
  `meeting_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '会议ID',
  `message_type` tinyint(1) NOT NULL COMMENT '消息类型',
  `message_content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '消息内容',
  `send_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人ID',
  `send_user_nick_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人昵称',
  `send_time` bigint(20) NULL DEFAULT NULL COMMENT '发送时间',
  `receive_type` tinyint(1) NULL DEFAULT NULL COMMENT '0:全员 1:指定接受人',
  `receive_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '接收联系人ID',
  `file_size` bigint(20) NULL DEFAULT NULL COMMENT '文件大小',
  `file_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件名',
  `file_type` tinyint(1) NULL DEFAULT NULL COMMENT '文件类型',
  `file_suffix` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件后缀',
  `status` tinyint(1) NULL DEFAULT 1 COMMENT '状态 0:正在发送 1:已发送',
  PRIMARY KEY (`message_id`) USING BTREE,
  INDEX `idx_meeting_id`(`meeting_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会议聊天信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for meeting_chat_message_18
-- ----------------------------
DROP TABLE IF EXISTS `meeting_chat_message_18`;
CREATE TABLE `meeting_chat_message_18`  (
  `message_id` bigint(16) NOT NULL COMMENT '消息ID',
  `meeting_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '会议ID',
  `message_type` tinyint(1) NOT NULL COMMENT '消息类型',
  `message_content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '消息内容',
  `send_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人ID',
  `send_user_nick_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人昵称',
  `send_time` bigint(20) NULL DEFAULT NULL COMMENT '发送时间',
  `receive_type` tinyint(1) NULL DEFAULT NULL COMMENT '0:全员 1:指定接受人',
  `receive_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '接收联系人ID',
  `file_size` bigint(20) NULL DEFAULT NULL COMMENT '文件大小',
  `file_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件名',
  `file_type` tinyint(1) NULL DEFAULT NULL COMMENT '文件类型',
  `file_suffix` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件后缀',
  `status` tinyint(1) NULL DEFAULT 1 COMMENT '状态 0:正在发送 1:已发送',
  PRIMARY KEY (`message_id`) USING BTREE,
  INDEX `idx_meeting_id`(`meeting_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会议聊天信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for meeting_chat_message_19
-- ----------------------------
DROP TABLE IF EXISTS `meeting_chat_message_19`;
CREATE TABLE `meeting_chat_message_19`  (
  `message_id` bigint(16) NOT NULL COMMENT '消息ID',
  `meeting_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '会议ID',
  `message_type` tinyint(1) NOT NULL COMMENT '消息类型',
  `message_content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '消息内容',
  `send_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人ID',
  `send_user_nick_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人昵称',
  `send_time` bigint(20) NULL DEFAULT NULL COMMENT '发送时间',
  `receive_type` tinyint(1) NULL DEFAULT NULL COMMENT '0:全员 1:指定接受人',
  `receive_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '接收联系人ID',
  `file_size` bigint(20) NULL DEFAULT NULL COMMENT '文件大小',
  `file_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件名',
  `file_type` tinyint(1) NULL DEFAULT NULL COMMENT '文件类型',
  `file_suffix` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件后缀',
  `status` tinyint(1) NULL DEFAULT 1 COMMENT '状态 0:正在发送 1:已发送',
  PRIMARY KEY (`message_id`) USING BTREE,
  INDEX `idx_meeting_id`(`meeting_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会议聊天信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for meeting_chat_message_20
-- ----------------------------
DROP TABLE IF EXISTS `meeting_chat_message_20`;
CREATE TABLE `meeting_chat_message_20`  (
  `message_id` bigint(16) NOT NULL COMMENT '消息ID',
  `meeting_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '会议ID',
  `message_type` tinyint(1) NOT NULL COMMENT '消息类型',
  `message_content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '消息内容',
  `send_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人ID',
  `send_user_nick_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人昵称',
  `send_time` bigint(20) NULL DEFAULT NULL COMMENT '发送时间',
  `receive_type` tinyint(1) NULL DEFAULT NULL COMMENT '0:全员 1:指定接受人',
  `receive_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '接收联系人ID',
  `file_size` bigint(20) NULL DEFAULT NULL COMMENT '文件大小',
  `file_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件名',
  `file_type` tinyint(1) NULL DEFAULT NULL COMMENT '文件类型',
  `file_suffix` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件后缀',
  `status` tinyint(1) NULL DEFAULT 1 COMMENT '状态 0:正在发送 1:已发送',
  PRIMARY KEY (`message_id`) USING BTREE,
  INDEX `idx_meeting_id`(`meeting_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会议聊天信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for meeting_chat_message_21
-- ----------------------------
DROP TABLE IF EXISTS `meeting_chat_message_21`;
CREATE TABLE `meeting_chat_message_21`  (
  `message_id` bigint(16) NOT NULL COMMENT '消息ID',
  `meeting_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '会议ID',
  `message_type` tinyint(1) NOT NULL COMMENT '消息类型',
  `message_content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '消息内容',
  `send_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人ID',
  `send_user_nick_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人昵称',
  `send_time` bigint(20) NULL DEFAULT NULL COMMENT '发送时间',
  `receive_type` tinyint(1) NULL DEFAULT NULL COMMENT '0:全员 1:指定接受人',
  `receive_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '接收联系人ID',
  `file_size` bigint(20) NULL DEFAULT NULL COMMENT '文件大小',
  `file_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件名',
  `file_type` tinyint(1) NULL DEFAULT NULL COMMENT '文件类型',
  `file_suffix` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件后缀',
  `status` tinyint(1) NULL DEFAULT 1 COMMENT '状态 0:正在发送 1:已发送',
  PRIMARY KEY (`message_id`) USING BTREE,
  INDEX `idx_meeting_id`(`meeting_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会议聊天信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for meeting_chat_message_22
-- ----------------------------
DROP TABLE IF EXISTS `meeting_chat_message_22`;
CREATE TABLE `meeting_chat_message_22`  (
  `message_id` bigint(16) NOT NULL COMMENT '消息ID',
  `meeting_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '会议ID',
  `message_type` tinyint(1) NOT NULL COMMENT '消息类型',
  `message_content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '消息内容',
  `send_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人ID',
  `send_user_nick_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人昵称',
  `send_time` bigint(20) NULL DEFAULT NULL COMMENT '发送时间',
  `receive_type` tinyint(1) NULL DEFAULT NULL COMMENT '0:全员 1:指定接受人',
  `receive_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '接收联系人ID',
  `file_size` bigint(20) NULL DEFAULT NULL COMMENT '文件大小',
  `file_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件名',
  `file_type` tinyint(1) NULL DEFAULT NULL COMMENT '文件类型',
  `file_suffix` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件后缀',
  `status` tinyint(1) NULL DEFAULT 1 COMMENT '状态 0:正在发送 1:已发送',
  PRIMARY KEY (`message_id`) USING BTREE,
  INDEX `idx_meeting_id`(`meeting_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会议聊天信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for meeting_chat_message_23
-- ----------------------------
DROP TABLE IF EXISTS `meeting_chat_message_23`;
CREATE TABLE `meeting_chat_message_23`  (
  `message_id` bigint(16) NOT NULL COMMENT '消息ID',
  `meeting_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '会议ID',
  `message_type` tinyint(1) NOT NULL COMMENT '消息类型',
  `message_content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '消息内容',
  `send_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人ID',
  `send_user_nick_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人昵称',
  `send_time` bigint(20) NULL DEFAULT NULL COMMENT '发送时间',
  `receive_type` tinyint(1) NULL DEFAULT NULL COMMENT '0:全员 1:指定接受人',
  `receive_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '接收联系人ID',
  `file_size` bigint(20) NULL DEFAULT NULL COMMENT '文件大小',
  `file_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件名',
  `file_type` tinyint(1) NULL DEFAULT NULL COMMENT '文件类型',
  `file_suffix` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件后缀',
  `status` tinyint(1) NULL DEFAULT 1 COMMENT '状态 0:正在发送 1:已发送',
  PRIMARY KEY (`message_id`) USING BTREE,
  INDEX `idx_meeting_id`(`meeting_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会议聊天信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for meeting_chat_message_24
-- ----------------------------
DROP TABLE IF EXISTS `meeting_chat_message_24`;
CREATE TABLE `meeting_chat_message_24`  (
  `message_id` bigint(16) NOT NULL COMMENT '消息ID',
  `meeting_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '会议ID',
  `message_type` tinyint(1) NOT NULL COMMENT '消息类型',
  `message_content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '消息内容',
  `send_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人ID',
  `send_user_nick_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人昵称',
  `send_time` bigint(20) NULL DEFAULT NULL COMMENT '发送时间',
  `receive_type` tinyint(1) NULL DEFAULT NULL COMMENT '0:全员 1:指定接受人',
  `receive_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '接收联系人ID',
  `file_size` bigint(20) NULL DEFAULT NULL COMMENT '文件大小',
  `file_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件名',
  `file_type` tinyint(1) NULL DEFAULT NULL COMMENT '文件类型',
  `file_suffix` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件后缀',
  `status` tinyint(1) NULL DEFAULT 1 COMMENT '状态 0:正在发送 1:已发送',
  PRIMARY KEY (`message_id`) USING BTREE,
  INDEX `idx_meeting_id`(`meeting_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会议聊天信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for meeting_chat_message_25
-- ----------------------------
DROP TABLE IF EXISTS `meeting_chat_message_25`;
CREATE TABLE `meeting_chat_message_25`  (
  `message_id` bigint(16) NOT NULL COMMENT '消息ID',
  `meeting_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '会议ID',
  `message_type` tinyint(1) NOT NULL COMMENT '消息类型',
  `message_content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '消息内容',
  `send_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人ID',
  `send_user_nick_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人昵称',
  `send_time` bigint(20) NULL DEFAULT NULL COMMENT '发送时间',
  `receive_type` tinyint(1) NULL DEFAULT NULL COMMENT '0:全员 1:指定接受人',
  `receive_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '接收联系人ID',
  `file_size` bigint(20) NULL DEFAULT NULL COMMENT '文件大小',
  `file_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件名',
  `file_type` tinyint(1) NULL DEFAULT NULL COMMENT '文件类型',
  `file_suffix` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件后缀',
  `status` tinyint(1) NULL DEFAULT 1 COMMENT '状态 0:正在发送 1:已发送',
  PRIMARY KEY (`message_id`) USING BTREE,
  INDEX `idx_meeting_id`(`meeting_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会议聊天信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for meeting_chat_message_26
-- ----------------------------
DROP TABLE IF EXISTS `meeting_chat_message_26`;
CREATE TABLE `meeting_chat_message_26`  (
  `message_id` bigint(16) NOT NULL COMMENT '消息ID',
  `meeting_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '会议ID',
  `message_type` tinyint(1) NOT NULL COMMENT '消息类型',
  `message_content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '消息内容',
  `send_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人ID',
  `send_user_nick_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人昵称',
  `send_time` bigint(20) NULL DEFAULT NULL COMMENT '发送时间',
  `receive_type` tinyint(1) NULL DEFAULT NULL COMMENT '0:全员 1:指定接受人',
  `receive_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '接收联系人ID',
  `file_size` bigint(20) NULL DEFAULT NULL COMMENT '文件大小',
  `file_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件名',
  `file_type` tinyint(1) NULL DEFAULT NULL COMMENT '文件类型',
  `file_suffix` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件后缀',
  `status` tinyint(1) NULL DEFAULT 1 COMMENT '状态 0:正在发送 1:已发送',
  PRIMARY KEY (`message_id`) USING BTREE,
  INDEX `idx_meeting_id`(`meeting_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会议聊天信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for meeting_chat_message_27
-- ----------------------------
DROP TABLE IF EXISTS `meeting_chat_message_27`;
CREATE TABLE `meeting_chat_message_27`  (
  `message_id` bigint(16) NOT NULL COMMENT '消息ID',
  `meeting_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '会议ID',
  `message_type` tinyint(1) NOT NULL COMMENT '消息类型',
  `message_content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '消息内容',
  `send_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人ID',
  `send_user_nick_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人昵称',
  `send_time` bigint(20) NULL DEFAULT NULL COMMENT '发送时间',
  `receive_type` tinyint(1) NULL DEFAULT NULL COMMENT '0:全员 1:指定接受人',
  `receive_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '接收联系人ID',
  `file_size` bigint(20) NULL DEFAULT NULL COMMENT '文件大小',
  `file_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件名',
  `file_type` tinyint(1) NULL DEFAULT NULL COMMENT '文件类型',
  `file_suffix` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件后缀',
  `status` tinyint(1) NULL DEFAULT 1 COMMENT '状态 0:正在发送 1:已发送',
  PRIMARY KEY (`message_id`) USING BTREE,
  INDEX `idx_meeting_id`(`meeting_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会议聊天信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for meeting_chat_message_28
-- ----------------------------
DROP TABLE IF EXISTS `meeting_chat_message_28`;
CREATE TABLE `meeting_chat_message_28`  (
  `message_id` bigint(16) NOT NULL COMMENT '消息ID',
  `meeting_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '会议ID',
  `message_type` tinyint(1) NOT NULL COMMENT '消息类型',
  `message_content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '消息内容',
  `send_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人ID',
  `send_user_nick_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人昵称',
  `send_time` bigint(20) NULL DEFAULT NULL COMMENT '发送时间',
  `receive_type` tinyint(1) NULL DEFAULT NULL COMMENT '0:全员 1:指定接受人',
  `receive_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '接收联系人ID',
  `file_size` bigint(20) NULL DEFAULT NULL COMMENT '文件大小',
  `file_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件名',
  `file_type` tinyint(1) NULL DEFAULT NULL COMMENT '文件类型',
  `file_suffix` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件后缀',
  `status` tinyint(1) NULL DEFAULT 1 COMMENT '状态 0:正在发送 1:已发送',
  PRIMARY KEY (`message_id`) USING BTREE,
  INDEX `idx_meeting_id`(`meeting_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会议聊天信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for meeting_chat_message_29
-- ----------------------------
DROP TABLE IF EXISTS `meeting_chat_message_29`;
CREATE TABLE `meeting_chat_message_29`  (
  `message_id` bigint(16) NOT NULL COMMENT '消息ID',
  `meeting_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '会议ID',
  `message_type` tinyint(1) NOT NULL COMMENT '消息类型',
  `message_content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '消息内容',
  `send_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人ID',
  `send_user_nick_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人昵称',
  `send_time` bigint(20) NULL DEFAULT NULL COMMENT '发送时间',
  `receive_type` tinyint(1) NULL DEFAULT NULL COMMENT '0:全员 1:指定接受人',
  `receive_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '接收联系人ID',
  `file_size` bigint(20) NULL DEFAULT NULL COMMENT '文件大小',
  `file_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件名',
  `file_type` tinyint(1) NULL DEFAULT NULL COMMENT '文件类型',
  `file_suffix` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件后缀',
  `status` tinyint(1) NULL DEFAULT 1 COMMENT '状态 0:正在发送 1:已发送',
  PRIMARY KEY (`message_id`) USING BTREE,
  INDEX `idx_meeting_id`(`meeting_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会议聊天信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for meeting_chat_message_30
-- ----------------------------
DROP TABLE IF EXISTS `meeting_chat_message_30`;
CREATE TABLE `meeting_chat_message_30`  (
  `message_id` bigint(16) NOT NULL COMMENT '消息ID',
  `meeting_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '会议ID',
  `message_type` tinyint(1) NOT NULL COMMENT '消息类型',
  `message_content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '消息内容',
  `send_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人ID',
  `send_user_nick_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人昵称',
  `send_time` bigint(20) NULL DEFAULT NULL COMMENT '发送时间',
  `receive_type` tinyint(1) NULL DEFAULT NULL COMMENT '0:全员 1:指定接受人',
  `receive_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '接收联系人ID',
  `file_size` bigint(20) NULL DEFAULT NULL COMMENT '文件大小',
  `file_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件名',
  `file_type` tinyint(1) NULL DEFAULT NULL COMMENT '文件类型',
  `file_suffix` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件后缀',
  `status` tinyint(1) NULL DEFAULT 1 COMMENT '状态 0:正在发送 1:已发送',
  PRIMARY KEY (`message_id`) USING BTREE,
  INDEX `idx_meeting_id`(`meeting_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会议聊天信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for meeting_chat_message_31
-- ----------------------------
DROP TABLE IF EXISTS `meeting_chat_message_31`;
CREATE TABLE `meeting_chat_message_31`  (
  `message_id` bigint(16) NOT NULL COMMENT '消息ID',
  `meeting_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '会议ID',
  `message_type` tinyint(1) NOT NULL COMMENT '消息类型',
  `message_content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '消息内容',
  `send_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人ID',
  `send_user_nick_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人昵称',
  `send_time` bigint(20) NULL DEFAULT NULL COMMENT '发送时间',
  `receive_type` tinyint(1) NULL DEFAULT NULL COMMENT '0:全员 1:指定接受人',
  `receive_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '接收联系人ID',
  `file_size` bigint(20) NULL DEFAULT NULL COMMENT '文件大小',
  `file_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件名',
  `file_type` tinyint(1) NULL DEFAULT NULL COMMENT '文件类型',
  `file_suffix` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件后缀',
  `status` tinyint(1) NULL DEFAULT 1 COMMENT '状态 0:正在发送 1:已发送',
  PRIMARY KEY (`message_id`) USING BTREE,
  INDEX `idx_meeting_id`(`meeting_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会议聊天信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for meeting_chat_message_32
-- ----------------------------
DROP TABLE IF EXISTS `meeting_chat_message_32`;
CREATE TABLE `meeting_chat_message_32`  (
  `message_id` bigint(16) NOT NULL COMMENT '消息ID',
  `meeting_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '会议ID',
  `message_type` tinyint(1) NOT NULL COMMENT '消息类型',
  `message_content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '消息内容',
  `send_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人ID',
  `send_user_nick_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '发送人昵称',
  `send_time` bigint(20) NULL DEFAULT NULL COMMENT '发送时间',
  `receive_type` tinyint(1) NULL DEFAULT NULL COMMENT '0:全员 1:指定接受人',
  `receive_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '接收联系人ID',
  `file_size` bigint(20) NULL DEFAULT NULL COMMENT '文件大小',
  `file_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件名',
  `file_type` tinyint(1) NULL DEFAULT NULL COMMENT '文件类型',
  `file_suffix` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '文件后缀',
  `status` tinyint(1) NULL DEFAULT 1 COMMENT '状态 0:正在发送 1:已发送',
  PRIMARY KEY (`message_id`) USING BTREE,
  INDEX `idx_meeting_id`(`meeting_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会议聊天信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for meeting_info
-- ----------------------------
DROP TABLE IF EXISTS `meeting_info`;
CREATE TABLE `meeting_info`  (
  `meeting_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '会议ID',
  `meeting_no` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '会议号',
  `meeting_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '会议主题',
  `create_time` datetime NULL DEFAULT NULL COMMENT '创建时间',
  `create_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '创建人',
  `join_type` tinyint(4) NULL DEFAULT NULL COMMENT '加入类型0:任何人可以加入 1:密码加入 2:联系人加入',
  `join_password` varchar(5) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '加入密码',
  `start_time` datetime NULL DEFAULT NULL COMMENT '开始时间',
  `end_time` datetime NULL DEFAULT NULL COMMENT '结束时间',
  `status` tinyint(1) NULL DEFAULT NULL COMMENT '状态 0:进行中 1:已结束',
  PRIMARY KEY (`meeting_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会议信息' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for meeting_member
-- ----------------------------
DROP TABLE IF EXISTS `meeting_member`;
CREATE TABLE `meeting_member`  (
  `meeting_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '会议ID',
  `user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '用户ID',
  `nick_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '昵称',
  `last_join_time` datetime NULL DEFAULT NULL COMMENT '最后入会时间',
  `status` tinyint(4) NULL DEFAULT NULL COMMENT '1:正常 0:已删除 -1被踢出会议',
  `member_type` tinyint(4) NULL DEFAULT NULL COMMENT '0:普通成员 1:主持人',
  `meeting_status` tinyint(4) NULL DEFAULT NULL COMMENT '状态 0:已结束 1:进行中',
  PRIMARY KEY (`meeting_id`, `user_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '参会人员' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for meeting_reserve
-- ----------------------------
DROP TABLE IF EXISTS `meeting_reserve`;
CREATE TABLE `meeting_reserve`  (
  `meeting_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '会议ID',
  `meeting_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '会议主题',
  `join_type` tinyint(4) NULL DEFAULT NULL COMMENT '加入类型0:任何人可以加入 1:密码加入 2:联系人加入',
  `join_password` varchar(5) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '加入密码',
  `duration` int(11) NULL DEFAULT NULL COMMENT '持续时间分钟',
  `start_time` datetime NULL DEFAULT NULL COMMENT '开始时间',
  `create_time` datetime NULL DEFAULT NULL COMMENT '创建时间',
  `create_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '创建人',
  `status` tinyint(1) NULL DEFAULT NULL COMMENT '0:未结束 1:已结束',
  PRIMARY KEY (`meeting_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会议预约' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for meeting_reserve_member
-- ----------------------------
DROP TABLE IF EXISTS `meeting_reserve_member`;
CREATE TABLE `meeting_reserve_member`  (
  `meeting_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '会议ID',
  `invite_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '邀请人ID',
  PRIMARY KEY (`meeting_id`, `invite_user_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '会议预约成员' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for user_contact
-- ----------------------------
DROP TABLE IF EXISTS `user_contact`;
CREATE TABLE `user_contact`  (
  `user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '用户ID',
  `contact_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '联系人ID',
  `status` tinyint(1) NULL DEFAULT NULL COMMENT '状态 0:待处理 1:好友 2:已删除好友 3:已拉黑好友',
  `last_update_time` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
  PRIMARY KEY (`user_id`, `contact_id`) USING BTREE,
  INDEX `idx_contact_id`(`contact_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '联系人' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for user_contact_apply
-- ----------------------------
DROP TABLE IF EXISTS `user_contact_apply`;
CREATE TABLE `user_contact_apply`  (
  `apply_id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增ID',
  `apply_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '申请人id',
  `receive_user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '接收人ID',
  `last_apply_time` bigint(20) NULL DEFAULT NULL COMMENT '最后申请时间',
  `status` tinyint(1) NULL DEFAULT NULL COMMENT '状态0:待处理 1:已同意  2:已拒绝 3:已拉黑',
  PRIMARY KEY (`apply_id`) USING BTREE,
  UNIQUE INDEX `idx_key`(`apply_user_id`, `receive_user_id`) USING BTREE,
  INDEX `idx_last_apply_time`(`last_apply_time`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 136938 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '联系人申请' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for user_info
-- ----------------------------
DROP TABLE IF EXISTS `user_info`;
CREATE TABLE `user_info`  (
  `user_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '用户ID',
  `email` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '邮箱',
  `nick_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '昵称',
  `join_type` tinyint(1) NULL DEFAULT NULL COMMENT '0:直接加入  1:同意后加好友',
  `sex` tinyint(1) NULL DEFAULT NULL COMMENT '性别 0:女 1:男',
  `password` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '密码',
  `status` tinyint(1) NULL DEFAULT NULL COMMENT '状态',
  `create_time` datetime NULL DEFAULT NULL COMMENT '创建时间',
  `last_login_time` bigint(20) NULL DEFAULT NULL COMMENT '最后登录时间',
  `last_off_time` bigint(13) NULL DEFAULT NULL COMMENT '最后离开时间',
  `meeting_no` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '个人会议号',
  PRIMARY KEY (`user_id`) USING BTREE,
  UNIQUE INDEX `idx_key_email`(`email`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '用户信息' ROW_FORMAT = DYNAMIC;

SET FOREIGN_KEY_CHECKS = 1;
