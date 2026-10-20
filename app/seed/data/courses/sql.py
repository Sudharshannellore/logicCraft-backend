"""SQL Foundations: Learn to query, join, and reason about relational databases."""

COURSE = {
    "id": "sql-foundations",
    "title": "SQL Foundations",
    "world": "Database World",
    "description": "Learn to query, join, and reason about relational databases.",
    "language": "sql",
    "modules": [{"id": "sm1", "title": "SELECT Basics"}, {"id": "sm2", "title": "Joins"}],
}

ZONES = [
    {
        "id": "sq-z1",
        "name": "Query Shores",
        "tagline": "Ask a table questions and get exactly the rows you need.",
        "difficulty": "easy",
        "nodes": [
            {"id": "sq1", "title": "SELECT Basics", "difficulty": "easy", "xp_reward": 50, "estimated_minutes": 10},
            {
                "id": "sq2",
                "title": "Filtering with WHERE",
                "difficulty": "easy",
                "xp_reward": 60,
                "estimated_minutes": 12,
            },
            {
                "id": "sq3",
                "title": "Sorting with ORDER BY",
                "difficulty": "easy",
                "xp_reward": 60,
                "estimated_minutes": 12,
            },
            {"id": "sq4", "title": "LIMIT & DISTINCT", "difficulty": "easy", "xp_reward": 60, "estimated_minutes": 12},
        ],
        "boss": {
            "id": "sq-z1-boss",
            "name": "Query Goblin",
            "sprite": "slime",
            "challenge": "Answer 3 questions about the shop database",
            "stages": 3,
            "xp_reward": 200,
        },
    },
    {
        "id": "sq-z2",
        "name": "Aggregate Mines",
        "tagline": "Summarise thousands of rows into answers.",
        "difficulty": "medium",
        "nodes": [
            {
                "id": "sq5",
                "title": "Aggregate Functions",
                "difficulty": "medium",
                "xp_reward": 90,
                "estimated_minutes": 18,
            },
            {"id": "sq6", "title": "GROUP BY", "difficulty": "medium", "xp_reward": 100, "estimated_minutes": 20},
            {"id": "sq7", "title": "HAVING", "difficulty": "medium", "xp_reward": 100, "estimated_minutes": 18},
            {"id": "sq8", "title": "Handling NULLs", "difficulty": "medium", "xp_reward": 90, "estimated_minutes": 15},
        ],
        "boss": {
            "id": "sq-z2-boss",
            "name": "Group-By Golem",
            "sprite": "bugSlime",
            "challenge": "Build a monthly sales report from raw orders",
            "stages": 4,
            "xp_reward": 350,
        },
    },
    {
        "id": "sq-z3",
        "name": "Join Fortress",
        "tagline": "Combine tables and write queries like a pro.",
        "difficulty": "hard",
        "nodes": [
            {
                "id": "sq9",
                "title": "INNER & OUTER Joins",
                "difficulty": "hard",
                "xp_reward": 140,
                "estimated_minutes": 25,
            },
            {"id": "sq10", "title": "Subqueries", "difficulty": "hard", "xp_reward": 160, "estimated_minutes": 30},
            {
                "id": "sq11",
                "title": "Window Functions",
                "difficulty": "hard",
                "xp_reward": 180,
                "estimated_minutes": 30,
            },
            {
                "id": "sq12",
                "title": "Indexes & Performance",
                "difficulty": "hard",
                "xp_reward": 160,
                "estimated_minutes": 25,
            },
        ],
        "boss": {
            "id": "sq-z3-boss",
            "name": "Join Dragon",
            "sprite": "recursionBoss",
            "challenge": "Join 4 tables to crack the final leaderboard query",
            "stages": 5,
            "xp_reward": 700,
        },
    },
]

