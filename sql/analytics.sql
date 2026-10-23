-- 1. Total rows in each target table
SELECT 'users' AS table_name, COUNT(*) AS total_rows FROM users
UNION ALL
SELECT 'posts' AS table_name, COUNT(*) AS total_rows FROM posts;

-- 2. Posts per user, including users with zero posts
SELECT
    u.id,
    u.name,
    u.company,
    COUNT(p.id) AS total_posts
FROM users AS u
LEFT JOIN posts AS p ON p.user_id = u.id
GROUP BY u.id, u.name, u.company
ORDER BY total_posts DESC, u.name;

-- 3. Posts with their author
SELECT
    p.id AS post_id,
    p.title,
    u.name AS author,
    u.email
FROM posts AS p
INNER JOIN users AS u ON u.id = p.user_id
ORDER BY p.id
LIMIT 20;

-- 4. Check for posts without a matching user (expected: zero rows)
SELECT p.*
FROM posts AS p
LEFT JOIN users AS u ON u.id = p.user_id
WHERE u.id IS NULL;

-- 5. Most recent load timestamps
SELECT 'users' AS table_name, MAX(loaded_at) AS last_load FROM users
UNION ALL
SELECT 'posts' AS table_name, MAX(loaded_at) AS last_load FROM posts;
