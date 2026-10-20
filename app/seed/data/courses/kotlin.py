"""Kotlin Essentials: Learn modern, concise and null-safe Kotlin, from first variables to coroutines."""

COURSE = {
    "id": "kotlin-essentials",
    "title": "Kotlin Essentials",
    "world": "Kotlin Island",
    "description": "Learn modern, concise and null-safe Kotlin, from your first variables to coroutines.",
    "language": "kotlin",
    "modules": [
        {"id": "kt-m1", "title": "Kotlin Basics"},
        {"id": "kt-m2", "title": "Functions, Nulls & Data"},
        {"id": "kt-m3", "title": "Functional & Async Kotlin"},
    ],
}

ZONES = [
    {
        "id": "kt-z1",
        "name": "Val Valley",
        "tagline": "Values, strings and the flow of a Kotlin program.",
        "difficulty": "easy",
        "nodes": [
            {"id": "kt1", "title": "val, var & Types", "difficulty": "easy", "xp_reward": 50, "estimated_minutes": 10},
            {"id": "kt2", "title": "String Templates", "difficulty": "easy", "xp_reward": 50, "estimated_minutes": 10},
            {
                "id": "kt3",
                "title": "if & when Expressions",
                "difficulty": "easy",
                "xp_reward": 60,
                "estimated_minutes": 12,
            },
            {"id": "kt4", "title": "Loops & Ranges", "difficulty": "easy", "xp_reward": 60, "estimated_minutes": 12},
        ],
        "boss": {
            "id": "kt-z1-boss",
            "name": "Var Slime",
            "sprite": "slime",
            "challenge": "Fix 3 snippets that mix up val, var, templates and ranges",
            "stages": 3,
            "xp_reward": 250,
        },
    },
    {
        "id": "kt-z2",
        "name": "Safe-Call Swamp",
        "tagline": "Functions, null safety and the data you carry.",
        "difficulty": "medium",
        "nodes": [
            {
                "id": "kt5",
                "title": "Functions & Default Arguments",
                "difficulty": "medium",
                "xp_reward": 90,
                "estimated_minutes": 18,
            },
            {"id": "kt6", "title": "Null Safety", "difficulty": "medium", "xp_reward": 100, "estimated_minutes": 18},
            {
                "id": "kt7",
                "title": "Collections: List & Map",
                "difficulty": "medium",
                "xp_reward": 100,
                "estimated_minutes": 20,
            },
            {
                "id": "kt8",
                "title": "Classes & Data Classes",
                "difficulty": "medium",
                "xp_reward": 110,
                "estimated_minutes": 20,
            },
        ],
        "boss": {
            "id": "kt-z2-boss",
            "name": "NullPointer Ghoul",
            "sprite": "bugSlime",
            "challenge": "Banish every possible null crash using ?., ?: and smart casts",
            "stages": 4,
            "xp_reward": 400,
        },
    },
    {
        "id": "kt-z3",
        "name": "Coroutine Citadel",
        "tagline": "Lambdas, clever types and code that waits without blocking.",
        "difficulty": "hard",
        "nodes": [
            {
                "id": "kt9",
                "title": "Lambdas & Higher-Order Functions",
                "difficulty": "hard",
                "xp_reward": 140,
                "estimated_minutes": 25,
            },
            {
                "id": "kt10",
                "title": "Extension Functions",
                "difficulty": "hard",
                "xp_reward": 150,
                "estimated_minutes": 25,
            },
            {"id": "kt11", "title": "Sealed Classes", "difficulty": "hard", "xp_reward": 150, "estimated_minutes": 28},
            {"id": "kt12", "title": "Coroutines", "difficulty": "hard", "xp_reward": 160, "estimated_minutes": 30},
        ],
        "boss": {
            "id": "kt-z3-boss",
            "name": "Suspend Sorcerer",
            "sprite": "recursionBoss",
            "challenge": "Predict the print order of launching, delaying and awaiting coroutines",
            "stages": 5,
            "xp_reward": 700,
        },
    },
]

