-- phpMyAdmin SQL Dump
-- version 3.5.1
-- http://www.phpmyadmin.net
--
-- Servidor: localhost
-- Tiempo de generación: 28-02-2023 a las 15:50:16
-- Versión del servidor: 5.5.24-log
-- Versión de PHP: 5.4.3

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Base de datos: `net_cube_2`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `alertas`
--

CREATE TABLE IF NOT EXISTS `alertas` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `FECHA` date NOT NULL,
  `HORA` time NOT NULL,
  `NOMBRE_MAQUINA` varchar(100) NOT NULL,
  `NIVEL` varchar(10) NOT NULL,
  `IP` varchar(20) NOT NULL,
  `TIPO_ALERTA` varchar(50) NOT NULL,
  `MENSAJE` text NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `configuracion`
--

CREATE TABLE IF NOT EXISTS `configuracion` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `EMAIL_RECEIVER` varchar(30) NOT NULL,
  `EMAIL_SENDER` varchar(30) NOT NULL,
  `PASSWORD_SENDER` varchar(30) NOT NULL,
  `SECONDS_INTERVAL` int(11) NOT NULL,
  `HARDDISK_ALERT` tinyint(1) NOT NULL,
  `HARDDISK_PARAM` varchar(10) NOT NULL,
  `WIFI_ALERT` tinyint(1) NOT NULL,
  `WIFI_PARAM` varchar(10) NOT NULL,
  `ETHERNET_ALERT` tinyint(1) NOT NULL,
  `ETHERNET_PARAM` varchar(10) NOT NULL,
  `DISCONNECTION_ALERT` tinyint(1) NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8mb4 AUTO_INCREMENT=2 ;

--
-- Volcado de datos para la tabla `configuracion`
--

INSERT INTO `configuracion` (`ID`, `EMAIL_RECEIVER`, `EMAIL_SENDER`, `PASSWORD_SENDER`, `SECONDS_INTERVAL`, `HARDDISK_ALERT`, `HARDDISK_PARAM`, `WIFI_ALERT`, `WIFI_PARAM`, `ETHERNET_ALERT`, `ETHERNET_PARAM`, `DISCONNECTION_ALERT`) VALUES
(1, '', '', '', 300, 0, '', 0, '', 0, '', 0);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `dispositivos`
--

CREATE TABLE IF NOT EXISTS `dispositivos` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `IP` varchar(250) NOT NULL,
  `HOSTNAME` varchar(250) NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8mb4 AUTO_INCREMENT=2 ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE IF NOT EXISTS `usuarios` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `EMAIL` varchar(100) NOT NULL,
  `PASSWORD` varchar(10) NOT NULL,
  `CHANGE_PASSWORD` tinyint(1) NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8mb4 AUTO_INCREMENT=22 ;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`ID`, `EMAIL`, `PASSWORD`, `CHANGE_PASSWORD`) VALUES
(15, 'admin', 'admin', 0);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
