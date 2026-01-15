-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:8889
-- Generation Time: Jan 15, 2026 at 10:00 PM
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
-- Table structure for table `users`
-- (Aceasta tabelă LIPSEA și este esențială pentru login!)
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` varchar(20) NOT NULL DEFAULT 'viewer'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `users`
-- User: admin / Parola: admin123
--

INSERT INTO `users` (`id`, `username`, `password`, `role`) VALUES
(1, 'admin', 'scrypt:32768:8:1$C0zX2z2z$adb863f35033c46755695627702750059e0996362955502750035033c4675569', 'admin');

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
('2', 'Echipament IT', 'Desktop', 'CJ-BV-PC01', 'Popescu Ion', 'USR01', '2023-05-10', '1', 'Grefier', '192.168.1.10', 'LAN', 'SN123456', 'MON123', '16GB', 'Windows 11', 'OEM-123', 'Office 2021', 'LIC-OFF-99', 'Bitdefender', 'Nu', '', 'Mouse, Tastatura', 'Tribunal', '1234', 'Functioneaza optim');

-- --------------------------------------------------------

--
-- Table structure for table `Interventii`
--

CREATE TABLE `Interventii` (
  `ID_INTERVENTIE` int(11) NOT NULL,
  `NR_INVENTAR` varchar(50) DEFAULT NULL,
  `TIP_ECHIPAMENT` varchar(50) DEFAULT NULL,
  `DATA_INTERVENTIE` date DEFAULT NULL,
  `TIP_INTERVENTIE` varchar(100) DEFAULT NULL,
  `TIP_OPERATIE` varchar(100) DEFAULT NULL,
  `DESCRIERE_INTERVENTIE` text,
  `componente_schimbate_adaugate` text,
  `DURATA_INTERVENTIE` varchar(50) DEFAULT NULL,
  `OPERATOR` varchar(100) DEFAULT NULL,
  `OBSERVATII` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `Interventii`
--

INSERT INTO `Interventii` (`ID_INTERVENTIE`, `NR_INVENTAR`, `TIP_ECHIPAMENT`, `DATA_INTERVENTIE`, `TIP_INTERVENTIE`, `TIP_OPERATIE`, `DESCRIERE_INTERVENTIE`, `componente_schimbate_adaugate`, `DURATA_INTERVENTIE`, `OPERATOR`, `OBSERVATII`) VALUES
(1, '3', 'Periferic', '2025-12-01', 'Hardware', 'Inlocuire Toner', 'Imprimanta printa cu dungi.', 'Cartus 85A', '30 min', 'Admin', 'Testat OK'),
(2, '2', 'Echipament IT', '2025-12-05', 'Software', 'Instalare OS', 'Reinstalare Windows 11', '', '2h', 'Admin', 'Activare licenta reusita');

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
('3', 'Periferic', 'Imprimanta', 'HP', 'LaserJet Pro', 'Secretariat', 'Elena M.', '2023-01-15', '', 'SN-PRN-001', '192.168.0.50', 'LAN', '512MB', 'A4', 'Alb-Negru', 'DA', 'Functionala', '', '', 'Tribunal', '', 'Necesita toner curand', '');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

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
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `Interventii`
--
ALTER TABLE `Interventii`
  MODIFY `ID_INTERVENTIE` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;