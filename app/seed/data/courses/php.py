"""PHP Essentials: Build dynamic, secure web back ends with modern PHP 8."""

COURSE = {
    "id": "php-essentials",
    "title": "PHP Essentials",
    "world": "ElePHPant Kingdom",
    "description": "Build dynamic, secure web back ends with modern PHP 8.",
    "language": "php",
    "modules": [
        {"id": "php-m1", "title": "PHP Basics"},
        {"id": "php-m2", "title": "Functions, Arrays & Forms"},
        {"id": "php-m3", "title": "Objects & Databases"},
    ],
}

ZONES = [
    {
        "id": "php-z1",
        "name": "Dollar Sign Dunes",
        "tagline": "Variables, strings and the flow of a script.",
        "difficulty": "easy",
        "nodes": [
            {
                "id": "php1",
                "title": "Variables & Types",
                "difficulty": "easy",
                "xp_reward": 50,
                "estimated_minutes": 10,
            },
            {
                "id": "php2",
                "title": "Strings & Interpolation",
                "difficulty": "easy",
                "xp_reward": 50,
                "estimated_minutes": 10,
            },
            {
                "id": "php3",
                "title": "Conditionals & match",
                "difficulty": "easy",
                "xp_reward": 60,
                "estimated_minutes": 12,
            },
            {"id": "php4", "title": "Loops", "difficulty": "easy", "xp_reward": 60, "estimated_minutes": 12},
        ],
        "boss": {
            "id": "php-z1-boss",
            "name": "Missing Semicolon Slime",
            "sprite": "slime",
            "challenge": "Patch 3 broken scripts before the parser melts down",
            "stages": 3,
            "xp_reward": 250,
        },
    },
    {
        "id": "php-z2",
        "name": "Array Archipelago",
        "tagline": "Reusable functions, mighty arrays and your first web forms.",
        "difficulty": "medium",
        "nodes": [
            {
                "id": "php5",
                "title": "Functions & Type Declarations",
                "difficulty": "medium",
                "xp_reward": 90,
                "estimated_minutes": 18,
            },
            {
                "id": "php6",
                "title": "Indexed & Associative Arrays",
                "difficulty": "medium",
                "xp_reward": 100,
                "estimated_minutes": 20,
            },
            {
                "id": "php7",
                "title": "Array Functions",
                "difficulty": "medium",
                "xp_reward": 100,
                "estimated_minutes": 20,
            },
            {
                "id": "php8",
                "title": "Handling Forms",
                "difficulty": "medium",
                "xp_reward": 110,
                "estimated_minutes": 20,
            },
        ],
        "boss": {
            "id": "php-z2-boss",
            "name": "Undefined Index Imp",
            "sprite": "bugSlime",
            "challenge": "Tame wild form input and reshape arrays without a single warning",
            "stages": 4,
            "xp_reward": 400,
        },
    },
    {
        "id": "php-z3",
        "name": "Object Citadel",
        "tagline": "Classes, contracts, errors and data that lives in a database.",
        "difficulty": "hard",
        "nodes": [
            {
                "id": "php9",
                "title": "Classes & Objects",
                "difficulty": "hard",
                "xp_reward": 140,
                "estimated_minutes": 25,
            },
            {
                "id": "php10",
                "title": "Interfaces & Traits",
                "difficulty": "hard",
                "xp_reward": 150,
                "estimated_minutes": 28,
            },
            {"id": "php11", "title": "Exceptions", "difficulty": "hard", "xp_reward": 150, "estimated_minutes": 28},
            {
                "id": "php12",
                "title": "Databases with PDO",
                "difficulty": "hard",
                "xp_reward": 160,
                "estimated_minutes": 30,
            },
        ],
        "boss": {
            "id": "php-z3-boss",
            "name": "SQL Injection Hydra",
            "sprite": "recursionBoss",
            "challenge": "Cut off every unsafe query head with prepared statements",
            "stages": 5,
            "xp_reward": 700,
        },
    },
]

