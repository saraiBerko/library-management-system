-- Part א.2.2 — required analytical queries for the library system.

-- 1. Books that currently have no available copy.
SELECT b.id, b.title
FROM books b
WHERE NOT EXISTS (
    SELECT 1
    FROM copies c
    WHERE c.book_id = b.id
      AND c.status = 'available'
)
ORDER BY b.title;

-- 2. Top 5 members by number of loans in the last year, with name and count.
SELECT m.id, m.name, COUNT(*) AS loan_count
FROM members m
JOIN loans l ON l.member_id = m.id
WHERE l.loan_date >= CURRENT_DATE - INTERVAL '1 year'
GROUP BY m.id, m.name
ORDER BY loan_count DESC
LIMIT 5;

-- 3. Books not borrowed at all in the last 12 months ("old" books).
SELECT b.id, b.title
FROM books b
WHERE NOT EXISTS (
    SELECT 1
    FROM loans l
    JOIN copies c ON c.id = l.copy_id
    WHERE c.book_id = b.id
      AND l.loan_date >= CURRENT_DATE - INTERVAL '12 months'
)
ORDER BY b.title;

-- 4. Average actual loan duration (days) by genre, returned loans only.
SELECT b.genre, AVG(l.returned_date - l.loan_date) AS avg_loan_days
FROM loans l
JOIN copies c ON c.id = l.copy_id
JOIN books b ON b.id = c.book_id
WHERE l.returned_date IS NOT NULL
GROUP BY b.genre
ORDER BY b.genre;
