create database perishable_management_system;
use  perishable_management_system;

CREATE TABLE FOOD_SOURCES (
    SOURCE_ID INT AUTO_INCREMENT,   -- Automatically increment the ID for new entries
    NAME VARCHAR(255) NOT NULL,     -- Source name should not be null
    CONTACT_NAME VARCHAR(255),      -- Contact person's name
    CONTACT VARCHAR(255) NOT NULL,  -- Contact info (phone or other) is required
    EMAIL VARCHAR(255) UNIQUE,      -- Email should be unique for each source
    DETAILS TEXT,                   -- Additional details about the source
    LOCALITY VARCHAR(255),          -- Locality information
    PINCODE VARCHAR(10) CHECK (PINCODE REGEXP '^[0-9]{6}$'), -- Ensuring pincode format (assuming 6 digits in this case)
    PRIMARY KEY (SOURCE_ID)         -- Set SOURCE_ID as the primary key
);

ALTER TABLE FOOD_SOURCES
    MODIFY DETAILS TEXT DEFAULT NULL,
    MODIFY LOCALITY VARCHAR(255) DEFAULT NULL,
    MODIFY PINCODE VARCHAR(10) DEFAULT NULL;


-- MULTIVALUED ATTR
CREATE TABLE TYPE_OF_SOURCE (
    SOURCE_ID INT,
    TYPE_SOURCE VARCHAR(255),
    PRIMARY KEY (SOURCE_ID, TYPE_SOURCE),
    FOREIGN KEY (SOURCE_ID) REFERENCES FOOD_SOURCES(SOURCE_ID)
);


-- FOOD_ITEM table
CREATE TABLE FOOD_ITEM (
    FOOD_ID INT AUTO_INCREMENT,      -- Auto-incrementing food item ID
    NAME VARCHAR(255) NOT NULL,      -- Name of the food item, cannot be null
    QUANTITY INT NOT NULL CHECK (QUANTITY > 0),  -- Quantity should be a positive integer
    CATEGORY VARCHAR(255),           -- Category of the food item (e.g., perishable/non-perishable)
    EXPIRY_DATE DATE,                -- Expiry date of the food item
    PRIMARY KEY (FOOD_ID)            -- FOOD_ID is the primary key
);

ALTER TABLE FOOD_ITEM
ADD COLUMN SOURCE_ID INT,
ADD FOREIGN KEY (SOURCE_ID) REFERENCES FOOD_SOURCES(SOURCE_ID);


-- PROVIDES RELATION (M:N RELATION)
CREATE TABLE PROVIDES (
    SOURCE_ID INT,
    FOOD_ID INT,
    PRIMARY KEY (SOURCE_ID, FOOD_ID),
    FOREIGN KEY (SOURCE_ID) REFERENCES FOOD_SOURCES(SOURCE_ID),
    FOREIGN KEY (FOOD_ID) REFERENCES FOOD_ITEM(FOOD_ID)
);

-- NGO table
CREATE TABLE NGO (
    NGO_ID INT AUTO_INCREMENT,       -- Auto-incrementing NGO ID
    NAME VARCHAR(255) NOT NULL,      -- Name of the NGO, cannot be null
    CONTACT_NAME VARCHAR(255),       -- Contact person's name
    CONTACT VARCHAR(255) NOT NULL,   -- Contact info (phone or other) is required
    EMAIL VARCHAR(255) UNIQUE,       -- Email should be unique for each NGO
    CATEGORY_REQ VARCHAR(255),       -- Required food category for the NGO
    ADDRESS TEXT,                    -- NGO's address
    PRIMARY KEY (NGO_ID)             -- NGO_ID is the primary key
);

ALTER TABLE NGO 
    MODIFY CATEGORY_REQ VARCHAR(255)DEFAULT NULL,
    MODIFY ADDRESS TEXT DEFAULT NULL;
    

-- DONATIONS table - WEAK ENTITY

