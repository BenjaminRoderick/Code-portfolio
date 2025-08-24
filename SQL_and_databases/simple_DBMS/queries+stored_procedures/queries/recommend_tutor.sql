connect to DB_NAME_HERE;

WITH interactions(pid, likes, comments) AS
(SELECT p.pid, COUNT(l.email), COUNT(UNIQUE c.cid)
FROM post p LEFT JOIN post_like l ON p.pid = l.pid
FULL OUTER JOIN post_comment c ON p.pid = c.pid
GROUP BY p.pid
ORDER BY p.pid)
SELECT t.email from tutor t
WHERE (SELECT COUNT(i.pid) FROM interactions i
WHERE i.likes >= 5 AND i.comments >= 1
AND i.pid IN (SELECT a.pid FROM advertises a
WHERE a.email = t.email AND a.name IN (SELECT s.name FROM service s
WHERE s.email = t.email AND s.subject = 'Trigonometry'))) >= 2--Update subject name as desired
;