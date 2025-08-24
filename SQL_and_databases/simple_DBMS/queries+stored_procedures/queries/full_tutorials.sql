--select all tutorial sessions where the number of participants is equal to the maximum number of participants
CONNECT TO DB_NAME_HERE;

SELECT t.name, t.tutorial_date, t.tutorial_time, t.location FROM tutorial_session t
WHERE t.max_participants = (SELECT COUNT(p.email_buyer) FROM purchase p
WHERE p.name = t.name
GROUP BY p.name)
ORDER BY t.tutorial_date
;