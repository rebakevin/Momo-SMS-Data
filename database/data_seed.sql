-- ============================================
-- MoMo SMS Data - Sample Data Seeding Script
-- ============================================
-- This script populates the database with sample data for testing
-- Run this after database_setup.sql

-- Transaction Categories
INSERT INTO `Transaction Categories` (`id`, `name`, `description`) VALUES
(1, 'Mobile Money Transfer', 'Person to person money transfer via mobile'),
(2, 'Bill Payment', 'Utility and service bill payments'),
(3, 'Airtime Purchase', 'Mobile airtime and data bundle purchases'),
(4, 'Merchant Payment', 'Payments to registered merchants'),
(5, 'Salary Payment', 'Salary and payroll disbursements');

-- Users
INSERT INTO `Users` (`id`, `name`, `phone_number`) VALUES
(1, 'Kevin Rebakure', '0788123630'),
(2, 'Jane Doe', '0789456123'),
(3, 'John Smith', '0787654321'),
(4, 'Alice Johnson', '0781111111'),
(5, 'Bob Wilson', '0782222222'),
(6, 'Sarah Williams', '0783333333'),
(7, 'David Brown', '0784444444');

-- Sample Transactions
-- Transaction 1: Initial balance (received)
INSERT INTO `Transactions` (
    `id`, `date`, `subject`, `body`, `status`, `service_center`, 
    `read`, `locked`, `date_sent`, `readable_date`, `contact_name`, 
    `transaction_id`, `amount`, `balance_after`, `direction`, 
    `category_id`, `user_id`
) VALUES (
    1, 
    '2026-03-10 09:15:00', 
    'Payment Received',
    'You have received RWF 50,000 from Kevin Rebakure',
    1,
    'MTN',
    '1',
    0,
    '2026-03-10 09:15:00',
    '10 Mar 2026 09:15:00 AM',
    'Kevin Rebakure',
    1001,
    50000.00,
    50000.00,
    'received',
    1,
    1
);

-- Transaction 2: Sent money
INSERT INTO `Transactions` (
    `id`, `date`, `subject`, `body`, `status`, `service_center`, 
    `read`, `locked`, `date_sent`, `readable_date`, `contact_name`, 
    `transaction_id`, `amount`, `balance_after`, `direction`, 
    `category_id`, `user_id`
) VALUES (
    2, 
    '2026-03-10 14:30:00', 
    'Payment Sent',
    'You have sent RWF 15,000 to Jane Doe',
    1,
    'Airtel',
    '1',
    0,
    '2026-03-10 14:30:00',
    '10 Mar 2026 02:30:00 PM',
    'Jane Doe',
    1002,
    15000.00,
    35000.00,
    'sent',
    1,
    2
);

-- Transaction 3: Bill payment
INSERT INTO `Transactions` (
    `id`, `date`, `subject`, `body`, `status`, `service_center`, 
    `read`, `locked`, `date_sent`, `readable_date`, `contact_name`, 
    `transaction_id`, `amount`, `balance_after`, `direction`, 
    `category_id`, `user_id`
) VALUES (
    3, 
    '2026-03-11 10:00:00', 
    'Bill Payment',
    'You have paid RWF 8,500 for electricity bill',
    1,
    'M-Money',
    '1',
    0,
    '2026-03-11 10:00:00',
    '11 Mar 2026 10:00:00 AM',
    'EUCL',
    1003,
    8500.00,
    26500.00,
    'sent',
    2,
    NULL
);

-- Transaction 4: Received salary
INSERT INTO `Transactions` (
    `id`, `date`, `subject`, `body`, `status`, `service_center`, 
    `read`, `locked`, `date_sent`, `readable_date`, `contact_name`, 
    `transaction_id`, `amount`, `balance_after`, `direction`, 
    `category_id`, `user_id`
) VALUES (
    4, 
    '2026-03-11 16:45:00', 
    'Salary Payment',
    'You have received RWF 120,000 from ABC Company',
    1,
    'MTN',
    '1',
    0,
    '2026-03-11 16:45:00',
    '11 Mar 2026 04:45:00 PM',
    'ABC Company',
    1004,
    120000.00,
    146500.00,
    'received',
    5,
    NULL
);