CREATE TABLE DONATIONS (
    DONATION_ID INT AUTO_INCREMENT,
    SOURCE_ID INT NOT NULL,
    NGO_ID INT NOT NULL,
    SOURCE VARCHAR(255) NOT NULL,
    DESTINATION VARCHAR(255) NOT NULL,
    QUANTITY INT NOT NULL CHECK (QUANTITY > 0),
    CATEGORY VARCHAR(255),
    PRIMARY KEY (DONATION_ID),
    FOREIGN KEY (SOURCE_ID) REFERENCES FOOD_SOURCES(SOURCE_ID),
    FOREIGN KEY (NGO_ID) REFERENCES NGO(NGO_ID)
);

-- DONATES TO RELATION - WEAK
CREATE TABLE DONATES_TO(
    SOURCE_ID INT,
    DONATION_ID INT,
    DATE_TIME DATETIME,
    PRIMARY KEY (SOURCE_ID, DONATION_ID),
    FOREIGN KEY (SOURCE_ID) REFERENCES FOOD_SOURCES(SOURCE_ID),
    FOREIGN KEY (DONATION_ID) REFERENCES DONATIONS(DONATION_ID)
);

-- RECIEVES RELATION - WEAK
CREATE TABLE RECEIVES (
    NGO_ID INT,
    DONATION_ID INT,
    PRIMARY KEY (NGO_ID, DONATION_ID),
    FOREIGN KEY (NGO_ID) REFERENCES NGO(NGO_ID),
    FOREIGN KEY (DONATION_ID) REFERENCES DONATIONS(DONATION_ID)
);


-- FOOD_PICKUP table
CREATE TABLE FOOD_PICKUP (
    PICKUP_ID INT AUTO_INCREMENT,    -- Auto-incrementing pickup ID
	SOURCE_ID INT NOT NULL,
    DRIVER_ID INT NOT NULL,          -- ID of the driver responsible for the pickup
    DRIVER_NAME VARCHAR(255),        -- Name of the driver
    CONTACT VARCHAR(255),            -- Contact info of the driver
    STATUS VARCHAR(50),              -- Status of the pickup (e.g., pending, completed)
    DESTINATION VARCHAR(255),        -- Destination of the pickup
    VEHICLE_TYPE VARCHAR(50),        -- Type of vehicle used for the pickup
    PRIMARY KEY (PICKUP_ID),          -- PICKUP_ID is the primary key
	FOREIGN KEY (SOURCE_ID) REFERENCES FOOD_SOURCES(SOURCE_ID)
);


-- IMPACT table
CREATE TABLE IMPACT (
    IMPACT_ID INT AUTO_INCREMENT,
    SOURCE_ID INT NOT NULL,
    NGO_ID INT NOT NULL,
    SOURCE VARCHAR(255) NOT NULL,
    DESTINATION VARCHAR(255) NOT NULL,
    FEEDBACK TEXT,
    RATE INT CHECK (RATE BETWEEN 1 AND 5),
    PEOPLE_HELPED INT CHECK (PEOPLE_HELPED >= 0),
    PRIMARY KEY (IMPACT_ID),
    FOREIGN KEY (SOURCE_ID) REFERENCES FOOD_SOURCES(SOURCE_ID),
    FOREIGN KEY (NGO_ID) REFERENCES NGO(NGO_ID)
);

-- SCHEDULES RELATION 
CREATE TABLE SCHEDULES (
    SOURCE_ID INT,
    PICKUP_ID INT,
    DATE DATE,
    TIME TIME,
    PRIMARY KEY (SOURCE_ID, PICKUP_ID),
    FOREIGN KEY (SOURCE_ID) REFERENCES FOOD_SOURCES(SOURCE_ID),
    FOREIGN KEY (PICKUP_ID) REFERENCES FOOD_PICKUP(PICKUP_ID)
);

