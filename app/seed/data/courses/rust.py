"""Rust Foundations: Learn safe, fast systems programming with ownership, enums, traits and iterators."""

COURSE = {
    "id": "rust-foundations",
    "title": "Rust Foundations",
    "world": "Ferris's Iron Forge",
    "description": "Learn safe, fast systems programming with Rust's ownership model, enums, traits and iterators.",
    "language": "rust",
    "modules": [
        {"id": "rs-m1", "title": "Rust Basics"},
        {"id": "rs-m2", "title": "Ownership & Data Modeling"},
        {"id": "rs-m3", "title": "Errors, Collections & Traits"},
    ],
}

ZONES = [
    {
        "id": "rs-z1",
        "name": "Rustbelt Shores",
        "tagline": "Variables, types, loops and functions on Ferris's home beach.",
        "difficulty": "easy",
        "nodes": [
            {
                "id": "rs1",
                "title": "Variables & Mutability",
                "difficulty": "easy",
                "xp_reward": 50,
                "estimated_minutes": 10,
            },
            {"id": "rs2", "title": "Data Types", "difficulty": "easy", "xp_reward": 50, "estimated_minutes": 10},
            {"id": "rs3", "title": "Control Flow", "difficulty": "easy", "xp_reward": 60, "estimated_minutes": 12},
            {"id": "rs4", "title": "Functions", "difficulty": "easy", "xp_reward": 60, "estimated_minutes": 12},
        ],
        "boss": {
            "id": "rs-z1-boss",
            "name": "Mutable Mudcrab",
            "sprite": "slime",
            "challenge": "Fix 3 snippets the compiler refuses to build",
            "stages": 3,
            "xp_reward": 250,
        },
    },
    {
        "id": "rs-z2",
        "name": "Borrow Checker Caverns",
        "tagline": "Learn who owns what, and model your data with structs and enums.",
        "difficulty": "medium",
        "nodes": [
            {"id": "rs5", "title": "Ownership", "difficulty": "medium", "xp_reward": 90, "estimated_minutes": 18},
            {
                "id": "rs6",
                "title": "Borrowing & References",
                "difficulty": "medium",
                "xp_reward": 100,
                "estimated_minutes": 20,
            },
            {
                "id": "rs7",
                "title": "Structs & Methods",
                "difficulty": "medium",
                "xp_reward": 100,
                "estimated_minutes": 20,
            },
            {"id": "rs8", "title": "Enums & match", "difficulty": "medium", "xp_reward": 110, "estimated_minutes": 20},
        ],
        "boss": {
            "id": "rs-z2-boss",
            "name": "The Borrow Warden",
            "sprite": "bugSlime",
            "challenge": "Untangle moves and borrows until every snippet compiles",
            "stages": 4,
            "xp_reward": 400,
        },
    },
    {
        "id": "rs-z3",
        "name": "Trait Forge Peaks",
        "tagline": "Handle errors safely, wield collections and forge reusable traits.",
        "difficulty": "hard",
        "nodes": [
            {"id": "rs9", "title": "Option & Result", "difficulty": "hard", "xp_reward": 140, "estimated_minutes": 25},
            {
                "id": "rs10",
                "title": "Vectors & HashMaps",
                "difficulty": "hard",
                "xp_reward": 150,
                "estimated_minutes": 28,
            },
            {"id": "rs11", "title": "Traits", "difficulty": "hard", "xp_reward": 150, "estimated_minutes": 28},
            {
                "id": "rs12",
                "title": "Iterators & Closures",
                "difficulty": "hard",
                "xp_reward": 160,
                "estimated_minutes": 30,
            },
        ],
        "boss": {
            "id": "rs-z3-boss",
            "name": "Lord Unwrap",
            "sprite": "recursionBoss",
            "challenge": "Replace every panicking unwrap with safe Option and Result handling",
            "stages": 5,
            "xp_reward": 700,
        },
    },
]

