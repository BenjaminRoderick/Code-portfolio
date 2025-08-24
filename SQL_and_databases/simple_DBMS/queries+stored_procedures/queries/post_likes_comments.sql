--Count the number of comments and likes for each post
CONNECT TO DB_NAME_HERE;

SELECT p.pid, COUNT(l.email) AS likes, COUNT(UNIQUE c.cid) AS comments
FROM post p LEFT JOIN post_like l ON p.pid = l.pid
FULL OUTER JOIN post_comment c ON p.pid = c.pid
GROUP BY p.pid
ORDER BY p.pid
;