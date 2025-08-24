CONNECT TO DB_NAME_HERE$

CREATE PROCEDURE make_advert (IN subj VARCHAR(30))
LANGUAGE SQL
BEGIN
    DECLARE t_name VARCHAR(50);
    DECLARE t_email VARCHAR(50);
    DECLARE likes INT;
    DECLARE comments INT;
    DECLARE pid INT;
    DECLARE max_pid INT;
    DECLARE iter INT DEFAULT 1;
    DECLARE today DATE;

    DECLARE at_end INT DEFAULT 0;
    DECLARE not_found CONDITION FOR SQLSTATE '02000';

    DECLARE c CURSOR FOR
        SELECT p.pid, COUNT(l.email), COUNT(UNIQUE c.cid), p.email, u.name
        FROM post p LEFT JOIN post_like l ON p.pid = l.pid
        FULL OUTER JOIN post_comment c ON p.pid = c.pid
        JOIN user u ON u.email = p.email 
        WHERE p.pid IN (SELECT UNIQUE(a.pid) FROM advertises a JOIN service s ON a.name = s.name
        WHERE a.email = s.email AND s.subject = subj)
        GROUP BY p.pid, p.post_date, p.email, u.name
        ORDER BY p.pid
        ;

    DECLARE m CURSOR FOR
        SELECT MAX(pID) FROM post;

    DECLARE d CURSOR FOR
        SELECT CURRENT DATE FROM sysibm.sysdummy1;

    DECLARE CONTINUE HANDLER FOR not_found SET at_end = 1;

    OPEN d;
    FETCH d INTO today;
    CLOSE d;
    
    OPEN m;
    FETCH m INTO max_pid;
    CLOSE m;

    OPEN c;
    FETCH c INTO pid, likes, comments, t_email, t_name;
    
    WHILE at_end = 0 DO
        IF (likes + 2 * comments) > 5 THEN
            INSERT INTO post (pid, title, post_date, body, email)
            VALUES (max_pid + iter, 'Today''s recommended tutor: ' || t_email, today, 
            'Looking for help with ' || subj || '? ' || t_name || ' has you covered!', 'ADMIN');
        END IF;
        FETCH c INTO pid, likes, comments, t_name, t_email;
        SET iter = iter + 1;
    END WHILE;
    CLOSE c;
END$
