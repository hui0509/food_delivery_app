/*
 Navicat Premium Data Transfer

 Source Server         : local
 Source Server Type    : MySQL
 Source Server Version : 50726
 Source Host           : localhost:3306
 Source Schema         : dba

 Target Server Type    : MySQL
 Target Server Version : 50726
 File Encoding         : 65001

 Date: 13/02/2026 22:43:38
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for cart
-- ----------------------------
DROP TABLE IF EXISTS `cart`;
CREATE TABLE `cart`  (
  `cart_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_phone` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `shop_id` int(11) NOT NULL,
  `dish_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL DEFAULT 1,
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cart_id`) USING BTREE,
  INDEX `user_phone`(`user_phone`) USING BTREE,
  INDEX `shop_id`(`shop_id`) USING BTREE,
  INDEX `dish_id`(`dish_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of cart
-- ----------------------------
INSERT INTO `cart` VALUES (4, '17516639860', 1, 1, 7, '2025-11-20 22:28:43');

-- ----------------------------
-- Table structure for delivery
-- ----------------------------
DROP TABLE IF EXISTS `delivery`;
CREATE TABLE `delivery`  (
  `order_id` int(11) NOT NULL COMMENT '订单的编号',
  `cons_phone` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `disp_id` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `deliver_time` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `ended` int(11) NOT NULL DEFAULT 0 COMMENT '是否结束',
  PRIMARY KEY (`order_id`) USING BTREE,
  UNIQUE INDEX `order_id`(`order_id`) USING BTREE,
  INDEX `cons_phone`(`cons_phone`) USING BTREE,
  INDEX `disp_id`(`disp_id`) USING BTREE,
  INDEX `deliver_time`(`deliver_time`) USING BTREE,
  INDEX `ended`(`ended`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of delivery
-- ----------------------------
INSERT INTO `delivery` VALUES (2, '13525112345', '010100', '20分钟', 0);
INSERT INTO `delivery` VALUES (3, '13525188888', '010101', '30分钟', 0);
INSERT INTO `delivery` VALUES (4, '15967789756', '010100', '', 0);
INSERT INTO `delivery` VALUES (12, '17516632907', '010101', '30分钟', 0);
INSERT INTO `delivery` VALUES (13, '17516632907', '010101', '30分钟', 0);
INSERT INTO `delivery` VALUES (20, '17516631000', '1000011', '30分钟', 0);
INSERT INTO `delivery` VALUES (21, '17516631000', '010100', '2025-11-28 00:00:00', 1);
INSERT INTO `delivery` VALUES (22, '17516631000', '010100', '30分钟', 0);
INSERT INTO `delivery` VALUES (23, '17516631000', '010100', '30分钟', 0);
INSERT INTO `delivery` VALUES (24, '17516631000', '010100', '2025-11-28 00:00:00', 0);
INSERT INTO `delivery` VALUES (26, '17516631000', '010101', '30分钟', 1);
INSERT INTO `delivery` VALUES (27, '17516631000', '010101', '30分钟', 0);
INSERT INTO `delivery` VALUES (28, '17516631000', '010100', '30分钟', 0);
INSERT INTO `delivery` VALUES (32, '17516631000', '010101', '30分钟', 0);
INSERT INTO `delivery` VALUES (33, '17516631000', '010100', '30分钟', 0);
INSERT INTO `delivery` VALUES (34, '17516631000', '1000011', '30分钟', 0);
INSERT INTO `delivery` VALUES (35, '17516631000', '010101', '30分钟', 1);
INSERT INTO `delivery` VALUES (36, '17516631000', '010101', '30分钟', 1);
INSERT INTO `delivery` VALUES (37, '17516639826', '1000011', '30分钟', 0);
INSERT INTO `delivery` VALUES (38, '17516632964', '010101', '30分钟', 0);
INSERT INTO `delivery` VALUES (39, '17516632964', '010101', '30分钟', 0);
INSERT INTO `delivery` VALUES (40, '17516631000', '10111', '30分钟', 0);
INSERT INTO `delivery` VALUES (41, '17516631000', '1000011', '30分钟', 0);
INSERT INTO `delivery` VALUES (43, '17516631000', '1000011', '30分钟', 0);
INSERT INTO `delivery` VALUES (47, '17516639826', '010101', '30分钟', 0);
INSERT INTO `delivery` VALUES (48, '17516631000', '010101', '30分钟', 0);

-- ----------------------------
-- Table structure for dish
-- ----------------------------
DROP TABLE IF EXISTS `dish`;
CREATE TABLE `dish`  (
  `dish_id` int(11) NOT NULL AUTO_INCREMENT,
  `shop_id` int(11) NOT NULL,
  `dish_name` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `price` decimal(10, 2) NOT NULL,
  `description` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
  `image_url` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `monthly_sales` int(11) NULL DEFAULT 0,
  `status` tinyint(1) NULL DEFAULT 1,
  `sort_order` int(11) NULL DEFAULT 0,
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`dish_id`) USING BTREE,
  INDEX `shop_id`(`shop_id`) USING BTREE,
  CONSTRAINT `fk_dish_shop` FOREIGN KEY (`shop_id`) REFERENCES `shop` (`shop_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 44 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of dish
-- ----------------------------
INSERT INTO `dish` VALUES (1, 1, '牛肉拉面', 20.00, '手工拉面配鲜嫩牛肉，汤底醇厚', '/images/dish/lanzhou.png', 181, 1, 1, '2025-11-19 16:53:59');
INSERT INTO `dish` VALUES (2, 1, '羊肉拉面', 22.00, '精选羊肉，滋补养生', '/images/dish/yangroulamian.jpg', 120, 1, 2, '2025-11-19 16:53:59');
INSERT INTO `dish` VALUES (3, 1, '素拉面', 15.00, '清淡素食，健康美味', '/images/dish/sulamian.jpg', 93, 1, 3, '2025-11-19 16:53:59');
INSERT INTO `dish` VALUES (4, 1, '大盘鸡拌面', 28.00, '新疆风味，鸡肉鲜嫩', '/images/dish/dapanji.jpg', 73, 1, 4, '2025-11-19 16:53:59');
INSERT INTO `dish` VALUES (5, 1, '凉拌牛肉', 18.00, '秘制调料，爽口开胃', '/images/dish/liangbanniurou.jpg', 53, 1, 5, '2025-11-19 16:53:59');
INSERT INTO `dish` VALUES (6, 2, '北京烤鸭(半只)', 50.00, '传统挂炉烤制，皮脆肉嫩', '/images/dish/kaoya_banzhi.jpg', 205, 1, 1, '2025-11-19 16:53:59');
INSERT INTO `dish` VALUES (7, 2, '北京烤鸭(整只)', 88.00, '家庭聚餐首选', '/images/dish/kaoya_zhengzhi.jpg', 159, 1, 2, '2025-11-19 16:53:59');
INSERT INTO `dish` VALUES (8, 2, '鸭架汤', 15.00, '烤鸭骨架熬制，鲜美滋补', '/images/dish/yajiatang.jpg', 93, 1, 3, '2025-11-19 16:53:59');
INSERT INTO `dish` VALUES (9, 2, '椒盐鸭架', 18.00, '香酥可口，下酒佳品', '/images/dish/jiaoyanyajia.jpg', 69, 1, 4, '2025-11-19 16:53:59');
INSERT INTO `dish` VALUES (10, 2, '荷叶饼', 5.00, '手工制作，薄而有韧性', '/images/dish/heyebing.jpg', 237, 1, 5, '2025-11-19 16:53:59');
INSERT INTO `dish` VALUES (11, 3, '经典麻辣烫', 18.00, '多种食材，麻辣鲜香', '/images/dish/jingdianmala.jpg', 317, 1, 1, '2025-11-19 16:53:59');
INSERT INTO `dish` VALUES (12, 3, '番茄麻辣烫', 16.00, '酸甜可口，不辣之选', '/images/dish/fanqiemala.jpg', 181, 1, 2, '2025-11-19 16:53:59');
INSERT INTO `dish` VALUES (13, 3, '骨汤麻辣烫', 17.00, '浓郁骨汤，营养丰富', '/images/dish/gutangmala.jpg', 149, 1, 3, '2025-11-19 16:53:59');
INSERT INTO `dish` VALUES (14, 3, '麻辣拌', 15.00, '干拌口味，香气扑鼻', '/images/dish/malaban.jpg', 201, 1, 4, '2025-11-19 16:53:59');
INSERT INTO `dish` VALUES (15, 3, '冒菜', 20.00, '四川风味，麻辣过瘾', '/images/dish/maocai.jpg', 124, 1, 5, '2025-11-19 16:53:59');
INSERT INTO `dish` VALUES (21, 5, '经典黄焖鸡', 20.00, '鸡肉鲜嫩，汤汁浓郁', '/images/dish/jingdianhuangmenji.jpg', 291, 1, 1, '2025-11-19 16:53:59');
INSERT INTO `dish` VALUES (22, 5, '黄焖排骨', 25.00, '排骨软烂，香气四溢', '/images/dish/huangmenpaigu.jpg', 146, 1, 2, '2025-11-19 16:53:59');
INSERT INTO `dish` VALUES (23, 5, '黄焖牛肉', 28.00, '牛肉大块，营养丰富', '/images/dish/huangmenniurou.jpg', 98, 1, 3, '2025-11-19 16:53:59');
INSERT INTO `dish` VALUES (24, 5, '黄焖茄子', 15.00, '素食之选，健康美味', '/images/dish/huangmenqiezi.jpg', 77, 1, 4, '2025-11-19 16:53:59');
INSERT INTO `dish` VALUES (25, 5, '米饭', 2.00, '东北大米，粒粒香醇', '/images/dish/mifan.jpg', 568, 1, 5, '2025-11-19 16:53:59');
INSERT INTO `dish` VALUES (26, 6, '扬州炒饭', 18.00, '粒粒分明，配料丰富', '/images/dish/yangzhouchaofan.jpg', 235, 1, 1, '2025-11-19 16:53:59');
INSERT INTO `dish` VALUES (27, 6, '虾仁炒饭', 22.00, '新鲜虾仁，鲜美可口', '/images/dish/xiarenchaofan.jpg', 158, 1, 2, '2025-11-19 16:53:59');
INSERT INTO `dish` VALUES (28, 6, '牛肉炒饭', 20.00, '牛肉鲜嫩，香气扑鼻', '/images/dish/niurouchaofan.jpg', 134, 1, 3, '2025-11-19 16:53:59');
INSERT INTO `dish` VALUES (29, 6, '鸡肉炒饭', 18.00, '鸡肉滑嫩，营养均衡', '/images/dish/jirouchaofan.jpg', 112, 1, 4, '2025-11-19 16:53:59');
INSERT INTO `dish` VALUES (30, 6, '素炒饭', 15.00, '多种蔬菜，清淡健康', '/images/dish/suchaofan.jpg', 89, 1, 5, '2025-11-19 16:53:59');
INSERT INTO `dish` VALUES (31, 7, '云雾乌龙奶盖', 15.00, '乌龙清冽裹奶香，云顶绵密入喉凉', '/images/dish/yun_wu_wu_long_nai_gai_00c77bc6.jpg', 154, 1, 1, '2025-11-23 15:42:33');
INSERT INTO `dish` VALUES (32, 7, '雪域草莓芝士', 15.00, '雪域红颜撞芝士，一口酸甜赴春期', '/images/dish/xue_yu_cao_mei_zhi_shi_44dcb43a.jpg', 204, 1, 2, '2025-11-23 15:43:11');
INSERT INTO `dish` VALUES (33, 7, ' 鎏金芋泥波波', 15.00, '鎏金芋泥藏软糯，波波弹润沁心甜', '/images/dish/liu_jin_yu_ni_bo_bo_7965d006.jpg', 202, 1, 3, '2025-11-23 15:43:44');
INSERT INTO `dish` VALUES (34, 7, '竹影抹茶拿铁', 15.00, '竹影清风融抹茶，拿铁温润醉时光', '/images/dish/zhu_ying_mo_cha_na_tie_a96a3eb2.jpg', 120, 1, 4, '2025-11-23 15:44:17');
INSERT INTO `dish` VALUES (35, 9, '经典韩式琥珀炸鸡', 30.00, '琥珀酱汁裹脆壳，甜香微辣越啃越上头', '/images/dish/jing_dian_han_shi_hu_po_zha_ji_12aa7e6c.jpg', 121, 1, 1, '2025-11-23 16:28:12');
INSERT INTO `dish` VALUES (36, 9, '蒜香酱油双拼炸鸡', 40.00, '蒜香醇厚+酱油鲜甜，双味暴击解馋瘾', '/images/dish/suan_xiang_jiang_you_shuang_pin_zha_ji_72782b83.jpg', 90, 1, 2, '2025-11-23 16:29:34');
INSERT INTO `dish` VALUES (37, 9, '芝士雪花炸鸡', 30.00, '芝士粉雪漫脆衣，咸香拉丝一口沦陷', '/images/dish/zhi_shi_xue_hua_zha_ji_305f49b5.jpg', 100, 1, 3, '2025-11-23 16:29:57');
INSERT INTO `dish` VALUES (38, 9, '韩式甜辣鸡腿堡套餐', 25.00, '甜辣炸鸡搭软堡，配饮品解锁完整韩系满足', '/images/dish/han_shi_tian_la_ji_tui_bao_tao_can_1163ba78.jpg', 120, 1, 4, '2025-11-23 16:30:59');
INSERT INTO `dish` VALUES (39, 10, '经典意式玛格丽特披萨（九寸）', 56.00, '番茄鲜醇撞芝士，罗勒点睛，复刻意式本味', '/images/dish/jing_dian_yi_shi_ma_ge_li_te_pi_sa_jiu_cun_591b0238.jpg', 152, 1, 1, '2025-11-23 16:51:16');
INSERT INTO `dish` VALUES (40, 10, '黑松露菌菇培根披萨（九寸）', 72.00, '黑松露奢香浸润，菌菇培根咸鲜交织，一口沦陷', '/images/dish/hei_song_lu_jun_gu_pei_gen_pi_sa_888b0d7c.jpg', 121, 1, 2, '2025-11-23 16:51:49');
INSERT INTO `dish` VALUES (41, 10, '香辣牛肉至尊披萨（九寸）', 69.00, '辣酱打底+嫩牛爆香，鲜辣过瘾，重口味者狂喜', '/images/dish/xiang_la_niu_rou_zhi_zun_pi_sa_24f5e1c1.jpg', 120, 1, 3, '2025-11-23 16:52:18');
INSERT INTO `dish` VALUES (42, 10, '海鲜至尊披萨（九寸）', 78.00, '深海鲜货齐聚，芝士裹着鲜甜，舌尖漫游海岸线', '/images/dish/hai_xian_zhi_zun_pi_sa_9edece8e.jpg', 101, 1, 4, '2025-11-23 16:52:51');
INSERT INTO `dish` VALUES (43, 10, '榴莲多多果肉披（九寸）', 88.00, '金枕榴莲果肉爆满，芝士拉丝裹甜香，甜品党挚爱\r\n', '/images/dish/liu_lian_duo_duo_guo_rou_pi_sa_fc1001dd.jpg', 202, 1, 5, '2025-11-23 16:53:21');

-- ----------------------------
-- Table structure for dispatcher
-- ----------------------------
DROP TABLE IF EXISTS `dispatcher`;
CREATE TABLE `dispatcher`  (
  `dispatcher_id` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `dispatcher_name` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `dispatcher_phone` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  PRIMARY KEY (`dispatcher_id`) USING BTREE,
  UNIQUE INDEX `dispatcher_id`(`dispatcher_id`) USING BTREE,
  INDEX `dispatcher_name`(`dispatcher_name`) USING BTREE,
  INDEX `dispatcher_phone`(`dispatcher_phone`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of dispatcher
-- ----------------------------
INSERT INTO `dispatcher` VALUES ('010100', '张三', '17516532007');
INSERT INTO `dispatcher` VALUES ('010101', '小明', '17516532016');
INSERT INTO `dispatcher` VALUES ('1000011', '李小龙', '17515532016');
INSERT INTO `dispatcher` VALUES ('10111', '赵八两', '17515532010');

-- ----------------------------
-- Table structure for issue_followup
-- ----------------------------
DROP TABLE IF EXISTS `issue_followup`;
CREATE TABLE `issue_followup`  (
  `followup_id` int(11) NOT NULL AUTO_INCREMENT,
  `issue_id` int(11) NOT NULL,
  `followup_type` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT 'user' COMMENT 'user/admin/system',
  `content` text CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `image_url` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
  `created_by` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`followup_id`) USING BTREE,
  INDEX `idx_issue_id`(`issue_id`) USING BTREE,
  INDEX `idx_created_time`(`created_time`) USING BTREE,
  CONSTRAINT `issue_followup_ibfk_1` FOREIGN KEY (`issue_id`) REFERENCES `order_issue` (`issue_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of issue_followup
-- ----------------------------
INSERT INTO `issue_followup` VALUES (1, 1, 'user', '用户提交问题报告：兰州拉面订单问题', NULL, '用户 17516631000', '2025-12-15 14:39:11');
INSERT INTO `issue_followup` VALUES (2, 1, 'admin', '管理员开始处理问题，备注：已通知商家重新发货，请顾客耐心等待', NULL, '管理员 17516630000', '2025-12-15 15:14:02');
INSERT INTO `issue_followup` VALUES (3, 1, 'system', '用户确认问题已解决', NULL, '系统', '2025-12-15 15:14:40');
INSERT INTO `issue_followup` VALUES (4, 2, 'user', '用户提交问题报告：东北麻辣烫订单问题', NULL, '用户 17516631000', '2025-12-15 15:34:03');

-- ----------------------------
-- Table structure for oorder
-- ----------------------------
DROP TABLE IF EXISTS `oorder`;
CREATE TABLE `oorder`  (
  `order_id` int(11) NOT NULL AUTO_INCREMENT,
  `shop_name` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `shop_id` int(11) NULL DEFAULT NULL,
  `order_money` int(11) NOT NULL,
  `order_way` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `cons_phone` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `cons_name` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `cons_addre` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `address_id` int(11) NULL DEFAULT NULL COMMENT '用户地址ID',
  `checked` int(11) NULL DEFAULT 0,
  `create_time` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `remark` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT '' COMMENT '订单备注',
  PRIMARY KEY (`order_id`) USING BTREE,
  UNIQUE INDEX `order_id`(`order_id`) USING BTREE,
  INDEX `shop_name`(`shop_name`) USING BTREE,
  INDEX `order_money`(`order_money`) USING BTREE,
  INDEX `order_way`(`order_way`) USING BTREE,
  INDEX `cons_phone`(`cons_phone`) USING BTREE,
  INDEX `cons_name`(`cons_name`) USING BTREE,
  INDEX `cons_addre`(`cons_addre`) USING BTREE,
  INDEX `checked`(`checked`) USING BTREE,
  INDEX `create_time`(`create_time`) USING BTREE,
  INDEX `idx_shop_id`(`shop_id`) USING BTREE,
  INDEX `idx_address_id`(`address_id`) USING BTREE,
  CONSTRAINT `fk_order_address_id` FOREIGN KEY (`address_id`) REFERENCES `user_address` (`address_id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_order_shop` FOREIGN KEY (`shop_id`) REFERENCES `shop` (`shop_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 61 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of oorder
-- ----------------------------
INSERT INTO `oorder` VALUES (2, '扬州炒饭', 6, 10, '人工订餐', '13525188888', '吴方', '郑州市中原区', NULL, 2, '2022-12-16 14:35:26', '');
INSERT INTO `oorder` VALUES (3, '兰州拉面', 1, 20, '人工订餐', '13525188888', '吴方', '郑州市中原区', NULL, 2, '2022-12-16 14:35:35', '');
INSERT INTO `oorder` VALUES (5, '北京烤鸭', 2, 10, '网上订餐', '17516632907', '元蓝', '浙江省义乌', NULL, 0, '2025-11-07 13:34:37', '');
INSERT INTO `oorder` VALUES (12, '东北麻辣烫', 3, 15, '网上订餐', '17516632907', '花都湖', '郑州市二七区', NULL, 2, '2025-11-18 21:30:25', '');
INSERT INTO `oorder` VALUES (13, '东北麻辣烫', 3, 15, '网上订餐', '17516632907', '成本', '浙江省义乌', NULL, 2, '2025-11-18 21:30:41', '');
INSERT INTO `oorder` VALUES (20, '兰州拉面', 1, 103, '网上订餐', '17516631000', '搜获', '郑州市管城回族区', NULL, 2, '2025-11-21 16:19:21', '');
INSERT INTO `oorder` VALUES (21, '北京烤鸭', 2, 176, '人工订餐', '17516631000', '小兰', '郑州市中原区', NULL, 2, '2025-11-21 16:43:46', '');
INSERT INTO `oorder` VALUES (22, '东北亮麻辣烫', 3, 15, '人工订餐', '17516631000', '时间', '郑州市惠济区', NULL, 2, '2025-11-21 18:03:12', '');
INSERT INTO `oorder` VALUES (23, '兰州拉面', 1, 20, '人工订餐', '17516631000', '航局', '郑州市市政府', NULL, 2, '2025-11-21 18:18:38', '');
INSERT INTO `oorder` VALUES (24, '北京烤鸭', 2, 176, '人工订餐', '17516631000', '阿才', '郑州市市政府', NULL, 2, '2025-11-21 18:36:24', '');
INSERT INTO `oorder` VALUES (25, '北京烤鸭', 2, 153, '人工订餐', '17516631000', '元氏', '浙江省义乌', NULL, 0, '2025-11-21 21:29:17', '');
INSERT INTO `oorder` VALUES (26, '兰州拉面', 1, 99, '网上订餐', '17516631000', '元芳', '浙江省义乌', NULL, 2, '2025-11-23 01:33:50', '');
INSERT INTO `oorder` VALUES (27, '奶茶', 7, 45, '自提', '17516631000', '元芳', '浙江省义乌', NULL, 2, '2025-11-23 15:52:14', '');
INSERT INTO `oorder` VALUES (28, '奶茶', 7, 45, '网上订餐', '17516631000', '元芳', '郑州市二七区', NULL, 2, '2025-11-23 16:35:18', '');
INSERT INTO `oorder` VALUES (32, '兰州拉面', 1, 103, '网上订餐', '17516631000', '元芳', '郑州市新郑市', NULL, 2, '2025-11-23 17:06:38', '');
INSERT INTO `oorder` VALUES (33, '兰州拉面', 1, 18, '自提', '17516631000', '元芳', '郑州市新密市', NULL, 2, '2025-11-23 17:07:04', '');
INSERT INTO `oorder` VALUES (34, '兰州拉面', 1, 103, '网上订餐', '17516631000', '加哈吉', '郑州市巩义市', NULL, 2, '2025-11-23 19:13:01', '');
INSERT INTO `oorder` VALUES (35, '韩式炸鸡', 9, 30, '自提', '17516631000', '远方', '郑州市管城回族区', NULL, 2, '2025-12-05 18:45:45', '');
INSERT INTO `oorder` VALUES (36, '东北麻辣烫', 3, 35, '网上订餐', '17516631000', '远方', '郑州市上街区', NULL, 2, '2025-12-09 16:41:24', '');
INSERT INTO `oorder` VALUES (37, '黄焖鸡米饭', 5, 37, '网上订餐', '17516639826', '元芳', '郑州市惠济区', NULL, 2, '2025-12-09 19:40:44', '');
INSERT INTO `oorder` VALUES (38, '鲜炒百味饭堂', 6, 22, '网上订餐', '17516632964', '小红', '郑州市金水区', NULL, 2, '2025-12-09 19:47:57', '');
INSERT INTO `oorder` VALUES (39, '芝香窑烤披萨坊', 10, 134, '网上订餐', '17516632964', '小兰', '郑州市中原区', NULL, 2, '2025-12-09 19:49:54', '');
INSERT INTO `oorder` VALUES (40, '兰州拉面', 1, 105, '网上订餐', '17516631000', '远方', '郑州市市政府', NULL, 2, '2025-12-15 14:14:31', '');
INSERT INTO `oorder` VALUES (41, '东北麻辣烫', 3, 86, '网上订餐', '17516631000', '远方', '桃园路75号', NULL, 1, '2025-12-15 15:27:29', '');
INSERT INTO `oorder` VALUES (42, '奶茶', 7, 30, '自提', '17516631000', '远方', '中原东路辅路', NULL, 0, '2025-12-15 15:28:47', '');
INSERT INTO `oorder` VALUES (43, '黄焖鸡米饭', 5, 45, '网上订餐', '17516631000', '远方', '高新区科学大道100号', NULL, 1, '2025-12-23 10:56:18', '');
INSERT INTO `oorder` VALUES (44, '东北麻辣烫', 3, 33, '网上订餐', '17516639826', '远方', '高新区科学大道100号', NULL, 0, '2025-12-23 10:57:48', '');
INSERT INTO `oorder` VALUES (45, '奶茶', 7, 30, '网上订餐', '17516639826', '远方', '高新区科学大道100号', NULL, 0, '2025-12-23 10:58:17', '');
INSERT INTO `oorder` VALUES (46, '芝香窑烤披萨坊', 10, 128, '网上订餐', '17516639826', '远方', '高新区科学大道100号', NULL, 0, '2025-12-23 11:00:10', '');
INSERT INTO `oorder` VALUES (47, '鲜炒百味饭堂', 6, 40, '网上订餐', '17516639826', '远方', '郑州市高新区科学大道100号', NULL, 2, '2025-12-23 11:00:54', '');
INSERT INTO `oorder` VALUES (48, '兰州拉面', 1, 42, '网上订餐', '17516631000', '远方', '河南省郑州市二七区', NULL, 2, '2025-12-23 11:25:55', '');
INSERT INTO `oorder` VALUES (49, '兰州拉面', 1, 179, '网上订餐', '17516631000', '远方', '河南省郑州市二七区', 1, 0, '2026-02-06 20:57:16', '');
INSERT INTO `oorder` VALUES (50, '东北麻辣烫', 3, 51, '网上订餐', '17516631000', '远方', '河南省郑州市二七区', 1, 0, '2026-02-06 21:01:23', '');
INSERT INTO `oorder` VALUES (51, '东北麻辣烫', 3, 51, '网上订餐', '17516631000', '远方', '河南省郑州市二七区', 1, 0, '2026-02-06 21:01:47', '');
INSERT INTO `oorder` VALUES (52, '兰州拉面', 1, 57, '自提', '17516633000', '阿任', '北京市北京市西城区西城区大学东路110号', 2, 0, '2026-02-06 21:15:00', '');
INSERT INTO `oorder` VALUES (53, '兰州拉面', 1, 42, '网上订餐', '17516631000', '阿任', '北京市北京市东城区西城区大学东路110号', 2, 0, '2026-02-06 21:24:25', '');
INSERT INTO `oorder` VALUES (54, '兰州拉面', 1, 42, '网上订餐', '17516631000', '阿任', '北京市北京市东城区西城区大学东路110号', 2, 0, '2026-02-13 11:00:44', '备注功能测试正常');
INSERT INTO `oorder` VALUES (55, '兰州拉面', 1, 37, '网上订餐', '17516631000', '阿任', '北京市北京市东城区西城区大学东路110号', 2, 0, '2026-02-13 11:10:38', '');
INSERT INTO `oorder` VALUES (56, '兰州拉面', 1, 20, '自提', '17516631000', '远方', '河南省郑州市二七区', 1, 0, '2026-02-13 11:13:13', '地址模块测试成功');
INSERT INTO `oorder` VALUES (57, '兰州拉面', 1, 22, '网上订餐', '17516631000', '阿任', '北京市北京市东城区西城区大学东路110号', 2, 0, '2026-02-13 11:13:45', '');
INSERT INTO `oorder` VALUES (58, '兰州拉面', 1, 75, '网上订餐', '17516631000', '远方', '河南省郑州市二七区', 1, 0, '2026-02-13 11:14:52', '');
INSERT INTO `oorder` VALUES (59, '北京烤鸭', 2, 70, '网上订餐', '17516631000', '远方', '河南省郑州市二七区', 1, 0, '2026-02-13 11:20:26', '功能正常');
INSERT INTO `oorder` VALUES (60, '兰州拉面', 1, 42, '网上订餐', '17516631000', '远方', '河南省郑州市二七区', 1, 0, '2026-02-13 21:01:46', '前端代码重组测试正常');

-- ----------------------------
-- Table structure for order_detail
-- ----------------------------
DROP TABLE IF EXISTS `order_detail`;
CREATE TABLE `order_detail`  (
  `detail_id` int(11) NOT NULL AUTO_INCREMENT,
  `order_id` int(11) NOT NULL,
  `dish_id` int(11) NOT NULL,
  `dish_name` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `price` decimal(10, 2) NOT NULL,
  `quantity` int(11) NOT NULL DEFAULT 1,
  `subtotal` decimal(10, 2) NOT NULL,
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`detail_id`) USING BTREE,
  INDEX `order_id`(`order_id`) USING BTREE,
  INDEX `dish_id`(`dish_id`) USING BTREE,
  CONSTRAINT `fk_order_detail_dish` FOREIGN KEY (`dish_id`) REFERENCES `dish` (`dish_id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_order_detail_order` FOREIGN KEY (`order_id`) REFERENCES `oorder` (`order_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 99 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of order_detail
-- ----------------------------
INSERT INTO `order_detail` VALUES (1, 20, 4, '大盘鸡拌面', 28.00, 1, 28.00, '2025-11-21 16:19:21');
INSERT INTO `order_detail` VALUES (2, 20, 1, '牛肉拉面', 20.00, 1, 20.00, '2025-11-21 16:19:21');
INSERT INTO `order_detail` VALUES (3, 20, 2, '羊肉拉面', 22.00, 1, 22.00, '2025-11-21 16:19:21');
INSERT INTO `order_detail` VALUES (4, 20, 3, '素拉面', 15.00, 1, 15.00, '2025-11-21 16:19:21');
INSERT INTO `order_detail` VALUES (5, 20, 5, '凉拌牛肉', 18.00, 1, 18.00, '2025-11-21 16:19:21');
INSERT INTO `order_detail` VALUES (6, 21, 6, '北京烤鸭(半只)', 50.00, 1, 50.00, '2025-11-21 16:43:46');
INSERT INTO `order_detail` VALUES (7, 21, 7, '北京烤鸭(整只)', 88.00, 1, 88.00, '2025-11-21 16:43:46');
INSERT INTO `order_detail` VALUES (8, 21, 8, '鸭架汤', 15.00, 1, 15.00, '2025-11-21 16:43:46');
INSERT INTO `order_detail` VALUES (9, 21, 9, '椒盐鸭架', 18.00, 1, 18.00, '2025-11-21 16:43:46');
INSERT INTO `order_detail` VALUES (10, 21, 10, '荷叶饼', 5.00, 1, 5.00, '2025-11-21 16:43:46');
INSERT INTO `order_detail` VALUES (11, 22, 14, '麻辣拌', 15.00, 1, 15.00, '2025-11-21 18:03:12');
INSERT INTO `order_detail` VALUES (12, 23, 1, '牛肉拉面', 20.00, 1, 20.00, '2025-11-21 18:18:38');
INSERT INTO `order_detail` VALUES (13, 24, 6, '北京烤鸭(半只)', 50.00, 1, 50.00, '2025-11-21 18:36:24');
INSERT INTO `order_detail` VALUES (14, 24, 7, '北京烤鸭(整只)', 88.00, 1, 88.00, '2025-11-21 18:36:24');
INSERT INTO `order_detail` VALUES (15, 24, 8, '鸭架汤', 15.00, 1, 15.00, '2025-11-21 18:36:24');
INSERT INTO `order_detail` VALUES (16, 24, 9, '椒盐鸭架', 18.00, 1, 18.00, '2025-11-21 18:36:24');
INSERT INTO `order_detail` VALUES (17, 24, 10, '荷叶饼', 5.00, 1, 5.00, '2025-11-21 18:36:24');
INSERT INTO `order_detail` VALUES (18, 25, 6, '北京烤鸭(半只)', 50.00, 1, 50.00, '2025-11-21 21:29:17');
INSERT INTO `order_detail` VALUES (19, 25, 7, '北京烤鸭(整只)', 88.00, 1, 88.00, '2025-11-21 21:29:17');
INSERT INTO `order_detail` VALUES (20, 25, 8, '鸭架汤', 15.00, 1, 15.00, '2025-11-21 21:29:17');
INSERT INTO `order_detail` VALUES (21, 26, 1, '牛肉拉面', 20.00, 2, 40.00, '2025-11-23 01:33:50');
INSERT INTO `order_detail` VALUES (22, 26, 2, '羊肉拉面', 22.00, 2, 44.00, '2025-11-23 01:33:50');
INSERT INTO `order_detail` VALUES (23, 26, 3, '素拉面', 15.00, 1, 15.00, '2025-11-23 01:33:50');
INSERT INTO `order_detail` VALUES (24, 27, 31, '云雾乌龙奶盖', 15.00, 2, 30.00, '2025-11-23 15:52:14');
INSERT INTO `order_detail` VALUES (25, 27, 32, '雪域草莓芝士', 15.00, 1, 15.00, '2025-11-23 15:52:14');
INSERT INTO `order_detail` VALUES (26, 28, 31, '云雾乌龙奶盖', 15.00, 1, 15.00, '2025-11-23 16:35:18');
INSERT INTO `order_detail` VALUES (27, 28, 32, '雪域草莓芝士', 15.00, 1, 15.00, '2025-11-23 16:35:18');
INSERT INTO `order_detail` VALUES (28, 28, 33, ' 鎏金芋泥波波', 15.00, 1, 15.00, '2025-11-23 16:35:18');
INSERT INTO `order_detail` VALUES (29, 32, 1, '牛肉拉面', 20.00, 1, 20.00, '2025-11-23 17:06:38');
INSERT INTO `order_detail` VALUES (30, 32, 2, '羊肉拉面', 22.00, 1, 22.00, '2025-11-23 17:06:38');
INSERT INTO `order_detail` VALUES (31, 32, 3, '素拉面', 15.00, 1, 15.00, '2025-11-23 17:06:38');
INSERT INTO `order_detail` VALUES (32, 32, 4, '大盘鸡拌面', 28.00, 1, 28.00, '2025-11-23 17:06:38');
INSERT INTO `order_detail` VALUES (33, 32, 5, '凉拌牛肉', 18.00, 1, 18.00, '2025-11-23 17:06:38');
INSERT INTO `order_detail` VALUES (34, 33, 5, '凉拌牛肉', 18.00, 1, 18.00, '2025-11-23 17:07:04');
INSERT INTO `order_detail` VALUES (35, 34, 1, '牛肉拉面', 20.00, 1, 20.00, '2025-11-23 19:13:01');
INSERT INTO `order_detail` VALUES (36, 34, 2, '羊肉拉面', 22.00, 1, 22.00, '2025-11-23 19:13:01');
INSERT INTO `order_detail` VALUES (37, 34, 3, '素拉面', 15.00, 1, 15.00, '2025-11-23 19:13:01');
INSERT INTO `order_detail` VALUES (38, 34, 4, '大盘鸡拌面', 28.00, 1, 28.00, '2025-11-23 19:13:01');
INSERT INTO `order_detail` VALUES (39, 34, 5, '凉拌牛肉', 18.00, 1, 18.00, '2025-11-23 19:13:01');
INSERT INTO `order_detail` VALUES (40, 35, 35, '经典韩式琥珀炸鸡', 30.00, 1, 30.00, '2025-12-05 18:45:45');
INSERT INTO `order_detail` VALUES (41, 36, 11, '经典麻辣烫', 18.00, 1, 18.00, '2025-12-09 16:41:24');
INSERT INTO `order_detail` VALUES (42, 36, 13, '骨汤麻辣烫', 17.00, 1, 17.00, '2025-12-09 16:41:24');
INSERT INTO `order_detail` VALUES (43, 37, 21, '经典黄焖鸡', 20.00, 1, 20.00, '2025-12-09 19:40:44');
INSERT INTO `order_detail` VALUES (44, 37, 25, '米饭', 2.00, 1, 2.00, '2025-12-09 19:40:44');
INSERT INTO `order_detail` VALUES (45, 37, 24, '黄焖茄子', 15.00, 1, 15.00, '2025-12-09 19:40:44');
INSERT INTO `order_detail` VALUES (46, 38, 27, '虾仁炒饭', 22.00, 1, 22.00, '2025-12-09 19:47:57');
INSERT INTO `order_detail` VALUES (47, 39, 39, '经典意式玛格丽特披萨（九寸）', 56.00, 1, 56.00, '2025-12-09 19:49:54');
INSERT INTO `order_detail` VALUES (48, 39, 42, '海鲜至尊披萨（九寸）', 78.00, 1, 78.00, '2025-12-09 19:49:54');
INSERT INTO `order_detail` VALUES (49, 40, 1, '牛肉拉面', 20.00, 3, 60.00, '2025-12-15 14:14:31');
INSERT INTO `order_detail` VALUES (50, 40, 3, '素拉面', 15.00, 3, 45.00, '2025-12-15 14:14:31');
INSERT INTO `order_detail` VALUES (51, 41, 11, '经典麻辣烫', 18.00, 1, 18.00, '2025-12-15 15:27:29');
INSERT INTO `order_detail` VALUES (52, 41, 12, '番茄麻辣烫', 16.00, 1, 16.00, '2025-12-15 15:27:29');
INSERT INTO `order_detail` VALUES (53, 41, 13, '骨汤麻辣烫', 17.00, 1, 17.00, '2025-12-15 15:27:29');
INSERT INTO `order_detail` VALUES (54, 41, 14, '麻辣拌', 15.00, 1, 15.00, '2025-12-15 15:27:29');
INSERT INTO `order_detail` VALUES (55, 41, 15, '冒菜', 20.00, 1, 20.00, '2025-12-15 15:27:29');
INSERT INTO `order_detail` VALUES (56, 42, 32, '雪域草莓芝士', 15.00, 1, 15.00, '2025-12-15 15:28:47');
INSERT INTO `order_detail` VALUES (57, 42, 33, ' 鎏金芋泥波波', 15.00, 1, 15.00, '2025-12-15 15:28:47');
INSERT INTO `order_detail` VALUES (58, 43, 21, '经典黄焖鸡', 20.00, 1, 20.00, '2025-12-23 10:56:18');
INSERT INTO `order_detail` VALUES (59, 43, 22, '黄焖排骨', 25.00, 1, 25.00, '2025-12-23 10:56:18');
INSERT INTO `order_detail` VALUES (60, 44, 11, '经典麻辣烫', 18.00, 1, 18.00, '2025-12-23 10:57:48');
INSERT INTO `order_detail` VALUES (61, 44, 14, '麻辣拌', 15.00, 1, 15.00, '2025-12-23 10:57:48');
INSERT INTO `order_detail` VALUES (62, 45, 31, '云雾乌龙奶盖', 15.00, 1, 15.00, '2025-12-23 10:58:17');
INSERT INTO `order_detail` VALUES (63, 45, 32, '雪域草莓芝士', 15.00, 1, 15.00, '2025-12-23 10:58:17');
INSERT INTO `order_detail` VALUES (64, 46, 39, '经典意式玛格丽特披萨（九寸）', 56.00, 1, 56.00, '2025-12-23 11:00:10');
INSERT INTO `order_detail` VALUES (65, 46, 40, '黑松露菌菇培根披萨（九寸）', 72.00, 1, 72.00, '2025-12-23 11:00:10');
INSERT INTO `order_detail` VALUES (66, 47, 26, '扬州炒饭', 18.00, 1, 18.00, '2025-12-23 11:00:54');
INSERT INTO `order_detail` VALUES (67, 47, 27, '虾仁炒饭', 22.00, 1, 22.00, '2025-12-23 11:00:54');
INSERT INTO `order_detail` VALUES (68, 48, 1, '牛肉拉面', 20.00, 1, 20.00, '2025-12-23 11:25:55');
INSERT INTO `order_detail` VALUES (69, 48, 2, '羊肉拉面', 22.00, 1, 22.00, '2025-12-23 11:25:55');
INSERT INTO `order_detail` VALUES (70, 49, 1, '牛肉拉面', 20.00, 6, 120.00, '2026-02-06 20:57:16');
INSERT INTO `order_detail` VALUES (71, 49, 2, '羊肉拉面', 22.00, 2, 44.00, '2026-02-06 20:57:16');
INSERT INTO `order_detail` VALUES (72, 49, 3, '素拉面', 15.00, 1, 15.00, '2026-02-06 20:57:16');
INSERT INTO `order_detail` VALUES (73, 50, 11, '经典麻辣烫', 18.00, 1, 18.00, '2026-02-06 21:01:23');
INSERT INTO `order_detail` VALUES (74, 50, 12, '番茄麻辣烫', 16.00, 1, 16.00, '2026-02-06 21:01:23');
INSERT INTO `order_detail` VALUES (75, 50, 13, '骨汤麻辣烫', 17.00, 1, 17.00, '2026-02-06 21:01:23');
INSERT INTO `order_detail` VALUES (76, 51, 11, '经典麻辣烫', 18.00, 1, 18.00, '2026-02-06 21:01:47');
INSERT INTO `order_detail` VALUES (77, 51, 12, '番茄麻辣烫', 16.00, 1, 16.00, '2026-02-06 21:01:47');
INSERT INTO `order_detail` VALUES (78, 51, 13, '骨汤麻辣烫', 17.00, 1, 17.00, '2026-02-06 21:01:47');
INSERT INTO `order_detail` VALUES (79, 52, 3, '素拉面', 15.00, 1, 15.00, '2026-02-06 21:15:00');
INSERT INTO `order_detail` VALUES (80, 52, 2, '羊肉拉面', 22.00, 1, 22.00, '2026-02-06 21:15:00');
INSERT INTO `order_detail` VALUES (81, 52, 1, '牛肉拉面', 20.00, 1, 20.00, '2026-02-06 21:15:00');
INSERT INTO `order_detail` VALUES (82, 53, 1, '牛肉拉面', 20.00, 1, 20.00, '2026-02-06 21:24:25');
INSERT INTO `order_detail` VALUES (83, 53, 2, '羊肉拉面', 22.00, 1, 22.00, '2026-02-06 21:24:25');
INSERT INTO `order_detail` VALUES (84, 54, 1, '牛肉拉面', 20.00, 1, 20.00, '2026-02-13 11:00:44');
INSERT INTO `order_detail` VALUES (85, 54, 2, '羊肉拉面', 22.00, 1, 22.00, '2026-02-13 11:00:44');
INSERT INTO `order_detail` VALUES (86, 55, 3, '素拉面', 15.00, 1, 15.00, '2026-02-13 11:10:38');
INSERT INTO `order_detail` VALUES (87, 55, 2, '羊肉拉面', 22.00, 1, 22.00, '2026-02-13 11:10:38');
INSERT INTO `order_detail` VALUES (88, 56, 1, '牛肉拉面', 20.00, 1, 20.00, '2026-02-13 11:13:13');
INSERT INTO `order_detail` VALUES (89, 57, 2, '羊肉拉面', 22.00, 1, 22.00, '2026-02-13 11:13:45');
INSERT INTO `order_detail` VALUES (90, 58, 1, '牛肉拉面', 20.00, 1, 20.00, '2026-02-13 11:14:52');
INSERT INTO `order_detail` VALUES (91, 58, 2, '羊肉拉面', 22.00, 1, 22.00, '2026-02-13 11:14:52');
INSERT INTO `order_detail` VALUES (92, 58, 3, '素拉面', 15.00, 1, 15.00, '2026-02-13 11:14:52');
INSERT INTO `order_detail` VALUES (93, 58, 5, '凉拌牛肉', 18.00, 1, 18.00, '2026-02-13 11:14:52');
INSERT INTO `order_detail` VALUES (94, 59, 6, '北京烤鸭(半只)', 50.00, 1, 50.00, '2026-02-13 11:20:26');
INSERT INTO `order_detail` VALUES (95, 59, 10, '荷叶饼', 5.00, 1, 5.00, '2026-02-13 11:20:26');
INSERT INTO `order_detail` VALUES (96, 59, 8, '鸭架汤', 15.00, 1, 15.00, '2026-02-13 11:20:26');
INSERT INTO `order_detail` VALUES (97, 60, 1, '牛肉拉面', 20.00, 1, 20.00, '2026-02-13 21:01:46');
INSERT INTO `order_detail` VALUES (98, 60, 2, '羊肉拉面', 22.00, 1, 22.00, '2026-02-13 21:01:46');

-- ----------------------------
-- Table structure for order_issue
-- ----------------------------
DROP TABLE IF EXISTS `order_issue`;
CREATE TABLE `order_issue`  (
  `issue_id` int(11) NOT NULL AUTO_INCREMENT,
  `order_id` int(11) NOT NULL,
  `user_phone` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `issue_type` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT 'delivery/product/order/payment/other',
  `urgency` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT 'medium' COMMENT 'low/medium/high',
  `title` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `description` text CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `image_url` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
  `expected_solution` varchar(500) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `status` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT 'pending' COMMENT 'pending/processing/resolved/closed',
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_time` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`issue_id`) USING BTREE,
  INDEX `order_id`(`order_id`) USING BTREE,
  INDEX `idx_user_phone`(`user_phone`) USING BTREE,
  INDEX `idx_status`(`status`) USING BTREE,
  INDEX `idx_created_time`(`created_time`) USING BTREE,
  CONSTRAINT `order_issue_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `oorder` (`order_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `order_issue_ibfk_2` FOREIGN KEY (`user_phone`) REFERENCES `user` (`telephone`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of order_issue
-- ----------------------------
INSERT INTO `order_issue` VALUES (1, 40, '17516631000', 'product', 'medium', '兰州拉面订单问题', '商品损坏，无法食用。', '', '重新发货', 'resolved', '2025-12-15 14:39:11', '2025-12-15 15:14:40');
INSERT INTO `order_issue` VALUES (2, 36, '17516631000', 'delivery', 'medium', '东北麻辣烫订单问题', '配送过慢，另外商家保温措施有问题，没有做好保温，饭菜都凉了', '', '只是提个建议，希望以后会改善', 'pending', '2025-12-15 15:34:03', '2025-12-15 15:34:03');

-- ----------------------------
-- Table structure for orderway
-- ----------------------------
DROP TABLE IF EXISTS `orderway`;
CREATE TABLE `orderway`  (
  `orderway_name` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '订餐方式',
  `count` int(11) NOT NULL COMMENT '该种方式的订餐数量',
  PRIMARY KEY (`orderway_name`) USING BTREE,
  UNIQUE INDEX `orderway_name`(`orderway_name`) USING BTREE,
  INDEX `count`(`count`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of orderway
-- ----------------------------
INSERT INTO `orderway` VALUES ('网上订餐', 81);
INSERT INTO `orderway` VALUES ('自提', 118);

-- ----------------------------
-- Table structure for review
-- ----------------------------
DROP TABLE IF EXISTS `review`;
CREATE TABLE `review`  (
  `review_id` int(11) NOT NULL AUTO_INCREMENT,
  `order_id` int(11) NOT NULL COMMENT '订单ID',
  `shop_id` int(11) NOT NULL COMMENT '店铺ID',
  `dish_id` int(11) NULL DEFAULT NULL COMMENT '菜品ID（为空则为店铺评价）',
  `user_phone` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '用户手机号',
  `rating` tinyint(1) NOT NULL COMMENT '评分1-5',
  `comment` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL COMMENT '评价内容',
  `review_type` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT 'shop' COMMENT '评价类型：shop/dish',
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `likes_count` int(11) NULL DEFAULT 0 COMMENT '点赞数',
  PRIMARY KEY (`review_id`) USING BTREE,
  INDEX `idx_order_id`(`order_id`) USING BTREE,
  INDEX `idx_shop_id`(`shop_id`) USING BTREE,
  INDEX `idx_dish_id`(`dish_id`) USING BTREE,
  INDEX `idx_user_phone`(`user_phone`) USING BTREE,
  INDEX `idx_created_time`(`created_time`) USING BTREE,
  CONSTRAINT `fk_review_dish` FOREIGN KEY (`dish_id`) REFERENCES `dish` (`dish_id`) ON DELETE SET NULL ON UPDATE RESTRICT,
  CONSTRAINT `fk_review_order` FOREIGN KEY (`order_id`) REFERENCES `oorder` (`order_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `fk_review_shop` FOREIGN KEY (`shop_id`) REFERENCES `shop` (`shop_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 61 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of review
-- ----------------------------
INSERT INTO `review` VALUES (1, 20, 1, 1, '17516631000', 5, '牛肉拉面非常好吃，汤底浓郁！', 'dish', '2025-11-22 10:00:00', 0);
INSERT INTO `review` VALUES (2, 20, 1, 4, '17516631000', 4, '大盘鸡拌面分量足，味道不错', 'dish', '2025-11-22 10:00:00', 0);
INSERT INTO `review` VALUES (3, 20, 1, NULL, '17516631000', 5, '店铺服务好，上菜快，推荐！', 'shop', '2025-11-22 10:00:00', 0);
INSERT INTO `review` VALUES (4, 21, 2, 6, '17516631000', 5, '北京烤鸭皮脆肉嫩，非常正宗', 'dish', '2025-11-22 11:00:00', 0);
INSERT INTO `review` VALUES (5, 21, 2, NULL, '17516631000', 4, '烤鸭味道不错，就是配送有点慢', 'shop', '2025-11-22 11:00:00', 0);
INSERT INTO `review` VALUES (6, 27, 7, 31, '17516631000', 5, '奶茶很好喝，奶盖很香！', 'dish', '2025-11-23 16:00:00', 0);
INSERT INTO `review` VALUES (7, 27, 7, NULL, '17516631000', 5, '奶茶店服务态度很好，推荐！', 'shop', '2025-11-23 16:00:00', 0);
INSERT INTO `review` VALUES (8, 34, 1, NULL, '17516631000', 4, '还不错，就是有点贵，希望价格调整一下', 'shop', '2025-12-09 15:48:24', 0);
INSERT INTO `review` VALUES (9, 34, 1, 1, '17516631000', 5, '凉拌牛肉：还不错，就是有点贵，希望价格调整一下', 'dish', '2025-12-09 15:48:24', 0);
INSERT INTO `review` VALUES (10, 34, 1, 2, '17516631000', 5, '大盘鸡拌面：还不错，就是有点贵，希望价格调整一下', 'dish', '2025-12-09 15:48:24', 0);
INSERT INTO `review` VALUES (11, 34, 1, 3, '17516631000', 5, '牛肉拉面：还不错，就是有点贵，希望价格调整一下', 'dish', '2025-12-09 15:48:24', 0);
INSERT INTO `review` VALUES (12, 34, 1, 4, '17516631000', 5, '素拉面：还不错，就是有点贵，希望价格调整一下', 'dish', '2025-12-09 15:48:24', 0);
INSERT INTO `review` VALUES (13, 34, 1, 5, '17516631000', 5, '羊肉拉面：还不错，就是有点贵，希望价格调整一下', 'dish', '2025-12-09 15:48:24', 0);
INSERT INTO `review` VALUES (14, 33, 1, NULL, '17516631000', 5, '不错，牛肉量足', 'shop', '2025-12-09 16:38:19', 0);
INSERT INTO `review` VALUES (15, 33, 1, 5, '17516631000', 5, '凉拌牛肉：不错，牛肉量足', 'dish', '2025-12-09 16:38:19', 0);
INSERT INTO `review` VALUES (16, 36, 3, NULL, '17516631000', 5, '很好吃，味道很香', 'shop', '2025-12-09 16:43:23', 0);
INSERT INTO `review` VALUES (17, 36, 3, 11, '17516631000', 5, '经典麻辣烫：很好吃，味道很香', 'dish', '2025-12-09 16:43:23', 0);
INSERT INTO `review` VALUES (18, 36, 3, 13, '17516631000', 5, '骨汤麻辣烫：很好吃，味道很香', 'dish', '2025-12-09 16:43:23', 0);
INSERT INTO `review` VALUES (19, 26, 1, NULL, '17516631000', 5, '整体体验良好', 'shop', '2025-12-09 16:45:39', 0);
INSERT INTO `review` VALUES (20, 26, 1, 2, '17516631000', 5, '素拉面：味道不错', 'dish', '2025-12-09 16:45:39', 0);
INSERT INTO `review` VALUES (21, 26, 1, 3, '17516631000', 5, '羊肉拉面：味道不错', 'dish', '2025-12-09 16:45:39', 0);
INSERT INTO `review` VALUES (22, 26, 1, 1, '17516631000', 5, '牛肉拉面：味道不错', 'dish', '2025-12-09 16:45:39', 0);
INSERT INTO `review` VALUES (23, 24, 2, NULL, '17516631000', 5, '整体体验良好', 'shop', '2025-12-09 16:45:49', 0);
INSERT INTO `review` VALUES (24, 24, 2, 6, '17516631000', 5, '北京烤鸭(半只)：味道不错', 'dish', '2025-12-09 16:45:49', 0);
INSERT INTO `review` VALUES (25, 24, 2, 8, '17516631000', 5, '椒盐鸭架：味道不错', 'dish', '2025-12-09 16:45:49', 0);
INSERT INTO `review` VALUES (26, 24, 2, 7, '17516631000', 5, '北京烤鸭(整只)：味道不错', 'dish', '2025-12-09 16:45:49', 0);
INSERT INTO `review` VALUES (27, 24, 2, 9, '17516631000', 5, '荷叶饼：味道不错', 'dish', '2025-12-09 16:45:49', 0);
INSERT INTO `review` VALUES (28, 24, 2, 10, '17516631000', 5, '鸭架汤：味道不错', 'dish', '2025-12-09 16:45:49', 0);
INSERT INTO `review` VALUES (29, 28, 7, NULL, '17516631000', 4, '整体体验良好', 'shop', '2025-12-09 16:46:12', 0);
INSERT INTO `review` VALUES (30, 28, 7, 31, '17516631000', 4, '鎏金芋泥波波：味道不错', 'dish', '2025-12-09 16:46:12', 0);
INSERT INTO `review` VALUES (31, 28, 7, 32, '17516631000', 4, '云雾乌龙奶盖：味道不错', 'dish', '2025-12-09 16:46:12', 0);
INSERT INTO `review` VALUES (32, 28, 7, 33, '17516631000', 4, '雪域草莓芝士：味道不错', 'dish', '2025-12-09 16:46:12', 0);
INSERT INTO `review` VALUES (33, 35, 9, 35, '17516639826', 4, '炸鸡口感很好，但配送时间有点长', 'dish', '2025-12-06 10:30:00', 0);
INSERT INTO `review` VALUES (34, 35, 9, NULL, '17516639826', 4, '店铺包装很用心，但希望能提供更多酱料选择', 'shop', '2025-12-06 10:30:00', 0);
INSERT INTO `review` VALUES (35, 32, 1, 1, '17516632964', 5, '牛肉拉面汤底浓郁，面条劲道！', 'dish', '2025-11-24 12:15:00', 0);
INSERT INTO `review` VALUES (36, 32, 1, 2, '17516632964', 4, '羊肉很新鲜，没有膻味，推荐尝试', 'dish', '2025-11-24 12:15:00', 0);
INSERT INTO `review` VALUES (37, 32, 1, NULL, '17516632964', 5, '配送速度快，包装完好，点赞！', 'shop', '2025-11-24 12:15:00', 0);
INSERT INTO `review` VALUES (38, 25, 2, 6, '17516631000', 3, '烤鸭皮不够脆，有点失望', 'dish', '2025-11-22 19:45:00', 0);
INSERT INTO `review` VALUES (39, 25, 2, 7, '17516631000', 4, '整只烤鸭分量很足，适合家庭聚餐', 'dish', '2025-11-22 19:45:00', 0);
INSERT INTO `review` VALUES (40, 25, 2, NULL, '17516631000', 3, '配送员服务态度一般，希望改进', 'shop', '2025-11-22 19:45:00', 0);
INSERT INTO `review` VALUES (41, 12, 3, 11, '17516632907', 5, '麻辣烫味道正宗，辣度刚好', 'dish', '2025-11-19 13:20:00', 0);
INSERT INTO `review` VALUES (42, 13, 3, NULL, '17516632907', 4, '价格实惠，食材新鲜，会再次光顾', 'shop', '2025-11-19 13:20:00', 0);
INSERT INTO `review` VALUES (43, 5, 2, 10, '17516632907', 5, '荷叶饼很薄很软，搭配烤鸭绝配！', 'dish', '2025-11-08 18:30:00', 0);
INSERT INTO `review` VALUES (44, 27, 7, 34, '17516639860', 5, '抹茶味道很纯正，奶盖也很绵密', 'dish', '2025-11-24 16:45:00', 0);
INSERT INTO `review` VALUES (45, 28, 7, 31, '17516639607', 4, '乌龙茶底很香，甜度适中', 'dish', '2025-11-24 14:20:00', 0);
INSERT INTO `review` VALUES (46, 28, 7, 32, '17516639607', 5, '草莓芝士口感丰富，强烈推荐！', 'dish', '2025-11-24 14:20:00', 0);
INSERT INTO `review` VALUES (50, 37, 5, NULL, '17516639826', 5, '味道很好，建议小伙伴们前来品尝', 'shop', '2025-12-09 19:41:51', 1);
INSERT INTO `review` VALUES (51, 37, 5, 21, '17516639826', 5, '米饭：味道很好，建议小伙伴们前来品尝', 'dish', '2025-12-09 19:41:51', 1);
INSERT INTO `review` VALUES (52, 37, 5, 24, '17516639826', 5, '经典黄焖鸡：味道很好，建议小伙伴们前来品尝', 'dish', '2025-12-09 19:41:51', 1);
INSERT INTO `review` VALUES (53, 37, 5, 25, '17516639826', 5, '黄焖茄子：味道很好，建议小伙伴们前来品尝', 'dish', '2025-12-09 19:41:51', 0);
INSERT INTO `review` VALUES (54, 38, 6, NULL, '17516632964', 5, '味道不错，推荐', 'shop', '2025-12-09 19:48:38', 1);
INSERT INTO `review` VALUES (55, 38, 6, 27, '17516632964', 4, '虾仁炒饭：味道不错，推荐', 'dish', '2025-12-09 19:48:38', 1);
INSERT INTO `review` VALUES (56, 39, 10, NULL, '17516632964', 5, '很美味，味道很棒，披萨也很大，配送快', 'shop', '2025-12-09 19:52:09', 2);
INSERT INTO `review` VALUES (57, 39, 10, 39, '17516632964', 4, '海鲜至尊披萨（九寸）：很美味，味道很棒，披萨也很大，配送快', 'dish', '2025-12-09 19:52:09', 1);
INSERT INTO `review` VALUES (58, 39, 10, 42, '17516632964', 5, '经典意式玛格丽特披萨（九寸）：很美味，味道很棒，披萨也很大，配送快', 'dish', '2025-12-09 19:52:09', 1);
INSERT INTO `review` VALUES (59, 23, 1, NULL, '17516631000', 5, '味道不错，牛肉筋道', 'shop', '2025-12-09 20:56:49', 2);
INSERT INTO `review` VALUES (60, 23, 1, 1, '17516631000', 5, '牛肉拉面：味道不错，牛肉筋道', 'dish', '2025-12-09 20:56:49', 2);

-- ----------------------------
-- Table structure for review_like
-- ----------------------------
DROP TABLE IF EXISTS `review_like`;
CREATE TABLE `review_like`  (
  `like_id` int(11) NOT NULL AUTO_INCREMENT,
  `review_id` int(11) NOT NULL COMMENT '评价ID',
  `user_phone` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '用户手机号',
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '点赞时间',
  PRIMARY KEY (`like_id`) USING BTREE,
  UNIQUE INDEX `unique_review_user`(`review_id`, `user_phone`) USING BTREE COMMENT '防止重复点赞',
  INDEX `idx_review_id`(`review_id`) USING BTREE,
  INDEX `idx_user_phone`(`user_phone`) USING BTREE,
  CONSTRAINT `fk_review_like_review` FOREIGN KEY (`review_id`) REFERENCES `review` (`review_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 26 CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = '评价点赞记录表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of review_like
-- ----------------------------
INSERT INTO `review_like` VALUES (5, 54, '17516631000', '2026-01-29 20:51:29');
INSERT INTO `review_like` VALUES (6, 58, '17516631000', '2026-01-29 20:51:30');
INSERT INTO `review_like` VALUES (7, 55, '17516631000', '2026-01-29 20:51:32');
INSERT INTO `review_like` VALUES (8, 50, '17516631000', '2026-01-29 20:51:33');
INSERT INTO `review_like` VALUES (9, 51, '17516631000', '2026-01-29 20:51:34');
INSERT INTO `review_like` VALUES (10, 52, '17516631000', '2026-01-29 20:51:35');
INSERT INTO `review_like` VALUES (14, 56, '17516631000', '2026-01-29 20:54:26');
INSERT INTO `review_like` VALUES (20, 60, '17516631000', '2026-01-29 21:08:44');
INSERT INTO `review_like` VALUES (21, 59, '17516631000', '2026-01-29 21:13:54');
INSERT INTO `review_like` VALUES (22, 59, '17516639826', '2026-01-29 21:16:02');
INSERT INTO `review_like` VALUES (23, 60, '17516639826', '2026-01-29 21:16:04');
INSERT INTO `review_like` VALUES (24, 57, '17516639826', '2026-01-29 21:16:06');
INSERT INTO `review_like` VALUES (25, 56, '17516639826', '2026-01-29 21:16:07');

-- ----------------------------
-- Table structure for shop
-- ----------------------------
DROP TABLE IF EXISTS `shop`;
CREATE TABLE `shop`  (
  `shop_id` int(11) NOT NULL AUTO_INCREMENT,
  `shop_name` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `owner_username` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `description` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
  `image_url` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `status` tinyint(1) NULL DEFAULT 1,
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`shop_id`) USING BTREE,
  UNIQUE INDEX `shop_name`(`shop_name`) USING BTREE,
  INDEX `idx_owner_username`(`owner_username`) USING BTREE,
  CONSTRAINT `fk_shop_owner_username` FOREIGN KEY (`owner_username`) REFERENCES `user` (`username`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 11 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of shop
-- ----------------------------
INSERT INTO `shop` VALUES (1, '兰州拉面', 'hui', '正宗兰州风味，手工拉面，汤鲜味美', '/images/shop/lanzhou.png', 1, '2025-10-19 16:53:59');
INSERT INTO `shop` VALUES (2, '北京烤鸭', 'iuh', '传统北京烤鸭，皮脆肉嫩，百年老店', '/images/shop/kaoya.jpg', 1, '2025-10-23 16:53:59');
INSERT INTO `shop` VALUES (3, '东北麻辣烫', 'hui', '新鲜食材，多种口味，麻辣鲜香', '/images/shop/mala.jpg', 1, '2025-10-23 16:53:59');
INSERT INTO `shop` VALUES (5, '黄焖鸡米饭', 'hui', '鲁菜经典，鸡肉鲜嫩，汤汁浓郁', '/images/shop/huanmeng.jpg', 1, '2025-11-10 16:53:59');
INSERT INTO `shop` VALUES (6, '鲜炒百味饭堂', 'hui', '淮扬名点，粒粒分明，色香味俱全', '/images/shop/yangzhou.jpg', 1, '2025-11-19 16:53:59');
INSERT INTO `shop` VALUES (7, '奶茶', 'hui', '一口温润甜醇，解锁日常小美好～', '/images/shop/nai_cha_31402454.jpg', 1, '2025-11-23 15:37:41');
INSERT INTO `shop` VALUES (9, '韩式炸鸡', 'iuh', '韩式炸鸡，一口鲜脆锁汁，地道韩味直击味蕾～', '/images/shop/han_shi_zha_ji_620c0882.jpg', 1, '2025-11-23 16:27:20');
INSERT INTO `shop` VALUES (10, '芝香窑烤披萨坊', 'iuh', '窑烤现制，芝香拉丝；一口饼底酥脆，满溢全球风味～', '/images/shop/zhi_xiang_yao_kao_pi_sa_fang_f1640052.jpg', 1, '2025-11-23 16:50:03');

-- ----------------------------
-- Table structure for user
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user`  (
  `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `username` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `password` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `telephone` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `role` int(11) NOT NULL,
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `is_super` tinyint(4) NULL DEFAULT 0 COMMENT '是否超级管理员，1=是，0=否',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `id`(`id`) USING BTREE COMMENT '主键索引，选UNIQUE',
  UNIQUE INDEX `uk_telephone`(`telephone`) USING BTREE,
  UNIQUE INDEX `uk_username`(`username`) USING BTREE,
  INDEX `username`(`username`) USING BTREE,
  INDEX `password`(`password`) USING BTREE,
  INDEX `telephone`(`telephone`) USING BTREE,
  INDEX `role`(`role`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 13 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of user
-- ----------------------------
INSERT INTO `user` VALUES (2, 'admin', '$2b$12$YujULoYpsU5OnblU9KLTMOPJlLUPy3aU9RteoHXeGkDS0DgPbwWvG', '17516630000', 1, '2025-10-20 15:10:37', 1);
INSERT INTO `user` VALUES (3, 'mty', '$2b$12$5pjh0R5w5uYy9UPkvJQLXONIKAKGOPUPXfVt52evHJj9f9iPjEf2G', '17516631000', 0, '2025-10-20 15:10:37', 0);
INSERT INTO `user` VALUES (9, 'hui', '$2b$12$fL7GBH8j56hsrCZV2WwRZOuxJBlSdhqP7HTO74LS.bkB307NUnUCq', '17516639860', 1, '2025-11-05 17:18:07', 0);
INSERT INTO `user` VALUES (10, 'iuh', '$2b$12$I7iM7zZnlveK0EzERqIPMOmNnaoTKOdf6J1lDGd2wbypcIb8aj16G', '17516639607', 1, '2025-11-10 20:02:57', 0);
INSERT INTO `user` VALUES (11, 'syy', '$2b$12$2yMhBPyQzqegg0osheR92OkJc0AaU0sdsIXgFs7DpE9DmjPRiu7Oa', '17516639826', 0, '2025-11-15 21:40:08', 0);
INSERT INTO `user` VALUES (12, 'wxe', '$2b$12$m9w2O1zwlPPpFLNUE7L6L.Y2NjJFeRcfeqmSCNFDZI23tkrrTKgie', '17516632964', 0, '2025-11-21 21:41:00', 0);

-- ----------------------------
-- Table structure for user_address
-- ----------------------------
DROP TABLE IF EXISTS `user_address`;
CREATE TABLE `user_address`  (
  `address_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_phone` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '关联用户手机号',
  `cons_name` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '收货人姓名',
  `cons_phone` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '收货人电话',
  `address_label` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '地址标签（如：家、公司、学校）',
  `province` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '省',
  `city` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '市',
  `district` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '区/县',
  `street` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '街道详细地址',
  `is_default` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否为默认地址（0-否，1-是）',
  `status` tinyint(1) NOT NULL DEFAULT 1 COMMENT '状态（0-删除，1-正常）',
  `created_time` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_time` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`address_id`) USING BTREE,
  INDEX `idx_user_phone`(`user_phone`) USING BTREE,
  INDEX `idx_is_default`(`is_default`) USING BTREE,
  INDEX `idx_status`(`status`) USING BTREE,
  CONSTRAINT `fk_user_address_user` FOREIGN KEY (`user_phone`) REFERENCES `user` (`telephone`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of user_address
-- ----------------------------
INSERT INTO `user_address` VALUES (1, '17516631000', '阿元', '17516631000', 'school', '河南省', '郑州市', '二七区', '大学路', 1, 1, '2026-02-06 20:18:56', '2026-02-13 22:35:40');
INSERT INTO `user_address` VALUES (2, '17516631000', '阿任', '17516631000', 'school', '北京市', '北京市', '东城区', '西城区大学东路110号', 0, 1, '2026-02-06 21:14:30', '2026-02-13 11:20:17');

-- ----------------------------
-- Table structure for user_msg
-- ----------------------------
DROP TABLE IF EXISTS `user_msg`;
CREATE TABLE `user_msg`  (
  `id` int(10) UNSIGNED NULL DEFAULT NULL,
  `real_name` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `sex` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `age` int(11) NULL DEFAULT NULL,
  `mail` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `phone` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `user_name` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `avatar_url` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT '/images/user/default-avatar.jpg' COMMENT '用户头像URL',
  UNIQUE INDEX `uk_phone`(`phone`) USING BTREE,
  INDEX `userid`(`id`) USING BTREE,
  INDEX `real_name`(`real_name`) USING BTREE,
  INDEX `sex`(`sex`) USING BTREE,
  INDEX `age`(`age`) USING BTREE,
  INDEX `mail`(`mail`) USING BTREE,
  INDEX `phone`(`phone`) USING BTREE,
  INDEX `user_name`(`user_name`) USING BTREE,
  CONSTRAINT `userid` FOREIGN KEY (`id`) REFERENCES `user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of user_msg
-- ----------------------------
INSERT INTO `user_msg` VALUES (2, '元', '男', 22, '320836@qq.com', '17516630000', 'admin', '/images/user/default-avatar.jpg');
INSERT INTO `user_msg` VALUES (3, '天宇', '男', 22, '787898@qq.com', '17516631000', 'mty', '/images/user/avatar_17516631000_8975610d.jpg');
INSERT INTO `user_msg` VALUES (12, '小王', '男', 25, 'bzcjbj@qq.com', '17516632964', 'wxe', '/images/user/avatar_17516632964_97ed7a33.jpg');
INSERT INTO `user_msg` VALUES (10, '真理', '男', 20, 'bvjb@qq.com', '17516639607', 'iuh', '/images/user/default-avatar.jpg');
INSERT INTO `user_msg` VALUES (11, '时空', '男', 20, 'cxbhabc@qq.com', '17516639826', 'syy', '/images/user/default-avatar.jpg');
INSERT INTO `user_msg` VALUES (9, '星空', '女', 25, 'bcjbj3313@qq.com', '17516639860', 'hui', '/images/user/default-avatar.jpg');

-- ----------------------------
-- View structure for v_order_detail
-- ----------------------------
DROP VIEW IF EXISTS `v_order_detail`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `v_order_detail` AS select `o`.`order_id` AS `order_id`,`o`.`shop_name` AS `shop_name`,`o`.`shop_id` AS `shop_id`,`o`.`order_money` AS `order_money`,`o`.`order_way` AS `order_way`,`o`.`cons_phone` AS `cons_phone`,`o`.`cons_name` AS `cons_name`,`o`.`cons_addre` AS `cons_addre`,`o`.`address_id` AS `address_id`,`o`.`checked` AS `checked`,`o`.`create_time` AS `create_time`,`ua`.`cons_name` AS `saved_cons_name`,`ua`.`cons_phone` AS `saved_cons_phone`,concat(`ua`.`province`,`ua`.`city`,`ua`.`district`,`ua`.`street`) AS `saved_full_address`,`ua`.`address_label` AS `address_label` from (`oorder` `o` left join `user_address` `ua` on((`o`.`address_id` = `ua`.`address_id`)));

-- ----------------------------
-- Procedure structure for migrate_old_addresses
-- ----------------------------
DROP PROCEDURE IF EXISTS `migrate_old_addresses`;
delimiter ;;
CREATE PROCEDURE `migrate_old_addresses`()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_order_id INT;
    DECLARE v_cons_phone VARCHAR(50);
    DECLARE v_cons_name VARCHAR(50);
    DECLARE v_cons_addre VARCHAR(50);
    DECLARE v_address_id INT;
    
    -- 游标遍历所有订单
    DECLARE cur CURSOR FOR 
        SELECT order_id, cons_phone, cons_name, cons_addre 
        FROM oorder 
        WHERE address_id IS NULL;
    
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    OPEN cur;
    
    read_loop: LOOP
        FETCH cur INTO v_order_id, v_cons_phone, v_cons_name, v_cons_addre;
        IF done THEN
            LEAVE read_loop;
        END IF;
        
        -- 检查用户是否有地址记录
        SELECT address_id INTO v_address_id 
        FROM user_address 
        WHERE user_phone = v_cons_phone 
          AND cons_name = v_cons_name 
          AND CONCAT(province, city, district, street) LIKE CONCAT('%', v_cons_addre, '%')
        LIMIT 1;
        
        -- 如果没有找到，创建一个新地址记录
        IF v_address_id IS NULL THEN
            INSERT INTO user_address (user_phone, cons_name, cons_phone, province, city, district, street, is_default)
            VALUES (v_cons_phone, v_cons_name, v_cons_phone, '河南省', '郑州市', '未知区域', v_cons_addre, 0);
            
            SET v_address_id = LAST_INSERT_ID();
        END IF;
        
        -- 更新订单的address_id
        UPDATE oorder SET address_id = v_address_id WHERE order_id = v_order_id;
    END LOOP;
    
    CLOSE cur;
END
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table delivery
-- ----------------------------
DROP TRIGGER IF EXISTS `wuliu_insert`;
delimiter ;;
CREATE TRIGGER `wuliu_insert` AFTER INSERT ON `delivery` FOR EACH ROW BEGIN
UPDATE oorder
SET oorder.checked=1
WHERE oorder.order_id=new.order_id;
END
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table oorder
-- ----------------------------
DROP TRIGGER IF EXISTS `order_insert`;
delimiter ;;
CREATE TRIGGER `order_insert` AFTER INSERT ON `oorder` FOR EACH ROW BEGIN
UPDATE orderway 
SET orderway.count=orderway.count+1
WHERE orderway.orderway_name=new.order_way;
END
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table oorder
-- ----------------------------
DROP TRIGGER IF EXISTS `order_update`;
delimiter ;;
CREATE TRIGGER `order_update` AFTER UPDATE ON `oorder` FOR EACH ROW BEGIN
if(new.order_way!=old.order_way)
	then
	UPDATE orderway SET orderway.count=orderway.count-1 WHERE orderway.orderway_name=old.order_way;
	UPDATE orderway SET orderway.count=orderway.count+1 WHERE orderway.orderway_name=new.order_way;
	END IF;
	END
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table oorder
-- ----------------------------
DROP TRIGGER IF EXISTS `order_delete`;
delimiter ;;
CREATE TRIGGER `order_delete` AFTER DELETE ON `oorder` FOR EACH ROW BEGIN
UPDATE orderway
SET orderway.count=orderway.count-1
WHERE orderway.orderway_name=old.order_way;
END
;;
delimiter ;

SET FOREIGN_KEY_CHECKS = 1;
