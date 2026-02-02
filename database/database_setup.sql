-- Disable foreign key checks temporarily to avoid issues during table creation
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `System Logs`;
DROP TABLE IF EXISTS `Transactions`;
DROP TABLE IF EXISTS `Users`;
DROP TABLE IF EXISTS `Transaction Categories`;

-- Create Transaction Categories table
CREATE TABLE `Transaction Categories`(
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL,
    `description` VARCHAR(255) NOT NULL
);

-- Create Users table
CREATE TABLE `Users`(
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(50) NOT NULL,
    `phone_number` VARCHAR(50) NOT NULL
);

-- Create Transactions table
-- Changed: Added category_id and user_id as foreign keys
CREATE TABLE `Transactions`(
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `date` DATETIME NOT NULL,
    `subject` VARCHAR(50) DEFAULT NULL,
    `body` TEXT DEFAULT NULL,
    `status` INT DEFAULT 1,
    `service_center` VARCHAR(255) DEFAULT '',
    `read` TINYTEXT DEFAULT NULL,
    `locked` INT DEFAULT 0,
    `date_sent` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `readable_date` VARCHAR(100) DEFAULT NULL,
    `contact_name` VARCHAR(50) DEFAULT NULL,
    `transaction_id` INT DEFAULT NULL,
    `amount` DOUBLE NOT NULL,
    `balance_after` DOUBLE DEFAULT 0,
    `direction` VARCHAR(10) NOT NULL,
    `category_id` BIGINT UNSIGNED DEFAULT NULL,
    `user_id` BIGINT UNSIGNED DEFAULT NULL,
    FOREIGN KEY (`category_id`) REFERENCES `Transaction Categories`(`id`) ON DELETE SET NULL,
    FOREIGN KEY (`user_id`) REFERENCES `Users`(`id`) ON DELETE SET NULL
);

-- Create System Logs table
CREATE TABLE `System Logs`(
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `type` VARCHAR(50) NOT NULL,
    `timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `message` TEXT NOT NULL,
    `transaction_id` BIGINT UNSIGNED DEFAULT NULL,
    `user_id` BIGINT UNSIGNED DEFAULT NULL,
    FOREIGN KEY (`transaction_id`) REFERENCES `Transactions`(`id`) ON DELETE SET NULL,
    FOREIGN KEY (`user_id`) REFERENCES `Users`(`id`) ON DELETE SET NULL
);

-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;