-- DRIVER ENTITY 
 CREATE TABLE DRIVERS (
    DRIVER_ID INT AUTO_INCREMENT PRIMARY KEY,  -- Unique identifier for each driver
    NAME VARCHAR(100) NOT NULL,               -- Driver's name
    PHONE_NUMBER VARCHAR(15) NOT NULL,        -- Contact phone number
    EMAIL VARCHAR(100),                       -- Email address (optional)
    LICENSE_NUMBER VARCHAR(50) DEFAULT NULL,      -- Driver's license number
    VEHICLE_TYPE VARCHAR(50) DEFAULT NULL,                 -- Type of vehicle (e.g., truck, van, bike)
    VEHICLE_NUMBER VARCHAR(20) DEFAULT NULL,               -- Vehicle registration number
    AVAILABILITY_STATUS ENUM('Available', 'Busy', 'Off-Duty') DEFAULT 'Available',  -- Current status of the driver
    LAST_PICKUP_DATE DATETIME DEFAULT NULL,                -- Last pickup time for tracking activity
    TOTAL_COMPLETED_PICKUPS INT DEFAULT 0     -- Total number of pickups completed
);

-- FOOD SOURCES 

INSERT INTO FOOD_SOURCES (NAME, CONTACT_NAME, CONTACT, EMAIL, DETAILS, LOCALITY, PINCODE) VALUES
('Fresh Farms', 'John Doe', '1234567890', 'john@freshfarms.com', 'Supplier of fresh produce', 'Green Valley', '560001'),
('Organic Oasis', 'Emma Brown', '9876543210', 'emma@organicoasis.com', 'Organic and pesticide-free food', 'Sunny Side', '560002'),
('Healthy Harvest', 'James Smith', '1122334455', 'james@healthyharvest.com', 'Supplier of grains and cereals', 'Riverside', '560003'),
('Dairy Delights', 'Olivia White', '5566778899', 'olivia@dairydelights.com', 'Specialized in dairy products', 'Hilltop', '560004'),
('Seafood Market', 'Liam Green', '9988776655', 'liam@seafoodmarket.com', 'Fresh seafood supplier', 'Coastline', '560005'),
('Orchard Fresh', 'Sophia Black', '7744112233', 'sophia@orchardfresh.com', 'Supplier of fresh fruits', 'Valley View', '560006'),
('Grain Hub', 'Henry Miller', '6677889900', 'henry@grainhub.com', 'Grains and pulses supplier', 'Uptown', '560007'),
('Poultry Palace', 'Lucas Gray', '4455667788', 'lucas@poultrypalace.com', 'Poultry and meat products', 'Downtown', '560008'),
('Greenhouse Gardens', 'Mia Moore', '3322115544', 'mia@greenhousegardens.com', 'Greenhouse vegetables', 'Countryside', '560009'),
('Farm Fresh', 'Noah Scott', '2211445566', 'noah@farmfresh.com', 'General supplier of perishable food', 'City Center', '560010');

select * from food_sources;
 

-- 	TYPE OF SOURCE 
INSERT INTO TYPE_OF_SOURCE (SOURCE_ID, TYPE_SOURCE) VALUES
(1, 'Produce'),
(2, 'Organic'),
(3, 'Grains'),
(4, 'Dairy'),
(5, 'Seafood'),
(6, 'Fruits'),
(7, 'Grains'),
(8, 'Poultry'),
(9, 'Vegetables'),
(10, 'General');

select * from type_of_source;

-- FOO_ITEM
INSERT INTO FOOD_ITEM (NAME, QUANTITY, CATEGORY, EXPIRY_DATE, SOURCE_ID) VALUES
('Apples', 50, 'Fruits', '2024-12-01', 6),
('Milk', 100, 'Dairy', '2024-11-20', 4),
('Wheat Flour', 200, 'Grains', '2025-01-15', 7),
('Chicken', 150, 'Poultry', '2024-11-18', 8),
('Tomatoes', 80, 'Vegetables', '2024-11-30', 9),
('Fish', 60, 'Seafood', '2024-11-15', 5),
('Rice', 300, 'Grains', '2025-02-01', 3),
('Carrots', 100, 'Vegetables', '2024-11-25', 9),
('Oranges', 120, 'Fruits', '2024-12-10', 6),
('Butter', 50, 'Dairy', '2024-11-22', 4);
select * from food_item;

-- PROVIDES
select * from provides;

