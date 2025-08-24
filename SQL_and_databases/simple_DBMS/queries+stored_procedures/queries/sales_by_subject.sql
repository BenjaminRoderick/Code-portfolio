--return the quantity of sales of services for each subject
CONNECT TO DB_NAME_HERE;

SELECT s.subject, COUNT(*) AS sales FROM
purchase p JOIN service s ON p.name = s.name
GROUP BY s.subject
ORDER BY s.subject
;