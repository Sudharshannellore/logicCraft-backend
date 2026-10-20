"""C# Foundations: Build real C# skills on modern .NET, from your first variable to LINQ and async code."""

COURSE = {
    "id": "csharp-foundations",
    "title": "C# Foundations",
    "world": "Sharpholm Kingdom",
    "description": "Build real C# skills on modern .NET, from your first variable to LINQ and async code.",
    "language": "csharp",
    "modules": [
        {"id": "cs-m1", "title": "Core Syntax"},
        {"id": "cs-m2", "title": "Methods & Objects"},
        {"id": "cs-m3", "title": "Collections, LINQ & Async"},
    ],
}

ZONES = [
    {
        "id": "cs-z1",
        "name": "Semicolon Shire",
        "tagline": "Values, text and the flow of a program.",
        "difficulty": "easy",
        "nodes": [
            {"id": "cs1", "title": "Variables & Types", "difficulty": "easy", "xp_reward": 50, "estimated_minutes": 10},
            {
                "id": "cs2",
                "title": "Strings & Interpolation",
                "difficulty": "easy",
                "xp_reward": 50,
                "estimated_minutes": 10,
            },
            {
                "id": "cs3",
                "title": "Conditionals & switch",
                "difficulty": "easy",
                "xp_reward": 55,
                "estimated_minutes": 11,
            },
            {"id": "cs4", "title": "Loops", "difficulty": "easy", "xp_reward": 60, "estimated_minutes": 12},
        ],
        "boss": {
            "id": "cs-z1-boss",
            "name": "Missing Semicolon Slime",
            "sprite": "slime",
            "challenge": "Fix 3 snippets that refuse to compile",
            "stages": 3,
            "xp_reward": 250,
        },
    },
    {
        "id": "cs-z2",
        "name": "Object Forge",
        "tagline": "Methods, collections and the classes that tie them together.",
        "difficulty": "medium",
        "nodes": [
            {"id": "cs5", "title": "Methods", "difficulty": "medium", "xp_reward": 90, "estimated_minutes": 18},
            {
                "id": "cs6",
                "title": "Arrays & List<T>",
                "difficulty": "medium",
                "xp_reward": 100,
                "estimated_minutes": 18,
            },
            {
                "id": "cs7",
                "title": "Classes & Properties",
                "difficulty": "medium",
                "xp_reward": 100,
                "estimated_minutes": 20,
            },
            {
                "id": "cs8",
                "title": "Interfaces & Inheritance",
                "difficulty": "medium",
                "xp_reward": 110,
                "estimated_minutes": 20,
            },
        ],
        "boss": {
            "id": "cs-z2-boss",
            "name": "Inheritance Hydra",
            "sprite": "bugSlime",
            "challenge": "Repair a tangled class hierarchy, one head at a time",
            "stages": 4,
            "xp_reward": 400,
        },
    },
    {
        "id": "cs-z3",
        "name": "LINQ Labyrinth",
        "tagline": "Query your data, survive errors and go async.",
        "difficulty": "hard",
        "nodes": [
            {
                "id": "cs9",
                "title": "Dictionary & Generics",
                "difficulty": "hard",
                "xp_reward": 140,
                "estimated_minutes": 25,
            },
            {"id": "cs10", "title": "LINQ", "difficulty": "hard", "xp_reward": 150, "estimated_minutes": 28},
            {"id": "cs11", "title": "Exceptions", "difficulty": "hard", "xp_reward": 140, "estimated_minutes": 25},
            {"id": "cs12", "title": "async / await", "difficulty": "hard", "xp_reward": 160, "estimated_minutes": 30},
        ],
        "boss": {
            "id": "cs-z3-boss",
            "name": "Deadlock Dragon",
            "sprite": "recursionBoss",
            "challenge": "Predict the output of LINQ queries and async code, round by round",
            "stages": 5,
            "xp_reward": 700,
        },
    },
]