LESSONS: list[dict] = [
    {
        "id": "sq1",
        "module_id": "sm1",
        "title": "Asking a Table for Data",
        "concept": "SELECT Basics",
        "explanation": (
            "`SELECT` is how you read data from a database table. "
            "You list the columns you want after `SELECT` and the table after `FROM`, or use `*` for every column. "
            "You can also compute new values and rename them with `AS`."
        ),
        "code_example": """SELECT name, salary
FROM employees;

SELECT *
FROM products;

SELECT name, price * 1.1 AS price_with_tax
FROM products;""",
        "code_walkthrough": [
            "`SELECT name, salary FROM employees;` returns just two columns for every employee.",
            "`SELECT * FROM products;` returns every column of the `products` table.",
            "`price * 1.1 AS price_with_tax` calculates a new value and gives the result column a readable name.",
        ],
        "key_points": [
            "`SELECT` chooses columns and `FROM` chooses the table.",
            "`*` means all columns; listing columns explicitly is clearer and often faster.",
            "`AS` creates an alias for a column or expression.",
        ],
        "analogy": (
            '`SELECT` is like asking a librarian for specific details: "From the employees '
            'shelf, just tell me names and salaries."'
        ),
        "quiz": {
            "question": "What does `SELECT * FROM products;` return?",
            "options": [
                "All columns and all rows of products",
                "Only the first row of products",
                "Only the id column of products",
                "The number of rows in products",
            ],
            "correct_index": 0,
            "explanation": "`*` selects every column, and without a `WHERE` clause every row is returned.",
        },
    },
    {
        "id": "sq2",
        "module_id": "sm1",
        "title": "Picking Rows with WHERE",
        "concept": "Filtering with WHERE",
        "explanation": (
            "`WHERE` filters rows so only those matching a condition are returned. "
            "Combine conditions with `AND` and `OR`, and use helpers like `BETWEEN`, `IN` and `LIKE`. "
            "Text values go in single quotes, as in `'Sales'`."
        ),
        "code_example": """SELECT name, salary
FROM employees
WHERE department = 'Sales'
  AND salary > 50000;

SELECT name FROM products
WHERE price BETWEEN 10 AND 20
   OR name LIKE 'Pro%';""",
        "code_walkthrough": [
            "`WHERE department = 'Sales'` keeps only rows in the Sales department.",
            "`AND salary > 50000` adds a second condition that must also be true.",
            "`price BETWEEN 10 AND 20` matches prices from 10 to 20, inclusive.",
            "`name LIKE 'Pro%'` matches names starting with \"Pro\"; `%` means any characters.",
        ],
        "key_points": [
            "`WHERE` filters rows before they are returned.",
            "`AND` needs both conditions to be true; `OR` needs at least one.",
            "`LIKE` uses `%` for any run of characters and `_` for exactly one.",
        ],
        "analogy": ("`WHERE` is like a sieve: only the rows that fit through the condition end up in your results."),
        "quiz": {
            "question": "Which condition finds names that start with the letter A?",
            "options": ["name = 'A%'", "name LIKE '%A'", "name IN ('A')", "name LIKE 'A%'"],
            "correct_index": 3,
            "explanation": "`LIKE 'A%'` matches an A followed by anything. `'%A'` would match names ending in A, and `=` doesn't use wildcards.",
        },
        "try_it": {
            "prompt": "Return the names of employees in the 'Engineering' department.",
            "starter_code": "SELECT name\nFROM employees\n-- add a filter here\n",
            "checks": [
                {
                    "pattern": r"(?i)select\s+name\s+from\s+employees",
                    "hint": "Keep `SELECT name FROM employees`.",
                },
                {
                    "pattern": r"(?i)where\s+department\s*=\s*[\"']Engineering[\"']",
                    "hint": "Add `WHERE department = 'Engineering'`.",
                },
            ],
            "expected_output": "Only the names of employees whose department is Engineering.",
        },
    },
    {
        "id": "sq3",
        "module_id": "sm1",
        "title": "Sorting Results with ORDER BY",
        "concept": "Sorting with ORDER BY",
        "explanation": (
            "`ORDER BY` sorts your results by one or more columns. "
            "`ASC` sorts from smallest to largest (the default) and `DESC` sorts from largest to smallest. "
            "With several columns, later ones break ties in earlier ones."
        ),
        "code_example": """SELECT name, department, salary
FROM employees
ORDER BY department ASC, salary DESC;

SELECT name, price
FROM products
ORDER BY price;""",
        "code_walkthrough": [
            "`ORDER BY department ASC` groups rows alphabetically by department.",
            "`, salary DESC` sorts employees within each department from highest to lowest salary.",
            "`ORDER BY price` sorts products from cheapest to most expensive, since `ASC` is the default.",
        ],
        "key_points": [
            "`ORDER BY` comes after `WHERE` in a query.",
            "`ASC` is the default; add `DESC` for descending order.",
            "Without `ORDER BY`, the database doesn't guarantee any row order.",
        ],
        "analogy": (
            "`ORDER BY` is like sorting a pile of exam papers, first by class and then by score within each class."
        ),
        "quiz": {
            "question": "What is the default sort direction of `ORDER BY salary`?",
            "options": ["Descending (highest first)", "Ascending (lowest first)", "Random", "Insertion order"],
            "correct_index": 1,
            "explanation": "When you don't specify a direction, SQL uses `ASC`, sorting from lowest to highest.",
        },
        "try_it": {
            "prompt": "List products from the most expensive to the cheapest.",
            "starter_code": "SELECT name, price\nFROM products\n-- sort here\n",
            "checks": [
                {
                    "pattern": r"(?i)from\s+products",
                    "hint": "Keep selecting from the `products` table.",
                },
                {
                    "pattern": r"(?i)order\s+by\s+price\s+desc",
                    "hint": "Use `ORDER BY price DESC` for highest first.",
                },
            ],
            "expected_output": "All products listed from the highest price to the lowest.",
        },
    },
    {
        "id": "sq4",
        "module_id": "sm1",
        "title": "Trimming Results with LIMIT and DISTINCT",
        "concept": "LIMIT & DISTINCT",
        "explanation": (
            "`DISTINCT` removes duplicate rows so each unique value appears once. "
            "`LIMIT` caps how many rows come back, and `OFFSET` skips rows first, which is useful for paging. "
            "Pair `LIMIT` with `ORDER BY` so you get a predictable top N."
        ),
        "code_example": """SELECT DISTINCT department
FROM employees;

SELECT name, salary
FROM employees
ORDER BY salary DESC
LIMIT 3;""",
        "code_walkthrough": [
            "`SELECT DISTINCT department` returns each department name only once.",
            "`ORDER BY salary DESC` puts the highest earners first.",
            "`LIMIT 3` keeps only the first three rows: the top three salaries.",
        ],
        "key_points": [
            "`DISTINCT` applies to the whole selected row, not just the first column.",
            "`LIMIT n` returns at most n rows.",
            "`LIMIT 10 OFFSET 20` skips 20 rows, then returns the next 10.",
        ],
        "analogy": (
            "`DISTINCT` is like a guest list where each name appears once; `LIMIT` is like a "
            "bouncer who lets in only the first few people in line."
        ),
        "quiz": {
            "question": "Which rows does `LIMIT 5 OFFSET 10` return?",
            "options": ["Rows 1 to 5", "Rows 5 to 10", "Rows 11 to 15", "Rows 10 to 15"],
            "correct_index": 2,
            "explanation": "`OFFSET 10` skips the first 10 rows, then `LIMIT 5` returns the next five: rows 11 through 15.",
        },
    },
    {
        "id": "sq5",
        "module_id": "sm1",
        "title": "Summarizing with COUNT, SUM and AVG",
        "concept": "Aggregate Functions",
        "explanation": (
            "Aggregate functions boil many rows down to a single value. "
            "The common ones are `COUNT`, `SUM`, `AVG`, `MIN` and `MAX`. "
            "Most aggregates ignore NULL values, and `COUNT(*)` counts every row."
        ),
        "code_example": """SELECT COUNT(*)    AS employee_count,
       AVG(salary) AS avg_salary,
       MAX(salary) AS top_salary,
       MIN(salary) AS lowest_salary,
       SUM(salary) AS payroll
FROM employees;""",
        "code_walkthrough": [
            "`COUNT(*)` counts all rows in `employees`.",
            "`AVG(salary)` computes the average salary.",
            "`MAX(salary)` and `MIN(salary)` find the highest and lowest values.",
            "`SUM(salary)` adds every salary to get the total payroll.",
        ],
        "key_points": [
            "Aggregates return one row when used without `GROUP BY`.",
            "`COUNT(*)` counts rows; `COUNT(column)` counts only non-NULL values.",
            "Use `AS` to give aggregate results clear names.",
        ],
        "analogy": (
            "Aggregates are like a receipt's summary line: instead of every item, you see "
            "the total, the item count and the priciest thing."
        ),
        "quiz": {
            "question": "If 2 of 10 employees have a NULL salary, what does `COUNT(salary)` return?",
            "options": ["8", "10", "2", "NULL"],
            "correct_index": 0,
            "explanation": "`COUNT(column)` skips NULLs, so only the 8 non-NULL salaries are counted. `COUNT(*)` would return 10.",
        },
    },
    {
        "id": "sq6",
        "module_id": "sm1",
        "title": "Summarizing per Group",
        "concept": "GROUP BY",
        "explanation": (
            "`GROUP BY` splits rows into groups that share a value and runs aggregate functions on each group. "
            "You get one result row per group, such as one row per department. "
            "Every selected column should be either in the `GROUP BY` or wrapped in an aggregate."
        ),
        "code_example": """SELECT department,
       COUNT(*)    AS headcount,
       AVG(salary) AS avg_salary
FROM employees
GROUP BY department;""",
        "code_walkthrough": [
            "`SELECT department` shows which group each result row belongs to.",
            "`COUNT(*) AS headcount` counts employees in each department.",
            "`AVG(salary) AS avg_salary` averages salaries within each department.",
            "`GROUP BY department` creates one group per distinct department.",
        ],
        "key_points": [
            "`GROUP BY` produces one row per unique group value.",
            "Aggregates are calculated separately for each group.",
            "Non-aggregated columns in `SELECT` belong in the `GROUP BY`.",
        ],
        "analogy": (
            "`GROUP BY` is like sorting laundry into piles by color, then counting how many items are in each pile."
        ),
        "quiz": {
            "question": "If `employees` has 50 rows across 4 departments, how many rows does `SELECT department, COUNT(*) FROM employees GROUP BY department;` return?",
            "options": ["1", "50", "200", "4"],
            "correct_index": 3,
            "explanation": "`GROUP BY` returns one row per distinct department, so you get 4 rows.",
        },
    },
    {
        "id": "sq7",
        "module_id": "sm1",
        "title": "Filtering Groups with HAVING",
        "concept": "HAVING",
        "explanation": (
            "`HAVING` filters groups after `GROUP BY` has done its work, so it can use aggregate results. "
            "`WHERE` filters individual rows before grouping and can't use aggregates. "
            "You can use both in one query: `WHERE` first, then grouping, then `HAVING`."
        ),
        "code_example": """SELECT department, AVG(salary) AS avg_salary
FROM employees
WHERE salary > 30000
GROUP BY department
HAVING AVG(salary) > 60000
ORDER BY avg_salary DESC;""",
        "code_walkthrough": [
            "`WHERE salary > 30000` drops individual low-salary rows before grouping.",
            "`GROUP BY department` groups the remaining rows.",
            "`HAVING AVG(salary) > 60000` keeps only departments whose average is above 60000.",
            "`ORDER BY avg_salary DESC` sorts the surviving groups by their average.",
        ],
        "key_points": [
            "`WHERE` filters rows; `HAVING` filters groups.",
            "Aggregates like `AVG()` and `COUNT()` are allowed in `HAVING` but not in `WHERE`.",
            "Clause order: `SELECT`, `FROM`, `WHERE`, `GROUP BY`, `HAVING`, `ORDER BY`, `LIMIT`.",
        ],
        "analogy": (
            "`WHERE` picks which students enter the contest; `HAVING` picks which teams "
            "advance based on their team scores."
        ),
        "quiz": {
            "question": "Which clause should you use to keep only departments with more than 5 employees?",
            "options": [
                "WHERE COUNT(*) > 5",
                "ORDER BY COUNT(*) > 5",
                "HAVING COUNT(*) > 5",
                "LIMIT 5",
            ],
            "correct_index": 2,
            "explanation": "The condition depends on an aggregate over each group, so it belongs in `HAVING`, after `GROUP BY department`.",
        },
    },
    {
        "id": "sq8",
        "module_id": "sm1",
        "title": "Working with Missing Values",
        "concept": "Handling NULLs",
        "explanation": (
            "`NULL` means a value is missing or unknown; it's not zero or an empty string. "
            "Comparing anything to NULL with `=` gives unknown, so you must use `IS NULL` or `IS NOT NULL`. "
            "`COALESCE()` returns the first non-NULL value, which is handy for supplying defaults."
        ),
        "code_example": """SELECT id, email
FROM users
WHERE created_at IS NULL;

SELECT name, COALESCE(department, 'Unassigned') AS dept
FROM employees;""",
        "code_walkthrough": [
            "`WHERE created_at IS NULL` finds users with no creation date recorded.",
            "`COALESCE(department, 'Unassigned')` uses the department if present, otherwise 'Unassigned'.",
            "`AS dept` names the resulting column.",
        ],
        "key_points": [
            "Use `IS NULL` and `IS NOT NULL`, never `= NULL`.",
            "Most arithmetic with NULL produces NULL.",
            "`COALESCE(a, b, ...)` returns the first argument that isn't NULL.",
        ],
        "analogy": (
            "NULL is like a blank on a form: you can't say whether it matches anything "
            "because you don't know what should be there."
        ),
        "quiz": {
            "question": "What does `SELECT * FROM users WHERE created_at = NULL;` return?",
            "options": [
                "All users with a NULL created_at",
                "No rows",
                "All users",
                "A syntax error",
            ],
            "correct_index": 1,
            "explanation": "Comparing with `= NULL` evaluates to unknown for every row, so nothing matches. Use `IS NULL` instead.",
        },
    },
    {
        "id": "sq9",
        "module_id": "sm2",
        "title": "Combining Tables with Joins",
        "concept": "INNER & OUTER Joins",
        "explanation": (
            "Joins combine rows from two tables using a matching column, such as `orders.user_id = users.id`. "
            "An `INNER JOIN` keeps only rows that match on both sides. "
            "A `LEFT JOIN` keeps every row from the left table and fills in NULLs where the right table has no match."
        ),
        "code_example": """-- INNER JOIN: only users who have orders
SELECT u.email, o.total
FROM users u
INNER JOIN orders o ON o.user_id = u.id;
-- LEFT JOIN: every user; total is NULL if they have no orders
SELECT u.email, o.total
FROM users u
LEFT JOIN orders o ON o.user_id = u.id;""",
        "code_walkthrough": [
            "`FROM users u` gives the table a short alias, `u`.",
            "`INNER JOIN orders o ON o.user_id = u.id` pairs each order with its user and drops users without orders.",
            "`LEFT JOIN orders o ON ...` keeps every user, even those with no orders.",
            "For users without orders, `o.total` comes back as NULL.",
        ],
        "key_points": [
            "`ON` specifies how rows from the two tables match.",
            "`INNER JOIN` returns only matches; `LEFT JOIN` keeps all left-side rows.",
            "Table aliases like `u` and `o` keep queries short and readable.",
        ],
        "analogy": (
            "An inner join is like a party where only couples get in; a left join lets in "
            "everyone from the left list, whether or not they brought a partner."
        ),
        "quiz": {
            "question": "With `users LEFT JOIN orders`, what happens to a user who has no orders?",
            "options": [
                "They appear once, with NULLs in the order columns",
                "They are left out of the results",
                "They cause an error",
                "They appear once for every order in the table",
            ],
            "correct_index": 0,
            "explanation": "A `LEFT JOIN` keeps every row from the left table; when there's no match, the right-side columns are NULL.",
        },
    },
    {
        "id": "sq10",
        "module_id": "sm2",
        "title": "Queries Inside Queries",
        "concept": "Subqueries",
        "explanation": (
            "A subquery is a `SELECT` nested inside another query, wrapped in parentheses. "
            "It can return a single value to compare against, or a list of values to use with `IN`. "
            'Subqueries let you answer questions in steps, like "who earns more than average?"'
        ),
        "code_example": """SELECT name, salary
FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees);

SELECT name
FROM products
WHERE id IN (SELECT product_id FROM orders);""",
        "code_walkthrough": [
            "`(SELECT AVG(salary) FROM employees)` runs first and returns one number: the average salary.",
            "`WHERE salary > (...)` keeps employees who earn more than that average.",
            "`(SELECT product_id FROM orders)` returns a list of every ordered product id.",
            "`WHERE id IN (...)` keeps only products that appear in at least one order.",
        ],
        "key_points": [
            "Subqueries go in parentheses.",
            "A scalar subquery returns one value; use it with `=`, `>` and similar operators.",
            "A subquery returning many rows works with `IN` or `EXISTS`.",
        ],
        "analogy": (
            'A subquery is like asking a friend a quick question ("what\'s the average?") '
            "before you answer the main question yourself."
        ),
        "quiz": {
            "question": "Which query finds products that have never been ordered?",
            "options": [
                "SELECT name FROM products WHERE id IN (SELECT product_id FROM orders);",
                "SELECT name FROM products WHERE id = (SELECT product_id FROM orders);",
                "SELECT name FROM orders WHERE product_id IS NULL;",
                "SELECT name FROM products WHERE id NOT IN (SELECT product_id FROM orders);",
            ],
            "correct_index": 3,
            "explanation": "`NOT IN` keeps products whose id doesn't appear in the subquery's list of ordered product ids (assuming `orders.product_id` contains no NULLs).",
        },
    },
    {
        "id": "sq11",
        "module_id": "sm2",
        "title": "Ranking and Running Totals with Window Functions",
        "concept": "Window Functions",
        "explanation": (
            "Window functions calculate values across a set of related rows while still returning every individual row. "
            "The `OVER (...)` clause defines the window: `PARTITION BY` splits rows into groups and `ORDER BY` sets the order within each group. "
            "Common examples are `ROW_NUMBER()`, `RANK()` and aggregates like `AVG()` used with `OVER`."
        ),
        "code_example": """SELECT name, department, salary,
       RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS dept_rank,
       AVG(salary) OVER (PARTITION BY department) AS dept_avg
FROM employees;""",
        "code_walkthrough": [
            "`SELECT name, department, salary` returns one row per employee, as usual.",
            "`RANK() OVER (PARTITION BY department ORDER BY salary DESC)` ranks employees by salary within their own department.",
            "`AVG(salary) OVER (PARTITION BY department)` shows each department's average salary on every row.",
            "Unlike `GROUP BY`, no rows are collapsed.",
        ],
        "key_points": [
            "Window functions keep every row, while `GROUP BY` collapses rows.",
            "`PARTITION BY` defines groups and `ORDER BY` inside `OVER` defines their order.",
            "`RANK()` gives ties the same rank; `ROW_NUMBER()` always gives unique numbers.",
        ],
        "analogy": (
            "A window function is like a class photo where each student's name tag also "
            "shows their rank in the class, without anyone leaving the picture."
        ),
        "quiz": {
            "question": "What is the key difference between `AVG(salary) OVER (PARTITION BY department)` and `AVG(salary) ... GROUP BY department`?",
            "options": [
                "The window version is always faster",
                "GROUP BY can't calculate averages",
                "The window version keeps every employee row; GROUP BY returns one row per department",
                "There is no difference",
            ],
            "correct_index": 2,
            "explanation": "Window functions attach the calculated value to each row, while `GROUP BY` collapses each group into a single row.",
        },
    },
    {
        "id": "sq12",
        "module_id": "sm2",
        "title": "Speeding Up Queries with Indexes",
        "concept": "Indexes & Performance",
        "explanation": (
            "An index is a separate, sorted lookup structure that helps the database find rows without scanning the whole table. "
            "Indexes speed up `WHERE` filters, joins and sorting on the indexed columns. "
            "They take extra storage and slow down inserts and updates slightly, so add them where queries actually need them."
        ),
        "code_example": """CREATE INDEX idx_orders_user_id ON orders(user_id);

-- Lookups and joins on user_id can now use the index
SELECT * FROM orders WHERE user_id = 42;

EXPLAIN QUERY PLAN
SELECT * FROM orders WHERE user_id = 42;""",
        "code_walkthrough": [
            "`CREATE INDEX idx_orders_user_id ON orders(user_id);` builds an index on the `user_id` column.",
            "`WHERE user_id = 42` can now jump straight to matching rows instead of scanning every order.",
            "`EXPLAIN QUERY PLAN` (SQLite) shows how the query will run, such as `SEARCH orders USING INDEX idx_orders_user_id`.",
        ],
        "key_points": [
            "Index columns that you filter, join or sort on often.",
            "Indexes speed up reads but add cost to writes and storage.",
            "Use `EXPLAIN QUERY PLAN` to check whether an index is actually used.",
        ],
        "analogy": (
            "An index is like the index at the back of a book: instead of reading every page, "
            "you jump straight to the right one."
        ),
        "quiz": {
            "question": "What is a downside of adding an index?",
            "options": [
                "It makes SELECT queries slower",
                "It uses extra storage and slows down inserts and updates",
                "It deletes duplicate rows",
                "It stops the column from containing NULLs",
            ],
            "correct_index": 1,
            "explanation": "Every insert, update or delete must also update the index, and the index itself takes up space.",
        },
    },
]
