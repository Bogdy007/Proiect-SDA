-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:8889
-- Generation Time: Dec 27, 2025 at 03:47 PM
-- Server version: 8.0.40
-- PHP Version: 8.3.14

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `inventar_it`
--

-- --------------------------------------------------------

--
-- Table structure for table `Echipamente`
--

CREATE TABLE `Echipamente` (
  `NR_INVENTAR` varchar(50) NOT NULL,
  `CATEGORIE` varchar(100) DEFAULT NULL,
  `TIP_CALC` varchar(100) DEFAULT NULL,
  `NUME_PC` varchar(100) DEFAULT NULL,
  `UTILIZATOR` varchar(100) DEFAULT NULL,
  `NR_USER` varchar(50) DEFAULT NULL,
  `DATA_ACHIZITIE` date DEFAULT NULL,
  `ETAJ` varchar(50) DEFAULT NULL,
  `FUNCTIE` varchar(100) DEFAULT NULL,
  `IP` varchar(50) DEFAULT NULL,
  `RETEA` varchar(50) DEFAULT NULL,
  `SERIE_UC` varchar(100) DEFAULT NULL,
  `SERIE_MON` varchar(100) DEFAULT NULL,
  `MEMORIE` varchar(100) DEFAULT NULL,
  `SISTEM_OPERARE` varchar(100) DEFAULT NULL,
  `LICENTA_SO` varchar(100) DEFAULT NULL,
  `OFFICE` varchar(100) DEFAULT NULL,
  `LICENTA_OFFICE` varchar(100) DEFAULT NULL,
  `ANTIVIRUS` varchar(100) DEFAULT NULL,
  `CAMERA` varchar(100) DEFAULT NULL,
  `TELEFON` varchar(50) DEFAULT NULL,
  `PERIFERICE` text,
  `PARCHET` varchar(100) DEFAULT NULL,
  `PASS` varchar(100) DEFAULT NULL,
  `OBS` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `Echipamente`
--

INSERT INTO `Echipamente` (`NR_INVENTAR`, `CATEGORIE`, `TIP_CALC`, `NUME_PC`, `UTILIZATOR`, `NR_USER`, `DATA_ACHIZITIE`, `ETAJ`, `FUNCTIE`, `IP`, `RETEA`, `SERIE_UC`, `SERIE_MON`, `MEMORIE`, `SISTEM_OPERARE`, `LICENTA_SO`, `OFFICE`, `LICENTA_OFFICE`, `ANTIVIRUS`, `CAMERA`, `TELEFON`, `PERIFERICE`, `PARCHET`, `PASS`, `OBS`) VALUES
('2', 'Echipament IT', 'eu', 'pc', '', '', NULL, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'da', '', '');

-- --------------------------------------------------------

--
-- Table structure for table `Interventii`
--

CREATE TABLE `Interventii` (
  `ID_INTERVENTIE` int NOT NULL,
  `NR_INVENTAR` varchar(50) DEFAULT NULL,
  `TIP_ECHIPAMENT` varchar(50) DEFAULT NULL,
  `DATA_INTERVENTIE` date DEFAULT NULL,
  `TIP_INTERVENTIE` varchar(100) DEFAULT NULL,
  `TIP_OPERATIE` varchar(100) DEFAULT NULL,
  `DESCRIERE_INTERVENTIE` text,
  `componente_schimbate_adaugate` text,
  `COMPONENTE` text,
  `DURATA` varchar(50) DEFAULT NULL,
  `OPERATOR` varchar(100) DEFAULT NULL,
  `OBSERVATII` text,
  `DURATA_INTERVENTIE` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `Interventii`
--

INSERT INTO `Interventii` (`ID_INTERVENTIE`, `NR_INVENTAR`, `TIP_ECHIPAMENT`, `DATA_INTERVENTIE`, `TIP_INTERVENTIE`, `TIP_OPERATIE`, `DESCRIERE_INTERVENTIE`, `componente_schimbate_adaugate`, `COMPONENTE`, `DURATA`, `OPERATOR`, `OBSERVATII`, `DURATA_INTERVENTIE`) VALUES
(2, '3', 'periferic', '2025-12-01', 'Hardware', 'inlocuire', '', '', NULL, NULL, 'eu', '', '1h'),
(3, '3', 'periferic', '2025-12-01', '', '', '', 'er', NULL, NULL, 'end', '', ''),
(4, '2', 'echipament', '2025-12-01', 'Software', '', '', 'eu', NULL, NULL, 'eu', '', '');

-- --------------------------------------------------------

--
-- Table structure for table `Periferice`
--

CREATE TABLE `Periferice` (
  `NR_INVENTAR` varchar(50) NOT NULL,
  `CATEGORIE` varchar(100) DEFAULT NULL,
  `TIP` varchar(100) DEFAULT NULL,
  `PRODUCATOR` varchar(100) DEFAULT NULL,
  `NUME_PERIFERICE` varchar(100) DEFAULT NULL,
  `UTILIZATOR` varchar(100) DEFAULT NULL,
  `NUME_USER` varchar(100) DEFAULT NULL,
  `DATA_ACHIZITIE` date DEFAULT NULL,
  `NUME_CALC` varchar(100) DEFAULT NULL,
  `SERIE_UC` varchar(100) DEFAULT NULL,
  `IP` varchar(50) DEFAULT NULL,
  `RETEA` varchar(100) DEFAULT NULL,
  `MEMORIE` varchar(100) DEFAULT NULL,
  `FORMAT` varchar(50) DEFAULT NULL,
  `CULOARE_IMPRIMARE` varchar(50) DEFAULT NULL,
  `DUPLEX` varchar(50) DEFAULT NULL,
  `STARE_PARAMETRI` varchar(100) DEFAULT NULL,
  `CAMERA` varchar(100) DEFAULT NULL,
  `ANTIVIRUS` varchar(100) DEFAULT NULL,
  `PARCHET` varchar(100) DEFAULT NULL,
  `PASS` varchar(100) DEFAULT NULL,
  `OBS` text,
  `OBS2` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `Periferice`
--

INSERT INTO `Periferice` (`NR_INVENTAR`, `CATEGORIE`, `TIP`, `PRODUCATOR`, `NUME_PERIFERICE`, `UTILIZATOR`, `NUME_USER`, `DATA_ACHIZITIE`, `NUME_CALC`, `SERIE_UC`, `IP`, `RETEA`, `MEMORIE`, `FORMAT`, `CULOARE_IMPRIMARE`, `DUPLEX`, `STARE_PARAMETRI`, `CAMERA`, `ANTIVIRUS`, `PARCHET`, `PASS`, `OBS`, `OBS2`) VALUES
('3', 'Periferic', 'Imprimanta', 'HP', '243ETG', 'eu', 'Vasile', NULL, 'Da', '', '192.168.0.1', 'daa', 'da', 'jpg', 'alb', 'da', 'f buna', 'da', '', '', '', '', ''),
('6', 'Periferic', 'sfsv', '', '', 'sdfsfs', '', NULL, 'sdcsd', '', '', '', '', '', '', '', '', '', '', '', '', '', '');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `Echipamente`
--
ALTER TABLE `Echipamente`
  ADD PRIMARY KEY (`NR_INVENTAR`);

--
-- Indexes for table `Interventii`
--
ALTER TABLE `Interventii`
  ADD PRIMARY KEY (`ID_INTERVENTIE`);

--
-- Indexes for table `Periferice`
--
ALTER TABLE `Periferice`
  ADD PRIMARY KEY (`NR_INVENTAR`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `Interventii`
--
ALTER TABLE `Interventii`
  MODIFY `ID_INTERVENTIE` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