LESSONS: list[dict] = [
    {
        "id": "rs1",
        "module_id": "rs-m1",
        "title": "let, mut and Shadowing",
        "concept": "Variables & Mutability",
        "explanation": (
            "In Rust, variables declared with `let` are immutable by default, so their value can't change. "
            "Add `mut` when you really need to change a value, and the compiler will check the rest for you. "
            "You can also shadow a variable by declaring a new one with the same name, and `const` creates "
            "a constant that never changes and must have a type annotation."
        ),
        "code_example": """fn main() {
    let x = 5;
    let mut score = 10;
    score += 5;
    println!("x = {x}, score = {score}"); // x = 5, score = 15
    let x = x * 2; // shadowing: a brand-new x
    println!("x = {x}"); // x = 10
    const MAX_LEVEL: u32 = 99;
    println!("max = {MAX_LEVEL}"); // max = 99
}""",
        "code_walkthrough": [
            "`let x = 5;` creates an immutable variable; writing `x = 6;` later would be a compile error.",
            "`let mut score = 10;` is mutable, so `score += 5;` is allowed and makes it 15.",
            '`println!("x = {x}, ...")` prints variables by putting their names inside `{}`.',
            "`let x = x * 2;` shadows the old `x` with a new variable whose value is 10.",
            "`const MAX_LEVEL: u32 = 99;` is a constant: always immutable and always typed.",
        ],
        "key_points": [
            "Variables are immutable by default; opt in to change with `let mut`.",
            "Shadowing with a new `let` creates a fresh variable and can even change its type.",
            "`const` values need a type annotation and are written in SCREAMING_SNAKE_CASE.",
        ],
        "analogy": (
            "An immutable variable is like a label printed on a box, while `let mut` is a label "
            "written on a sticky note you're allowed to peel off and rewrite."
        ),
        "quiz": {
            "question": "What happens when you compile this?\n\nlet x = 5;\nx = 6;",
            "options": [
                "x becomes 6",
                "A compile error: cannot assign twice to an immutable variable",
                "The program panics at runtime",
                "x silently stays 5",
            ],
            "correct_index": 1,
            "explanation": "`x` was declared without `mut`, so the compiler rejects the second assignment before the program ever runs.",
        },
        "try_it": {
            "prompt": "The hero loses a life! Make `lives` mutable, then subtract 1 from it so the program prints 2.",
            "starter_code": 'fn main() {\n    let lives = 3;\n    // lives -= 1;\n    println!("Lives left: {lives}");\n}\n',
            "checks": [
                {
                    "pattern": r"let\s+mut\s+lives\s*=\s*3",
                    "hint": "Declare the variable with `let mut lives = 3;`.",
                },
                {
                    "pattern": r"(?m)^\s*lives\s*(-=\s*1|=\s*lives\s*-\s*1)\s*;",
                    "hint": "Uncomment (or write) the line `lives -= 1;`.",
                },
            ],
            "expected_output": "Lives left: 2",
        },
    },
    {
        "id": "rs2",
        "module_id": "rs-m1",
        "title": "Numbers, Booleans, Chars and Friends",
        "concept": "Data Types",
        "explanation": (
            "Rust is statically typed: every value has a type known at compile time, though the compiler can "
            "usually infer it for you. Scalar types include integers like `i32` and `u8`, floats like `f64`, "
            "`bool` and `char`. Compound types group values: a tuple holds a fixed mix of types, and an array "
            "holds a fixed number of values of one type."
        ),
        "code_example": """fn main() {
    let level: u8 = 7;
    let speed: f64 = 2.5;
    let alive: bool = true;
    let grade: char = 'A';
    println!("{level} {speed} {alive} {grade}"); // 7 2.5 true A
    let pos: (i32, i32) = (3, -4);
    println!("{:?} x={}", pos, pos.0); // (3, -4) x=3
    let scores: [u32; 3] = [10, 20, 30];
    println!("{:?} len={}", scores, scores.len()); // [10, 20, 30] len=3
}""",
        "code_walkthrough": [
            "`u8` is an unsigned 8-bit integer (0 to 255) and `f64` is a 64-bit floating-point number.",
            "`char` uses single quotes and holds one Unicode character, like `'A'`.",
            "`(i32, i32)` is a tuple; `pos.0` reads its first element.",
            "`[u32; 3]` is an array of exactly three `u32` values.",
            "`{:?}` prints a value with its Debug format, which works for tuples and arrays.",
        ],
        "key_points": [
            "Integers default to `i32` and floats default to `f64` when no type is given.",
            "Signed types (`i8`..`i128`) allow negatives; unsigned types (`u8`..`u128`) don't.",
            "Tuples and arrays have a fixed length that is part of their type.",
        ],
        "analogy": (
            "Types are like the shapes on a toddler's sorting toy: each value has to fit the slot "
            "it's put in, and the compiler checks every slot before you play."
        ),
        "quiz": {
            "question": "What type does Rust infer for `let n = 42;` when nothing else constrains it?",
            "options": ["u8", "i64", "i32", "usize"],
            "correct_index": 2,
            "explanation": "Integer literals default to `i32` unless the surrounding code requires a different type.",
        },
    },
    {
        "id": "rs3",
        "module_id": "rs-m1",
        "title": "Branching and Looping",
        "concept": "Control Flow",
        "explanation": (
            "`if` chooses a branch based on a `bool` condition, and because it's an expression it can produce "
            "a value. Rust has three loops: `loop` repeats forever until you `break` (and can return a value), "
            "`while` repeats while a condition holds, and `for` walks through a range or collection."
        ),
        "code_example": """fn main() {
    let hp = 7;
    let state = if hp > 0 { "alive" } else { "defeated" };
    println!("{state}"); // alive
    let mut count = 0;
    let result = loop {
        count += 1;
        if count == 3 { break count * 10; }
    };
    println!("{result}"); // 30
    let mut fuel = 3;
    while fuel > 0 { fuel -= 1; }
    println!("fuel {fuel}"); // fuel 0
    for i in 1..=3 { println!("lap {i}"); } // lap 1, lap 2, lap 3
}""",
        "code_walkthrough": [
            '`if hp > 0 { "alive" } else { "defeated" }` is an expression, so its result is stored in `state`.',
            "`loop` runs until `break count * 10;`, which exits and hands back 30 as the loop's value.",
            "`while fuel > 0` keeps subtracting until `fuel` reaches 0.",
            "`1..=3` is an inclusive range, so the `for` loop visits 1, 2 and 3.",
        ],
        "key_points": [
            "Conditions must be a real `bool`; Rust never treats numbers as true or false.",
            "`if` and `loop` are expressions that can return values.",
            "`a..b` excludes `b`, while `a..=b` includes it.",
        ],
        "analogy": (
            "`for` is like walking down a numbered row of lockers, `while` is like refilling a cup "
            "until it's full, and `loop` is a treadmill you stay on until you choose to step off."
        ),
        "quiz": {
            "question": "How many times does `for i in 0..5 { }` run its body?",
            "options": ["5 times", "6 times", "4 times", "It never stops"],
            "correct_index": 0,
            "explanation": "`0..5` is a half-open range covering 0, 1, 2, 3 and 4, so the body runs 5 times.",
        },
    },
    {
        "id": "rs4",
        "module_id": "rs-m1",
        "title": "Writing Your Own Functions",
        "concept": "Functions",
        "explanation": (
            "Functions are declared with `fn`, and every parameter must have a type annotation. "
            "The return type comes after `->`, and the last expression in the body (with no semicolon) "
            "becomes the return value. Use `return` only when you want to leave a function early."
        ),
        "code_example": """fn add(a: i32, b: i32) -> i32 {
    a + b // no semicolon: this is the return value
}

fn greet(name: &str) {
    println!("Hello, {name}!");
}

fn main() {
    let total = add(2, 3);
    println!("total = {total}"); // total = 5
    greet("Ferris"); // Hello, Ferris!
}""",
        "code_walkthrough": [
            "`fn add(a: i32, b: i32) -> i32` takes two `i32` values and promises to return an `i32`.",
            "`a + b` has no semicolon, so it's an expression whose value is returned.",
            "`fn greet(name: &str)` has no `->`, so it returns the empty unit type `()`.",
            "`main` is where every Rust program starts running.",
        ],
        "key_points": [
            "Parameter types are always required; return types go after `->`.",
            "The final expression without a semicolon is the return value.",
            "Function and variable names use snake_case by convention.",
        ],
        "analogy": (
            "A function is like a recipe card: it lists the exact ingredients it needs (typed parameters) "
            "and says exactly what dish comes out (the return type)."
        ),
        "quiz": {
            "question": "Why doesn't this compile?\n\nfn five() -> i32 {\n    5;\n}",
            "options": [
                "Functions can't return numbers",
                "`five` needs a parameter",
                "It needs the `return` keyword before every value",
                "`5;` is a statement, so the body returns `()` instead of an `i32`",
            ],
            "correct_index": 3,
            "explanation": "The semicolon turns `5` into a statement. Remove it so `5` is the final expression and gets returned.",
        },
        "try_it": {
            "prompt": "Write a function `square` that takes an `i32` and returns its square, so the program prints 49.",
            "starter_code": '// fn square(...) -> ... { ... }\n\nfn main() {\n    println!("{}", square(7));\n}\n',
            "checks": [
                {
                    "pattern": r"fn\s+square\s*\(\s*\w+\s*:\s*i32\s*\)\s*->\s*i32",
                    "hint": "Start with `fn square(n: i32) -> i32 {`.",
                },
                {
                    "pattern": r"\w+\s*\*\s*\w+|\.pow\s*\(\s*2\s*\)",
                    "hint": "Multiply the number by itself, like `n * n`.",
                },
            ],
            "expected_output": "49",
        },
    },
    {
        "id": "rs5",
        "module_id": "rs-m2",
        "title": "Who Owns This Value?",
        "concept": "Ownership",
        "explanation": (
            "Every value in Rust has exactly one owner, and the value is dropped (freed) when its owner goes "
            "out of scope. Assigning a heap value like a `String` to another variable, or passing it to a "
            "function, moves ownership, and the old variable can no longer be used. Simple types like "
            "integers implement `Copy`, so they are copied instead of moved."
        ),
        "code_example": """fn takes(s: String) {
    println!("took {s}");
}

fn main() {
    let a = String::from("sword");
    let b = a; // ownership moves from a to b
    // println!("{a}"); // error: borrow of moved value: `a`
    let c = b.clone(); // a deep copy, so b stays valid
    println!("{b} {c}"); // sword sword
    takes(c); // took sword
    let n = 5;
    let m = n; // i32 is Copy, so n is still usable
    println!("{n} {m}"); // 5 5
}""",
        "code_walkthrough": [
            "`let b = a;` moves the `String` into `b`; `a` is no longer valid.",
            "Uncommenting the `println!` that uses `a` would fail to compile.",
            "`b.clone()` makes a full copy of the heap data, so both `b` and `c` are usable.",
            "`takes(c)` moves `c` into the function, which drops it when it finishes.",
            "`let m = n;` copies the integer, so both `n` and `m` can be printed.",
        ],
        "key_points": [
            "Each value has one owner, and it's dropped when the owner goes out of scope.",
            "Assigning or passing a `String` moves it; use `.clone()` for an explicit deep copy.",
            "Small `Copy` types like integers, `bool` and `char` are copied, not moved.",
        ],
        "analogy": (
            "Ownership is like handing someone your only house key: once you give it away, you can't "
            "open the door yourself unless you cut a copy (`clone`) first."
        ),
        "quiz": {
            "question": 'What happens if you use `a` after this?\n\nlet a = String::from("hi");\nlet b = a;',
            "options": [
                'It prints "hi" as usual',
                "It prints an empty string",
                "A compile error, because the value moved to `b`",
                "The program panics at runtime",
            ],
            "correct_index": 2,
            "explanation": "`let b = a;` moves ownership of the `String` to `b`, and the compiler rejects any later use of `a`.",
        },
    },
    {
        "id": "rs6",
        "module_id": "rs-m2",
        "title": "Borrowing Without Taking",
        "concept": "Borrowing & References",
        "explanation": (
            "A reference lets you use a value without taking ownership of it, which is called borrowing. "
            "`&T` is a shared reference for reading, and `&mut T` is a mutable reference for changing the value. "
            "The borrow checker enforces one rule: at any moment you can have many `&` references or exactly "
            "one `&mut` reference, but not both."
        ),
        "code_example": """fn count(s: &str) -> usize {
    s.len()
}

fn power_up(s: &mut String) {
    s.push_str("!!");
}

fn main() {
    let mut cry = String::from("charge");
    println!("{}", count(&cry)); // 6
    power_up(&mut cry);
    println!("{cry}"); // charge!!
}""",
        "code_walkthrough": [
            "`fn count(s: &str)` borrows text to read it; the caller keeps ownership.",
            "`count(&cry)` passes a shared reference, and `&String` converts to `&str` automatically.",
            "`fn power_up(s: &mut String)` borrows mutably, so it can change the string in place.",
            "`power_up(&mut cry)` requires `cry` to be declared with `let mut`.",
            "After both borrows end, `cry` is still owned by `main` and prints `charge!!`.",
        ],
        "key_points": [
            "`&value` borrows to read; `&mut value` borrows to modify.",
            "Many shared borrows OR one mutable borrow at a time, never both.",
            "References must never outlive the value they point to.",
        ],
        "analogy": (
            "Borrowing is like a library book: lots of people can read copies of the same page at once, "
            "but only one person at a time gets to write notes in it."
        ),
        "quiz": {
            "question": "Which of these is allowed by the borrow checker?",
            "options": [
                "Two `&mut` references to the same value in use at once",
                "Any number of `&` references to the same value at once",
                "A `&mut` and a `&` reference to the same value in use at once",
                "A reference that outlives the value it points to",
            ],
            "correct_index": 1,
            "explanation": "Shared references only read, so any number of them can coexist. A mutable reference must be the only one in use.",
        },
    },
    {
        "id": "rs7",
        "module_id": "rs-m2",
        "title": "Building Your Own Types with Structs",
        "concept": "Structs & Methods",
        "explanation": (
            "A struct groups related named fields into one custom type. "
            "Methods are defined in an `impl` block, and their first parameter (`&self`, `&mut self` or `self`) "
            "says how they use the instance. Functions without `self`, like `new`, are associated functions "
            "called with `Type::name()`."
        ),
        "code_example": """#[derive(Debug)]
struct Hero { name: String, hp: u32 }

impl Hero {
    fn new(name: &str) -> Self { Hero { name: name.to_string(), hp: 100 } }
    fn take_hit(&mut self, dmg: u32) { self.hp -= dmg; }
    fn is_alive(&self) -> bool { self.hp > 0 }
}

fn main() {
    let mut hero = Hero::new("Ferris");
    hero.take_hit(30);
    println!("{} alive: {}", hero.name, hero.is_alive()); // Ferris alive: true
    println!("{hero:?}"); // Hero { name: "Ferris", hp: 70 }
}""",
        "code_walkthrough": [
            "`struct Hero { name: String, hp: u32 }` defines a type with two named fields.",
            "`#[derive(Debug)]` lets you print the whole struct with `{:?}`.",
            "`Hero::new(...)` is an associated function that builds a hero with 100 hp.",
            "`take_hit(&mut self, ...)` changes a field, so it borrows the hero mutably.",
            "`is_alive(&self)` only reads, so a shared borrow is enough.",
        ],
        "key_points": [
            "Structs bundle named fields into a single type.",
            "Methods live in `impl` blocks and take `self`, `&self` or `&mut self`.",
            "`Self` inside an `impl` block is shorthand for the type being implemented.",
        ],
        "analogy": (
            "A struct is like a character sheet in a role-playing game, and its methods are the "
            "actions that character knows how to perform."
        ),
        "quiz": {
            "question": "What does `&mut self` as a method's first parameter mean?",
            "options": [
                "The method takes ownership of the struct",
                "The method has no access to the struct",
                "The method can only read the struct's fields",
                "The method borrows the struct mutably so it can change its fields",
            ],
            "correct_index": 3,
            "explanation": "`&mut self` is a mutable borrow of the instance, so the method may modify fields without taking ownership.",
        },
    },
    {
        "id": "rs8",
        "module_id": "rs-m2",
        "title": "Enums and Pattern Matching",
        "concept": "Enums & match",
        "explanation": (
            "An enum defines a type that is exactly one of several variants, and each variant can carry its "
            "own data. `match` compares a value against patterns, runs the arm that fits and can pull data "
            "out of the variant. Matches must be exhaustive, so the compiler makes sure you handle every case."
        ),
        "code_example": """enum Move { Walk(u32), Jump, Cast(String) }

fn main() {
    let moves = [Move::Walk(3), Move::Jump, Move::Cast(String::from("fireball"))];
    for m in &moves {
        match m {
            Move::Walk(steps) => println!("walk {steps} steps"), // walk 3 steps
            Move::Jump => println!("jump!"),                     // jump!
            Move::Cast(spell) => println!("cast {spell}"),       // cast fireball
        }
    }
}""",
        "code_walkthrough": [
            "`enum Move` has three variants: `Walk` carries a number, `Jump` carries nothing, `Cast` carries a `String`.",
            "`for m in &moves` borrows each move in turn instead of moving it out of the array.",
            "`Move::Walk(steps)` matches a walk and binds its number to `steps`.",
            "Each arm runs only for its own variant, so the three lines print in order.",
            "Deleting any arm would be a compile error, because the match would no longer be exhaustive.",
        ],
        "key_points": [
            "Enum variants can hold different kinds and amounts of data.",
            "`match` must cover every possible variant; `_` is a catch-all arm.",
            "Patterns can destructure a variant and bind its data to names.",
        ],
        "analogy": (
            "An enum is like a vending machine button panel: you press exactly one button, and `match` "
            "is the machine deciding which snack to drop for each button."
        ),
        "quiz": {
            "question": "What happens if a `match` on an enum doesn't handle every variant and has no `_` arm?",
            "options": [
                "It fails to compile, because matches must be exhaustive",
                "The unhandled variants are silently ignored",
                "It panics at runtime when an unhandled variant appears",
                "It returns a default value",
            ],
            "correct_index": 0,
            "explanation": "The compiler checks that every possible value is covered and reports an error for any missing variant.",
        },
        "try_it": {
            "prompt": 'Add the missing match arm so `Light::Yellow` prints "slow".',
            "starter_code": (
                "enum Light { Red, Yellow, Green }\n\n"
                "fn main() {\n"
                "    for light in [Light::Red, Light::Yellow, Light::Green] {\n"
                "        match light {\n"
                '            Light::Red => println!("stop"),\n'
                '            Light::Green => println!("go"),\n'
                "            // add the missing arm here\n"
                "        }\n"
                "    }\n"
                "}\n"
            ),
            "checks": [
                {
                    "pattern": r"Light\s*::\s*Yellow\s*=>\s*(\{\s*)?println!\s*\(\s*\"slow\"\s*\)",
                    "hint": 'Add the arm `Light::Yellow => println!("slow"),`.',
                },
            ],
            "expected_output": "stop\nslow\ngo",
        },
    },
    {
        "id": "rs9",
        "module_id": "rs-m3",
        "title": "No Nulls, No Exceptions: Option and Result",
        "concept": "Option & Result",
        "explanation": (
            "Rust has no null: a value that might be missing is an `Option<T>`, which is either `Some(value)` "
            "or `None`. An operation that can fail returns a `Result<T, E>`, which is either `Ok(value)` or "
            "`Err(error)`. The `?` operator unwraps an `Ok` or returns the `Err` early, keeping error handling short."
        ),
        "code_example": """fn double(s: &str) -> Result<i32, std::num::ParseIntError> {
    let n: i32 = s.trim().parse()?; // ? returns the Err early
    Ok(n * 2)
}

fn main() {
    let bag = ["potion", "map"];
    println!("{:?}", bag.get(0)); // Some("potion")
    println!("{}", bag.get(5).unwrap_or(&"empty")); // empty
    println!("{:?}", double("21")); // Ok(42)
    match double("abc") {
        Ok(v) => println!("got {v}"),
        Err(e) => println!("error: {e}"), // error: invalid digit found in string
    }
}""",
        "code_walkthrough": [
            "`bag.get(0)` returns `Some(...)` because index 0 exists.",
            '`bag.get(5)` is `None`, so `unwrap_or(&"empty")` supplies a fallback instead of crashing.',
            "`s.trim().parse()?` either gives the parsed number or returns the parse error from `double`.",
            '`double("21")` succeeds and returns `Ok(42)`.',
            '`match` on the `Result` handles both outcomes, printing the error for `"abc"`.',
        ],
        "key_points": [
            "`Option` replaces null: `Some(value)` or `None`.",
            "`Result` represents success or failure: `Ok(value)` or `Err(error)`.",
            "Prefer `match`, `?`, `unwrap_or` and friends over `unwrap()`, which panics on `None` or `Err`.",
        ],
        "analogy": (
            "An `Option` is like a gift box that might be empty, and a `Result` is like a delivery that "
            "arrives either with your package or with a note explaining what went wrong."
        ),
        "quiz": {
            "question": "Inside a function that returns `Result`, what does `?` do when applied to an `Err`?",
            "options": [
                "It panics with the error message",
                "It returns that error early from the enclosing function",
                "It converts the error into `None`",
                "It ignores the error and keeps going",
            ],
            "correct_index": 1,
            "explanation": "`?` unwraps an `Ok` value, but on `Err` it immediately returns the error to the caller.",
        },
    },
    {
        "id": "rs10",
        "module_id": "rs-m3",
        "title": "Growable Lists and Key-Value Maps",
        "concept": "Vectors & HashMaps",
        "explanation": (
            "`Vec<T>` is a growable list of values of one type, stored on the heap. "
            "`HashMap<K, V>` stores values under unique keys for fast lookup. "
            "The `entry` API lets you update a key's value or insert a default in a single step."
        ),
        "code_example": """use std::collections::HashMap;

fn main() {
    let mut scores = vec![40, 10, 30];
    scores.push(20);
    scores.sort();
    println!("{:?} len={}", scores, scores.len()); // [10, 20, 30, 40] len=4
    let mut inventory: HashMap<&str, u32> = HashMap::new();
    inventory.insert("potion", 2);
    *inventory.entry("potion").or_insert(0) += 1;
    *inventory.entry("key").or_insert(0) += 1;
    println!("{:?}", inventory.get("potion")); // Some(3)
    println!("{}", inventory["key"]); // 1
    println!("{}", inventory.len()); // 2
}""",
        "code_walkthrough": [
            "`vec![40, 10, 30]` creates a vector, `push` adds to the end and `sort` orders it in place.",
            "`HashMap::new()` needs `use std::collections::HashMap;` at the top of the file.",
            '`insert("potion", 2)` stores a value under the key "potion".',
            "`entry(k).or_insert(0)` returns a mutable reference to the value, inserting 0 first if the key is missing.",
            '`get` returns an `Option`, while `inventory["key"]` panics if the key doesn\'t exist.',
        ],
        "key_points": [
            "Vectors grow with `push`; `v.get(i)` returns an `Option` while `v[i]` panics when out of range.",
            "HashMaps store unique keys; inserting an existing key replaces its value.",
            "HashMap iteration order is unpredictable, so sort the keys if order matters.",
        ],
        "analogy": (
            "A vector is like a backpack you can keep stuffing items into, and a HashMap is like a wall "
            "of labeled hooks where you hang each item under its own name."
        ),
        "quiz": {
            "question": "What does `map.entry(key).or_insert(0)` give you?",
            "options": [
                "Always a fresh 0, overwriting any old value",
                "A copy of the old value",
                "An `Option` that you must unwrap",
                "A mutable reference to the existing value, or to a newly inserted 0",
            ],
            "correct_index": 3,
            "explanation": "`or_insert` inserts the default only when the key is missing, then returns `&mut V` so you can update it in place.",
        },
    },
    {
        "id": "rs11",
        "module_id": "rs-m3",
        "title": "Shared Behavior with Traits",
        "concept": "Traits",
        "explanation": (
            "A trait defines a set of methods that a type promises to provide, similar to an interface "
            "in other languages. Traits can include default method implementations that types get for free. "
            "Functions can accept any type implementing a trait with `impl Trait` or generic trait bounds."
        ),
        "code_example": """trait Speak {
    fn sound(&self) -> String;
    fn speak(&self) -> String {
        format!("It says {}", self.sound()) // default method
    }
}
struct Cat;
struct Robot { model: u32 }
impl Speak for Cat { fn sound(&self) -> String { "meow".to_string() } }
impl Speak for Robot { fn sound(&self) -> String { format!("beep-{}", self.model) } }
fn greet(x: &impl Speak) { println!("{}", x.speak()); }
fn main() {
    greet(&Cat); // It says meow
    greet(&Robot { model: 7 }); // It says beep-7
}""",
        "code_walkthrough": [
            "`trait Speak` requires a `sound` method and provides a default `speak` method.",
            "`impl Speak for Cat` and `impl Speak for Robot` each supply their own `sound`.",
            "Both types get `speak` for free from the trait's default implementation.",
            "`fn greet(x: &impl Speak)` accepts a reference to any type that implements `Speak`.",
        ],
        "key_points": [
            "A trait lists methods that implementing types must provide.",
            "Default methods let types share behavior without repeating code.",
            "`impl Trait` and generic bounds like `<T: Speak>` accept any implementing type.",
        ],
        "analogy": (
            "A trait is like a job description: any type that signs the contract by implementing its "
            "methods can be hired wherever that job is needed."
        ),
        "quiz": {
            "question": "What does a function with the parameter `x: &impl Speak` accept?",
            "options": [
                "A reference to any type that implements the `Speak` trait",
                "Only the `Speak` trait itself, not real values",
                "Only values of one specific struct",
                "A reference to any type at all",
            ],
            "correct_index": 0,
            "explanation": '`impl Speak` means "some type that implements `Speak`", so the compiler accepts any implementor.',
        },
    },
    {
        "id": "rs12",
        "module_id": "rs-m3",
        "title": "Iterator Chains and Closures",
        "concept": "Iterators & Closures",
        "explanation": (
            "A closure is an anonymous function written `|args| body` that can capture variables from its "
            "surroundings. Iterators produce a sequence of items, and adapters like `map` and `filter` "
            "transform them lazily. Nothing happens until a consumer such as `collect`, `sum` or `count` "
            "pulls the items through."
        ),
        "code_example": """fn main() {
    let scores = vec![12, 45, 7, 30, 21];
    let bonus = 5;
    let add_bonus = |s: &i32| s + bonus; // a closure that captures `bonus`
    let boosted: Vec<i32> = scores.iter().map(add_bonus).collect();
    println!("{:?}", boosted); // [17, 50, 12, 35, 26]
    let high: Vec<i32> = scores.iter().copied().filter(|s| *s >= 20).collect();
    println!("{:?}", high); // [45, 30, 21]
    let total: i32 = scores.iter().sum();
    println!("{total}"); // 115
}""",
        "code_walkthrough": [
            "`|s: &i32| s + bonus` is a closure that reads `bonus` from the surrounding scope.",
            "`scores.iter()` yields references to each score without consuming the vector.",
            "`.map(add_bonus).collect()` applies the closure to every item and gathers the results into a `Vec`.",
            "`.copied().filter(|s| *s >= 20)` keeps only scores of at least 20.",
            "`.sum()` consumes the iterator and adds everything up to 115.",
        ],
        "key_points": [
            "Closures use `|args| body` and can capture variables from their environment.",
            "`iter()` borrows items, while `into_iter()` on a `Vec` takes ownership of them.",
            "Adapters are lazy; a consumer like `collect`, `sum` or `count` runs the chain.",
        ],
        "analogy": (
            "An iterator chain is like an assembly line: `map` and `filter` are stations along the belt, "
            "but nothing moves until `collect` switches the conveyor on."
        ),
        "quiz": {
            "question": "Iterator adapters like `map` and `filter` are lazy. What does that mean?",
            "options": [
                "They run on a background thread",
                "They copy the whole collection before starting",
                "They do no work until a consumer like `collect` or `sum` pulls items through",
                "They can only be used once per program",
            ],
            "correct_index": 2,
            "explanation": "Adapters just build up a description of the work; a consuming method actually drives the iteration.",
        },
        "try_it": {
            "prompt": "Replace the 0 with an iterator chain that counts how many numbers in `nums` are even.",
            "starter_code": (
                "fn main() {\n"
                "    let nums = vec![3, 8, 10, 5, 6];\n"
                "    let evens = 0; // replace 0 with an iterator chain\n"
                '    println!("{evens}");\n'
                "}\n"
            ),
            "checks": [
                {
                    "pattern": r"nums\s*\.\s*(into_)?iter\s*\(\s*\)",
                    "hint": "Start the chain with `nums.iter()`.",
                },
                {
                    "pattern": r"(?s)\.\s*filter\s*\(.*%\s*2\s*==\s*0",
                    "hint": "Keep even numbers with `.filter(|n| *n % 2 == 0)`.",
                },
                {
                    "pattern": r"\.\s*count\s*\(\s*\)",
                    "hint": "Finish with `.count()` to count the remaining items.",
                },
            ],
            "expected_output": "3",
        },
    },
]
