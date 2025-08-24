--query over purchases, advertises and post_like -> find users who bought a service and liked a post about it
CONNECT TO DB_NAME_HERE;

SELECT p.email_buyer FROM purchase p
WHERE EXISTS (SELECT * FROM advertises a
WHERE a.name = p.name AND a.email = p.email_seller
AND a.pid IN (SELECT l.pid FROM post_like l
WHERE l.email = p.email_buyer))
ORDER BY p.email_buyer
;