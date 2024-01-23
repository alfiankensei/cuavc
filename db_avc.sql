/*
 Navicat Premium Data Transfer

 Source Server         : Rasp AVC
 Source Server Type    : MySQL
 Source Server Version : 100521
 Source Host           : 172.20.5.132:3306
 Source Schema         : db_avc

 Target Server Type    : MySQL
 Target Server Version : 100521
 File Encoding         : 65001

 Date: 23/01/2024 10:43:31
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for command_log
-- ----------------------------
DROP TABLE IF EXISTS `command_log`;
CREATE TABLE `command_log`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cmd_id` tinyint(4) NULL DEFAULT NULL,
  `server_time` timestamp(0) NULL DEFAULT current_timestamp(0),
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 122164 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for present_avc
-- ----------------------------
DROP TABLE IF EXISTS `present_avc`;
CREATE TABLE `present_avc`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `gardu_id` tinyint(4) NULL DEFAULT NULL,
  `golongan_avc` tinyint(4) NULL DEFAULT 0,
  `golongan_gto` tinyint(4) NULL DEFAULT 0,
  `path_image` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `status` tinyint(4) NULL DEFAULT 0,
  `detect_time` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `server_time` timestamp(0) NULL DEFAULT current_timestamp(0),
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 60831 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