-- NGO
INSERT INTO NGO (NAME, CONTACT_NAME, CONTACT, EMAIL, CATEGORY_REQ, ADDRESS) VALUES
('Helping Hands', 'Alice Taylor', '1231231234', 'alice@helpinghands.org', 'Fruits', '123 Charity St'),
('Food for All', 'Bob Martin', '3213214321', 'bob@foodforall.org', 'Grains', '456 Relief Road'),
('Care Givers', 'Charlie Evans', '9879879876', 'charlie@caregivers.org', 'Vegetables', '789 Support Ave'),
('Feed the Hungry', 'David Clark', '6546546543', 'david@feedthehungry.org', 'Dairy', '1011 Outreach Blvd'),
('Nourish Now', 'Eva Adams', '2223334445', 'eva@nourishnow.org', 'Poultry', '2022 Wellness Lane'),
('Food Bridge', 'George Young', '5556667778', 'george@foodbridge.org', 'Seafood', '3033 Unity Street'),
('Hope Kitchen', 'Hannah Wilson', '4445556669', 'hannah@hopekitchen.org', 'Fruits', '4044 Service Row'),
('Safe Haven', 'Ivy Thompson', '8889990001', 'ivy@safehaven.org', 'Grains', '5055 Secure Lane'),
('Shelter Support', 'Jack Brown', '1112223334', 'jack@sheltersupport.org', 'Vegetables', '6066 Help Circle'),
('Blessed Meals', 'Karen Green', '6667778882', 'karen@blessedmeals.org', 'General', '7077 Aid Park');

SELECT * FROM NGO;

-- DONATIONS 
INSERT INTO DONATIONS (SOURCE_ID, NGO_ID, SOURCE, DESTINATION, QUANTITY, CATEGORY) VALUES
(1, 1, 'Fresh Farms', 'Helping Hands', 30, 'Fruits'),
(2, 2, 'Organic Oasis', 'Food for All', 100, 'Grains'),
(3, 3, 'Healthy Harvest', 'Care Givers', 50, 'Vegetables'),
(4, 4, 'Dairy Delights', 'Feed the Hungry', 80, 'Dairy'),
(5, 5, 'Seafood Market', 'Nourish Now', 20, 'Seafood'),
(6, 6, 'Orchard Fresh', 'Food Bridge', 70, 'Fruits'),
(7, 7, 'Grain Hub', 'Safe Haven', 150, 'Grains'),
(8, 8, 'Poultry Palace', 'Hope Kitchen', 60, 'Poultry'),
(9, 9, 'Greenhouse Gardens', 'Shelter Support', 90, 'Vegetables'),
(10, 10, 'Farm Fresh', 'Blessed Meals', 200, 'General');
SELECT * FROM DONATIONS;

SELECT * FROM RECEIVES;
SELECT * FROM DONATES_TO;
select * from users;

-- DRIVERS
INSERT INTO DRIVERS (NAME, PHONE_NUMBER, EMAIL, LICENSE_NUMBER, VEHICLE_TYPE, VEHICLE_NUMBER, AVAILABILITY_STATUS, LAST_PICKUP_DATE, TOTAL_COMPLETED_PICKUPS) VALUES
('John Doe', '1234567890', 'john.doe@example.com', 'DL12345', 'Truck', 'KA-01-AB-1234', 'Available', '2024-11-12 10:30:00', 5),
('Emma Brown', '9876543210', 'emma.brown@example.com', 'DL23456', 'Van', 'KA-02-CD-2345', 'Busy', '2024-11-13 14:00:00', 8),
('Michael Smith', '5556667778', 'michael.smith@example.com', 'DL34567', 'Bike', 'KA-03-EF-3456', 'Off-Duty', NULL, 2),
('Olivia Johnson', '8889990001', 'olivia.johnson@example.com', 'DL45678', 'Truck', 'KA-04-GH-4567', 'Available', '2024-11-10 08:15:00', 12),
('William White', '1112223334', 'william.white@example.com', 'DL56789', 'Van', 'KA-05-IJ-5678', 'Busy', '2024-11-11 09:45:00', 4),
('Sophia Martinez', '2223334445', 'sophia.martinez@example.com', 'DL67890', 'Bike', 'KA-06-KL-6789', 'Available', '2024-11-09 07:00:00', 10),
('James Davis', '3334445556', 'james.davis@example.com', 'DL78901', 'Truck', 'KA-07-MN-7890', 'Off-Duty', NULL, 0),
('Isabella Garcia', '4445556667', 'isabella.garcia@example.com', 'DL89012', 'Van', 'KA-08-OP-8901', 'Busy', '2024-11-08 16:30:00', 6),
('Ethan Wilson', '5556667778', 'ethan.wilson@example.com', 'DL90123', 'Truck', 'KA-09-QR-9012', 'Available', '2024-11-07 12:20:00', 9),
('Charlotte Lopez', '6667778889', 'charlotte.lopez@example.com', 'DL01234', 'Bike', 'KA-10-ST-0123', 'Available', '2024-11-06 10:10:00', 3);

