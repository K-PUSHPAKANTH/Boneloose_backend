-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Mar 27, 2026 at 04:48 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.1.25

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `boneloss`
--

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `full_name` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `is_verified` int(11) DEFAULT 1,
  `role` enum('dentist','student','research') DEFAULT 'dentist',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `otp` varchar(6) DEFAULT NULL,
  `otp_expiry` datetime DEFAULT NULL,
  `otp_verified` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `full_name`, `email`, `phone`, `password`, `is_verified`, `role`, `created_at`, `otp`, `otp_expiry`, `otp_verified`) VALUES
(2, 'Sri Kanth', 'test@gmail.com', '9876543210', '123456', 1, 'dentist', '2026-02-19 08:30:53', NULL, NULL, 0),
(3, 'Sri', 'pushpa29224@gmail.com', '12345', 'password123', 1, 'dentist', '2026-02-26 09:06:10', NULL, NULL, 0),
(4, 'Sri', 'srik29924@gmail.com', '7729047460', 'srik@12345', 1, 'dentist', '2026-03-06 08:37:03', NULL, NULL, 0),
(5, 'Deva', 'punugotideva618@gmail.com', '7993537243', '11008600', 1, 'dentist', '2026-03-06 08:50:34', NULL, NULL, 0),
(6, 'srikanth', 'sri292242@gmail.com', '12345678', '87654321', 1, 'dentist', '2026-03-12 05:17:19', NULL, NULL, 0),
(7, 'srikanth', 'srik@gmail.com', '12345678', '87654321', 1, 'dentist', '2026-03-12 05:19:06', NULL, NULL, 0),
(8, 'vishal', 'vishal@gmail.com', '12345679', '87654321', 1, 'dentist', '2026-03-12 06:46:41', NULL, NULL, 0),
(9, 'mahi', 'mahi@gmail.com', '123456789', '987654321', 1, 'dentist', '2026-03-12 07:00:31', NULL, NULL, 0),
(10, 'sidhu', 'sidhu@gmail.com', '1233654', '7894562', 1, 'dentist', '2026-03-12 07:21:37', NULL, NULL, 0),
(11, 'string', 'srinivasvellaturi61@gmail.com', 'string', 'string', 1, 'dentist', '2026-03-13 04:09:16', '000000', NULL, 0),
(12, 'Srinjvas', 'sri1@899.co@', '8/8/', 'bbbbhujA1…', 1, 'dentist', '2026-03-13 05:36:25', NULL, NULL, 0),
(13, 'srikanth', 'abhi@gmail.com1234', '12345667', '87654329', 1, 'dentist', '2026-03-13 07:59:58', NULL, NULL, 0),
(14, 'Layn', 'layna4115@gmail.com', '6374258264', 'Layna@123', 1, 'dentist', '2026-03-16 04:45:41', NULL, NULL, 0),
(15, 'Dr Ravi', 'dentist@gmail.com', '9999999999', '123456', 1, 'dentist', '2026-03-16 05:28:04', NULL, NULL, 0),
(16, 'Rahul', 'student@gmail.com', '8888888888', '123456', 1, 'student', '2026-03-16 05:28:43', NULL, NULL, 0),
(17, 'Prof Kumar', 'research@gmail.com', '7777777777', '123456', 1, 'research', '2026-03-16 05:29:11', NULL, NULL, 0),
(18, 'vishnu', 'vishnu@gmail.com', '1236454', '@123645', 1, 'dentist', '2026-03-17 08:36:01', NULL, NULL, 0),
(19, 'Testuser', 'sample@saveetha.com', '9876543210', 'Testusertest@123', 1, 'dentist', '2026-03-24 04:02:52', NULL, NULL, 0);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
