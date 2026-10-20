"""Swift Essentials: Learn modern Swift, the language behind iPhone, iPad and Mac apps."""

COURSE = {
    "id": "swift-essentials",
    "title": "Swift Essentials",
    "world": "Swiftwing Isles",
    "description": "Learn modern Swift, the safe and fast language behind iPhone, iPad and Mac apps.",
    "language": "swift",
    "modules": [
        {"id": "sw-m1", "title": "Swift Basics"},
        {"id": "sw-m2", "title": "Functions & Data"},
        {"id": "sw-m3", "title": "Modeling with Types"},
    ],
}

ZONES = [
    {
        "id": "sw-z1",
        "name": "Swiftlet Shores",
        "tagline": "Constants, strings and the flow of a Swift program.",
        "difficulty": "easy",
        "nodes": [
            {
                "id": "sw1",
                "title": "Constants & Variables",
                "difficulty": "easy",
                "xp_reward": 50,
                "estimated_minutes": 10,
            },
            {
                "id": "sw2",
                "title": "Strings & Interpolation",
                "difficulty": "easy",
                "xp_reward": 50,
                "estimated_minutes": 10,
            },
            {
                "id": "sw3",
                "title": "Conditionals & switch",
                "difficulty": "easy",
                "xp_reward": 55,
                "estimated_minutes": 11,
            },
            {"id": "sw4", "title": "Loops", "difficulty": "easy", "xp_reward": 60, "estimated_minutes": 12},
        ],
        "boss": {
            "id": "sw-z1-boss",
            "name": "Semicolon Slime",
            "sprite": "slime",
            "challenge": "Repair 3 tiny Swift programs that refuse to compile",
            "stages": 3,
            "xp_reward": 250,
        },
    },
    {
        "id": "sw-z2",
        "name": "Optional Orchard",
        "tagline": "Functions, optionals and the collections every app needs.",
        "difficulty": "medium",
        "nodes": [
            {
                "id": "sw5",
                "title": "Functions & Argument Labels",
                "difficulty": "medium",
                "xp_reward": 90,
                "estimated_minutes": 18,
            },
            {"id": "sw6", "title": "Optionals", "difficulty": "medium", "xp_reward": 100, "estimated_minutes": 19},
            {
                "id": "sw7",
                "title": "Arrays & Dictionaries",
                "difficulty": "medium",
                "xp_reward": 100,
                "estimated_minutes": 19,
            },
            {
                "id": "sw8",
                "title": "Structs vs Classes",
                "difficulty": "medium",
                "xp_reward": 110,
                "estimated_minutes": 20,
            },
        ],
        "boss": {
            "id": "sw-z2-boss",
            "name": "Nil Nibbler",
            "sprite": "bugSlime",
            "challenge": "Unwrap a basket of optionals without a single crash",
            "stages": 4,
            "xp_reward": 400,
        },
    },
    {
        "id": "sw-z3",
        "name": "Protocol Peaks",
        "tagline": "Model your data with enums, protocols, closures and errors.",
        "difficulty": "hard",
        "nodes": [
            {
                "id": "sw9",
                "title": "Enums & Associated Values",
                "difficulty": "hard",
                "xp_reward": 140,
                "estimated_minutes": 25,
            },
            {"id": "sw10", "title": "Protocols", "difficulty": "hard", "xp_reward": 150, "estimated_minutes": 27},
            {"id": "sw11", "title": "Closures", "difficulty": "hard", "xp_reward": 150, "estimated_minutes": 28},
            {"id": "sw12", "title": "Error Handling", "difficulty": "hard", "xp_reward": 160, "estimated_minutes": 30},
        ],
        "boss": {
            "id": "sw-z3-boss",
            "name": "Throwing Titan",
            "sprite": "recursionBoss",
            "challenge": "Catch every error it throws across 5 escalating rounds",
            "stages": 5,
            "xp_reward": 700,
        },
    },
]

