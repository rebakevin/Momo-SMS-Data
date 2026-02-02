CREATE TABLE `transactions`(
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
    `user_id` BIGINT NOT NULL,
    `category_id` INT NOT NULL,
    `amount` DOUBLE NOT NULL,
    `balance_after` DOUBLE NOT NULL,
    `direction` VARCHAR(5) NOT NULL
);
CREATE TABLE `users`(
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(50) NOT NULL,
    `phone_number` VARCHAR(50) NOT NULL
);
CREATE TABLE `transaction_categories`(
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL,
    `description` VARCHAR(255) NOT NULL
);
CREATE TABLE `system_logs`(
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `type` VARCHAR(10) NOT NULL,
    `timestamp` TIMESTAMP NOT NULL,
    `message` TEXT NOT NULL,
    `transaction_id` BIGINT NOT NULL,
    `user_id` BIGINT NOT NULL
);
ALTER TABLE
    `system_logs` ADD CONSTRAINT `system_logs_user_id_foreign` FOREIGN KEY(`user_id`) REFERENCES `users`(`id`);
ALTER TABLE
    `transactions` ADD CONSTRAINT `transactions_id_foreign` FOREIGN KEY(`category_id`) REFERENCES `transaction_categories`(`id`);
ALTER TABLE
    `system_logs` ADD CONSTRAINT `system_logs_transaction_id_foreign` FOREIGN KEY(`transaction_id`) REFERENCES `transactions`(`id`);
ALTER TABLE
    `transactions` ADD CONSTRAINT `transactions_user_id_foreign` FOREIGN KEY(`user_id`) REFERENCES `users`(`id`);