LESSONS: list[dict] = [
    {
        "id": "cs1",
        "module_id": "cs-m1",
        "title": "Storing Values in Typed Variables",
        "concept": "Variables & Types",
        "explanation": (
            "C# is statically typed: every variable has a type such as `int`, `double`, `bool` or `string`, "
            "and the compiler checks that you only store matching values in it. "
            "With `var` the compiler infers the type from the value you assign, but the type is still fixed after that."
        ),
        "code_example": """int lives = 3;
double speed = 2.5;
bool isHero = true;
string name = "Pixel";
var coins = 100;                     // compiler infers int
lives = lives - 1;
Console.WriteLine(name);             // Pixel
Console.WriteLine(lives);            // 2
Console.WriteLine(isHero);           // True
Console.WriteLine(speed * 2);        // 5
Console.WriteLine(coins.GetType());  // System.Int32
Console.WriteLine(7 / 2);            // 3 (integer division)""",
        "code_walkthrough": [
            "`int`, `double`, `bool` and `string` declare variables for whole numbers, decimals, true/false and text.",
            "`var coins = 100;` lets the compiler infer the type `int` from the value.",
            "`lives = lives - 1;` changes the value, so `lives` is now 2.",
            "`Console.WriteLine(isHero)` prints `True`: C# writes booleans with a capital letter.",
            "`coins.GetType()` reveals the real .NET type behind `int`: `System.Int32`.",
            "`7 / 2` divides two integers, so the result is `3`, not 3.5.",
        ],
        "key_points": [
            "Every variable has a type that can't change after it's declared.",
            "`var` is still strongly typed; the compiler just works the type out for you.",
            "Use `double` (or `decimal` for money) when you need fractions; `int / int` drops them.",
        ],
        "analogy": (
            "Typed variables are like labeled storage bins: the bin marked `int` only accepts whole numbers, "
            "and the compiler is the strict warehouse manager who checks every delivery."
        ),
        "quiz": {
            "question": 'What happens when you compile `var level = 1; level = "two";`?',
            "options": [
                'level becomes "two"',
                "A compile error, because level is an int",
                "An exception is thrown when the program runs",
                "level becomes 2",
            ],
            "correct_index": 1,
            "explanation": "`var` infers `int` from `1`, and a variable's type can't change, so assigning a string is a compile-time error.",
        },
    },
    {
        "id": "cs2",
        "module_id": "cs-m1",
        "title": "Building Text with String Interpolation",
        "concept": "String Interpolation",
        "explanation": (
            "A `string` holds text, and putting `$` in front of a string literal lets you drop values straight in with `{braces}`. "
            "Strings come with handy members such as `Length`, `ToUpper()`, `Contains()` and `Replace()`. "
            "Strings are immutable, so methods like `Replace()` return a new string instead of changing the original."
        ),
        "code_example": """string hero = "Ada";
int level = 7;
string msg = $"{hero} reached level {level}!";
Console.WriteLine(msg);                        // Ada reached level 7!
Console.WriteLine(msg.Length);                 // 20
Console.WriteLine(hero.ToUpper());             // ADA
Console.WriteLine(msg.Contains("level"));      // True
Console.WriteLine($"Next: {level + 1}");       // Next: 8
Console.WriteLine(msg.Replace("Ada", "Max"));  // Max reached level 7!""",
        "code_walkthrough": [
            '`$"{hero} reached level {level}!"` is an interpolated string: each `{...}` is replaced by its value.',
            "`msg.Length` counts every character, including spaces and the `!`: 20.",
            '`hero.ToUpper()` returns a new uppercase string, "ADA".',
            '`msg.Contains("level")` returns `true`, which prints as `True`.',
            "`{level + 1}` shows you can put any expression inside the braces.",
            '`msg.Replace("Ada", "Max")` returns a new string; `msg` itself is unchanged.',
        ],
        "key_points": [
            "Prefix a string with `$` to use `{expression}` placeholders.",
            "String methods return new strings because strings are immutable.",
            "`Length` is a property (no parentheses); `ToUpper()` is a method (with parentheses).",
        ],
        "analogy": (
            "An interpolated string is like a fill-in-the-blanks form: the `{}` slots are blanks, "
            "and C# writes the current values into them when the line runs."
        ),
        "quiz": {
            "question": "With `int a = 10, b = 5;`, which line prints `Score: 15`?",
            "options": [
                'Console.WriteLine("Score: {a + b}");',
                'Console.WriteLine("Score: " + a + b);',
                "Console.WriteLine('Score: ' + (a + b));",
                'Console.WriteLine($"Score: {a + b}");',
            ],
            "correct_index": 3,
            "explanation": (
                'Only the `$` string evaluates `{a + b}`. Without `$` the braces print literally, `"Score: " + a + b` '
                'builds "Score: 105" from left to right, and single quotes are for a single `char`, so that line won\'t compile.'
            ),
        },
        "try_it": {
            "prompt": "Use string interpolation with `name` and `gems` to print `Hi, Sam! You have 3 gems.`",
            "starter_code": (
                'string name = "Sam";\nint gems = 3;\n// Print: Hi, Sam! You have 3 gems.\nConsole.WriteLine("");\n'
            ),
            "checks": [
                {
                    "pattern": r'(\$@?|@\$)"[^"]*\{\s*name\s*\}',
                    "hint": 'Start the string with `$` and put `{name}` inside it: `$"Hi, {name}! ..."`.',
                },
                {
                    "pattern": r'(\$@?|@\$)"[^"]*\{\s*gems\s*\}',
                    "hint": "Insert the gem count with `{gems}` inside the same `$` string.",
                },
            ],
            "expected_output": "Hi, Sam! You have 3 gems.",
        },
    },
    {
        "id": "cs3",
        "module_id": "cs-m1",
        "title": "Making Decisions with if and switch",
        "concept": "Switch Expressions",
        "explanation": (
            "`if`, `else if` and `else` run different code depending on a `bool` condition. "
            "A switch expression (`value switch { ... }`) picks a result by matching the value against patterns, top to bottom, "
            "and `_` is the catch-all. "
            "For a quick either/or value, the ternary operator `condition ? a : b` keeps it to one line."
        ),
        "code_example": """int hp = 35;
if (hp > 50)
    Console.WriteLine("Healthy");
else if (hp > 20)
    Console.WriteLine("Hurt");                   // Hurt
else
    Console.WriteLine("Critical");
string rank = hp switch
{
    >= 90 => "S",
    >= 50 => "A",
    _ => "B",
};
Console.WriteLine(rank);                         // B
Console.WriteLine(hp > 20 ? "Fight!" : "Run!");  // Fight!""",
        "code_walkthrough": [
            "`if (hp > 50)` is false for 35, so C# checks the next condition.",
            '`else if (hp > 20)` is true, so "Hurt" is printed and the `else` is skipped.',
            "`hp switch { ... }` tries each arm in order: `>= 90` and `>= 50` don't match 35.",
            '`_ => "B"` is the discard pattern that matches anything left, so `rank` is "B".',
            '`hp > 20 ? "Fight!" : "Run!"` picks "Fight!" because the condition is true.',
        ],
        "key_points": [
            "Conditions must be real `bool` values; C# won't treat `0` or `null` as false.",
            "Switch expressions return a value and check their arms from top to bottom.",
            "Finish a switch expression with `_` so every possible value is handled.",
        ],
        "analogy": (
            "A switch expression is like a sorting hat: the value walks past each rule in turn "
            "and is placed by the first one that fits."
        ),
        "quiz": {
            "question": "What does the `_` arm do in a switch expression?",
            "options": [
                "Matches any value that no earlier arm matched",
                "Matches only null",
                "Throws an exception",
                "Skips the switch and returns the original value",
            ],
            "correct_index": 0,
            "explanation": "`_` is the discard pattern. It matches everything, so placed last it acts as the default case.",
        },
    },
    {
        "id": "cs4",
        "module_id": "cs-m1",
        "title": "Repeating Work with for, foreach and while",
        "concept": "Loops",
        "explanation": (
            "A `for` loop repeats with a counter that has a start, a condition and a step. "
            "`foreach` walks through every item of an array or list without needing an index. "
            "A `while` loop keeps going as long as its condition is true, so make sure something changes each time."
        ),
        "code_example": """for (int i = 1; i <= 3; i++)
{
    Console.WriteLine($"Wave {i}");  // Wave 1, Wave 2, Wave 3
}
string[] loot = ["sword", "shield"];
foreach (string item in loot)
{
    Console.WriteLine(item);         // sword, shield
}
int energy = 10;
while (energy > 3)
{
    energy -= 4;
}
Console.WriteLine(energy);           // 2""",
        "code_walkthrough": [
            "`int i = 1` starts the counter, `i <= 3` is checked before each pass, and `i++` runs after each pass.",
            "The `for` loop prints Wave 1, Wave 2 and Wave 3 on separate lines.",
            '`string[] loot = ["sword", "shield"];` creates an array with a C# 12 collection expression.',
            "`foreach (string item in loot)` hands you each item in turn.",
            "The `while` loop subtracts 4 from 10, then from 6, and stops when `energy` is 2.",
        ],
        "key_points": [
            "Use `for` when you need the index or a fixed number of repeats.",
            "Use `foreach` to visit every item in a collection.",
            "A `while` loop whose condition never becomes false runs forever.",
        ],
        "analogy": (
            "A `for` loop is like running laps with a lap counter; `foreach` is like handing a flyer "
            "to every person in a queue; `while` is like eating chips until the bag is empty."
        ),
        "quiz": {
            "question": "How many times does the body of `for (int i = 0; i < 4; i++)` run?",
            "options": ["3", "5", "4", "It runs forever"],
            "correct_index": 2,
            "explanation": "`i` takes the values 0, 1, 2 and 3. When `i` reaches 4 the condition `i < 4` is false, so the body runs 4 times.",
        },
        "try_it": {
            "prompt": "Write a `for` loop that counts from 1 to 5 and adds each number to `total`.",
            "starter_code": (
                "int total = 0;\n// Loop from 1 to 5 and add each number to total\n\nConsole.WriteLine(total);\n"
            ),
            "checks": [
                {
                    "pattern": r"for\s*\(\s*(int|var)\s+\w+\s*=\s*1\s*;",
                    "hint": "Start a `for` loop at 1: `for (int i = 1; ...)`.",
                },
                {
                    "pattern": r"<=\s*5\b|<\s*6\b",
                    "hint": "Keep looping while the counter is `<= 5`.",
                },
                {
                    "pattern": r"total\s*\+=|total\s*=\s*total\s*\+",
                    "hint": "Add the counter to the running sum with `total += i;`.",
                },
            ],
            "expected_output": "15",
        },
    },
    {
        "id": "cs5",
        "module_id": "cs-m2",
        "title": "Packaging Logic into Methods",
        "concept": "Methods",
        "explanation": (
            "A method is a named block of code with typed parameters and a return type (`void` when it returns nothing). "
            "Short methods can use the `=>` expression-bodied syntax, and parameters can have default values. "
            "With top-level statements you can declare methods below the code that calls them."
        ),
        "code_example": """Console.WriteLine(Add(2, 3));               // 5
Console.WriteLine(Greet("Ada"));            // Hello, Ada!
Console.WriteLine(Greet());                 // Hello, traveler!
Console.WriteLine(Damage(10, crit: true));  // 20

static int Add(int a, int b)
{
    return a + b;
}
static string Greet(string name = "traveler") => $"Hello, {name}!";
static int Damage(int hit, bool crit = false) => crit ? hit * 2 : hit;""",
        "code_walkthrough": [
            "`static int Add(int a, int b)` takes two `int` parameters and promises to return an `int`.",
            "`return a + b;` sends the result back to the caller, so `Add(2, 3)` is 5.",
            '`string name = "traveler"` is a default value, used when `Greet()` is called without an argument.',
            "`=>` gives a one-line method body whose expression is the return value.",
            "`Damage(10, crit: true)` uses a named argument, which makes the call easy to read: 20.",
        ],
        "key_points": [
            "Every parameter and return value has a type; use `void` when nothing is returned.",
            "Default parameters make arguments optional, and named arguments make calls clearer.",
            "Keep methods small and focused on one job.",
        ],
        "analogy": (
            "A method is like a recipe card: give it the ingredients (arguments) and it always "
            "follows the same steps to hand back a dish (the return value)."
        ),
        "quiz": {
            "question": "What does a `void` return type mean?",
            "options": [
                "The method returns null",
                "The method doesn't return a value",
                "The method can return any type",
                "The method can't take parameters",
            ],
            "correct_index": 1,
            "explanation": "`void` means the method does its work without handing a value back, so you can't use its call as a value.",
        },
    },
    {
        "id": "cs6",
        "module_id": "cs-m2",
        "title": "Collecting Items in Arrays and Lists",
        "concept": "List<T>",
        "explanation": (
            "An array (`int[]`) holds a fixed number of items of one type, accessed by a zero-based index. "
            "A `List<T>` works like an array that can grow and shrink, with methods such as `Add`, `Remove` and `Contains`. "
            "Arrays report their size with `Length`, while lists use `Count`."
        ),
        "code_example": """int[] scores = [90, 75, 60];
Console.WriteLine(scores[0]);                 // 90
Console.WriteLine(scores.Length);             // 3

List<string> party = ["Ada", "Linus"];
party.Add("Grace");
party.Remove("Linus");
Console.WriteLine(party.Count);               // 2
Console.WriteLine(string.Join(", ", party));  // Ada, Grace
Console.WriteLine(party.Contains("Grace"));   // True""",
        "code_walkthrough": [
            "`int[] scores = [90, 75, 60];` creates an array of three `int` values.",
            "`scores[0]` reads the first item, because indexes start at 0.",
            '`List<string> party = ["Ada", "Linus"];` creates a list that only holds strings.',
            '`party.Add("Grace")` appends to the end and `party.Remove("Linus")` deletes the first match.',
            '`string.Join(", ", party)` glues the items into one string for printing.',
        ],
        "key_points": [
            "Indexes start at 0, and reading past the end throws an exception.",
            "Use an array for a fixed size and a `List<T>` when the size changes.",
            "The `<T>` means the list holds one specific type, like `List<string>`.",
        ],
        "analogy": (
            "An array is like an egg carton with a fixed number of slots; a `List<T>` is like a "
            "backpack that stretches as you add more loot."
        ),
        "quiz": {
            "question": "With `int[] scores = [90, 75, 60];`, what happens when you read `scores[3]`?",
            "options": [
                "An IndexOutOfRangeException is thrown",
                "It returns 0",
                "It returns 60",
                "It returns null",
            ],
            "correct_index": 0,
            "explanation": "The valid indexes are 0, 1 and 2. Reading index 3 is outside the array, so .NET throws an IndexOutOfRangeException.",
        },
        "try_it": {
            "prompt": 'Add "Potion" to the `bag` list, then print how many items it holds.',
            "starter_code": (
                'List<string> bag = ["Sword", "Shield"];\n'
                '// Add "Potion" to bag\n'
                "\n"
                "Console.WriteLine(/* item count */);\n"
            ),
            "checks": [
                {
                    "pattern": r'bag\s*\.\s*Add\s*\(\s*"Potion"\s*\)',
                    "hint": 'Call `bag.Add("Potion");`.',
                },
                {
                    "pattern": r"bag\s*\.\s*Count\b",
                    "hint": "Lists report their size with `bag.Count`.",
                },
            ],
            "expected_output": "3",
        },
    },
    {
        "id": "cs7",
        "module_id": "cs-m2",
        "title": "Designing Your Own Types with Classes",
        "concept": "Classes & Properties",
        "explanation": (
            "A class is a blueprint that bundles data (properties) and behavior (methods), and `new` creates an object from it. "
            "Properties use `get` and `set` accessors to control who can read or change a value. "
            "A constructor runs when the object is created and sets up its starting state."
        ),
        "code_example": """var hero = new Hero("Ada");
hero.TakeDamage(30);
Console.WriteLine($"{hero.Name}: {hero.Health} HP");  // Ada: 70 HP
Console.WriteLine(hero.IsAlive);                      // True

class Hero
{
    public string Name { get; }
    public int Health { get; private set; } = 100;
    public bool IsAlive => Health > 0;

    public Hero(string name) => Name = name;

    public void TakeDamage(int amount) => Health -= amount;
}""",
        "code_walkthrough": [
            '`new Hero("Ada")` calls the constructor, which stores "Ada" in `Name`.',
            "`public string Name { get; }` is read-only: it can only be set in the constructor.",
            "`{ get; private set; } = 100` lets anyone read `Health` but only the class change it, starting at 100.",
            "`IsAlive => Health > 0` is a computed property that's worked out each time you read it.",
            "`TakeDamage(30)` lowers `Health` from 100 to 70.",
        ],
        "key_points": [
            "A class is the blueprint; each object made with `new` is a separate instance.",
            "Expose data through properties and keep setters private when outside code shouldn't change them.",
            "In a top-level program, class declarations go after the top-level statements.",
        ],
        "analogy": (
            "A class is like a character template in a game editor, and each object is a character "
            "spawned from it with its own name and health bar."
        ),
        "quiz": {
            "question": "What does `public int Health { get; private set; }` mean?",
            "options": [
                "Nobody can read or change Health",
                "Anyone can read and change Health",
                "Health can only be set once, by an object initializer",
                "Anyone can read Health, but only code inside the class can change it",
            ],
            "correct_index": 3,
            "explanation": "The `get` accessor is public, while `private set` restricts writing to code inside the class itself.",
        },
    },
    {
        "id": "cs8",
        "module_id": "cs-m2",
        "title": "Sharing Behavior with Interfaces and Inheritance",
        "concept": "Interfaces & Inheritance",
        "explanation": (
            "An interface is a contract that lists members a class promises to provide, and a class can implement many interfaces. "
            "Inheritance (`class Paladin : Knight`) lets a class reuse and extend a single base class. "
            "A base method marked `virtual` can be replaced in a derived class with `override`, and `base` calls the original version."
        ),
        "code_example": """IAttacker[] squad = [new Knight(), new Paladin()];
foreach (IAttacker unit in squad)
    Console.WriteLine(unit.Attack());
// Sword slash!
// Sword slash! + Holy light!

interface IAttacker { string Attack(); }
class Knight : IAttacker
{
    public virtual string Attack() => "Sword slash!";
}
class Paladin : Knight
{
    public override string Attack() => base.Attack() + " + Holy light!";
}""",
        "code_walkthrough": [
            "`interface IAttacker { string Attack(); }` declares a contract with one method.",
            "`class Knight : IAttacker` implements the interface and marks `Attack` as `virtual`.",
            "`class Paladin : Knight` inherits from `Knight`, so it's also an `IAttacker`.",
            "`override` replaces the method, and `base.Attack()` reuses the Knight's version.",
            "The loop calls `Attack()` through the interface, and each object runs its own version.",
        ],
        "key_points": [
            "A class can inherit from one base class but implement many interfaces.",
            "Mark a method `virtual` in the base class and `override` it in derived classes.",
            "Code written against an interface works with any class that implements it.",
        ],
        "analogy": (
            "An interface is like a job description that lists the skills required; inheritance is like "
            "a family recipe that each generation can follow as-is or tweak."
        ),
        "quiz": {
            "question": "How many base classes and interfaces can a single C# class have?",
            "options": [
                "Many base classes and many interfaces",
                "One base class and one interface",
                "One base class and any number of interfaces",
                "No base classes, only interfaces",
            ],
            "correct_index": 2,
            "explanation": "C# allows single inheritance for classes, but a class can implement as many interfaces as it needs.",
        },
    },
    {
        "id": "cs9",
        "module_id": "cs-m3",
        "title": "Key-Value Lookups and Generic Types",
        "concept": "Dictionary & Generics",
        "explanation": (
            "A `Dictionary<TKey, TValue>` stores values by a unique key, so you can look them up quickly by name or ID. "
            "Use `TryGetValue` or `ContainsKey` when a key might be missing, because reading a missing key with `[]` throws. "
            "Generics like `<TKey, TValue>` and `<T>` let one class or method work with many types while staying type-safe."
        ),
        "code_example": """Dictionary<string, int> stock = new()
{
    ["potion"] = 3,
    ["ether"] = 1,
};
stock["potion"] += 2;
Console.WriteLine(stock["potion"]);            // 5
Console.WriteLine(stock.ContainsKey("bomb"));  // False
if (stock.TryGetValue("ether", out int count))
    Console.WriteLine($"ether x{count}");      // ether x1
Console.WriteLine(Describe(42));               // Int32: 42
Console.WriteLine(Describe("hi"));             // String: hi

static string Describe<T>(T value) => $"{typeof(T).Name}: {value}";""",
        "code_walkthrough": [
            "`Dictionary<string, int>` maps string keys to int values, filled with an index initializer.",
            '`stock["potion"] += 2;` reads the value for "potion", adds 2 and stores 5.',
            '`ContainsKey("bomb")` safely checks for a key and returns `False`.',
            "`TryGetValue` returns `true` and puts the value in `count` only if the key exists.",
            "`Describe<T>` is a generic method: `T` becomes `int` (Int32) or `string` (String) based on the argument.",
        ],
        "key_points": [
            "Each key in a dictionary is unique; assigning to an existing key overwrites its value.",
            "Prefer `TryGetValue` over `[]` when a key might not exist.",
            "Generics give you reusable, type-safe code without casting.",
        ],
        "analogy": (
            "A dictionary is like a coat check: you hand over a ticket (the key) and instantly get "
            "back the right coat (the value)."
        ),
        "quiz": {
            "question": 'What happens when you read `stock["bomb"]` and "bomb" is not a key in the dictionary?',
            "options": [
                "A KeyNotFoundException is thrown",
                "It returns 0",
                "It returns null",
                'The key "bomb" is added with the value 0',
            ],
            "correct_index": 0,
            "explanation": "The `[]` indexer throws KeyNotFoundException for a missing key. Use `TryGetValue` to look up safely.",
        },
    },
    {
        "id": "cs10",
        "module_id": "cs-m3",
        "title": "Querying Collections with LINQ",
        "concept": "LINQ",
        "explanation": (
            "LINQ (Language Integrated Query) adds methods like `Where`, `Select`, `OrderBy`, `Count` and `Sum` to any collection. "
            "You pass small lambda functions such as `s => s >= 60` to describe what to keep or how to transform each item. "
            "Queries like `Where` and `Select` run lazily, only when you loop over or consume the results."
        ),
        "code_example": """int[] scores = [42, 88, 15, 97, 63];
var high = scores.Where(s => s >= 60).OrderByDescending(s => s);
Console.WriteLine(string.Join(", ", high));    // 97, 88, 63
Console.WriteLine(scores.Max());               // 97
Console.WriteLine(scores.Count(s => s < 50));  // 2
Console.WriteLine(scores.Sum());               // 305
var labels = scores.Select(s => $"#{s}").Take(2);
Console.WriteLine(string.Join(" ", labels));   // #42 #88""",
        "code_walkthrough": [
            "`Where(s => s >= 60)` keeps only the scores of 60 or more.",
            "`OrderByDescending(s => s)` sorts the kept scores from highest to lowest: 97, 88, 63.",
            "`Max()` and `Sum()` boil the whole array down to a single number.",
            "`Count(s => s < 50)` counts the items that pass the test: 42 and 15.",
            '`Select(s => $"#{s}")` transforms each score into a label, and `Take(2)` keeps the first two.',
        ],
        "key_points": [
            "`Where` filters, `Select` transforms and `OrderBy` sorts.",
            "LINQ never changes the original collection; it produces new results.",
            "Call `ToList()` or `ToArray()` when you want to run a query once and keep the results.",
        ],
        "analogy": (
            "LINQ is like a conveyor belt of machines: one sieve removes items you don't want, "
            "the next paints them, and the last one stacks them in order."
        ),
        "quiz": {
            "question": "What does `new[] { 1, 2, 3, 4 }.Where(n => n % 2 == 0).Select(n => n * 10)` produce?",
            "options": ["10, 30", "20, 40", "10, 20, 30, 40", "60"],
            "correct_index": 1,
            "explanation": "`Where` keeps the even numbers 2 and 4, then `Select` multiplies each by 10, giving 20 and 40.",
        },
        "try_it": {
            "prompt": "Use LINQ's `Where` to keep only the names longer than 3 letters.",
            "starter_code": (
                'string[] names = ["Ada", "Grace", "Linus", "Bo"];\n'
                "var longNames = names; // filter me\n"
                "\n"
                'Console.WriteLine(string.Join(", ", longNames));\n'
            ),
            "checks": [
                {
                    "pattern": r"names\s*\.\s*Where\s*\(",
                    "hint": "Call `names.Where(...)` with a lambda.",
                },
                {
                    "pattern": r"\.\s*Length\s*(>\s*3|>=\s*4)\b",
                    "hint": "Test each name with `n => n.Length > 3`.",
                },
            ],
            "expected_output": "Grace, Linus",
        },
    },
    {
        "id": "cs11",
        "module_id": "cs-m3",
        "title": "Handling Errors with try, catch and finally",
        "concept": "Exceptions",
        "explanation": (
            "When something goes wrong at runtime, .NET throws an exception that stops normal flow until it's caught. "
            "Put risky code in a `try` block, handle specific exception types in `catch`, and put cleanup in `finally`, which always runs. "
            'You can raise your own errors with `throw new SomeException("message")`.'
        ),
        "code_example": """int gold = 50, price = 80;
try
{
    if (price > gold) throw new InvalidOperationException("Not enough gold");
    Console.WriteLine("Bought the sword");      // skipped
}
catch (InvalidOperationException ex)
{
    Console.WriteLine($"Error: {ex.Message}");  // Error: Not enough gold
}
finally
{
    Console.WriteLine("Shop closed");           // Shop closed
}""",
        "code_walkthrough": [
            "The code inside `try` runs normally until something throws.",
            '`throw new InvalidOperationException("Not enough gold")` fires because 80 > 50, so "Bought the sword" is skipped.',
            "`catch (InvalidOperationException ex)` matches that exception type and reads its `Message`.",
            '`finally` runs afterwards no matter what, so "Shop closed" is always printed.',
        ],
        "key_points": [
            "Catch specific exception types rather than catching every `Exception`.",
            "`finally` is for cleanup that must always happen.",
            "For expected problems like bad user input, prefer checks such as `int.TryParse` over exceptions.",
        ],
        "analogy": (
            "Exceptions are like a fire alarm: normal work stops, everyone heads to the nearest "
            "`catch` assembly point, and `finally` is the sweep-up that always happens afterwards."
        ),
        "quiz": {
            "question": "When does a `finally` block run?",
            "options": [
                "Only when an exception is thrown",
                "Only when no exception is thrown",
                "Only if the catch block rethrows the exception",
                "Whether or not an exception was thrown",
            ],
            "correct_index": 3,
            "explanation": "`finally` runs after the `try` (and any `catch`) in both the success and the error case, which makes it ideal for cleanup.",
        },
    },
    {
        "id": "cs12",
        "module_id": "cs-m3",
        "title": "Waiting Without Blocking: async and await",
        "concept": "async / await",
        "explanation": (
            "Slow operations such as web requests, file reads or timers return a `Task` (or `Task<T>` for a result). "
            "Inside an `async` method, `await` pauses that method until the task finishes, freeing the thread to do other work meanwhile. "
            "`Task.WhenAll` starts several tasks together and waits for all of them."
        ),
        "code_example": """Console.WriteLine("Loading...");           // Loading...
string map = await LoadMapAsync("Forest");
Console.WriteLine(map);                     // Forest loaded
Task<int> a = GetScoreAsync(10);
Task<int> b = GetScoreAsync(20);
int[] results = await Task.WhenAll(a, b);
Console.WriteLine(results.Sum());           // 30

static async Task<string> LoadMapAsync(string name)
{
    await Task.Delay(500);                  // waits without blocking a thread
    return $"{name} loaded";
}
static async Task<int> GetScoreAsync(int points) { await Task.Delay(100); return points; }""",
        "code_walkthrough": [
            "Top-level statements can use `await` directly, so no special `Main` method is needed.",
            '`await LoadMapAsync("Forest")` pauses until the task completes, then gives back its `string` result.',
            "`async Task<string>` means the method runs asynchronously and eventually produces a `string`.",
            "`await Task.Delay(500)` waits half a second without tying up a thread.",
            "`GetScoreAsync(10)` and `GetScoreAsync(20)` start right away and run at the same time.",
            "`await Task.WhenAll(a, b)` waits for both and returns their results as an array: 10 + 20 = 30.",
        ],
        "key_points": [
            "Async methods return `Task` or `Task<T>`, and their names end in `Async` by convention.",
            "`await` pauses the method, not the whole program.",
            "Avoid `.Result` and `.Wait()`, which block the thread; use `await` all the way up.",
        ],
        "analogy": (
            "`await` is like ordering at a busy cafe and getting a buzzer: instead of standing at the "
            "counter, you go do other things until the buzzer tells you your order is ready."
        ),
        "quiz": {
            "question": "What does `await` do when the task it's waiting on hasn't finished yet?",
            "options": [
                "Blocks the thread until the task finishes",
                "Cancels the task",
                "Pauses the method and frees the thread until the task completes",
                "Restarts the task on a new thread",
            ],
            "correct_index": 2,
            "explanation": "`await` suspends only the current method and returns control to the caller, so the thread can do other work until the task is done.",
        },
    },
]
