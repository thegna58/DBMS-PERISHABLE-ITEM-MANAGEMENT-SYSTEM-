

-- TRIGGER 
DELIMITER //

CREATE TRIGGER afterDonationInsert
AFTER INSERT ON DONATIONS
FOR EACH ROW
BEGIN
    -- Insert a record into the DONATES_TO table (linking the source to the donation)
    INSERT INTO DONATES_TO (SOURCE_ID, DONATION_ID, DATE_TIME)
    VALUES (NEW.SOURCE_ID, NEW.DONATION_ID, NOW());

    -- Insert a record into the RECEIVES table (linking the NGO to the donation)
    INSERT INTO RECEIVES (NGO_ID, DONATION_ID)
    VALUES (NEW.NGO_ID, NEW.DONATION_ID);
    
END //

DELIMITER ;
select*from ngo;
INSERT INTO DONATIONS (SOURCE_ID, NGO_ID, SOURCE, DESTINATION, QUANTITY, CATEGORY)
VALUES (1, 1, 'Food Source A', 'Food Bank', 100, 'Canned Goods');
select* from donations;
select*from DONATES_TO;
select*from RECEIVES;

DELIMITER $$

CREATE FUNCTION GetDonationSource(ngo_id INT, required_category VARCHAR(255), required_quantity INT)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE source_id INT;
    DECLARE food_id INT;
    DECLARE total_quantity INT;
    DECLARE donation_quantity INT;

    -- Start by selecting the source with the closest expiry date for the required food category and quantity
    SELECT f.FOOD_ID, f.QUANTITY, f.EXPIRY_DATE, fs.SOURCE_ID
    INTO food_id, total_quantity, @expiry_date, source_id
    FROM FOOD_ITEM f
    JOIN PROVIDES p ON f.FOOD_ID = p.FOOD_ID
    JOIN FOOD_SOURCES fs ON p.SOURCE_ID = fs.SOURCE_ID
    JOIN NGO n ON n.NGO_ID = ngo_id
    WHERE f.CATEGORY = required_category
      AND f.QUANTITY >= required_quantity
    ORDER BY f.EXPIRY_DATE ASC
    LIMIT 1;

    -- Check if a valid source was found
    IF source_id IS NOT NULL THEN
        SET donation_quantity = LEAST(total_quantity, required_quantity);

        -- Insert donation details into the DONATIONS table
        INSERT INTO DONATIONS (SOURCE_ID, NGO_ID, SOURCE, DESTINATION, QUANTITY, CATEGORY)
        VALUES (source_id, ngo_id, 
                (SELECT NAME FROM FOOD_SOURCES WHERE SOURCE_ID = source_id LIMIT 1), 
                (SELECT NAME FROM NGO WHERE NGO_ID = ngo_id LIMIT 1), 
                donation_quantity, required_category);

        -- Return the source ID for reference
        RETURN source_id;
    ELSE
        -- No valid source found, return NULL or an appropriate value
        RETURN NULL;
    END IF;
END $$

DELIMITER ;

drop function  GetDonationSource;
SELECT GetDonationSource(1, 'Grain', 15);

