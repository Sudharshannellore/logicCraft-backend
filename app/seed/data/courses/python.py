"""Python Mastery: Go from zero to confident Python developer through hands-on, gamified lessons."""

COURSE = {
    "id": "python-mastery",
    "title": "Python Mastery",
    "world": "Python World",
    "description": "Go from zero to confident Python developer through hands-on, gamified lessons.",
    "language": "python",
    "modules": [
        {"id": "m1", "title": "Python Basics"},
        {"id": "m2", "title": "Control Flow"},
        {"id": "m3", "title": "Functions"},
        {"id": "m4", "title": "Data Structures"},
        {"id": "m5", "title": "Object-Oriented Programming"},
        {"id": "m6", "title": "Algorithms"},
        {"id": "m7", "title": "Advanced Python"},
    ],
}

ZONES = [
    {
        "id": "py-z1",
        "name": "Syntax Meadows",
        "tagline": "Your first steps: store values, make decisions, repeat.",
        "difficulty": "easy",
        "nodes": [
            {"id": "py1", "title": "Variables", "difficulty": "easy", "xp_reward": 50, "estimated_minutes": 10},
            {"id": "py2", "title": "Data Types", "difficulty": "easy", "xp_reward": 50, "estimated_minutes": 10},
            {"id": "py3", "title": "Input & Output", "difficulty": "easy", "xp_reward": 50, "estimated_minutes": 10},
            {"id": "py4", "title": "Conditions", "difficulty": "easy", "xp_reward": 60, "estimated_minutes": 12},
            {"id": "py5", "title": "Loops", "difficulty": "easy", "xp_reward": 70, "estimated_minutes": 15},
        ],
        "boss": {
            "id": "py-z1-boss",
            "name": "Loop Golem",
            "sprite": "slime",
            "challenge": "Solve 3 problems mixing conditions and loops",
            "stages": 3,
            "xp_reward": 250,
        },
    },
    {
        "id": "py-z2",
        "name": "Data Forest",
        "tagline": "Organise data and write reusable, safe code.",
        "difficulty": "medium",
        "nodes": [
            {"id": "py6", "title": "Functions", "difficulty": "medium", "xp_reward": 90, "estimated_minutes": 18},
            {"id": "py7", "title": "Lists", "difficulty": "medium", "xp_reward": 100, "estimated_minutes": 20},
            {"id": "py8", "title": "Tuples & Sets", "difficulty": "medium", "xp_reward": 100, "estimated_minutes": 18},
            {"id": "py9", "title": "Dictionaries", "difficulty": "medium", "xp_reward": 110, "estimated_minutes": 20},
            {
                "id": "py10",
                "title": "String Methods",
                "difficulty": "medium",
                "xp_reward": 100,
                "estimated_minutes": 18,
            },
            {
                "id": "py11",
                "title": "Error Handling",
                "difficulty": "medium",
                "xp_reward": 110,
                "estimated_minutes": 20,
            },
        ],
        "boss": {
            "id": "py-z2-boss",
            "name": "Bug Hydra",
            "sprite": "bugSlime",
            "challenge": "Fix a buggy inventory program before time runs out",
            "stages": 4,
            "xp_reward": 400,
        },
    },
    {
        "id": "py-z3",
        "name": "Algorithm Volcano",
        "tagline": "Think like an engineer: objects, recursion and algorithms.",
        "difficulty": "hard",
        "nodes": [
            {
                "id": "py12",
                "title": "Object-Oriented Programming",
                "difficulty": "hard",
                "xp_reward": 150,
                "estimated_minutes": 30,
            },
            {"id": "py13", "title": "Recursion", "difficulty": "hard", "xp_reward": 160, "estimated_minutes": 30},
            {
                "id": "py14",
                "title": "Sorting Algorithms",
                "difficulty": "hard",
                "xp_reward": 180,
                "estimated_minutes": 35,
            },
            {
                "id": "py15",
                "title": "Searching & Binary Search",
                "difficulty": "hard",
                "xp_reward": 180,
                "estimated_minutes": 30,
            },
            {"id": "py16", "title": "File Handling", "difficulty": "hard", "xp_reward": 150, "estimated_minutes": 25},
        ],
        "boss": {
            "id": "py-z3-boss",
            "name": "Recursion Dragon",
            "sprite": "recursionBoss",
            "challenge": "Survive recursion, sorting and binary-search rounds",
            "stages": 5,
            "xp_reward": 800,
        },
    },
]

