-- MySQL dump 10.13  Distrib 5.7.21, for macos10.13 (x86_64)
--
-- Host: localhost    Database: orderinfo
-- ------------------------------------------------------
-- Server version 5.7.21

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders_server`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `orders_server` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `customer` varchar(30) NOT NULL,
  `red` int(11) DEFAULT NULL,
  `blue` int(11) DEFAULT NULL,
  `green` int(11) DEFAULT NULL,
  `yellow` int(11) DEFAULT NULL,
  `black` int(11) DEFAULT NULL,
  `white` int(11) DEFAULT NULL,
  `pending` tinyint(1) DEFAULT NULL,
  `orderdate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `tokendate` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `shipdate` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `shipped` boolean DEFAULT FALSE,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `orders_app`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `orders_app` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `orderid` int(11) NOT NULL,
  `carid` int(11) NOT NULL DEFAULT -1,
  `red` int(11) DEFAULT NULL,
  `blue` int(11) DEFAULT NULL,
  `green` int(11) DEFAULT NULL,
  `yellow` int(11) DEFAULT NULL,
  `black` int(11) DEFAULT NULL,
  `white` int(11) DEFAULT NULL,
  `arriveAtReceiving` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `loadedDate` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `arriveAtShipping` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `unloadedDate` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;


DROP TABLE IF EXISTS `carinfo`;
-- auto-generated definition
CREATE TABLE `carinfo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `carId` int(11) NOT NULL DEFAULT 0,
  `position` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;

/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-05-17 16:20:26
