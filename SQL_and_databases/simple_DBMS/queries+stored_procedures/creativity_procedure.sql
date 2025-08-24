CONNECT TO DB_NAME_HERE$

CREATE PROCEDURE enforce_level (IN user_email VARCHAR(30))
LANGUAGE SQL
BEGIN
    DECLARE user_level VARCHAR(20);
    DECLARE service_level VARCHAR(20);
    DECLARE seller_email VARCHAR(30);
    DECLARE service_name VARCHAR(50);
    DECLARE subject VARCHAR(30);
    DECLARE price INT;
    DECLARE p_date DATE;
    DECLARE today DATE;
    DECLARE at_end INT DEFAULT 0;
    DECLARE not_found CONDITION FOR SQLSTATE '02000';

    DECLARE c CURSOR FOR
        SELECT s.email, s.name, s.subject, s.price, s.edu_level, p.purchase_date
        FROM service s JOIN purchase p ON s.email=p.email_seller
        WHERE p.email_buyer = user_email
        AND p.name = s.name
        ;

    DECLARE l CURSOR FOR
        SELECT s.edu_level FROM student s
        WHERE s.email = user_email
        ;

    DECLARE d CURSOR FOR
        SELECT CURRENT DATE FROM sysibm.sysdummy1
        ;

    DECLARE CONTINUE HANDLER FOR not_found SET at_end = 1;

    IF EXISTS (SELECT name FROM sysibm.systables WHERE name = 'cancelled_purchase')
        THEN
        DROP TABLE cancelled_purchase;
        COMMIT;
    END IF;

    CREATE TABLE cancelled_purchase
    (
        email_buyer VARCHAR(50) NOT NULL,
        email_seller VARCHAR(50) NOT NULL,
        name VARCHAR(50) NOT NULL,
        purchase_date DATE,
        cancelled_date DATE,
        price INT,
        PRIMARY KEY (email_buyer, email_seller, name),
        FOREIGN KEY (email_buyer) REFERENCES User,
        FOREIGN KEY (email_seller, name) REFERENCES Service ON DELETE CASCADE
    );
    COMMIT;

    OPEN l;
    FETCH l INTO user_level;
    CLOSE l;

    OPEN d;
    FETCH d INTO today;
    CLOSE d;

    OPEN c;
    FETCH c INTO seller_email, service_name, subject, price, service_level, p_date;

    WHILE at_end = 0 DO
        IF service_level != user_level THEN
            INSERT INTO cancelled_purchase (email_buyer, email_seller, name, purchase_date, cancelled_date, price)
            VALUES (user_email, seller_email, service_name, p_date, today, price);

            DELETE FROM purchase
            WHERE email_buyer = user_email AND email_seller = seller_email AND name = service_name;
        END IF;
        FETCH c INTO seller_email, service_name, subject, price, service_level, p_date;
    END WHILE;
    CLOSE c;
END$