LESSONS: list[dict] = [
    {
        "id": "py1",
        "module_id": "m1",
        "title": "Storing Values in Variables",
        "concept": "Variables",
        "explanation": (
            "A variable is a name that points to a value so you can use it later. "
            "You create one with the `=` sign, and you can reassign it at any time. "
            "Python figures out the type for you, so there's no need to declare it."
        ),
        "code_example": """name = "Ada"
age = 36
age = age + 1  # reassign using the old value
print(name, age)  # Ada 37""",
        "code_walkthrough": [
            '`name = "Ada"` creates a variable called `name` holding the text "Ada".',
            "`age = 36` stores the number 36 in `age`.",
            "`age = age + 1` reads the current value (36), adds 1 and stores 37 back in `age`.",
            "`print(name, age)` prints both values separated by a space: `Ada 37`.",
        ],
        "key_points": [
            "Use `=` to assign a value to a name; the right side is evaluated first.",
            "Variables can be reassigned, even to a value of a different type.",
            "Names are case-sensitive and should be descriptive, like `user_age`.",
        ],
        "analogy": (
            "A variable is like a labeled box: the label is the name, and you can "
            "swap out what's inside whenever you like."
        ),
        "quiz": {
            "question": "What does this print?\n\nx = 5\nx = x * 2\nprint(x)",
            "options": ["5", "25", "10", "x"],
            "correct_index": 2,
            "explanation": "`x * 2` uses the current value 5, giving 10, which is stored back in `x`.",
        },
        "try_it": {
            "prompt": 'Create a variable called `city` set to "Paris", then print it.',
            "starter_code": "# create a variable called city\n\n",
            "checks": [
                {
                    "pattern": r"city\s*=\s*[\"']Paris[\"']",
                    "hint": 'Assign the text "Paris" to `city` using `=`.',
                },
                {
                    "pattern": r"print\s*\(\s*city\s*\)",
                    "hint": "Pass the variable to `print()` without quotes: `print(city)`.",
                },
            ],
            "expected_output": "Paris",
        },
    },
    {
        "id": "py2",
        "module_id": "m1",
        "title": "Numbers, Text and True/False",
        "concept": "Data Types",
        "explanation": (
            "Every value in Python has a type that decides what you can do with it. "
            "The basics are `int` (whole numbers), `float` (decimals), `str` (text) and `bool` (True/False). "
            "You can check a type with `type()` and convert between types with functions like `int()` and `str()`."
        ),
        "code_example": """count = 42           # int
price = 9.99         # float
label = "apple"      # str
in_stock = True      # bool
print(type(price))   # <class 'float'>
print(int("7") + 3)  # 10""",
        "code_walkthrough": [
            "`count = 42` is an `int`, a whole number.",
            "`price = 9.99` is a `float` because it has a decimal point.",
            '`label = "apple"` is a `str`; text always goes inside quotes.',
            "`in_stock = True` is a `bool`; note the capital T.",
            "`type(price)` reports the type of a value: `<class 'float'>`.",
            '`int("7")` converts the text "7" into the number 7, so adding 3 gives 10.',
        ],
        "key_points": [
            "The core types are `int`, `float`, `str` and `bool`.",
            "`type()` tells you what type a value is.",
            "Convert types explicitly with `int()`, `float()` and `str()`.",
        ],
        "analogy": (
            "Data types are like containers in a kitchen: you pour soup into a bowl and "
            "slice bread on a board. The container tells you what you can do with what's inside."
        ),
        "quiz": {
            "question": "What is the type of the result of `3 / 2` in Python 3?",
            "options": ["int", "float", "str", "bool"],
            "correct_index": 1,
            "explanation": "The `/` operator always returns a float in Python 3, so `3 / 2` is `1.5`. Use `//` for whole-number division.",
        },
    },
    {
        "id": "py3",
        "module_id": "m1",
        "title": "Talking to the User",
        "concept": "Input & Output",
        "explanation": (
            "`print()` shows output on the screen, and `input()` pauses the program to read what the user types. "
            "`input()` always gives you a string, so convert it with `int()` or `float()` if you need a number. "
            "f-strings (strings starting with `f`) let you drop variables straight into text using `{}`."
        ),
        "code_example": """name = input("What's your name? ")
age = int(input("Age? "))
print(f"Hi {name}, next year you'll be {age + 1}!")
print("a", "b", sep="-")  # a-b""",
        "code_walkthrough": [
            '`input("What\'s your name? ")` shows a prompt and returns whatever the user types as a string.',
            '`int(input("Age? "))` reads text and converts it to a whole number so we can do math with it.',
            "The f-string fills in `{name}` and evaluates `{age + 1}` right inside the text.",
            '`sep="-"` changes the separator `print()` puts between values, giving `a-b`.',
        ],
        "key_points": [
            "`input()` always returns a string.",
            "Wrap `input()` in `int()` or `float()` when you need a number.",
            'f-strings like `f"Hi {name}"` are the easiest way to build output text.',
        ],
        "analogy": (
            "`input()` and `print()` are like a waiter: one takes your order, the other brings out the result."
        ),
        "quiz": {
            "question": "If the user types 25, what type of value does `input()` return?",
            "options": ["str", "int", "float", "It depends on what was typed"],
            "correct_index": 0,
            "explanation": '`input()` always returns a string, here "25". You must convert it with `int()` to do arithmetic.',
        },
        "try_it": {
            "prompt": "Use an f-string to print `Hello, Sam!` using the `name` variable.",
            "starter_code": 'name = "Sam"\n# print the greeting with an f-string\n',
            "checks": [
                {
                    "pattern": r"print\s*\(\s*f[\"']Hello, \{\s*name\s*\}![\"']\s*\)",
                    "hint": 'Try `print(f"Hello, {name}!")`: the `f` goes right before the opening quote.',
                },
            ],
            "expected_output": "Hello, Sam!",
        },
    },
    {
        "id": "py4",
        "module_id": "m2",
        "title": "Making Decisions with if",
        "concept": "Conditions",
        "explanation": (
            "`if` statements let your program choose what to do based on a condition that is True or False. "
            "You can chain extra checks with `elif` and add a fallback with `else`. "
            "Python checks them from top to bottom and runs only the first branch whose condition is True."
        ),
        "code_example": """temp = 28
if temp > 30:
    print("Hot")
elif temp > 20:
    print("Warm")   # Warm
else:
    print("Cool")""",
        "code_walkthrough": [
            "`temp = 28` sets the value we'll test.",
            "`if temp > 30:` is False (28 is not above 30), so its block is skipped.",
            '`elif temp > 20:` is True, so `print("Warm")` runs.',
            "`else:` is skipped because a branch already ran.",
        ],
        "key_points": [
            "Indentation (usually 4 spaces) marks which lines belong to each branch.",
            "Only the first True branch runs; the rest are skipped.",
            "Combine conditions with `and`, `or` and `not`.",
        ],
        "analogy": (
            "It's like choosing clothes: if it's raining, grab an umbrella; else if it's sunny, "
            "wear sunglasses; otherwise, just head out."
        ),
        "quiz": {
            "question": 'What prints when `score = 85`?\n\nif score >= 60:\n    print("Pass")\nelif score >= 80:\n    print("Great")\nelse:\n    print("Fail")',
            "options": ["Great", "Pass and Great", "Fail", "Pass"],
            "correct_index": 3,
            "explanation": '`score >= 60` is checked first and is True, so "Pass" prints and the `elif` is never checked.',
        },
    },
    {
        "id": "py5",
        "module_id": "m2",
        "title": "Repeating Work with Loops",
        "concept": "Loops",
        "explanation": (
            "Loops let you repeat code without copying it. "
            "A `for` loop walks through each item in a sequence, such as `range()` or a list. "
            "A `while` loop keeps going as long as its condition stays True."
        ),
        "code_example": """for i in range(3):
    print(i)        # 0, 1, 2
total = 0
n = 1
while n <= 4:
    total += n
    n += 1
print(total)        # 10""",
        "code_walkthrough": [
            "`for i in range(3):` runs the block with `i` set to 0, 1 and then 2.",
            "`total = 0` and `n = 1` set up the counters for the `while` loop.",
            "`while n <= 4:` keeps looping while `n` is 4 or less.",
            "`total += n` adds `n` to the running total, and `n += 1` moves on so the loop eventually stops.",
            "`print(total)` shows 1 + 2 + 3 + 4 = 10.",
        ],
        "key_points": [
            "`range(stop)` counts from 0 up to, but not including, `stop`.",
            "Use `for` when you know what to loop over, `while` when looping until something changes.",
            "`break` exits a loop early and `continue` skips to the next pass.",
        ],
        "analogy": (
            "A `for` loop is like dealing a card to each player at the table; a `while` loop is "
            "like stirring soup until it boils."
        ),
        "quiz": {
            "question": "Which numbers does `range(2, 6)` produce?",
            "options": ["2, 3, 4, 5, 6", "2, 3, 4, 5", "3, 4, 5, 6", "0, 1, 2, 3, 4, 5"],
            "correct_index": 1,
            "explanation": "`range(start, stop)` includes `start` but stops before `stop`, so it gives 2, 3, 4, 5.",
        },
        "try_it": {
            "prompt": "Use a `for` loop over `range(1, 6)` to add the numbers 1 to 5 into `total`.",
            "starter_code": "total = 0\n# loop here\n\nprint(total)\n",
            "checks": [
                {
                    "pattern": r"for\s+\w+\s+in\s+range\s*\(\s*1\s*,\s*6\s*\)\s*:",
                    "hint": "Start with `for n in range(1, 6):`.",
                },
                {
                    "pattern": r"total\s*(\+=|=\s*total\s*\+)",
                    "hint": "Inside the loop, add the number to the total with `total += n`.",
                },
            ],
            "expected_output": "15",
        },
    },
    {
        "id": "py6",
        "module_id": "m3",
        "title": "Packaging Code into Functions",
        "concept": "Functions",
        "explanation": (
            "A function is a named, reusable block of code that you define with `def`. "
            "It can take inputs (parameters) and send a result back with `return`. "
            "Parameters can have default values, so callers only pass what they need."
        ),
        "code_example": """def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

print(greet("Mia"))            # Hello, Mia!
print(greet("Leo", "Hi"))      # Hi, Leo!""",
        "code_walkthrough": [
            '`def greet(name, greeting="Hello"):` defines a function with two parameters; `greeting` has a default.',
            '`return f"{greeting}, {name}!"` builds a string and sends it back to the caller.',
            '`greet("Mia")` uses the default greeting, giving `Hello, Mia!`.',
            '`greet("Leo", "Hi")` overrides the default, giving `Hi, Leo!`.',
        ],
        "key_points": [
            "Define functions with `def name(params):` and an indented body.",
            "`return` hands a value back; without it, a function returns `None`.",
            "Default parameter values make arguments optional.",
        ],
        "analogy": (
            "A function is like a recipe: write it once, then cook it whenever you want with different ingredients."
        ),
        "quiz": {
            "question": "What does a function return if it has no `return` statement?",
            "options": ["0", "An empty string", "None", "It raises an error"],
            "correct_index": 2,
            "explanation": "Python functions return `None` automatically when they finish without hitting a `return` with a value.",
        },
        "try_it": {
            "prompt": "Define a function `square(n)` that returns `n` multiplied by itself.",
            "starter_code": "# define square(n) here\n\n\nprint(square(4))\n",
            "checks": [
                {
                    "pattern": r"def\s+square\s*\(\s*\w+\s*\)\s*:",
                    "hint": "Start with `def square(n):`.",
                },
                {
                    "pattern": r"return\s+(\w+\s*\*\s*\w+|\w+\s*\*\*\s*2)",
                    "hint": "Return the result, e.g. `return n * n`.",
                },
            ],
            "expected_output": "16",
        },
    },
    {
        "id": "py7",
        "module_id": "m4",
        "title": "Keeping Things in Order with Lists",
        "concept": "Lists",
        "explanation": (
            "A list holds an ordered collection of items inside square brackets. "
            "You access items by position (index), starting at 0, and negative indexes count from the end. "
            "Lists are mutable, so you can add, remove and change items after creating them."
        ),
        "code_example": """fruits = ["apple", "banana"]
fruits.append("cherry")
print(fruits[0])     # apple
print(fruits[-1])    # cherry
print(len(fruits))   # 3
print(fruits[1:])    # ['banana', 'cherry']""",
        "code_walkthrough": [
            '`fruits = ["apple", "banana"]` creates a list with two items.',
            '`fruits.append("cherry")` adds an item to the end.',
            "`fruits[0]` gets the first item and `fruits[-1]` gets the last.",
            "`len(fruits)` counts the items: 3.",
            "`fruits[1:]` slices from index 1 to the end, returning a new list.",
        ],
        "key_points": [
            "Indexes start at 0; `-1` is the last item.",
            "`append()`, `insert()`, `remove()` and `pop()` change a list in place.",
            "Slicing `items[start:stop]` excludes the `stop` index.",
        ],
        "analogy": (
            "A list is like a numbered shopping list: items stay in order, and you can "
            "add or cross off entries whenever you want."
        ),
        "quiz": {
            "question": "Given `nums = [10, 20, 30, 40]`, what is `nums[1:3]`?",
            "options": ["[20, 30]", "[10, 20, 30]", "[20, 30, 40]", "[10, 20]"],
            "correct_index": 0,
            "explanation": "Slicing starts at index 1 (20) and stops before index 3, so you get `[20, 30]`.",
        },
    },
    {
        "id": "py8",
        "module_id": "m4",
        "title": "Fixed Tuples and Unique Sets",
        "concept": "Tuples & Sets",
        "explanation": (
            "A tuple is like a list that can't be changed after it's created, which makes it great for fixed groups such as coordinates. "
            "A set is an unordered collection that automatically removes duplicates. "
            "Sets also support fast membership checks and math-style operations like intersection."
        ),
        "code_example": """point = (3, 4)
x, y = point           # unpacking
print(x + y)           # 7
tags = {"py", "js", "py"}
print(len(tags))       # 2 (duplicates removed)
print({1, 2} & {2, 3}) # {2}""",
        "code_walkthrough": [
            "`point = (3, 4)` creates a tuple with parentheses.",
            "`x, y = point` unpacks the tuple into two variables.",
            '`tags = {"py", "js", "py"}` creates a set; the duplicate "py" is dropped.',
            "`len(tags)` is 2 because a set only keeps unique values.",
            "`&` finds the intersection: items found in both sets.",
        ],
        "key_points": [
            "Tuples are immutable: you can't add, remove or reassign items.",
            "Sets store unique items and have no guaranteed order.",
            "Use `|` for union, `&` for intersection and `-` for difference.",
        ],
        "analogy": (
            "A tuple is like a printed date of birth: fixed forever. A set is like a guest list "
            "where each name only counts once, no matter how often it's written."
        ),
        "quiz": {
            "question": "What happens when you run `t = (1, 2, 3)` and then `t[0] = 10`?",
            "options": [
                "`t` becomes (10, 2, 3)",
                "`t` becomes (10, 1, 2, 3)",
                "Nothing changes and no error occurs",
                "A TypeError is raised",
            ],
            "correct_index": 3,
            "explanation": "Tuples are immutable, so item assignment raises `TypeError: 'tuple' object does not support item assignment`.",
        },
    },
    {
        "id": "py9",
        "module_id": "m4",
        "title": "Looking Things Up with Dictionaries",
        "concept": "Dictionaries",
        "explanation": (
            "A dictionary stores key-value pairs, so you can look up a value by its key instead of a position. "
            "Keys must be unique and are usually strings or numbers. "
            "Use `d[key]` to read or set a value, and `d.get(key, default)` to read safely when a key might be missing."
        ),
        "code_example": """stock = {"apple": 3, "banana": 5}
stock["cherry"] = 5           # add a new key
stock["apple"] += 1
print(stock["apple"])         # 4
print(stock.get("kiwi", 0))   # 0
for fruit, qty in stock.items():
    print(fruit, qty)         # apple 4 / banana 5 / cherry 5""",
        "code_walkthrough": [
            '`stock = {"apple": 3, "banana": 5}` creates a dictionary with two keys.',
            '`stock["cherry"] = 5` adds a new key-value pair.',
            '`stock["apple"] += 1` updates an existing value from 3 to 4.',
            '`stock.get("kiwi", 0)` returns the default 0 because "kiwi" isn\'t a key.',
            "`stock.items()` gives each key and value together so the loop can unpack them.",
        ],
        "key_points": [
            "Dictionaries map unique keys to values.",
            "Assigning to a new key adds it; assigning to an existing key replaces the value.",
            "`d[key]` raises `KeyError` for missing keys, while `d.get(key)` returns `None` or your default.",
        ],
        "analogy": (
            "A dictionary is like a real dictionary or a phone book: you look up a word (key) "
            "to find its definition (value)."
        ),
        "quiz": {
            "question": 'Given `d = {"a": 1}`, what happens when you run `d["b"]`?',
            "options": ["It returns None", "It raises a KeyError", "It returns 0", 'It adds "b" with value None'],
            "correct_index": 1,
            "explanation": 'Reading a missing key with square brackets raises `KeyError`. Use `d.get("b")` to get `None` instead.',
        },
        "try_it": {
            "prompt": 'Add the key "cherry" with the value 4 to the `prices` dictionary.',
            "starter_code": 'prices = {"apple": 2, "banana": 1}\n# add cherry here\n\nprint(prices["cherry"])\n',
            "checks": [
                {
                    "pattern": r"prices\s*\[\s*[\"']cherry[\"']\s*\]\s*=\s*4",
                    "hint": 'Assign to a new key with `prices["cherry"] = 4`.',
                },
            ],
            "expected_output": "4",
        },
    },
    {
        "id": "py10",
        "module_id": "m4",
        "title": "Shaping Text with String Methods",
        "concept": "String Methods",
        "explanation": (
            "Strings come with built-in methods for cleaning, searching and reshaping text. "
            "Strings are immutable, so methods like `upper()` and `replace()` return a new string rather than changing the original. "
            "`split()` breaks text into a list, and `join()` glues a list back into text."
        ),
        "code_example": """msg = "  Hello, World  "
clean = msg.strip()
print(clean.upper())                  # HELLO, WORLD
print(clean.replace("World", "Py"))   # Hello, Py
print(clean.split(", "))              # ['Hello', 'World']
print("-".join(["a", "b", "c"]))      # a-b-c""",
        "code_walkthrough": [
            "`msg.strip()` removes the spaces at the start and end.",
            "`clean.upper()` returns an all-caps copy.",
            '`clean.replace("World", "Py")` swaps one piece of text for another.',
            '`clean.split(", ")` cuts the string at each ", " and returns a list.',
            '`"-".join([...])` joins list items into one string with "-" between them.',
        ],
        "key_points": [
            "String methods return new strings; the original never changes.",
            "`strip()`, `lower()`, `upper()` and `replace()` are everyday cleaning tools.",
            "`split()` turns text into a list and `join()` turns a list into text.",
        ],
        "analogy": (
            "String methods are like photo filters: applying one gives you an edited copy "
            "while the original photo stays untouched."
        ),
        "quiz": {
            "question": 'What does this print?\n\ns = "hi"\ns.upper()\nprint(s)',
            "options": ["HI", "Hi", "hi", "None"],
            "correct_index": 2,
            "explanation": '`upper()` returns a new string, but the result was never saved, so `s` is still "hi". Use `s = s.upper()` to keep it.',
        },
        "try_it": {
            "prompt": "Print the value of `word` in all uppercase letters.",
            "starter_code": 'word = "python"\n# print word in uppercase\n',
            "checks": [
                {
                    "pattern": r"word\s*\.\s*upper\s*\(\s*\)",
                    "hint": "Call the `upper()` method on `word`.",
                },
                {
                    "pattern": r"print\s*\(",
                    "hint": "Wrap the result in `print()` so it shows up.",
                },
            ],
            "expected_output": "PYTHON",
        },
    },
    {
        "id": "py11",
        "module_id": "m7",
        "title": "Handling Errors Gracefully",
        "concept": "Error Handling",
        "explanation": (
            "When something goes wrong, Python raises an exception, which normally crashes the program. "
            "Wrapping risky code in `try` and catching specific exceptions with `except` lets you recover instead. "
            "`else` runs only if no error happened, and `finally` always runs, which is handy for cleanup."
        ),
        "code_example": """try:
    num = int("abc")
except ValueError as err:
    print("Oops:", err)  # Oops: invalid literal for int() with base 10: 'abc'
else:
    print("Converted!")
finally:
    print("Done")        # Done""",
        "code_walkthrough": [
            "`try:` marks the code that might fail.",
            '`int("abc")` can\'t convert letters to a number, so it raises a `ValueError`.',
            "`except ValueError as err:` catches that error and stores it in `err` so we can print a friendly message.",
            "`else:` is skipped because an error occurred.",
            '`finally:` runs no matter what, so "Done" always prints.',
        ],
        "key_points": [
            "Catch specific exceptions (like `ValueError`) instead of using a bare `except:`.",
            "`else` runs only when the `try` block succeeded.",
            "`finally` always runs, whether or not an error happened.",
        ],
        "analogy": (
            "`try`/`except` is like a safety net under a trapeze: if you slip, you land safely and the show goes on."
        ),
        "quiz": {
            "question": "When does a `finally` block run?",
            "options": [
                "Always, whether or not an exception occurred",
                "Only when an exception occurred",
                "Only when no exception occurred",
                "Only if the `except` block re-raises the error",
            ],
            "correct_index": 0,
            "explanation": "`finally` is guaranteed to run after the `try` (and any `except` or `else`), which is why it's used for cleanup.",
        },
        "try_it": {
            "prompt": 'Add an `except` block that catches `ZeroDivisionError` and prints "Cannot divide by zero".',
            "starter_code": "try:\n    result = 10 / 0\n# add an except block here\n",
            "checks": [
                {
                    "pattern": r"except\s+ZeroDivisionError",
                    "hint": "Catch the specific error: `except ZeroDivisionError:`.",
                },
                {
                    "pattern": r"print\s*\(\s*[\"']Cannot divide by zero[\"']\s*\)",
                    "hint": 'Inside the except block, `print("Cannot divide by zero")`.',
                },
            ],
            "expected_output": "Cannot divide by zero",
        },
    },
    {
        "id": "py12",
        "module_id": "m5",
        "title": "Building Your Own Objects with Classes",
        "concept": "Object-Oriented Programming",
        "explanation": (
            "A class is a blueprint for creating objects that bundle data (attributes) and behavior (methods) together. "
            "The special `__init__` method runs when you create an object and sets up its starting attributes. "
            "Every method receives `self`, which refers to the specific object the method was called on."
        ),
        "code_example": """class Dog:
    def __init__(self, name):
        self.name = name
    def speak(self):
        return f"{self.name} says woof!"
rex = Dog("Rex")
print(rex.speak())   # Rex says woof!
print(rex.name)      # Rex""",
        "code_walkthrough": [
            "`class Dog:` defines a new blueprint called `Dog`.",
            "`def __init__(self, name):` is the constructor that runs when a `Dog` is created.",
            "`self.name = name` stores the name on that particular dog.",
            "`def speak(self):` defines a method that uses the object's own `name`.",
            '`rex = Dog("Rex")` creates an instance, and `rex.speak()` calls its method.',
        ],
        "key_points": [
            "A class is a blueprint; an object (instance) is something built from it.",
            "`__init__` sets up each new object's attributes.",
            "`self` is the current object and is the first parameter of every instance method.",
        ],
        "analogy": (
            "A class is like a cookie cutter and objects are the cookies: same shape, "
            "but each cookie can have its own frosting."
        ),
        "quiz": {
            "question": "Inside a method, what does `self` refer to?",
            "options": [
                "The class itself",
                "The parent class",
                "The module the class is defined in",
                "The specific object the method was called on",
            ],
            "correct_index": 3,
            "explanation": "When you call `rex.speak()`, Python passes `rex` as `self`, so the method works with that object's data.",
        },
    },
    {
        "id": "py13",
        "module_id": "m6",
        "title": "Functions That Call Themselves",
        "concept": "Recursion",
        "explanation": (
            "Recursion is when a function solves a problem by calling itself on a smaller version of the same problem. "
            "Every recursive function needs a base case that stops the calls, plus a recursive case that moves toward it. "
            "Without a base case, the calls never end and Python raises a `RecursionError`."
        ),
        "code_example": """def factorial(n):
    if n <= 1:                    # base case
        return 1
    return n * factorial(n - 1)   # recursive case

print(factorial(5))               # 120""",
        "code_walkthrough": [
            "`def factorial(n):` defines the recursive function.",
            "`if n <= 1: return 1` is the base case that stops the recursion.",
            "`return n * factorial(n - 1)` calls itself with a smaller number each time.",
            "`factorial(5)` unwinds as 5 * 4 * 3 * 2 * 1 = 120.",
        ],
        "key_points": [
            "Always define a base case that returns without recursing.",
            "Each recursive call must move closer to the base case.",
            "Python limits recursion depth (about 1000 calls by default).",
        ],
        "analogy": (
            "Recursion is like Russian nesting dolls: you keep opening smaller dolls until "
            "you reach the tiny one that doesn't open (the base case)."
        ),
        "quiz": {
            "question": "What happens if a recursive function has no base case?",
            "options": [
                "It returns None",
                "It keeps calling itself until Python raises a RecursionError",
                "Python automatically adds a base case",
                "It runs exactly once",
            ],
            "correct_index": 1,
            "explanation": "Without a stopping point, calls pile up until the maximum recursion depth is exceeded and Python raises `RecursionError`.",
        },
    },
    {
        "id": "py14",
        "module_id": "m6",
        "title": "Putting Data in Order",
        "concept": "Sorting Algorithms",
        "explanation": (
            "Sorting algorithms arrange items in order, and studying them teaches how to compare and swap data step by step. "
            "Bubble sort repeatedly swaps neighbors that are out of order, which is simple but slow, at O(n^2) comparisons. "
            "In real code, use Python's built-in `sorted()` or `list.sort()`, which run in O(n log n)."
        ),
        "code_example": """def bubble_sort(items):
    for i in range(len(items)):
        for j in range(len(items) - 1 - i):
            if items[j] > items[j + 1]:
                items[j], items[j + 1] = items[j + 1], items[j]
    return items
print(bubble_sort([5, 2, 9, 1]))        # [1, 2, 5, 9]
print(sorted([3, 1, 2], reverse=True))  # [3, 2, 1]""",
        "code_walkthrough": [
            "The outer loop `for i in range(len(items))` makes one pass per item.",
            "The inner loop stops `i` places early because the largest values have already bubbled to the end.",
            "`if items[j] > items[j + 1]:` checks whether two neighbors are out of order.",
            "`items[j], items[j + 1] = items[j + 1], items[j]` swaps them in one line.",
            "`sorted(..., reverse=True)` is the built-in way to sort, here from largest to smallest.",
        ],
        "key_points": [
            "Bubble sort swaps adjacent out-of-order items and takes O(n^2) time.",
            "Faster algorithms like merge sort and Timsort run in O(n log n).",
            "`sorted()` returns a new list; `list.sort()` sorts in place.",
        ],
        "analogy": (
            "Bubble sort is like lining up kids by height by repeatedly swapping any two "
            "neighbors standing in the wrong order until no swaps are needed."
        ),
        "quiz": {
            "question": "What is the worst-case time complexity of bubble sort?",
            "options": ["O(1)", "O(log n)", "O(n^2)", "O(n)"],
            "correct_index": 2,
            "explanation": "Bubble sort uses nested loops over the list, comparing roughly n * n pairs in the worst case, so it is O(n^2).",
        },
    },
    {
        "id": "py15",
        "module_id": "m6",
        "title": "Finding Things Fast with Binary Search",
        "concept": "Searching & Binary Search",
        "explanation": (
            "Linear search checks items one by one, which takes O(n) time. "
            "Binary search is much faster, O(log n), but only works on sorted data: it checks the middle item and throws away the half that can't contain the target. "
            "It keeps halving the search range until it finds the item or the range is empty."
        ),
        "code_example": """def binary_search(items, target):
    low, high = 0, len(items) - 1
    while low <= high:
        mid = (low + high) // 2
        if items[mid] == target: return mid
        if items[mid] < target: low = mid + 1
        else: high = mid - 1
    return -1
print(binary_search([1, 3, 5, 7, 9], 7))  # 3""",
        "code_walkthrough": [
            "`low, high = 0, len(items) - 1` sets the search range to the whole list.",
            "`while low <= high:` keeps searching while the range isn't empty.",
            "`mid = (low + high) // 2` picks the middle index using whole-number division.",
            "If the middle value is too small, `low = mid + 1` searches the right half; otherwise `high = mid - 1` searches the left.",
            "`return -1` signals the target wasn't found; here 7 is found at index 3.",
        ],
        "key_points": [
            "Binary search requires the data to be sorted first.",
            "Each step halves the search space, giving O(log n) time.",
            "Python's `bisect` module provides ready-made binary search helpers.",
        ],
        "analogy": (
            "It's like finding a word in a paper dictionary: open to the middle, decide which "
            "half the word is in, and repeat."
        ),
        "quiz": {
            "question": "What must be true about a list before you can use binary search on it?",
            "options": [
                "It must be sorted",
                "It must contain only unique values",
                "It must have an even number of items",
                "It must contain only integers",
            ],
            "correct_index": 0,
            "explanation": "Binary search decides which half to discard by comparing with the middle value, which only works if the list is sorted.",
        },
    },
    {
        "id": "py16",
        "module_id": "m7",
        "title": "Reading and Writing Files",
        "concept": "File Handling",
        "explanation": (
            "`open()` gives you a file object you can read from or write to, depending on the mode. "
            'Use `"r"` to read, `"w"` to write (which erases existing content) and `"a"` to append. '
            "The `with` statement closes the file automatically, even if an error occurs."
        ),
        "code_example": r"""with open("notes.txt", "w") as f:
    f.write("Buy milk\n")
    f.write("Call mom\n")
with open("notes.txt") as f:
    for line in f:
        print(line.strip())  # Buy milk / Call mom""",
        "code_walkthrough": [
            '`open("notes.txt", "w")` opens the file for writing, creating it if needed.',
            '`f.write("Buy milk\\n")` writes text; `\\n` adds a line break.',
            "Leaving the `with` block closes the file automatically.",
            '`open("notes.txt")` defaults to read mode `"r"`.',
            "`for line in f:` reads one line at a time, and `strip()` removes the trailing newline.",
        ],
        "key_points": [
            "Always prefer `with open(...) as f:` so files close automatically.",
            'Mode `"w"` overwrites, `"a"` appends and `"r"` reads.',
            "Looping over a file object reads it line by line, which saves memory.",
        ],
        "analogy": (
            "A file is like a notebook: open it, read or write a few pages, and close it "
            "when you're done. `with` is the friend who always closes it for you."
        ),
        "quiz": {
            "question": "Which mode adds text to the end of an existing file without erasing it?",
            "options": ['"r"', '"w"', '"x"', '"a"'],
            "correct_index": 3,
            "explanation": '`"a"` (append) writes to the end of the file. `"w"` would wipe the existing content first.',
        },
    },
]