-- Transaction 5: Airtime purchase
INSERT INTO `Transactions` (
    `id`, `date`, `subject`, `body`, `status`, `service_center`, 
    `read`, `locked`, `date_sent`, `readable_date`, `contact_name`, 
    `transaction_id`, `amount`, `balance_after`, `direction`, 
    `category_id`, `user_id`
) VALUES (
    5, 
    '2026-03-12 08:20:00', 
    'Airtime Purchase',
    'You have purchased RWF 2,000 airtime',
    1,
    'Airtel',
    '1',
    0,
    '2026-03-12 08:20:00',
    '12 Mar 2026 08:20:00 AM',
    'Airtel Rwanda',
    1005,
    2000.00,
    144500.00,
    'sent',
    3,
    NULL
);

-- Transaction 6: Merchant payment
INSERT INTO `Transactions` (
    `id`, `date`, `subject`, `body`, `status`, `service_center`, 
    `read`, `locked`, `date_sent`, `readable_date`, `contact_name`, 
    `transaction_id`, `amount`, `balance_after`, `direction`, 
    `category_id`, `user_id`
) VALUES (
    6, 
    '2026-03-12 11:10:00', 
    'Merchant Payment',
    'You have paid RWF 5,500 to Simba Supermarket',
    1,
    'M-Money',
    '1',
    0,
    '2026-03-12 11:10:00',
    '12 Mar 2026 11:10:00 AM',
    'Simba Supermarket',
    1006,
    5500.00,
    139000.00,
    'sent',
    4,
    NULL
);

-- Transaction 7: Received from friend
INSERT INTO `Transactions` (
    `id`, `date`, `subject`, `body`, `status`, `service_center`, 
    `read`, `locked`, `date_sent`, `readable_date`, `contact_name`, 
    `transaction_id`, `amount`, `balance_after`, `direction`, 
    `category_id`, `user_id`
) VALUES (
    7, 
    '2026-03-12 15:30:00', 
    'Money Transfer',
    'You have received RWF 10,000 from John Smith',
    1,
    'MTN',
    '1',
    0,
    '2026-03-12 15:30:00',
    '12 Mar 2026 03:30:00 PM',
    'John Smith',
    1007,
    10000.00,
    149000.00,
    'received',
    1,
    3
);

-- System Logs
INSERT INTO `System Logs` (`type`, `timestamp`, `message`, `transaction_id`, `user_id`) VALUES
('INFO', '2026-03-10 09:15:00', 'Transaction 1001 created successfully', 1, 1),
('INFO', '2026-03-10 14:30:00', 'Transaction 1002 created successfully', 2, 2),
('INFO', '2026-03-11 10:00:00', 'Bill payment transaction 1003 completed', 3, NULL),
('INFO', '2026-03-11 16:45:00', 'Salary payment transaction 1004 received', 4, NULL),
('INFO', '2026-03-12 08:20:00', 'Airtime purchase transaction 1005 completed', 5, NULL),
('INFO', '2026-03-12 11:10:00', 'Merchant payment transaction 1006 completed', 6, NULL),
('INFO', '2026-03-12 15:30:00', 'Transaction 1007 created successfully', 7, 3),
('INFO', '2026-03-12 09:00:00', 'Database seeded with sample data', NULL, NULL);

-- Summary
SELECT 'Data seeding completed successfully!' AS Status;
SELECT COUNT(*) AS 'Total Transaction Categories' FROM `Transaction Categories`;
SELECT COUNT(*) AS 'Total Users' FROM `Users`;
SELECT COUNT(*) AS 'Total Transactions' FROM `Transactions`;
SELECT COUNT(*) AS 'Total System Logs' FROM `System Logs`;
