DELIMITER $$

CREATE FUNCTION GetFoodSourceImpact(source_id INT)
RETURNS VARCHAR(1000)
DETERMINISTIC 
BEGIN
    DECLARE sourceName VARCHAR(255);
    DECLARE totalFoodItems INT DEFAULT 0;
    DECLARE totalNGOsSupported INT DEFAULT 0;
    DECLARE totalQuantityDonated INT DEFAULT 0;
    DECLARE avgRating DECIMAL(3,2) DEFAULT 0.0;
    DECLARE totalPeopleHelped INT DEFAULT 0;

    -- Get the Source Name (ensure only 1 result)
    SELECT NAME 
    INTO sourceName
    FROM FOOD_SOURCES 
    WHERE SOURCE_ID = source_id
    LIMIT 1;

    -- Get Total Food Items Provided (ensure only 1 result)
    SELECT COUNT(DISTINCT FOOD_ID)
    INTO totalFoodItems
    FROM PROVIDES
    WHERE SOURCE_ID = source_id
    LIMIT 1;

    -- Get Total NGOs Supported (ensure only 1 result)
    SELECT COUNT(DISTINCT NGO_ID)
    INTO totalNGOsSupported
    FROM DONATIONS
    WHERE SOURCE_ID = source_id
    LIMIT 1;

    -- Get Total Quantity Donated (ensure only 1 result)
    SELECT SUM(QUANTITY)
    INTO totalQuantityDonated
    FROM DONATIONS
    WHERE SOURCE_ID = source_id
    LIMIT 1;

    -- Get Average Rating from NGOs and Total People Helped (ensure only 1 result)
    SELECT 
        IFNULL(ROUND(AVG(RATE), 2), 0.0), 
        IFNULL(SUM(PEOPLE_HELPED), 0)
    INTO 
        avgRating, 
        totalPeopleHelped
    FROM IMPACT
    WHERE SOURCE_ID = source_id
    LIMIT 1;

    -- Return all details as a formatted string
    RETURN CONCAT(
        'Food Source: ', sourceName, 
        ', Total Food Items Provided: ', totalFoodItems,
        ', Total NGOs Supported: ', totalNGOsSupported,
        ', Total Quantity Donated: ', totalQuantityDonated, ' kg',
        ', Average Rating: ', avgRating,
        ', Total People Helped: ', totalPeopleHelped
    );
END $$

DELIMITER ;

drop function GetFoodSourceImpact;

SELECT GetFoodSourceImpact(1);

-- TRIGGER
DELIMITER $$

CREATE TRIGGER after_food_item_insert
AFTER INSERT ON FOOD_ITEM
FOR EACH ROW
BEGIN
    -- Step 1: Insert into PROVIDES table
    -- Assuming the source_id is provided during the food item insert, we use the NEW keyword to access the inserted record
    -- In case the source ID is passed with the insert (make sure you have the column SOURCE_ID in FOOD_ITEM)
    IF NEW.SOURCE_ID IS NOT NULL THEN
        INSERT INTO PROVIDES (SOURCE_ID, FOOD_ID)
        VALUES (NEW.SOURCE_ID, NEW.FOOD_ID);
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Source ID is required for the donation';
    END IF;

END $$

DELIMITER ;
-- Insert a new food item donated by a source with SOURCE_ID 1
INSERT INTO FOOD_ITEM (NAME, QUANTITY, CATEGORY, EXPIRY_DATE, SOURCE_ID)
VALUES ('Rice', 100, 'Non-perishable', '2025-12-31', 1);

select * from food_item;

-- PROCEDURE 
drop procedure GetTopDemandedCategories;
DELIMITER //

CREATE PROCEDURE GetTopDemandedCategories(
    IN p_top_n INT
)
BEGIN
    -- Find the top demanded food categories from NGOs
    SELECT 
        fs.SOURCE_ID,
        fs.NAME AS SourceName,
        ngo.NGO_ID,
        ngo.NAME AS NGOName,
        ngo.CATEGORY_REQ AS RequestedCategory,
        COUNT(ngo.CATEGORY_REQ) AS RequestCount
    FROM 
        NGO ngo
    INNER JOIN DONATIONS d ON ngo.NGO_ID = d.NGO_ID
    INNER JOIN FOOD_SOURCES fs ON fs.SOURCE_ID = d.SOURCE_ID
    GROUP BY fs.SOURCE_ID, fs.NAME, ngo.NGO_ID, ngo.NAME, ngo.CATEGORY_REQ
    ORDER BY RequestCount DESC
    LIMIT p_top_n;
END //
DELIMITER ;

-- Example 1: Get the top 3 most demanded food categories
CALL GetTopDemandedCategories(1);

-- Example 2: Get the top 5 most demanded food categories
CALL GetTopDemandedCategories(5);