SELECT * FROM DRIVERS;

-- FOOD PICKUP
INSERT INTO FOOD_PICKUP (SOURCE_ID, DRIVER_ID, DRIVER_NAME, CONTACT, STATUS, DESTINATION, VEHICLE_TYPE) VALUES
(1, 1, 'John Doe', '1234567890', 'Pending', 'Helping Hands', 'Truck'),
(2, 2, 'Emma Brown', '9876543210', 'Completed', 'Food for All', 'Van'),
(3, 3, 'Michael Smith', '5556667778', 'Pending', 'Care Givers', 'Bike'),
(4, 4, 'Olivia Johnson', '8889990001', 'Pending', 'Feed the Hungry', 'Truck'),
(5, 5, 'William White', '1112223334', 'Completed', 'Nourish Now', 'Van'),
(6, 6, 'Sophia Martinez', '2223334445', 'Completed', 'Food Bridge', 'Bike'),
(7, 7, 'James Davis', '3334445556', 'Pending', 'Safe Haven', 'Truck'),
(8, 8, 'Isabella Garcia', '4445556667', 'Completed', 'Hope Kitchen', 'Van'),
(9, 9, 'Ethan Wilson', '5556667778', 'Pending', 'Shelter Support', 'Truck'),
(10, 10, 'Charlotte Lopez', '6667778889', 'Completed', 'Blessed Meals', 'Bike');


-- IMPACT
INSERT INTO IMPACT (SOURCE_ID, NGO_ID, SOURCE, DESTINATION, FEEDBACK, RATE, PEOPLE_HELPED) VALUES
(1, 1, 'Fresh Farms', 'Helping Hands', 'Great quality fruits!', 5, 100),
(2, 2, 'Organic Oasis', 'Food for All', 'Timely delivery, very satisfied', 4, 80),
(3, 3, 'Healthy Harvest', 'Care Givers', 'Fresh grains, much appreciated', 5, 150),
(4, 4, 'Dairy Delights', 'Feed the Hungry', 'Good dairy products', 4, 120),
(5, 5, 'Seafood Market', 'Nourish Now', 'Fresh seafood, quick delivery', 5, 60),
(6, 6, 'Orchard Fresh', 'Food Bridge', 'Good quality fruits', 4, 90),
(7, 7, 'Grain Hub', 'Safe Haven', 'Excellent service', 5, 200),
(8, 8, 'Poultry Palace', 'Hope Kitchen', 'Good poultry products', 3, 70),
(9, 9, 'Greenhouse Gardens', 'Shelter Support', 'Fresh vegetables, well received', 4, 130),
(10, 10, 'Farm Fresh', 'Blessed Meals', 'Mixed items, satisfactory', 3, 110);

SELECT * FROM SCHEDULES;
INSERT INTO SCHEDULES (SOURCE_ID, PICKUP_ID, DATE, TIME) VALUES
(1, 1, '2024-11-15', '10:00:00'),
(2, 2, '2024-11-16', '11:30:00'),
(3, 3, '2024-11-17', '12:45:00'),
(4, 4, '2024-11-18', '14:00:00'),
(5, 5, '2024-11-19', '09:15:00'),
(6, 6, '2024-11-20', '08:30:00'),
(7, 7, '2024-11-21', '13:20:00'),
(8, 8, '2024-11-22', '15:50:00'),
(9, 9, '2024-11-23', '07:10:00'),
(10, 10, '2024-11-24', '16:40:00');

select * from users;