LESSONS: list[dict] = [
    {
        "id": "sw1",
        "module_id": "sw-m1",
        "title": "let, var and Swift Types",
        "concept": "Constants and Variables",
        "explanation": (
            "Swift stores values with `let` (a constant that can never change) and `var` (a variable you can update). "
            "Every value has a type such as `Int`, `Double`, `String` or `Bool`, and Swift usually infers it from the starting value. "
            "You can also write the type yourself with an annotation like `let price: Double = 2.5`."
        ),
        "code_example": """let name = "Ada"           // constant: can't change
var score = 10             // variable: can change
score += 5
let price: Double = 2.5    // explicit type annotation
print(name)                // Ada
print(score)               // 15
print(price * 2)           // 5.0""",
        "code_walkthrough": [
            '`let name = "Ada"` creates a constant; Swift infers its type as `String`.',
            "`var score = 10` creates a variable of type `Int` that can be updated.",
            "`score += 5` adds 5, so `score` becomes 15.",
            "`let price: Double = 2.5` spells out the type with an annotation.",
            "`price * 2` is a `Double`, so it prints as `5.0`, not `5`.",
        ],
        "key_points": [
            "Prefer `let`; switch to `var` only when the value really needs to change.",
            "Swift infers types, but a value's type can never change once it's set.",
            "A `Double` always prints with a decimal point, like `5.0`.",
        ],
        "analogy": (
            "`let` is like a name carved into stone, while `var` is like a name written on a "
            "whiteboard that you can wipe and rewrite."
        ),
        "quiz": {
            "question": "What happens when you write `let lives = 3` and then `lives = 4`?",
            "options": [
                "lives becomes 4",
                "A compile-time error",
                "lives stays 3 silently",
                "The app crashes at runtime",
            ],
            "correct_index": 1,
            "explanation": "Constants declared with `let` can't be reassigned, so the compiler rejects the code before it ever runs.",
        },
    },
    {
        "id": "sw2",
        "module_id": "sw-m1",
        "title": "Building Text with String Interpolation",
        "concept": "String Interpolation",
        "explanation": (
            r"Strings in Swift are written in double quotes, and you can join them with `+`. "
            r"String interpolation drops any value or expression straight into a string with `\(...)`. "
            r"Strings also come with handy tools like `count`, `uppercased()` and `hasPrefix(_:)`."
        ),
        "code_example": r"""let player = "Mia"
let level = 7
print("Hi, \(player)! You are level \(level).")  // Hi, Mia! You are level 7.
print("Next level: \(level + 1)")                // Next level: 8
print(player.count)                              // 3
print(player.uppercased())                       // MIA
let banner = "Quest" + " " + "Start"
print(banner)                                    // Quest Start
print(banner.hasPrefix("Quest"))                 // true""",
        "code_walkthrough": [
            r"`\(player)` and `\(level)` insert the values of those constants into the text.",
            r"`\(level + 1)` shows that any expression works inside interpolation, giving 8.",
            '`player.count` is the number of characters in "Mia": 3.',
            '`player.uppercased()` returns a new string, "MIA", and leaves `player` unchanged.',
            '`+` joins strings together, and `hasPrefix("Quest")` checks how a string starts.',
        ],
        "key_points": [
            r"Use `\(value)` to put values inside a string; no manual conversion needed.",
            "Swift strings always use double quotes.",
            "String methods like `uppercased()` return new strings instead of changing the original.",
        ],
        "analogy": (
            r"Interpolation is like a fill-in-the-blanks form: `\(...)` marks a blank, and Swift "
            "writes in the current value for you."
        ),
        "quiz": {
            "question": r'What does `print("Total: \(4 * 2)")` print?',
            "options": [r"Total: \(4 * 2)", "Total: 4 * 2", "Total: (8)", "Total: 8"],
            "correct_index": 3,
            "explanation": r"Swift evaluates the expression inside `\(...)` and inserts the result, so the output is `Total: 8`.",
        },
        "try_it": {
            "prompt": r"Use string interpolation to print `Hero has 3 lives` using the `hero` and `lives` constants.",
            "starter_code": 'let hero = "Hero"\nlet lives = 3\n// print the message here\n',
            "checks": [
                {
                    "pattern": r"print\s*\(",
                    "hint": "Call `print(...)` to show the message.",
                },
                {
                    "pattern": r"\\\(\s*hero\s*\)",
                    "hint": r"Insert the name with `\(hero)`.",
                },
                {
                    "pattern": r"\\\(\s*lives\s*\)",
                    "hint": r"Insert the number with `\(lives)`.",
                },
            ],
            "expected_output": "Hero has 3 lives",
        },
    },
    {
        "id": "sw3",
        "module_id": "sw-m1",
        "title": "Making Decisions with if and switch",
        "concept": "Conditional Statements",
        "explanation": (
            "`if` and `else` run different code depending on a condition, which in Swift must be a real `Bool`. "
            "A `switch` compares one value against many patterns, including ranges like `80..<90`. "
            "Swift's `switch` must cover every possible value (often with `default`) and never falls through to the next case by accident."
        ),
        "code_example": """let score = 82
if score >= 50 {
    print("Passed")           // Passed
} else {
    print("Try again")
}
switch score {
case 90...100:
    print("Grade A")
case 80..<90:
    print("Grade B")          // Grade B
default:
    print("Keep practicing")
}""",
        "code_walkthrough": [
            '`score >= 50` is true, so "Passed" is printed and the `else` block is skipped.',
            "Swift doesn't need parentheses around the condition, but the braces are required.",
            "`case 90...100` matches the closed range 90 through 100, which 82 is not in.",
            '`case 80..<90` matches 80 up to (but not including) 90, so "Grade B" is printed.',
            "`default` catches every other value, making the `switch` exhaustive.",
        ],
        "key_points": [
            "Conditions must be `Bool`; Swift has no truthy numbers or strings.",
            "A `switch` must be exhaustive, so add `default` when the cases don't cover everything.",
            "Cases don't fall through; the `switch` ends after the first matching case runs.",
        ],
        "analogy": (
            "A `switch` is like a sorting machine at a post office: each letter drops into exactly "
            "one slot, and there's always a slot for anything unusual."
        ),
        "quiz": {
            "question": "In Swift, what happens after a matching `case` in a `switch` finishes running?",
            "options": [
                "The switch ends; there is no implicit fallthrough",
                "Execution falls through to the next case",
                "The switch restarts from the top",
                "Nothing, unless you wrote `break` at the end of the case",
            ],
            "correct_index": 0,
            "explanation": "Swift exits the `switch` automatically after the matching case. If you really want to continue into the next case, you must write `fallthrough`.",
        },
    },
    {
        "id": "sw4",
        "module_id": "sw-m1",
        "title": "Repeating Work with for-in and while",
        "concept": "For-In Loops",
        "explanation": (
            "A `for-in` loop runs once for each item in a range, array or other sequence. "
            "Ranges come in two flavors: `1...3` includes the last number, while `0..<3` stops just before it. "
            "A `while` loop keeps repeating as long as its condition stays true."
        ),
        "code_example": r"""for i in 1...3 {
    print(i)                       // 1, then 2, then 3
}
let fruits = ["apple", "kiwi"]
for (index, fruit) in fruits.enumerated() {
    print("\(index): \(fruit)")    // 0: apple, then 1: kiwi
}
var countdown = 3
while countdown > 0 {
    countdown -= 1
}
print(countdown)                   // 0""",
        "code_walkthrough": [
            "`for i in 1...3` runs three times, with `i` set to 1, 2 and 3.",
            "`for (index, fruit) in fruits.enumerated()` gives you each position and value together.",
            "Each item is printed on its own line, like `0: apple` and `1: kiwi`.",
            "`while countdown > 0` keeps subtracting 1 until `countdown` reaches 0.",
        ],
        "key_points": [
            "`a...b` includes `b`; `a..<b` stops just before `b`.",
            "Use `enumerated()` when you need both the index and the value.",
            "Make sure a `while` loop's condition eventually becomes false.",
        ],
        "analogy": (
            "A `for-in` loop is like a teacher calling the roll: every name on the list gets "
            "called exactly once, in order."
        ),
        "quiz": {
            "question": "How many times does `for i in 0..<5 { }` run its body?",
            "options": ["4", "6", "5", "0"],
            "correct_index": 2,
            "explanation": "The half-open range `0..<5` contains 0, 1, 2, 3 and 4, which is 5 values.",
        },
        "try_it": {
            "prompt": "Use a `for-in` loop over the range `1...5` to add each number to `total`.",
            "starter_code": "var total = 0\n// write your loop here\n\nprint(total)\n",
            "checks": [
                {
                    "pattern": r"for\s+\w+\s+in\s+\(?\s*1\s*\.\.\.\s*5",
                    "hint": "Start your loop with `for n in 1...5 {`.",
                },
                {
                    "pattern": r"total\s*(\+=|=\s*total\s*\+)",
                    "hint": "Inside the loop, add the number with `total += n`.",
                },
            ],
            "expected_output": "15",
        },
    },
    {
        "id": "sw5",
        "module_id": "sw-m2",
        "title": "Functions That Read Like Sentences",
        "concept": "Functions",
        "explanation": (
            "You define a function with `func`, list its parameters with their types, and declare the return type after `->`. "
            "Swift parameters have argument labels that callers write, which makes calls read like plain English. "
            "Use `_` to drop a label, and give a parameter a separate outside label like `from start: Int` when it reads better."
        ),
        "code_example": r"""func greet(person: String) -> String {
    return "Hello, \(person)!"
}
func add(_ a: Int, _ b: Int) -> Int {
    a + b                          // one expression: implicit return
}
func move(from start: Int, to end: Int) -> Int {
    end - start
}
print(greet(person: "Leo"))        // Hello, Leo!
print(add(2, 3))                   // 5
print(move(from: 2, to: 9))        // 7""",
        "code_walkthrough": [
            '`greet(person:)` uses the parameter name as its label, so you call it as `greet(person: "Leo")`.',
            "`_ a: Int` removes the label, so `add` is called as `add(2, 3)`.",
            "A function whose body is a single expression, like `a + b`, returns it without writing `return`.",
            "In `move(from start: Int, to end: Int)`, callers use `from` and `to`, while the body uses `start` and `end`.",
            "`move(from: 2, to: 9)` returns `9 - 2`, which is 7.",
        ],
        "key_points": [
            "The return type goes after `->`; functions without one return nothing.",
            "Argument labels are part of the call, so `add(2, 3)` only works when the labels are `_`.",
            "Choose labels that make the call site read like a sentence.",
        ],
        "analogy": (
            'Argument labels are like the labels on a form: "from" and "to" tell everyone '
            "exactly which box each value belongs in."
        ),
        "quiz": {
            "question": "Given `func add(_ a: Int, _ b: Int) -> Int`, which call compiles?",
            "options": ["add(a: 2, b: 3)", "add(2, 3)", "add(_: 2, _: 3)", "add(a 2, b 3)"],
            "correct_index": 1,
            "explanation": "The `_` means the parameters have no argument label, so you pass the values without labels: `add(2, 3)`.",
        },
    },
    {
        "id": "sw6",
        "module_id": "sw-m2",
        "title": "Handling Missing Values Safely",
        "concept": "Optionals",
        "explanation": (
            "An optional, written with a `?` like `String?`, holds either a value or `nil` (no value at all). "
            "Swift won't let you use an optional as if it were a plain value, which prevents a whole class of crashes. "
            "You unwrap it safely with `if let`, `guard let`, or supply a fallback with the nil-coalescing operator `??`."
        ),
        "code_example": r"""var nickname: String? = nil
print(nickname ?? "Anonymous")   // Anonymous
nickname = "Ace"
if let nickname {
    print("Hi, \(nickname)!")    // Hi, Ace!
}
let number = Int("42")           // Int? because parsing can fail
print(number)                    // Optional(42)
print(Int("abc") == nil)         // true
print((number ?? 0) + 8)         // 50""",
        "code_walkthrough": [
            '`String? = nil` starts with no value, so `nickname ?? "Anonymous"` uses the fallback.',
            "`if let nickname` unwraps the optional into a plain `String` inside the braces (Swift 5.7+ shorthand).",
            '`Int("42")` returns an `Int?`, because text like "abc" can\'t become a number.',
            "Printing an optional directly shows the wrapper, `Optional(42)`, and Swift warns you about it.",
            "`(number ?? 0) + 8` unwraps to 42 and adds 8, giving 50.",
        ],
        "key_points": [
            '`T?` means "a `T` or `nil`"; plain types can never be `nil`.',
            "Unwrap with `if let` or `guard let`, or use `??` to give a default.",
            "Avoid force unwrapping with `!`; it crashes if the value is `nil`.",
        ],
        "analogy": (
            "An optional is like a gift box: there might be something inside or it might be empty, "
            "so you open it carefully before using what's inside."
        ),
        "quiz": {
            "question": 'What is the type of `Int("42")`?',
            "options": ["Int", "String", "Double", "Int?"],
            "correct_index": 3,
            "explanation": 'Turning a `String` into an `Int` can fail (think "abc"), so Swift returns an optional `Int?`.',
        },
        "try_it": {
            "prompt": 'Print `username`, or "Guest" if it is `nil`, using the nil-coalescing operator `??`.',
            "starter_code": 'let username: String? = nil\n// print the username, falling back to "Guest"\n',
            "checks": [
                {
                    "pattern": r"print\s*\(",
                    "hint": "Call `print(...)` to show the result.",
                },
                {
                    "pattern": r"username\s*\?\?\s*\"Guest\"",
                    "hint": 'Use `username ?? "Guest"`.',
                },
            ],
            "expected_output": "Guest",
        },
    },
    {
        "id": "sw7",
        "module_id": "sw-m2",
        "title": "Storing Collections in Arrays and Dictionaries",
        "concept": "Arrays and Dictionaries",
        "explanation": (
            "An array is an ordered list of values of one type, like `[Int]`, accessed by an index starting at 0. "
            "A dictionary stores key-value pairs, like `[String: Int]`, and you look values up by key. "
            "Looking up a key returns an optional, because the key might not exist."
        ),
        "code_example": """var scores = [90, 75, 88]
scores.append(100)
print(scores.count)              // 4
print(scores[0])                 // 90
print(scores.sorted())           // [75, 88, 90, 100]
var ages = ["Ana": 30, "Ben": 25]
ages["Cy"] = 41
print(ages["Ana"] ?? 0)          // 30
print(ages["Zed"])               // nil
print(ages.count)                // 3""",
        "code_walkthrough": [
            "`var scores = [90, 75, 88]` creates an `[Int]`; it must be `var` so we can `append`.",
            "`scores[0]` reads the first item, and `sorted()` returns a new sorted array.",
            '`["Ana": 30, "Ben": 25]` creates a `[String: Int]` dictionary.',
            '`ages["Cy"] = 41` adds a new key, bringing the count to 3.',
            '`ages["Ana"]` is an `Int?`, so `?? 0` unwraps it; the missing key "Zed" gives `nil`.',
        ],
        "key_points": [
            "Collections declared with `let` can't be changed; use `var` to add or remove items.",
            "Reading an array index that doesn't exist crashes, so check `count` or use `first` and `last`.",
            "Dictionary lookups return optionals, and dictionaries have no guaranteed order.",
        ],
        "analogy": (
            "An array is like a numbered row of lockers, while a dictionary is like a phone book "
            "where you find a number by looking up a name."
        ),
        "quiz": {
            "question": 'If `ages` is a `[String: Int]`, what is the type of `ages["Ana"]`?',
            "options": ["Int?", "Int", "String", "[Int]"],
            "correct_index": 0,
            "explanation": "The key might be missing, so a dictionary lookup returns an optional: `Int?`.",
        },
    },
    {
        "id": "sw8",
        "module_id": "sw-m2",
        "title": "Value Types vs Reference Types",
        "concept": "Structures and Classes",
        "explanation": (
            "Structs and classes both group properties and methods into your own custom types. "
            "A struct is a value type: assigning it to a new variable makes an independent copy. "
            "A class is a reference type: assigning it shares the same object, so a change through one name is seen through every name."
        ),
        "code_example": """struct Stats {
    var hp: Int
}
class Hero {
    var hp: Int
    init(hp: Int) { self.hp = hp }
}
let a = Stats(hp: 10)
var b = a                  // b is a copy
b.hp = 99
print(a.hp, b.hp)          // 10 99
let h1 = Hero(hp: 10)
let h2 = h1                // h2 points to the same object
h2.hp = 99
print(h1.hp, h2.hp)        // 99 99""",
        "code_walkthrough": [
            "`struct Stats` gets a free memberwise initializer, so `Stats(hp: 10)` just works.",
            "`class Hero` needs its own `init` to set up its properties.",
            "`var b = a` copies the struct, so changing `b.hp` leaves `a.hp` at 10.",
            "`let h2 = h1` copies the reference, so `h1` and `h2` are the same hero and both show 99.",
            "`h2` is a `let`, yet `h2.hp = 99` works, because `let` only fixes which object `h2` points to.",
        ],
        "key_points": [
            "Structs are copied on assignment; classes are shared by reference.",
            "Swift favors structs by default; reach for a class when you need shared identity or inheritance.",
            "Classes need an initializer for their stored properties; structs get one automatically.",
        ],
        "analogy": (
            "A struct is like handing someone a photocopy of your notes, while a class is like "
            "sharing a link to the same online document."
        ),
        "quiz": {
            "question": "What does this print?\n\nstruct Box { var n: Int }\nvar a = Box(n: 1)\nvar b = a\nb.n = 5\nprint(a.n)",
            "options": ["5", "nil", "1", "A compile error"],
            "correct_index": 2,
            "explanation": "`Box` is a struct, so `var b = a` makes a copy. Changing `b.n` doesn't affect `a`, which still holds 1.",
        },
    },
    {
        "id": "sw9",
        "module_id": "sw-m3",
        "title": "Enums That Carry Extra Data",
        "concept": "Enumerations",
        "explanation": (
            "An enum defines a type with a fixed set of cases, like the four directions on a compass. "
            "Swift enum cases can carry associated values, so each case can hold its own extra data. "
            "You read that data back with a `switch`, which must handle every case."
        ),
        "code_example": r"""enum Direction { case north, south, east, west }
enum Reward {
    case xp(Int)
    case badge(name: String)
}
let heading = Direction.north
print(heading)                       // north
let prize = Reward.badge(name: "Bug Hunter")
switch prize {
case .xp(let amount):
    print("Gained \(amount) XP")
case .badge(let name):
    print("Unlocked \(name)")        // Unlocked Bug Hunter
}""",
        "code_walkthrough": [
            "`enum Direction` lists four simple cases on one line.",
            "Printing an enum value shows its case name, so `print(heading)` prints `north`.",
            "`case xp(Int)` and `case badge(name: String)` each carry their own associated value.",
            '`Reward.badge(name: "Bug Hunter")` creates a value with its data attached.',
            "`case .badge(let name)` matches that case and pulls the data out into `name`.",
        ],
        "key_points": [
            "Enums model a value that can be exactly one of a fixed set of options.",
            "Associated values let each case carry different data.",
            "A `switch` over an enum must handle every case, so the compiler catches forgotten ones.",
        ],
        "analogy": (
            "An enum with associated values is like a set of labeled envelopes: the label tells you "
            "which kind it is, and each envelope can hold its own contents."
        ),
        "quiz": {
            "question": "Given `enum Reward { case xp(Int) }`, which line creates a `Reward` value?",
            "options": ["Reward.xp", "Reward.xp(50)", "Reward(xp: 50)", "Reward.xp = 50"],
            "correct_index": 1,
            "explanation": "A case with an associated value is created by passing the value, like a function call: `Reward.xp(50)`.",
        },
    },
    {
        "id": "sw10",
        "module_id": "sw-m3",
        "title": "Shared Abilities with Protocols",
        "concept": "Protocols",
        "explanation": (
            "A protocol is a blueprint that lists the methods and properties a type must provide. "
            "Structs, classes and enums adopt a protocol by declaring conformance and implementing its requirements. "
            "Code can then work with any conforming type, which is the heart of Swift's protocol-oriented style."
        ),
        "code_example": r"""protocol Describable {
    func describe() -> String
}
struct Sword: Describable {
    let damage: Int
    func describe() -> String { "Sword with \(damage) damage" }
}
struct Potion: Describable {
    func describe() -> String { "Potion that heals 50 HP" }
}
let items: [any Describable] = [Sword(damage: 12), Potion()]
for item in items { print(item.describe()) }
// Sword with 12 damage
// Potion that heals 50 HP""",
        "code_walkthrough": [
            "`protocol Describable` requires a `describe()` method that returns a `String`.",
            "`struct Sword: Describable` declares conformance and implements `describe()`.",
            "`Potion` conforms too, with its own completely different implementation.",
            "`[any Describable]` is an array that can hold any type conforming to the protocol.",
            "The loop calls `describe()` on each item, and each type answers in its own way.",
        ],
        "key_points": [
            "A protocol defines what a type can do, not how it does it.",
            "Conforming types must implement every requirement, or the code won't compile.",
            "Protocol extensions can add default implementations that every conforming type gets for free.",
        ],
        "analogy": (
            "A protocol is like a job description: anyone who can do the listed tasks can take "
            "the job, however they choose to do them."
        ),
        "quiz": {
            "question": "What does a type need in order to conform to a protocol?",
            "options": [
                "It must be a class",
                "It must inherit from a base class",
                "It must be a struct",
                "It must provide everything the protocol requires",
            ],
            "correct_index": 3,
            "explanation": "Structs, classes and enums can all conform; they just have to satisfy every requirement, either directly or through a default implementation in a protocol extension.",
        },
    },
    {
        "id": "sw11",
        "module_id": "sw-m3",
        "title": "Passing Code Around with Closures",
        "concept": "Closures",
        "explanation": (
            "A closure is a block of code you can store in a variable or pass to a function, like a function without a name. "
            "Swift has a short trailing closure syntax and shorthand argument names like `$0` and `$1`. "
            "Collection methods such as `map`, `filter`, `reduce` and `sorted(by:)` take closures to transform data."
        ),
        "code_example": r"""let numbers = [3, 8, 1, 6]
let doubled = numbers.map { $0 * 2 }
let big = numbers.filter { $0 > 4 }
let total = numbers.reduce(0, +)
let descending = numbers.sorted { $0 > $1 }
print(doubled)                 // [6, 16, 2, 12]
print(big)                     // [8, 6]
print(total)                   // 18
print(descending)              // [8, 6, 3, 1]
let greet = { (name: String) -> String in "Hi, \(name)" }
print(greet("Zoe"))            // Hi, Zoe""",
        "code_walkthrough": [
            "`numbers.map { $0 * 2 }` uses a trailing closure, where `$0` is each element in turn.",
            "`filter { $0 > 4 }` keeps only the elements for which the closure returns `true`.",
            "`reduce(0, +)` starts at 0 and combines the elements with `+`, giving 18.",
            "`sorted { $0 > $1 }` compares two elements at a time to sort from largest to smallest.",
            "`{ (name: String) -> String in ... }` is a full closure stored in `greet` and called like a function.",
        ],
        "key_points": [
            "Closures are unnamed functions you can store and pass around.",
            "When a closure is the last argument, you can write it after the parentheses as a trailing closure.",
            "`$0`, `$1` are shorthand names for a closure's first and second parameters.",
        ],
        "analogy": (
            "A closure is like a recipe card you hand to a chef: `map` is the chef who follows "
            "your card for every ingredient on the counter."
        ),
        "quiz": {
            "question": "What does `[1, 2, 3].map { $0 * 10 }` return?",
            "options": ["[10, 20, 30]", "60", "[1, 2, 3]", "[10]"],
            "correct_index": 0,
            "explanation": "`map` runs the closure on every element and returns a new array of the results.",
        },
        "try_it": {
            "prompt": "Use `filter` with a closure to keep only the even numbers from `nums`.",
            "starter_code": "let nums = [1, 2, 3, 4, 5, 6]\nlet evens = nums // keep only the even numbers\n\nprint(evens)\n",
            "checks": [
                {
                    "pattern": r"nums\s*\.\s*filter\s*[({]",
                    "hint": "Call `nums.filter { ... }` with a closure.",
                },
                {
                    "pattern": r"%\s*2\s*==\s*0",
                    "hint": "A number is even when `$0 % 2 == 0`.",
                },
            ],
            "expected_output": "[2, 4, 6]",
        },
    },
    {
        "id": "sw12",
        "module_id": "sw-m3",
        "title": "Throwing and Catching Errors",
        "concept": "Error Handling",
        "explanation": (
            "Functions marked `throws` can report a problem by throwing an error, usually a custom enum that conforms to `Error`. "
            "You call them with `try` inside a `do` block and handle failures in one or more `catch` blocks. "
            "`try?` is a shortcut that turns any error into `nil` when you only care whether the call worked."
        ),
        "code_example": r"""enum BankError: Error { case insufficientFunds(needed: Int) }
func withdraw(_ amount: Int, from balance: Int) throws -> Int {
    guard amount <= balance else { throw BankError.insufficientFunds(needed: amount - balance) }
    return balance - amount
}
do {
    print(try withdraw(30, from: 100))   // 70
    print(try withdraw(80, from: 50))    // throws, so nothing prints here
} catch BankError.insufficientFunds(let needed) {
    print("Short by \(needed) coins")    // Short by 30 coins
} catch {
    print("Unexpected error: \(error)")
}
print((try? withdraw(5, from: 1)) ?? 0) // 0""",
        "code_walkthrough": [
            "`enum BankError: Error` defines the errors this code can throw, with extra data attached.",
            "`throws` marks `withdraw` as a function that can fail, and `guard ... else { throw ... }` exits early on bad input.",
            "Inside `do`, every throwing call needs `try`; the first call succeeds and prints 70.",
            "The second call throws, so Swift jumps straight to the matching `catch` and prints `Short by 30 coins`.",
            "The final `catch` with no pattern handles any other error, using the automatic `error` constant.",
            "`(try? withdraw(5, from: 1)) ?? 0` turns the thrown error into `nil` and falls back to 0.",
        ],
        "key_points": [
            "Mark failing functions with `throws`, and call them with `try`.",
            "`do`/`catch` handles errors; a final plain `catch` covers anything not matched earlier.",
            "`try?` converts an error into `nil`, which pairs nicely with `??` for a fallback value.",
        ],
        "analogy": (
            "Throwing an error is like a referee blowing a whistle: play stops immediately, and the "
            "nearest `catch` decides what happens next."
        ),
        "quiz": {
            "question": "What does `try? riskyCall()` produce if `riskyCall()` throws an error?",
            "options": ["The app crashes", "The error is rethrown", "nil", "An empty string"],
            "correct_index": 2,
            "explanation": "`try?` swallows the error and returns `nil` instead, so the result is always an optional.",
        },
    },
]