LESSONS: list[dict] = [
    {
        "id": "kt1",
        "module_id": "kt-m1",
        "title": "Storing Values with val and var",
        "concept": "Variables and types",
        "explanation": (
            "Kotlin declares read-only variables with `val` (can't be reassigned) and mutable ones with `var`. "
            "Every value has a type such as `Int`, `Double`, `String` or `Boolean`, and Kotlin usually infers it for you. "
            "You can also write the type explicitly after a colon, like `val lives: Int = 3`."
        ),
        "code_example": """fun main() {
    val name = "Ada"          // read-only, inferred as String
    var score = 10            // mutable, inferred as Int
    score += 5
    val lives: Int = 3        // explicit type
    val isReady = true        // Boolean
    println(name)             // Ada
    println(score)            // 15
    println(lives * 2)        // 6
    println(isReady)          // true
}""",
        "code_walkthrough": [
            "`fun main()` is the entry point where every Kotlin program starts.",
            '`val name = "Ada"` creates a read-only variable; Kotlin infers the type `String`.',
            "`var score = 10` creates a variable that can change, so `score += 5` makes it 15.",
            "`val lives: Int = 3` spells out the type explicitly after a colon.",
            "`println(...)` prints each value on its own line.",
        ],
        "key_points": [
            "Prefer `val`; use `var` only when the value really needs to change.",
            "Kotlin infers types, but you can always write them after a colon.",
            "A variable's type is fixed: an `Int` variable can never hold a `String`.",
        ],
        "analogy": (
            "A `val` is like a name carved into a stone tablet, while a `var` is a name "
            "written on a whiteboard that you can wipe and rewrite."
        ),
        "quiz": {
            "question": "What happens with this code?\n\nval x = 10\nx = 20",
            "options": [
                "x becomes 20",
                "It doesn't compile: a val cannot be reassigned",
                "x stays 10 silently",
                "It crashes at runtime",
            ],
            "correct_index": 1,
            "explanation": 'A `val` can be assigned only once, so the compiler rejects `x = 20` with "Val cannot be reassigned".',
        },
    },
    {
        "id": "kt2",
        "module_id": "kt-m1",
        "title": "Building Text with String Templates",
        "concept": "String templates",
        "explanation": (
            "String templates let you drop values straight into a string with `$name`. "
            "For anything more than a plain variable, such as math or a property, wrap it in curly braces: `${level + 1}`. "
            "This is cleaner and less error-prone than gluing strings together with `+`."
        ),
        "code_example": """fun main() {
    val hero = "Kira"
    val level = 7
    val coins = 120
    println("$hero is level $level")          // Kira is level 7
    println("Next level: ${level + 1}")       // Next level: 8
    println("Name has ${hero.length} letters") // Name has 4 letters
    println("$hero has ${coins / 2} gold left") // Kira has 60 gold left
}""",
        "code_walkthrough": [
            "`$hero` and `$level` insert the variables' values into the string.",
            "`${level + 1}` evaluates the expression inside the braces, giving 8.",
            '`${hero.length}` reads a property, so it needs braces: "Kira" has 4 letters.',
            "`${coins / 2}` divides 120 by 2 and inserts 60.",
        ],
        "key_points": [
            "Use `$name` for simple variables.",
            "Use `${...}` for expressions, function calls and properties.",
            "Write `\\$` when you need a literal dollar sign in a string.",
        ],
        "analogy": (
            "A string template is like a fill-in-the-blanks card: the `$` marks the blanks, "
            "and Kotlin fills them in when the line runs."
        ),
        "quiz": {
            "question": 'What does `println("Sum: ${2 + 3}")` print?',
            "options": ["Sum: ${2 + 3}", "Sum: 2 + 3", "Sum: 23", "Sum: 5"],
            "correct_index": 3,
            "explanation": "Everything inside `${...}` is evaluated as code, so `2 + 3` becomes 5 before it is inserted.",
        },
        "try_it": {
            "prompt": "Use a string template to print `Kira has 3 lives` using the variables `name` and `lives`.",
            "starter_code": 'fun main() {\n    val name = "Kira"\n    val lives = 3\n    // print: Kira has 3 lives\n}\n',
            "checks": [
                {
                    "pattern": r"println\s*\(\s*\"",
                    "hint": "Call `println` with a string.",
                },
                {
                    "pattern": r"\$\{?\s*name\b",
                    "hint": "Insert the name with `$name`.",
                },
                {
                    "pattern": r"\$\{?\s*lives\b",
                    "hint": "Insert the number of lives with `$lives`.",
                },
            ],
            "expected_output": "Kira has 3 lives",
        },
    },
    {
        "id": "kt3",
        "module_id": "kt-m1",
        "title": "Making Decisions with if and when",
        "concept": "if and when expressions",
        "explanation": (
            'In Kotlin, `if` is an expression, so it can return a value directly: `val status = if (hp > 50) "healthy" else "hurt"`. '
            "`when` is Kotlin's more powerful replacement for `switch`, matching a value against several branches. "
            "When you use `when` as an expression, it usually needs an `else` branch so every case has a result."
        ),
        "code_example": """fun main() {
    val hp = 35
    val status = if (hp > 50) "healthy" else "hurt"
    println(status)                        // hurt
    val rank = when {
        hp >= 90 -> "S"
        hp >= 30 -> "B"
        else -> "D"
    }
    println(rank)                          // B
    when (rank) {
        "S", "A" -> println("Top tier!")
        else -> println("Keep training")   // Keep training
    }
}""",
        "code_walkthrough": [
            '`if (hp > 50) "healthy" else "hurt"` returns a value, so it can be assigned to `status`.',
            "`when { ... }` with no argument checks each condition from top to bottom and picks the first true one.",
            '`hp >= 30` is the first true condition for 35, so `rank` is "B".',
            '`when (rank)` compares `rank` to each branch; `"S", "A"` matches either value.',
            "`else` catches everything that no other branch matched.",
        ],
        "key_points": [
            "`if` and `when` are expressions that can return values.",
            "Kotlin has no ternary `? :` operator; use `if`/`else` instead.",
            "`when` branches can list several values separated by commas.",
        ],
        "analogy": (
            "`when` is like a sorting hat: it looks at the value, checks each house in order, "
            "and sends it to the first one that fits."
        ),
        "quiz": {
            "question": 'What does this print?\n\nval n = 0\nval sign = when {\n    n > 0 -> "positive"\n    n < 0 -> "negative"\n    else -> "zero"\n}\nprintln(sign)',
            "options": ["positive", "negative", "zero", "Nothing; it doesn't compile"],
            "correct_index": 2,
            "explanation": 'Neither `n > 0` nor `n < 0` is true for 0, so the `else` branch supplies "zero".',
        },
    },
    {
        "id": "kt4",
        "module_id": "kt-m1",
        "title": "Repeating Work with Loops and Ranges",
        "concept": "Loops and ranges",
        "explanation": (
            "Kotlin's `for` loop walks through anything iterable, like a range or a list. "
            "Ranges describe a run of numbers: `1..3` includes the end, `0 until 3` (or `0..<3`) stops before it, and `downTo` counts backwards. "
            "A `while` loop repeats as long as its condition stays true."
        ),
        "code_example": """fun main() {
    for (i in 1..3) println("Wave $i")   // Wave 1, Wave 2, Wave 3
    for (i in 0 until 6 step 2) print(i) // 024
    println()
    for (i in 3 downTo 1) print(i)       // 321
    println()
    val loot = listOf("gem", "key")
    for ((index, item) in loot.withIndex()) {
        println("$index: $item")         // 0: gem, then 1: key
    }
    var shield = 3
    while (shield > 0) shield--
    println("Shield: $shield")           // Shield: 0
}""",
        "code_walkthrough": [
            "`1..3` is an inclusive range, so the loop prints Wave 1, Wave 2 and Wave 3 on separate lines.",
            "`0 until 6 step 2` gives 0, 2 and 4; `print` writes them on one line without spaces.",
            "`3 downTo 1` counts backwards: 3, 2, 1.",
            "`loot.withIndex()` gives each item with its position, unpacked into `(index, item)`.",
            "`while (shield > 0) shield--` keeps subtracting 1 until `shield` reaches 0.",
        ],
        "key_points": [
            "`a..b` includes `b`; `a until b` and `a..<b` stop just before `b`.",
            "`downTo` counts down and `step` changes the jump size.",
            "Loop straight over a list with `for (item in list)`; no index needed.",
        ],
        "analogy": (
            "A range is like a staircase: `1..3` means climb from step 1 up to and including step 3, "
            "while `until` means stop just before the last step."
        ),
        "quiz": {
            "question": "Which numbers does `for (i in 1 until 4)` loop over?",
            "options": ["1, 2, 3", "1, 2, 3, 4", "0, 1, 2, 3", "4, 3, 2, 1"],
            "correct_index": 0,
            "explanation": "`until` excludes the end value, so the range stops at 3. Use `1..4` to include 4.",
        },
        "try_it": {
            "prompt": "Write a `for` loop over a range that prints the numbers 1 to 5, one per line.",
            "starter_code": "fun main() {\n    // loop from 1 to 5 here\n}\n",
            "checks": [
                {
                    "pattern": r"for\s*\(\s*\w+\s+in\s+1\s*(\.\.\s*5|\.\.<\s*6|until\s+6)\s*\)",
                    "hint": "Loop with `for (i in 1..5)`.",
                },
                {
                    "pattern": r"println\s*\(",
                    "hint": "Print each number with `println`.",
                },
            ],
            "expected_output": "1\n2\n3\n4\n5",
        },
    },
    {
        "id": "kt5",
        "module_id": "kt-m2",
        "title": "Functions with Default and Named Arguments",
        "concept": "Default arguments",
        "explanation": (
            "Functions are declared with `fun`, list their parameters with types, and put the return type after the parentheses. "
            "Parameters can have default values, so callers can skip them, and named arguments let you pass values in any order. "
            "A function whose body is a single expression can use `=` instead of curly braces and a `return`."
        ),
        "code_example": """fun greet(name: String, greeting: String = "Hello"): String {
    return "$greeting, $name!"
}

fun area(width: Int, height: Int = width) = width * height

fun main() {
    println(greet("Kira"))                         // Hello, Kira!
    println(greet("Kira", "Welcome back"))         // Welcome back, Kira!
    println(greet(greeting = "Hey", name = "Max")) // Hey, Max!
    println(area(4))                               // 16
    println(area(4, 2))                            // 8
}""",
        "code_walkthrough": [
            '`greeting: String = "Hello"` gives the parameter a default, used when the caller leaves it out.',
            "`: String` after the parentheses declares the return type.",
            "`fun area(...) = width * height` is a single-expression function; Kotlin infers that it returns `Int`.",
            "`height: Int = width` defaults to an earlier parameter, so `area(4)` is a 4 by 4 square: 16.",
            '`greet(greeting = "Hey", name = "Max")` uses named arguments, so the order doesn\'t matter.',
        ],
        "key_points": [
            "Default values replace most of the overloaded functions you'd write in Java.",
            "Named arguments make calls with many parameters easy to read.",
            "Use `=` for short single-expression functions.",
        ],
        "analogy": (
            "Default arguments are like a coffee order that comes with regular milk unless you "
            "ask for oat milk by name."
        ),
        "quiz": {
            "question": 'What does this print?\n\nfun tag(text: String, sep: String = "-") = "$sep$text$sep"\nprintln(tag("hi", sep = "*"))',
            "options": ["-hi-", "*hi*", "hi*", "A compile error"],
            "correct_index": 1,
            "explanation": 'The named argument `sep = "*"` replaces the default "-", so the text is wrapped in stars.',
        },
    },
    {
        "id": "kt6",
        "module_id": "kt-m2",
        "title": "Taming null with Null Safety",
        "concept": "Null safety",
        "explanation": (
            "In Kotlin, a normal type like `String` can never be null; only a nullable type like `String?` can. "
            "The compiler makes you handle the null case, using the safe call `?.` (returns null instead of crashing) and the Elvis operator `?:` (supplies a fallback). "
            "After you check `if (x != null)`, Kotlin smart-casts `x` to the non-null type for you."
        ),
        "code_example": """fun describe(name: String?) {
    println(name?.length)        // safe call: null if name is null
    println(name ?: "Guest")     // Elvis: fallback when name is null
    if (name != null) println(name.uppercase()) // smart cast to String
}

fun main() {
    describe("Zed")
    // 3
    // Zed
    // ZED
    describe(null)
    // null
    // Guest
}""",
        "code_walkthrough": [
            "`name: String?` means the parameter may hold a string or `null`.",
            "`name?.length` returns the length, or `null` when `name` is null, instead of crashing.",
            '`name ?: "Guest"` uses "Guest" only when `name` is null.',
            "Inside `if (name != null)`, Kotlin knows `name` is a `String`, so `name.uppercase()` is allowed.",
            '`describe(null)` prints `null` and "Guest", and skips the uppercase line.',
        ],
        "key_points": [
            "Add `?` to a type to allow null; plain types are always non-null.",
            "`?.` safely calls through a nullable value; `?:` provides a default.",
            "Avoid `!!`: it throws a NullPointerException if the value is null.",
        ],
        "analogy": (
            "A nullable type is like a gift box that might be empty: `?.` peeks inside safely, "
            "and `?:` hands you a backup gift when the box is empty."
        ),
        "quiz": {
            "question": "What is `len` here?\n\nval name: String? = null\nval len = name?.length ?: 0",
            "options": ["null", "A NullPointerException is thrown", "A compile error", "0"],
            "correct_index": 3,
            "explanation": "`name?.length` is null because `name` is null, so the Elvis operator falls back to 0.",
        },
        "try_it": {
            "prompt": "Print the length of `nickname`, or 0 if it is null, using a safe call `?.` and the Elvis operator `?:`.",
            "starter_code": "fun main() {\n    val nickname: String? = null\n    // print nickname's length, or 0 if it's null\n}\n",
            "checks": [
                {
                    "pattern": r"nickname\s*\?\.\s*length",
                    "hint": "Use `nickname?.length` to read the length safely.",
                },
                {
                    "pattern": r"\?:\s*0\b",
                    "hint": "Add `?: 0` to fall back to 0.",
                },
                {
                    "pattern": r"println\s*\(",
                    "hint": "Print the result with `println`.",
                },
            ],
            "expected_output": "0",
        },
    },
    {
        "id": "kt7",
        "module_id": "kt-m2",
        "title": "Grouping Data in Lists and Maps",
        "concept": "Kotlin collections",
        "explanation": (
            "A `List` holds items in order and a `Map` stores values under keys. "
            "`listOf` and `mapOf` create read-only collections, while `mutableListOf` and `mutableMapOf` create ones you can change. "
            "You read items with square brackets: `list[0]` or `map[key]`, which returns null for a missing key."
        ),
        "code_example": """fun main() {
    val heroes = listOf("Kira", "Max", "Zed")
    println(heroes[0])                 // Kira
    println(heroes.size)               // 3
    val party = mutableListOf("Kira")
    party.add("Max")
    println(party)                     // [Kira, Max]
    val scores = mapOf("Kira" to 120, "Max" to 95)
    println(scores["Max"])             // 95
    println(scores["Zed"])             // null
    val inventory = mutableMapOf("potion" to 2)
    inventory["potion"] = 3
    inventory["key"] = 1
    println(inventory)                 // {potion=3, key=1}
}""",
        "code_walkthrough": [
            "`listOf(...)` creates a read-only list; `heroes[0]` reads the first item.",
            '`mutableListOf("Kira")` can grow, so `party.add("Max")` works.',
            '`"Kira" to 120` builds a key-value pair for `mapOf`.',
            '`scores["Zed"]` returns `null` because that key doesn\'t exist.',
            "`inventory[...] = ...` updates or adds an entry, and printing a map shows `{key=value}` pairs.",
        ],
        "key_points": [
            "Read-only collections (`listOf`, `mapOf`) have no `add` or `put`.",
            "Use `mutableListOf` and `mutableMapOf` when contents need to change.",
            "Map lookups with `map[key]` return a nullable value.",
        ],
        "analogy": (
            "A list is like a numbered line of treasure chests, and a map is like a key ring "
            "where each labeled key opens one chest."
        ),
        "quiz": {
            "question": "What happens with this code?\n\nval ids = listOf(1, 2)\nids.add(3)",
            "options": [
                "ids becomes [1, 2, 3]",
                "It throws an exception at runtime",
                "A compile error, because a read-only List has no add",
                "ids stays [1, 2] silently",
            ],
            "correct_index": 2,
            "explanation": "`listOf` returns a read-only `List`, which has no `add` function. Use `mutableListOf` to add items.",
        },
    },
    {
        "id": "kt8",
        "module_id": "kt-m2",
        "title": "Modeling Things with Classes and Data Classes",
        "concept": "Data classes",
        "explanation": (
            "A class bundles data (properties) and behavior (functions), and its primary constructor sits right in the class header. "
            "Marking a class `data` makes Kotlin generate `toString`, `equals`, `hashCode` and `copy` for you. "
            "Data classes are ideal for simple value holders like API responses or game items."
        ),
        "code_example": """class Hero(val name: String, var hp: Int = 100) {
    fun takeHit(damage: Int) { hp -= damage }
}

data class Item(val name: String, val power: Int)

fun main() {
    val hero = Hero("Kira")
    hero.takeHit(30)
    println("${hero.name} has ${hero.hp} HP")  // Kira has 70 HP
    val sword = Item("Sword", 10)
    println(sword)                             // Item(name=Sword, power=10)
    println(sword == Item("Sword", 10))        // true
    println(sword.copy(power = 15))            // Item(name=Sword, power=15)
}""",
        "code_walkthrough": [
            "`class Hero(val name: String, var hp: Int = 100)` declares properties right in the constructor.",
            "`takeHit(30)` lowers `hp` from 100 to 70.",
            "`data class Item(...)` gets a readable `toString`, so printing it shows `Item(name=Sword, power=10)`.",
            "`==` on data classes compares property values, so two equal swords are `true`.",
            "`copy(power = 15)` makes a new item with one property changed.",
        ],
        "key_points": [
            "Properties declared with `val`/`var` in the constructor become class members.",
            "`data class` generates `toString`, `equals`, `hashCode`, `copy` and `componentN`.",
            "Plain classes print as something like `Hero@1b6d3586`; data classes print their values.",
        ],
        "analogy": (
            "A class is like a character sheet template, and a data class is a template that "
            "also comes with a built-in photocopier and comparison tool."
        ),
        "quiz": {
            "question": "Given `data class Point(val x: Int, val y: Int)`, what does `println(Point(1, 2))` print?",
            "options": ["Point(x=1, y=2)", "Point@1b6d3586", "(1, 2)", "{x=1, y=2}"],
            "correct_index": 0,
            "explanation": "Data classes generate a `toString` that shows the class name and each property as `name=value`.",
        },
    },
    {
        "id": "kt9",
        "module_id": "kt-m3",
        "title": "Passing Code Around with Lambdas",
        "concept": "Higher-order functions",
        "explanation": (
            "A lambda is a small function you can store in a variable or pass as an argument, written in braces like `{ n: Int -> n * 2 }`. "
            "A higher-order function takes another function as a parameter (or returns one), like `filter` and `map`. "
            "If a lambda has one parameter you can call it `it`, and if it's the last argument it can go outside the parentheses."
        ),
        "code_example": """fun applyTwice(x: Int, action: (Int) -> Int): Int = action(action(x))

fun main() {
    val double = { n: Int -> n * 2 }
    println(double(5))                      // 10
    println(applyTwice(3, double))          // 12
    println(applyTwice(3) { it + 10 })      // 23
    val coins = listOf(5, 12, 8, 20)
    println(coins.filter { it > 7 })        // [12, 8, 20]
    println(coins.map { it * 10 })          // [50, 120, 80, 200]
    println(coins.fold(0) { acc, c -> acc + c }) // 45
}""",
        "code_walkthrough": [
            "`action: (Int) -> Int` is a function type: it takes an `Int` and returns an `Int`.",
            "`{ n: Int -> n * 2 }` is a lambda stored in `double`; `applyTwice(3, double)` doubles twice: 12.",
            "`applyTwice(3) { it + 10 }` uses trailing lambda syntax and the implicit `it`: 3 + 10 + 10 = 23.",
            "`filter { it > 7 }` keeps 12, 8 and 20; `map { it * 10 }` multiplies each coin.",
            "`fold(0) { acc, c -> acc + c }` starts at 0 and adds every coin, giving 45.",
        ],
        "key_points": [
            "Lambdas are written in braces: parameters, then `->`, then the body.",
            "Use `it` for a lambda's single parameter.",
            "A trailing lambda can move outside the call's parentheses.",
        ],
        "analogy": (
            "A higher-order function is like a kitchen appliance with swappable blades: the "
            "machine stays the same, and the lambda you plug in decides what it does."
        ),
        "quiz": {
            "question": "In `names.map { it.length }`, what is `it`?",
            "options": [
                "The whole list",
                "The index of the current item",
                "The value returned by map",
                "The current element, the lambda's single parameter",
            ],
            "correct_index": 3,
            "explanation": "When a lambda has exactly one parameter, Kotlin names it `it`. Here it is each name in turn.",
        },
        "try_it": {
            "prompt": "Use `filter` with a lambda to keep only the even numbers from `nums`.",
            "starter_code": "fun main() {\n    val nums = listOf(1, 2, 3, 4, 5, 6)\n    val evens = nums // keep only even numbers\n    println(evens)\n}\n",
            "checks": [
                {
                    "pattern": r"nums\s*\.\s*filter\s*[({]",
                    "hint": "Call `nums.filter { ... }` with a lambda.",
                },
                {
                    "pattern": r"%\s*2\s*==\s*0",
                    "hint": "A number is even when `it % 2 == 0`.",
                },
            ],
            "expected_output": "[2, 4, 6]",
        },
    },
    {
        "id": "kt10",
        "module_id": "kt-m3",
        "title": "Teaching Old Types New Tricks with Extensions",
        "concept": "Extension functions",
        "explanation": (
            "Extension functions let you add new functions to an existing type, even one you didn't write, like `String` or `Int`. "
            "Inside the extension, `this` refers to the value it was called on, and you can often leave `this` out. "
            "Extensions don't actually change the class; they're resolved at compile time and can only use its public members."
        ),
        "code_example": """fun String.shout(): String = uppercase() + "!"

fun Int.isEven(): Boolean = this % 2 == 0

val String.vowelCount: Int
    get() = count { it in "aeiou" }

fun main() {
    println("level up".shout())     // LEVEL UP!
    println(7.isEven())             // false
    println(42.isEven())            // true
    println("adventure".vowelCount) // 4
}""",
        "code_walkthrough": [
            "`fun String.shout()` adds a `shout` function to every `String`.",
            '`uppercase()` is called on the receiver, so "level up" becomes "LEVEL UP!".',
            "`this % 2 == 0` inside `Int.isEven()` uses `this` for the number itself.",
            "`val String.vowelCount` is an extension property with a custom getter.",
            '`count { it in "aeiou" }` counts a, e, u and e in "adventure": 4.',
        ],
        "key_points": [
            "Declare an extension as `fun Type.name()`.",
            "`this` inside an extension is the receiver object.",
            "Extensions can't access private members and don't modify the original class.",
        ],
        "analogy": (
            "An extension function is like a phone case with a built-in stand: you add a new "
            "feature without opening up the phone itself."
        ),
        "quiz": {
            "question": "Which statement about extension functions is true?",
            "options": [
                "They can read the class's private properties",
                "They add behavior without modifying the original class",
                "They only work on classes you wrote yourself",
                "They must be declared inside the class",
            ],
            "correct_index": 1,
            "explanation": "Extensions are resolved statically and live outside the class, so they add behavior without changing it or seeing its private members.",
        },
    },
    {
        "id": "kt11",
        "module_id": "kt-m3",
        "title": "Closed Families of Types with Sealed Classes",
        "concept": "Sealed classes",
        "explanation": (
            "A sealed class (or sealed interface) defines a fixed set of subtypes that must be declared in the same module and package. "
            "Because the compiler knows every possible subtype, a `when` over a sealed type can be exhaustive without an `else` branch. "
            "Sealed classes are perfect for modeling states and results, like loading, success and error."
        ),
        "code_example": """sealed class Quest
data class Won(val xp: Int) : Quest()
data class Lost(val reason: String) : Quest()
data object InProgress : Quest()

fun report(q: Quest): String = when (q) {  // no else needed
    is Won -> "Victory! +${q.xp} XP"
    is Lost -> "Defeat: ${q.reason}"
    InProgress -> "Still fighting..."
}
fun main() {
    println(report(Won(150)))           // Victory! +150 XP
    println(report(Lost("out of HP")))  // Defeat: out of HP
    println(report(InProgress))         // Still fighting...
}""",
        "code_walkthrough": [
            "`sealed class Quest` declares a closed family of types.",
            "`Won`, `Lost` and `InProgress` are the only subtypes; `data object` is a single instance with a readable name.",
            "`when (q)` covers every subtype, so the compiler doesn't require an `else`.",
            "`is Won ->` smart-casts `q` to `Won`, so `q.xp` is available in that branch.",
            "If you add a new subtype later, the compiler flags every `when` that doesn't handle it.",
        ],
        "key_points": [
            "Sealed types restrict which subclasses can exist.",
            "`when` over a sealed type is checked for exhaustiveness at compile time.",
            "Use `data object` (Kotlin 1.9+) for subtypes that carry no data.",
        ],
        "analogy": (
            "A sealed class is like a traffic light: it can only ever be red, yellow or green, "
            "so you can plan for every case with nothing left over."
        ),
        "quiz": {
            "question": "Why can a `when` over a sealed class skip the `else` branch?",
            "options": [
                "Because sealed classes can't be used in when",
                "Because else is never allowed in Kotlin",
                "Because the compiler knows every possible subtype",
                "Because missing cases simply return null",
            ],
            "correct_index": 2,
            "explanation": "All subtypes of a sealed class are known at compile time, so the compiler can verify that every case is handled.",
        },
    },
    {
        "id": "kt12",
        "module_id": "kt-m3",
        "title": "Doing Many Things at Once with Coroutines",
        "concept": "Kotlin coroutines",
        "explanation": (
            "Coroutines let you write asynchronous code that reads top to bottom, using the kotlinx-coroutines library. "
            "`launch` starts a coroutine that runs alongside your code, `async` starts one that returns a result you `await`, and `delay` pauses a coroutine without blocking its thread. "
            "`runBlocking` bridges normal code and coroutines, which is handy in `main` and in tests."
        ),
        "code_example": """// Needs the kotlinx-coroutines-core library
import kotlinx.coroutines.*

fun main() = runBlocking {
    val job = launch {
        delay(100)
        println("Loot collected!")      // 3) Loot collected!
    }
    val gold = async { delay(50); 42 }
    println("Exploring...")             // 1) Exploring...
    println("Found ${gold.await()} gold") // 2) Found 42 gold
    job.join()
    println("Quest complete")           // 4) Quest complete
}""",
        "code_walkthrough": [
            "`runBlocking { ... }` starts a coroutine scope and waits for everything inside it to finish.",
            '`launch { ... }` and `async { ... }` start coroutines that run while `main` keeps going, so "Exploring..." prints first.',
            "`gold.await()` suspends until the `async` block finishes after 50 ms and returns 42.",
            "`delay(100)` suspends the launched coroutine without blocking the thread, so it prints third.",
            '`job.join()` waits for the launched coroutine before printing "Quest complete".',
        ],
        "key_points": [
            "`launch` is fire-and-forget; `async` returns a `Deferred` you `await`.",
            "`delay` suspends a coroutine; it doesn't block the thread like `Thread.sleep`.",
            "Coroutines need the `kotlinx-coroutines-core` dependency.",
        ],
        "analogy": (
            "Coroutines are like a chef juggling dishes: while the soup simmers (`delay`), the chef "
            "chops vegetables instead of standing and staring at the pot."
        ),
        "quiz": {
            "question": "What does `delay(1000)` do inside a coroutine?",
            "options": [
                "Suspends that coroutine for 1 second while the thread does other work",
                "Blocks the whole thread for 1 second",
                "Cancels the coroutine after 1 second",
                "Starts a new thread that sleeps for 1 second",
            ],
            "correct_index": 0,
            "explanation": "`delay` is a suspending function: it pauses only the current coroutine, leaving the thread free to run other coroutines.",
        },
    },
]
