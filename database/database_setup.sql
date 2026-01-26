CREATE TABLE `Transactions`(
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `date` DATETIME NOT NULL,
    `subject` VARCHAR(50) NOT NULL,
    `body` TEXT NOT NULL,
    `status` INT NOT NULL,
    `service_center` VARCHAR(255) NOT NULL,
    `read` TINYTEXT NOT NULL,
    `locked` INT NOT NULL,
    `date_sent` TIMESTAMP NOT NULL,
    `readable_date` VARCHAR(100) NOT NULL,
    `contact_name` VARCHAR(50) NOT NULL,
    `transaction_id` INT NOT NULL,
    `amount` DOUBLE NOT NULL,
    `balance_after` DOUBLE NOT NULL,
    `direction` VARCHAR(5) NOT NULL
);
CREATE TABLE `Users`(
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(50) NOT NULL,
    `phone_number` VARCHAR(50) NOT NULL
);
CREATE TABLE `Transaction Categories`(
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL,
    `description` VARCHAR(255) NOT NULL
);
CREATE TABLE `System Logs`(
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `type` VARCHAR(10) NOT NULL,
    `timestamp` TIMESTAMP NOT NULL,
    `message` TEXT NOT NULL,
    `transaction_id` BIGINT NOT NULL,
    `user_id` BIGINT NOT NULL
);
ALTER TABLE
    `System Logs` ADD CONSTRAINT `system logs_user_id_foreign` FOREIGN KEY(`user_id`) REFERENCES `Users`(`id`);
ALTER TABLE
    `Transactions` ADD CONSTRAINT `transactions_id_foreign` FOREIGN KEY(`id`) REFERENCES `Transaction Categories`(`id`);
ALTER TABLE
    `System Logs` ADD CONSTRAINT `system logs_transaction_id_foreign` FOREIGN KEY(`transaction_id`) REFERENCES `Transactions`(`id`);
ALTER TABLE
    `Users` ADD CONSTRAINT `users_id_foreign` FOREIGN KEY(`id`) REFERENCES `Transactions`(`id`);