LESSONS: list[dict] = [
    {
        "id": "php1",
        "module_id": "php-m1",
        "title": "Dollar Signs and Data Types",
        "concept": "Variables and data types",
        "explanation": (
            "Every PHP variable starts with a `$`, and you create one simply by assigning a value to it. "
            "PHP decides the type from the value: common types are string, int, float, bool, array and null. "
            "`var_dump()` and `get_debug_type()` show you exactly what type a value has, which is handy when debugging."
        ),
        "code_example": r"""<?php
$name = "Ada";         // string
$age = 36;             // int
$price = 9.99;         // float
$isAdmin = false;      // bool
echo get_debug_type($name), "\n";   // string
echo get_debug_type($age), "\n";    // int
echo get_debug_type($price), "\n";  // float
var_dump($isAdmin);                 // bool(false)""",
        "code_walkthrough": [
            "`<?php` opens a block of PHP code; everything after it is run by the PHP engine.",
            '`$name = "Ada";` creates a variable just by assigning to it; no keyword is needed.',
            '`echo` prints values; the comma lets you print several values in a row, and `"\\n"` adds a line break.',
            "`get_debug_type()` returns the type name as a string: `string`, `int` and `float` here.",
            "`var_dump($isAdmin)` prints both the type and the value: `bool(false)`.",
        ],
        "key_points": [
            "Variable names start with `$` and are case-sensitive (`$age` and `$Age` are different).",
            "PHP is dynamically typed: a variable's type comes from the value it holds.",
            "Use `var_dump()` when you need to see a value's exact type and contents.",
        ],
        "analogy": (
            "A variable is like a labeled jar: the `$` label tells PHP it's a jar, and whatever you pour "
            "in (text, a number, true/false) decides what kind of jar it is."
        ),
        "quiz": {
            "question": 'What does `var_dump("5" + 3);` print?',
            "options": ['string(2) "53"', "int(8)", "float(8)", "A TypeError"],
            "correct_index": 1,
            "explanation": (
                'The `+` operator always does math in PHP, so the numeric string "5" becomes the integer 5 '
                "and the result is `int(8)`. To join strings, PHP uses the `.` operator instead."
            ),
        },
    },
    {
        "id": "php2",
        "module_id": "php-m1",
        "title": "Building Text with Strings",
        "concept": "String interpolation",
        "explanation": (
            "Double-quoted strings replace variables with their values (interpolation), while single-quoted "
            "strings print everything exactly as written. "
            "Wrap a variable in curly braces like `{$name}` when it sits right next to other text. "
            "The `.` operator joins strings, and built-in functions such as `strlen()`, `strtoupper()` and "
            "`str_contains()` help you inspect and change them."
        ),
        "code_example": r"""<?php
$name = "Ada";
$lang = 'PHP';
echo "Hi, $name!\n";                 // Hi, Ada!
echo 'Hi, $name!' . "\n";            // Hi, $name!
echo "Version: {$lang} 8\n";         // Version: PHP 8
echo strtoupper($name) . "\n";       // ADA
echo strlen("Logicraft") . "\n";     // 9
var_dump(str_contains("Logicraft", "craft")); // bool(true)""",
        "code_walkthrough": [
            '`"Hi, $name!\\n"` is double-quoted, so `$name` is replaced with "Ada".',
            "`'Hi, $name!'` is single-quoted, so the text is printed literally, dollar sign and all.",
            '`.` joins the single-quoted string with `"\\n"` to add a line break.',
            "`{$lang}` uses curly braces to mark exactly where the variable name ends.",
            "`strtoupper()`, `strlen()` and `str_contains()` (new in PHP 8) uppercase, count and search a string.",
        ],
        "key_points": [
            "Double quotes interpolate variables; single quotes don't.",
            "Use `.` (not `+`) to join strings together.",
            "Use `{$var}` when a variable is surrounded by other text.",
        ],
        "analogy": (
            "A double-quoted string is like a fill-in-the-blanks form that PHP completes for you; "
            "a single-quoted string is a photocopy that stays exactly as written."
        ),
        "quiz": {
            "question": "What does this print?\n\n$item = 'sword';\necho 'You found a $item';",
            "options": ["You found a sword", "You found a", "An error", "You found a $item"],
            "correct_index": 3,
            "explanation": "Single-quoted strings don't interpolate, so `$item` is printed literally.",
        },
        "try_it": {
            "prompt": (
                "Use ONE double-quoted string with interpolation to print: Welcome, Sam! You have 3 coins. "
                "(Use the `$user` and `$coins` variables.)"
            ),
            "starter_code": '<?php\n$user = "Sam";\n$coins = 3;\n// echo your greeting here\n',
            "checks": [
                {
                    "pattern": r"echo\s*\"[^\"\n]*\$user\b[^\"\n]*\$coins\b[^\"\n]*\"",
                    "hint": 'Write one `echo "..."` string that contains both `$user` and `$coins`.',
                },
                {
                    "pattern": r"Welcome,",
                    "hint": 'Start the message with "Welcome,".',
                },
            ],
            "expected_output": "Welcome, Sam! You have 3 coins.",
        },
    },
    {
        "id": "php3",
        "module_id": "php-m1",
        "title": "Making Decisions with if and match",
        "concept": "match expression",
        "explanation": (
            "`if`, `elseif` and `else` run different blocks of code depending on whether a condition is true. "
            "PHP 8's `match` expression compares one value against several options and returns the matching result. "
            "Unlike `switch`, `match` uses strict comparison (`===`), needs no `break`, and throws an "
            "`UnhandledMatchError` if nothing matches and there is no `default`."
        ),
        "code_example": r"""<?php
$score = 82;
if ($score >= 90) {
    echo "Gold\n";
} elseif ($score >= 75) {
    echo "Silver\n";              // Silver
} else {
    echo "Bronze\n";
}
$day = "sat";
$type = match ($day) {
    "sat", "sun" => "weekend",
    default => "weekday",
};
echo $type;                       // weekend""",
        "code_walkthrough": [
            "`if ($score >= 90)` is false for 82, so PHP moves on to the `elseif`.",
            '`elseif ($score >= 75)` is true, so "Silver" is printed and the `else` is skipped.',
            "`match ($day)` compares `$day` against each arm using strict `===` comparison.",
            '`"sat", "sun" => "weekend"` lets one arm handle several values.',
            '`default => "weekday"` is the fallback, and the chosen value is stored in `$type`.',
        ],
        "key_points": [
            "Conditions go in parentheses and code blocks in curly braces.",
            "`match` returns a value, compares strictly and never falls through.",
            "Add a `default` arm to a `match` unless every possible value is covered.",
        ],
        "analogy": (
            "`match` is like a vending machine: press a button (the value) and you get exactly the snack "
            "for that button, or a default if the button doesn't exist."
        ),
        "quiz": {
            "question": (
                'What does this print?\n\n$x = "1";\necho match ($x) {\n    1 => "int",\n    "1" => "string",\n'
                '    default => "other",\n};'
            ),
            "options": ["string", "int", "other", "An UnhandledMatchError"],
            "correct_index": 0,
            "explanation": (
                '`match` uses strict comparison, so the string "1" does not match the integer 1 but does '
                'match the string "1".'
            ),
        },
        "try_it": {
            "prompt": (
                'Use `match` on `$weather` to set `$advice`: "sun" gives "Wear sunglasses", "rain" gives '
                '"Take an umbrella", and anything else gives "Enjoy your day".'
            ),
            "starter_code": '<?php\n$weather = "rain";\n// $advice = match (...) { ... };\n\necho $advice;\n',
            "checks": [
                {
                    "pattern": r"\$advice\s*=\s*match\s*\(\s*\$weather\s*\)",
                    "hint": "Start with `$advice = match ($weather) {`.",
                },
                {
                    "pattern": r"[\"']rain[\"']\s*=>\s*[\"']Take an umbrella[\"']",
                    "hint": 'Add the arm `"rain" => "Take an umbrella",`.',
                },
                {
                    "pattern": r"default\s*=>",
                    "hint": 'Finish with a `default => "Enjoy your day",` arm.',
                },
            ],
            "expected_output": "Take an umbrella",
        },
    },
    {
        "id": "php4",
        "module_id": "php-m1",
        "title": "Repeating Work with Loops",
        "concept": "Loops",
        "explanation": (
            "A `for` loop repeats code with a counter that has a start, a condition and a step. "
            "`foreach` is PHP's favorite loop: it walks through every element of an array, optionally giving "
            "you each key too. "
            "A `while` loop keeps going for as long as its condition stays true."
        ),
        "code_example": r"""<?php
for ($i = 1; $i <= 3; $i++) {
    echo $i, " ";                 // 1 2 3
}
echo "\n";
$fruits = ["apple", "kiwi"];
foreach ($fruits as $index => $fruit) {
    echo "$index: $fruit\n";      // 0: apple, then 1: kiwi
}
$n = 3;
while ($n > 0) {
    echo $n--, "...";             // 3...2...1...
}""",
        "code_walkthrough": [
            "`$i = 1` starts the counter, `$i <= 3` is checked before each pass, and `$i++` runs after each pass.",
            "`foreach ($fruits as $index => $fruit)` gives each key and value in turn.",
            "Inside double quotes, `$index` and `$fruit` are interpolated into the line.",
            "`while ($n > 0)` repeats until `$n` reaches 0.",
            "`$n--` prints the current value and then decreases it, so you get 3, 2, then 1.",
        ],
        "key_points": [
            "Use `foreach` to loop over arrays; it's the most common loop in PHP.",
            "Use `for` when you need a counter, and `while` when you loop until a condition changes.",
            "Make sure a `while` loop's condition eventually becomes false, or it runs forever.",
        ],
        "analogy": (
            "`foreach` is like a teacher calling the register: every name on the list gets called exactly "
            "once, in order."
        ),
        "quiz": {
            "question": "Which loop is the most natural way to visit every key and value of an array?",
            "options": ["for", "while", "foreach", "do...while"],
            "correct_index": 2,
            "explanation": "`foreach ($array as $key => $value)` hands you each key and value without managing a counter.",
        },
    },
    {
        "id": "php5",
        "module_id": "php-m2",
        "title": "Functions with Type Declarations",
        "concept": "Type declarations",
        "explanation": (
            "Functions package reusable code: they take parameters and can `return` a value. "
            "Modern PHP lets you declare the type of each parameter and of the return value, so mistakes are "
            "caught early. "
            "Adding `declare(strict_types=1);` at the top of a file stops PHP from quietly converting values, "
            "and arrow functions (`fn`) give you short one-line functions."
        ),
        "code_example": r"""<?php
declare(strict_types=1);
function add(int $a, int $b): int
{
    return $a + $b;
}
function greet(string $name = "friend"): string
{
    return "Hello, $name!";
}
$double = fn(int $x): int => $x * 2;
echo add(2, 3), "\n";            // 5
echo greet(), "\n";              // Hello, friend!
echo greet("Ada"), "\n";         // Hello, Ada!
echo $double(21);                // 42""",
        "code_walkthrough": [
            "`declare(strict_types=1);` makes PHP throw a `TypeError` instead of converting wrong types.",
            "`function add(int $a, int $b): int` declares two int parameters and an int return value.",
            '`string $name = "friend"` gives the parameter a default used when no argument is passed.',
            "`fn(int $x): int => $x * 2` is an arrow function that returns its expression automatically.",
            "`$double(21)` calls the function stored in the variable and returns 42.",
        ],
        "key_points": [
            "Type declarations document your function and catch bugs early.",
            "`declare(strict_types=1);` must be the very first statement in the file.",
            "Default parameter values cover missing arguments.",
        ],
        "analogy": (
            "Type declarations are like labeled slots in a shape-sorter toy: only the right shape fits, "
            "so mistakes are obvious straight away."
        ),
        "quiz": {
            "question": (
                'In a file with `declare(strict_types=1);`, what happens when you call `add("2", 3)` on '
                "`function add(int $a, int $b): int`?"
            ),
            "options": ["It returns 5", 'It returns "23"', "A TypeError is thrown", "It returns 0"],
            "correct_index": 2,
            "explanation": (
                'With strict types on, PHP refuses to convert the string `"2"` into an int and throws a TypeError.'
            ),
        },
    },
    {
        "id": "php6",
        "module_id": "php-m2",
        "title": "Lists and Maps with PHP Arrays",
        "concept": "Associative arrays",
        "explanation": (
            "A PHP array can be an indexed list (keys 0, 1, 2...) or an associative array with string keys, "
            "much like a dictionary. "
            "`$list[] = value` appends to the end, and `count()` tells you how many elements there are. "
            "The null coalescing operator `??` gives a safe fallback when a key might not exist."
        ),
        "code_example": r"""<?php
$colors = ["red", "green"];
$colors[] = "blue";
echo $colors[0], "\n";                  // red
echo count($colors), "\n";              // 3
$user = ["name" => "Sam", "age" => 25];
$user["email"] = "sam@example.com";
echo $user["name"], "\n";               // Sam
echo $user["city"] ?? "unknown", "\n";  // unknown
foreach ($user as $key => $value) {
    echo "$key=$value\n";  // name=Sam, age=25, email=sam@example.com
}""",
        "code_walkthrough": [
            '`["red", "green"]` creates an indexed array with keys 0 and 1.',
            '`$colors[] = "blue";` appends "blue" at the next index, so `count($colors)` is 3.',
            '`["name" => "Sam", "age" => 25]` creates an associative array with string keys.',
            '`$user["email"] = ...` adds a new key-value pair.',
            '`$user["city"] ?? "unknown"` falls back to "unknown" because the key doesn\'t exist.',
            "`foreach ($user as $key => $value)` walks every pair in insertion order.",
        ],
        "key_points": [
            "Indexed arrays use numeric keys starting at 0; associative arrays use named keys.",
            "Use `$array[] = value` to append and `count()` to get the size.",
            "Use `??` or `isset()` before reading keys that might be missing.",
        ],
        "analogy": (
            "An indexed array is like a numbered row of lockers; an associative array is like a set of "
            "drawers with name labels."
        ),
        "quiz": {
            "question": 'What does `$items[] = "x";` do?',
            "options": [
                'Appends "x" to the end of the array',
                'Replaces the whole array with "x"',
                'Inserts "x" at the start of the array',
                "Throws an error because no index was given",
            ],
            "correct_index": 0,
            "explanation": "Empty square brackets on assignment append the value at the next available integer key.",
        },
    },
    {
        "id": "php7",
        "module_id": "php-m2",
        "title": "Transforming Arrays with Built-in Functions",
        "concept": "Array functions",
        "explanation": (
            "PHP ships with dozens of array functions so you rarely need to write loops by hand. "
            "`array_map()` transforms every element, `array_filter()` keeps the elements that pass a test, and "
            "`array_reduce()` or `array_sum()` boil an array down to a single value. "
            "Watch out: `array_filter()` keeps the original keys, so use `array_values()` if you need a fresh 0, 1, 2 list."
        ),
        "code_example": r"""<?php
$prices = [5, 12, 8, 20];
$doubled = array_map(fn($p) => $p * 2, $prices);
$big = array_filter($prices, fn($p) => $p > 10);
$total = array_reduce($prices, fn($sum, $p) => $sum + $p, 0);
echo implode(", ", $doubled), "\n";          // 10, 24, 16, 40
echo json_encode($big), "\n";                // {"1":12,"3":20}
echo json_encode(array_values($big)), "\n";  // [12,20]
echo $total, "\n";                           // 45
echo array_sum($prices);                     // 45""",
        "code_walkthrough": [
            "`array_map(fn($p) => $p * 2, $prices)` takes the callback first and returns a new, doubled array.",
            "`array_filter($prices, fn($p) => $p > 10)` takes the array first and keeps only 12 and 20.",
            "`json_encode($big)` reveals that the filtered array kept its original keys 1 and 3.",
            "`array_values($big)` re-numbers the keys from 0, giving the list `[12,20]`.",
            "`array_reduce(...)` starts at 0 and adds each price; `array_sum()` is a shortcut for the same total.",
        ],
        "key_points": [
            "`array_map` transforms, `array_filter` selects, `array_reduce` combines.",
            "The argument order differs: `array_map($callback, $array)` but `array_filter($array, $callback)`.",
            "`implode()` joins array values into a string with a separator.",
        ],
        "analogy": (
            "Think of a factory line: `array_map` paints every item, `array_filter` removes the faulty ones, "
            "and `array_reduce` packs everything into one box."
        ),
        "quiz": {
            "question": "Which call keeps only the positive numbers in `$nums`?",
            "options": [
                "array_map($nums, fn($n) => $n > 0)",
                "array_filter(fn($n) => $n > 0, $nums)",
                "array_reduce($nums, fn($n) => $n > 0)",
                "array_filter($nums, fn($n) => $n > 0)",
            ],
            "correct_index": 3,
            "explanation": (
                "`array_filter` takes the array first and a callback second, keeping elements where the "
                "callback returns true."
            ),
        },
        "try_it": {
            "prompt": "Use `array_filter` to keep only the even numbers from `$nums`.",
            "starter_code": (
                '<?php\n$nums = [1, 2, 3, 4, 5, 6];\n$evens = []; // replace [] with array_filter(...)\n\necho implode(", ", $evens);\n'
            ),
            "checks": [
                {
                    "pattern": r"array_filter\s*\(\s*\$nums\s*,",
                    "hint": "Call `array_filter($nums, ...)` with the array first.",
                },
                {
                    "pattern": r"%\s*2\s*===?\s*0|0\s*===?\s*\$\w+\s*%\s*2",
                    "hint": "A number is even when `$n % 2 === 0`.",
                },
            ],
            "expected_output": "2, 4, 6",
        },
    },
    {
        "id": "php8",
        "module_id": "php-m2",
        "title": "Reading Form Data Safely",
        "concept": "Form handling",
        "explanation": (
            "When a browser sends a form, PHP puts the fields in the superglobal arrays `$_GET` (from the URL) "
            "and `$_POST` (from the request body). "
            "Never trust this input: validate it, and always escape it with `htmlspecialchars()` before "
            "printing it into HTML. "
            "Escaping turns characters like `<` into `&lt;`, which stops attackers from injecting scripts (XSS)."
        ),
        "code_example": r"""<?php
// Request: search.php?q=<b>PHP</b>
$query = $_GET["q"] ?? "";
$safe = htmlspecialchars($query, ENT_QUOTES, "UTF-8");
echo "You searched for: $safe";
// You searched for: &lt;b&gt;PHP&lt;/b&gt;

if ($_SERVER["REQUEST_METHOD"] === "POST") {
    $email = trim($_POST["email"] ?? "");
    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        echo "Please enter a valid email.";
    }
}""",
        "code_walkthrough": [
            '`$_GET["q"] ?? ""` reads the `q` URL parameter, or an empty string if it is missing.',
            '`htmlspecialchars($query, ENT_QUOTES, "UTF-8")` escapes `<`, `>`, `&` and quotes.',
            "The browser now shows `<b>PHP</b>` as plain text instead of treating it as HTML.",
            '`$_SERVER["REQUEST_METHOD"] === "POST"` checks whether a form was submitted.',
            "`filter_var($email, FILTER_VALIDATE_EMAIL)` validates the trimmed email before you use it.",
        ],
        "key_points": [
            "`$_GET` holds URL parameters and `$_POST` holds submitted form fields.",
            "Validate input on the server, even if the browser already checked it.",
            "Escape output with `htmlspecialchars()` every time you print user data into HTML.",
        ],
        "analogy": (
            "Escaping output is like putting a letter from a stranger inside a glass display case: everyone "
            "can read it, but it can't reach out and touch anything."
        ),
        "quiz": {
            "question": "Why pass user input through `htmlspecialchars()` before echoing it into a page?",
            "options": [
                "It makes the page load faster",
                "It stops injected HTML and JavaScript from running (XSS)",
                "It checks that the input is a valid email address",
                "It protects SQL queries from injection",
            ],
            "correct_index": 1,
            "explanation": (
                "`htmlspecialchars()` converts characters like `<` and `>` into HTML entities, so injected "
                "markup is displayed as text instead of running. SQL injection needs prepared statements instead."
            ),
        },
        "try_it": {
            "prompt": "This comment came from a user. Change the `echo` so it prints `htmlspecialchars($comment)` instead.",
            "starter_code": "<?php\n$comment = '<script>alert(\"hi\")</script>';\n// print it safely\necho $comment;\n",
            "checks": [
                {
                    "pattern": r"echo\s*\(?\s*htmlspecialchars\s*\(\s*\$comment\b",
                    "hint": "Write `echo htmlspecialchars($comment);`.",
                },
            ],
            "expected_output": "&lt;script&gt;alert(&quot;hi&quot;)&lt;/script&gt;",
        },
    },
    {
        "id": "php9",
        "module_id": "php-m3",
        "title": "Blueprints with Classes and Objects",
        "concept": "Classes and objects",
        "explanation": (
            "A class is a blueprint that bundles data (properties) and behavior (methods); `new` builds an "
            "object from it. "
            "Visibility keywords control access: `public` members can be used anywhere, while `private` ones are "
            "only reachable inside the class through `$this`. "
            "PHP 8's constructor promotion lets you declare and set properties right in the constructor's parameters."
        ),
        "code_example": r"""<?php
class Player
{
    private int $xp = 0;
    public function __construct(public string $name) {}
    public function gainXp(int $amount): int
    {
        $this->xp += $amount;
        return $this->xp;
    }
}
$hero = new Player("Ada");
echo $hero->name, "\n";          // Ada
echo $hero->gainXp(50), "\n";    // 50
echo $hero->gainXp(25);          // 75""",
        "code_walkthrough": [
            "`class Player` defines the blueprint for player objects.",
            "`private int $xp = 0;` is a typed property that only the class's own methods can touch.",
            "`__construct(public string $name)` uses constructor promotion to create and fill a public `$name` property.",
            "`$this->xp += $amount;` updates the property on the current object.",
            '`new Player("Ada")` creates an object, and `->` accesses its properties and methods.',
        ],
        "key_points": [
            "Use `new ClassName(...)` to create an object and `->` to use its members.",
            "Keep properties `private` and expose behavior through `public` methods.",
            "Constructor promotion (`public string $name` in the constructor) removes boilerplate.",
        ],
        "analogy": (
            "A class is a cookie cutter and objects are the cookies: same shape, but each cookie can have "
            "its own sprinkles (property values)."
        ),
        "quiz": {
            "question": "What happens if code outside the class runs `echo $hero->xp;`?",
            "options": [
                "It prints 0",
                "An Error is thrown because `$xp` is private",
                "It prints null",
                "It prints the player's name",
            ],
            "correct_index": 1,
            "explanation": "Private properties can only be accessed from inside the class, so PHP throws an Error.",
        },
    },
    {
        "id": "php10",
        "module_id": "php-m3",
        "title": "Sharing Behavior with Interfaces and Traits",
        "concept": "Interfaces and traits",
        "explanation": (
            "An interface is a contract: it lists methods a class promises to implement, without any code. "
            "A trait is a reusable chunk of methods that you can copy into any class with `use`. "
            "A class can extend only one parent class, but it can implement many interfaces and use many traits."
        ),
        "code_example": r"""<?php
interface Shape {
    public function area(): float;
}
trait Greets {
    public function hello(): string { return "Hi from " . static::class; }
}
class Square implements Shape {
    use Greets;
    public function __construct(private float $side) {}
    public function area(): float { return $this->side ** 2; }
}
$sq = new Square(3);
echo $sq->area(), "\n";          // 9
echo $sq->hello();               // Hi from Square""",
        "code_walkthrough": [
            "`interface Shape` declares that every shape must have an `area(): float` method.",
            "`trait Greets` holds a ready-made `hello()` method that classes can reuse.",
            "`class Square implements Shape` promises to provide `area()`; PHP errors if it doesn't.",
            "`use Greets;` copies the trait's methods into `Square`, and `static::class` is the class name.",
            "`$this->side ** 2` squares the side: 3 squared prints as 9.",
        ],
        "key_points": [
            "Interfaces define what a class must do; they contain no implementation.",
            "Traits share method code between unrelated classes with `use TraitName;`.",
            "Code can accept any `Shape` without caring which class it really is.",
        ],
        "analogy": (
            "An interface is a job description listing required skills; a trait is a training course any "
            "employee can take to gain those skills instantly."
        ),
        "quiz": {
            "question": "How does a class add the methods from a trait called `Loggable`?",
            "options": [
                "class A extends Loggable",
                "class A implements Loggable",
                "By calling Loggable::copy() in the constructor",
                "With `use Loggable;` inside the class body",
            ],
            "correct_index": 3,
            "explanation": "Traits are pulled into a class with a `use` statement inside the class body.",
        },
    },
    {
        "id": "php11",
        "module_id": "php-m3",
        "title": "Handling Errors with Exceptions",
        "concept": "Exceptions",
        "explanation": (
            "When something goes wrong, code can `throw` an exception object to stop normal execution. "
            "A `try` block wraps risky code, and a matching `catch` block handles the problem instead of "
            "crashing the script. "
            "A `finally` block runs either way, which makes it perfect for clean-up work."
        ),
        "code_example": r"""<?php
function divide(int $a, int $b): float {
    if ($b === 0) {
        throw new InvalidArgumentException("Cannot divide by zero");
    }
    return $a / $b;
}
try {
    echo divide(10, 4), "\n";    // 2.5
    echo divide(1, 0), "\n";     // never printed
} catch (InvalidArgumentException $e) {
    echo "Error: ", $e->getMessage(), "\n";  // Error: Cannot divide by zero
} finally {
    echo "Done";                 // Done
}""",
        "code_walkthrough": [
            '`throw new InvalidArgumentException("...")` stops the function and sends the error upward.',
            "`divide(10, 4)` succeeds and prints 2.5.",
            "`divide(1, 0)` throws, so the rest of the `try` block is skipped.",
            "`catch (InvalidArgumentException $e)` handles it, and `$e->getMessage()` returns the message.",
            '`finally` always runs, so "Done" is printed last.',
        ],
        "key_points": [
            "Throw exceptions for situations your code can't handle normally.",
            "Catch the most specific exception type you can handle.",
            "Use `finally` for clean-up that must happen whether or not an error occurred.",
        ],
        "analogy": (
            "An exception is like a fire alarm: normal work stops immediately, and the trained "
            "responders (the `catch` block) take over."
        ),
        "quiz": {
            "question": "When does a `finally` block run?",
            "options": [
                "Always, whether or not an exception was thrown",
                "Only when an exception is caught",
                "Only when no exception is thrown",
                "Only when the script is about to exit",
            ],
            "correct_index": 0,
            "explanation": "`finally` runs after the `try` (and any `catch`) no matter how they finished.",
        },
    },
    {
        "id": "php12",
        "module_id": "php-m3",
        "title": "Talking to Databases with PDO",
        "concept": "PDO prepared statements",
        "explanation": (
            "PDO (PHP Data Objects) is PHP's built-in way to talk to databases such as MySQL, PostgreSQL and SQLite. "
            "Prepared statements send the SQL with placeholders (`?` or `:name`) first and the values separately, "
            "so user input can never change the query. "
            "Never paste user input straight into a SQL string: that is how SQL injection attacks happen."
        ),
        "code_example": r"""<?php
$pdo = new PDO("sqlite::memory:");
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
$pdo->exec("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)");
$insert = $pdo->prepare("INSERT INTO users (name, email) VALUES (?, ?)");
$insert->execute(["Ada", "ada@example.com"]);
$insert->execute(["Sam", "sam@example.com"]);

$email = "sam@example.com";  // imagine this came from $_POST
$stmt = $pdo->prepare("SELECT id, name FROM users WHERE email = :email");
$stmt->execute(["email" => $email]);
$user = $stmt->fetch(PDO::FETCH_ASSOC);
echo "{$user['name']} has id {$user['id']}";  // Sam has id 2""",
        "code_walkthrough": [
            '`new PDO("sqlite::memory:")` connects to a temporary in-memory SQLite database.',
            "`PDO::ERRMODE_EXCEPTION` makes database errors throw exceptions (the default since PHP 8).",
            '`prepare("... VALUES (?, ?)")` builds a reusable statement with positional placeholders.',
            "`execute([...])` sends the values separately, so they're always treated as data, never as SQL.",
            '`:email` is a named placeholder filled by `["email" => $email]`.',
            "`fetch(PDO::FETCH_ASSOC)` returns the matching row as an associative array.",
        ],
        "key_points": [
            "Always use prepared statements with placeholders for any value that comes from outside.",
            "A prepared statement can be executed many times with different values.",
            "Turn on exception error mode so database failures are never silently ignored.",
        ],
        "analogy": (
            "A prepared statement is like a printed form with blank boxes: people can only write in the "
            "boxes, never rewrite the questions on the form."
        ),
        "quiz": {
            "question": "Which code safely looks up a user by an email that came from a form?",
            "options": [
                "$pdo->query(\"SELECT * FROM users WHERE email = '$email'\")",
                '$pdo->query("SELECT * FROM users WHERE email = \'" . addslashes($email) . "\'")',
                '$stmt = $pdo->prepare("SELECT * FROM users WHERE email = ?"); $stmt->execute([$email]);',
                '$pdo->exec("SELECT * FROM users WHERE email = $email")',
            ],
            "correct_index": 2,
            "explanation": (
                "Only the prepared statement keeps the value separate from the SQL. Building the query string "
                "from user input, even with `addslashes()`, leaves room for SQL injection."
            ),
        },
        "try_it": {
            "prompt": (
                "The query below pastes `$name` straight into the SQL. Rewrite it with `$pdo->prepare()` using a "
                "placeholder, then pass `$name` to `execute()`."
            ),
            "starter_code": (
                "<?php\n"
                '$pdo = new PDO("sqlite::memory:");\n'
                '$pdo->exec("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)");\n'
                "$pdo->exec(\"INSERT INTO users (name) VALUES ('Ada'), ('Sam')\");\n"
                "\n"
                '$name = "Sam"; // pretend this came from a form\n'
                "// UNSAFE: fix this with prepare() and execute()\n"
                "$stmt = $pdo->query(\"SELECT id FROM users WHERE name = '$name'\");\n"
                "echo $stmt->fetchColumn();\n"
            ),
            "checks": [
                {
                    "pattern": r"->\s*prepare\s*\(\s*[\"'][^\"']*name\s*=\s*(\?|:\w+)",
                    "hint": 'Use `$pdo->prepare("SELECT id FROM users WHERE name = ?")`.',
                },
                {
                    "pattern": r"->\s*execute\s*\(\s*\[[^\]]*\$name",
                    "hint": "Pass the value separately: `$stmt->execute([$name]);`.",
                },
            ],
            "expected_output": "2",
        },
    },
]
