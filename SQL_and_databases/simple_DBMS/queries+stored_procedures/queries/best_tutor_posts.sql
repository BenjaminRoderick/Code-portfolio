--Fetch a list of all post titles and post_dates from users that are tutors and have more than 5 likes
CONNECT TO DB_NAME_HERE;

SELECT title, post_date FROM post p
WHERE p.email IN (SELECT t.email FROM tutor t)
AND (SELECT COUNT(l.email) FROM post_like l
WHERE l.pid = p.pid
GROUP BY p.pid) > 5
ORDER BY post_date
;