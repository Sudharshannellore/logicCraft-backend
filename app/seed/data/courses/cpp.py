"""C++ Foundations: Learn modern C++17, from variables and pointers to classes, templates and the STL."""

COURSE = {
    "id": "cpp-foundations",
    "title": "C++ Foundations",
    "world": "Iron Citadel",
    "description": "Learn modern C++17, from variables and pointers to classes, templates and the STL.",
    "language": "cpp",
    "modules": [
        {"id": "cpp-m1", "title": "Basics & Control Flow"},
        {"id": "cpp-m2", "title": "Functions, Memory & Classes"},
        {"id": "cpp-m3", "title": "Modern C++ & the STL"},
    ],
}

ZONES = [
    {
        "id": "cpp-z1",
        "name": "Semicolon Shores",
        "tagline": "Types, input and output, and the flow of a program.",
        "difficulty": "easy",
        "nodes": [
            {
                "id": "cpp1",
                "title": "Variables & Types",
                "difficulty": "easy",
                "xp_reward": 50,
                "estimated_minutes": 10,
            },
            {"id": "cpp2", "title": "Input & Output", "difficulty": "easy", "xp_reward": 50, "estimated_minutes": 10},
            {"id": "cpp3", "title": "Conditionals", "difficulty": "easy", "xp_reward": 60, "estimated_minutes": 12},
            {"id": "cpp4", "title": "Loops", "difficulty": "easy", "xp_reward": 60, "estimated_minutes": 12},
        ],
        "boss": {
            "id": "cpp-z1-boss",
            "name": "Segfault Slime",
            "sprite": "slime",
            "challenge": "Fix 3 snippets that won't compile or print the wrong thing",
            "stages": 3,
            "xp_reward": 250,
        },
    },
    {
        "id": "cpp-z2",
        "name": "Pointer Pass",
        "tagline": "Functions, memory addresses and your very first classes.",
        "difficulty": "medium",
        "nodes": [
            {
                "id": "cpp5",
                "title": "Functions & Overloading",
                "difficulty": "medium",
                "xp_reward": 90,
                "estimated_minutes": 18,
            },
            {
                "id": "cpp6",
                "title": "References & Pointers",
                "difficulty": "medium",
                "xp_reward": 100,
                "estimated_minutes": 18,
            },
            {
                "id": "cpp7",
                "title": "std::string & std::vector",
                "difficulty": "medium",
                "xp_reward": 100,
                "estimated_minutes": 20,
            },
            {
                "id": "cpp8",
                "title": "Classes & Constructors",
                "difficulty": "medium",
                "xp_reward": 110,
                "estimated_minutes": 20,
            },
        ],
        "boss": {
            "id": "cpp-z2-boss",
            "name": "Dangling Pointer Wraith",
            "sprite": "bugSlime",
            "challenge": "Hunt down pointer and reference bugs before they crash the realm",
            "stages": 4,
            "xp_reward": 400,
        },
    },
    {
        "id": "cpp-z3",
        "name": "Template Forge",
        "tagline": "Polymorphism, generic code and the power tools of the STL.",
        "difficulty": "hard",
        "nodes": [
            {
                "id": "cpp9",
                "title": "Inheritance & Polymorphism",
                "difficulty": "hard",
                "xp_reward": 140,
                "estimated_minutes": 25,
            },
            {"id": "cpp10", "title": "Templates", "difficulty": "hard", "xp_reward": 150, "estimated_minutes": 25},
            {
                "id": "cpp11",
                "title": "STL Containers & Algorithms",
                "difficulty": "hard",
                "xp_reward": 150,
                "estimated_minutes": 28,
            },
            {
                "id": "cpp12",
                "title": "Smart Pointers & RAII",
                "difficulty": "hard",
                "xp_reward": 160,
                "estimated_minutes": 30,
            },
        ],
        "boss": {
            "id": "cpp-z3-boss",
            "name": "Memory Leak Leviathan",
            "sprite": "recursionBoss",
            "challenge": "Refactor leaky new/delete code into safe, modern C++",
            "stages": 5,
            "xp_reward": 700,
        },
    },
]

LESSONS: list[dict] = [
    {
        "id": "cpp1",
        "module_id": "cpp-m1",
        "title": "Storing Values with Types",
        "concept": "Variables and data types",
        "explanation": (
            "C++ is statically typed: every variable has a type such as `int`, `double`, `char`, `bool` or `std::string`, "
            "and that type is fixed when you compile. "
            "The type decides what values fit and how operations behave; for example, dividing two `int`s throws away the remainder. "
            "The `auto` keyword lets the compiler deduce the type from the value you assign."
        ),
        "code_example": r"""#include <iostream>
#include <string>

int main() {
    int lives = 3;
    double speed = 1.5;
    char grade = 'A';
    bool alive = true;
    std::string hero = "Ada";
    auto coins = 42;                                    // deduced as int
    std::cout << hero << " has " << lives << " lives\n";  // Ada has 3 lives
    std::cout << speed * 2 << " " << grade << " " << alive << "\n";  // 3 A 1
    std::cout << coins / 5 << "\n";                     // 8
}""",
        "code_walkthrough": [
            "`int`, `double`, `char` and `bool` are built-in types for whole numbers, decimals, single characters and true/false.",
            '`std::string hero = "Ada";` stores text and needs `#include <string>`.',
            "`auto coins = 42;` lets the compiler deduce `int` from the literal `42`.",
            "`speed * 2` is `3.0`, which `std::cout` prints as `3`, and `true` prints as `1` by default.",
            "`coins / 5` divides two integers, so the result is `8` and the remainder is dropped.",
        ],
        "key_points": [
            "Every variable has a fixed type chosen at compile time.",
            "Integer division truncates: `7 / 2` is `3`, while `7.0 / 2` is `3.5`.",
            "Always initialize variables; an uninitialized local `int` holds garbage.",
        ],
        "analogy": (
            "Types are like differently shaped containers: an egg carton holds eggs, a bottle holds liquid, "
            "and C++ checks you never pour soup into the egg carton."
        ),
        "quiz": {
            "question": "What does this print?\n\nint a = 7;\nint b = 2;\nstd::cout << a / b;",
            "options": ["3.5", "3", "4", "3.0"],
            "correct_index": 1,
            "explanation": "Both operands are `int`, so C++ performs integer division and drops the remainder, giving 3.",
        },
    },
    {
        "id": "cpp2",
        "module_id": "cpp-m1",
        "title": "Talking to the Player with cin and cout",
        "concept": "Basic input and output",
        "explanation": (
            "The `<iostream>` header gives you `std::cout` for printing and `std::cin` for reading keyboard input. "
            "You send values to `std::cout` with `<<` and pull values out of `std::cin` with `>>`, and both can be chained. "
            "Reading with `>>` stops at whitespace, so use `std::getline` when you need a whole line of text."
        ),
        "code_example": r"""#include <iostream>
#include <string>

int main() {
    std::string name;
    int age = 0;
    std::cout << "Name and age? ";
    std::cin >> name >> age;                 // you type: Sam 20
    std::cout << "Hi, " << name << "! Next year you'll be " << age + 1 << ".\n";
    // Hi, Sam! Next year you'll be 21.
}""",
        "code_walkthrough": [
            "`#include <iostream>` brings in `std::cout` and `std::cin`.",
            '`std::cout << "Name and age? ";` prints a prompt without a line break.',
            "`std::cin >> name >> age;` reads one word into `name`, then a number into `age`.",
            "`age + 1` is calculated before printing, because `+` binds tighter than `<<`.",
            '`"\\n"` ends the line; `std::endl` does the same but also flushes the output, which is slower.',
        ],
        "key_points": [
            "`std::cout <<` prints and `std::cin >>` reads; both can be chained.",
            "`std::cin >>` reads one whitespace-separated word or number at a time.",
            'Use `std::getline(std::cin, line)` to read a full line, spaces included, and prefer `"\\n"` over `std::endl`.',
        ],
        "analogy": (
            "`std::cout` is a megaphone pointing at the screen and `std::cin` is an ear listening to the keyboard; "
            "the arrows `<<` and `>>` show which way the words travel."
        ),
        "quiz": {
            "question": "The player types `Ada Lovelace` and presses Enter. What is stored in `name`?\n\nstd::string name;\nstd::cin >> name;",
            "options": ["Ada Lovelace", "Lovelace", "Ada", "Nothing; it's an error"],
            "correct_index": 2,
            "explanation": "`>>` stops reading at whitespace, so only `Ada` is stored. Use `std::getline` to read the whole line.",
        },
    },
    {
        "id": "cpp3",
        "module_id": "cpp-m1",
        "title": "Making Decisions with if and the Ternary",
        "concept": "Conditional statements",
        "explanation": (
            "`if`, `else if` and `else` run different blocks of code depending on whether a condition is true. "
            "The ternary operator `condition ? a : b` picks one of two values in a single expression. "
            "Compare with `==`, `!=`, `<`, `>`, `<=` and `>=`, and combine conditions with `&&`, `||` and `!`."
        ),
        "code_example": r"""#include <iostream>
#include <string>

int main() {
    int hp = 35;
    if (hp > 70) {
        std::cout << "Healthy\n";
    } else if (hp > 30) {
        std::cout << "Wounded\n";   // Wounded
    } else {
        std::cout << "Critical\n";
    }
    std::string status = (hp > 0) ? "alive" : "defeated";
    std::cout << status << "\n";    // alive
}""",
        "code_walkthrough": [
            "`if (hp > 70)` is false because `hp` is 35, so that block is skipped.",
            '`else if (hp > 30)` is true, so "Wounded" is printed and the remaining branches are skipped.',
            "The final `else` only runs when every earlier condition was false.",
            '`(hp > 0) ? "alive" : "defeated"` picks "alive" because the condition is true.',
        ],
        "key_points": [
            "Only the first matching branch of an `if` / `else if` chain runs.",
            "Use `==` to compare; a single `=` assigns, which is a classic bug.",
            "A `switch` statement is a tidy alternative when comparing one integer or enum against many fixed values.",
        ],
        "analogy": (
            "An `if` chain is like a dungeon door with several keyholes: you try them in order, "
            "and the first key that fits decides which room you enter."
        ),
        "quiz": {
            "question": "What does `if (x = 5)` do in C++?",
            "options": [
                "Compares x with 5",
                "Fails to compile",
                "Assigns 5 to x, and the condition is always true",
                "Is true only if x was already 5",
            ],
            "correct_index": 2,
            "explanation": "A single `=` assigns. The expression's value is 5, which is non-zero and therefore true. Use `==` to compare.",
        },
        "try_it": {
            "prompt": 'Use the ternary operator to set `result` to "pass" if `score` is 50 or more, otherwise "fail".',
            "starter_code": r"""#include <iostream>
#include <string>

int main() {
    int score = 72;
    // declare result here using ? :

    std::cout << result << "\n";
}
""",
            "checks": [
                {
                    "pattern": r"(std::string|string|auto|const\s+char\s*\*)\s+result\s*=",
                    "hint": "Declare the variable, for example `std::string result = ...;`.",
                },
                {
                    "pattern": r"score\s*>=\s*50\s*\)?\s*\?\s*\"pass\"\s*:\s*\"fail\"",
                    "hint": 'Use the form `score >= 50 ? "pass" : "fail"`.',
                },
            ],
            "expected_output": "pass",
        },
    },
    {
        "id": "cpp4",
        "module_id": "cpp-m1",
        "title": "Repeating Actions with Loops",
        "concept": "Loops",
        "explanation": (
            "A `for` loop has three parts: a starting statement, a condition checked before each pass, and a step that runs after each pass. "
            "A `while` loop keeps going as long as its condition stays true, which suits loops where you don't know the count in advance. "
            "A range-based `for` (`for (int x : items)`) visits every element of a container."
        ),
        "code_example": r"""#include <iostream>

int main() {
    for (int i = 1; i <= 3; ++i) {
        std::cout << i << " ";               // 1 2 3
    }
    std::cout << "\n";
    int countdown = 3;
    while (countdown > 0) {
        std::cout << countdown-- << "...";   // 3...2...1...
    }
    std::cout << "Go!\n";                    // Go! (same line)
}""",
        "code_walkthrough": [
            "`int i = 1` starts the counter, `i <= 3` is checked before each pass, and `++i` runs after each pass.",
            '`std::cout << i << " ";` prints 1, 2 and 3 separated by spaces.',
            "`while (countdown > 0)` repeats until `countdown` reaches 0.",
            "`countdown--` prints the current value first, then subtracts 1.",
            '`"Go!"` is printed after the loop ends, so the second line reads `3...2...1...Go!`.',
        ],
        "key_points": [
            "Use `for` when you know how many times to repeat.",
            "Use `while` when you repeat until something changes; make sure it eventually becomes false.",
            "`break` exits a loop early and `continue` skips to the next pass.",
        ],
        "analogy": (
            "A `for` loop is like running laps with a lap counter, while a `while` loop is like "
            "running until you hear the whistle."
        ),
        "quiz": {
            "question": "How many times does this loop body run?\n\nfor (int i = 0; i < 5; i += 2) { ... }",
            "options": ["3", "2", "5", "6"],
            "correct_index": 0,
            "explanation": "`i` takes the values 0, 2 and 4. At 6 the condition `i < 5` is false, so the body runs 3 times.",
        },
        "try_it": {
            "prompt": "Write a `for` loop that adds the numbers 1 to 5 into `sum`.",
            "starter_code": r"""#include <iostream>

int main() {
    int sum = 0;
    // write your loop here

    std::cout << sum << "\n";
}
""",
            "checks": [
                {
                    "pattern": r"\bfor\s*\(",
                    "hint": "Start a loop with `for (int i = 1; i <= 5; ++i)`.",
                },
                {
                    "pattern": r"sum\s*(\+=|=\s*sum\s*\+)",
                    "hint": "Add the counter to the total with `sum += i;`.",
                },
            ],
            "expected_output": "15",
        },
    },
    {
        "id": "cpp5",
        "module_id": "cpp-m2",
        "title": "Reusable Code with Functions",
        "concept": "Function overloading",
        "explanation": (
            "A function bundles code under a name, takes typed parameters and declares the type of value it returns (or `void` for nothing). "
            "C++ lets several functions share a name as long as their parameter lists differ; this is called overloading, "
            "and the compiler picks the best match from the arguments. "
            "Parameters can also have default values that are used when the caller leaves them out."
        ),
        "code_example": r"""#include <iostream>
#include <string>

int area(int w, int h) { return w * h; }
double area(double r) { return 3.14159 * r * r; }
void greet(const std::string& name = "player") {
    std::cout << "Welcome, " << name << "!\n";
}

int main() {
    std::cout << area(3, 4) << "\n";    // 12
    std::cout << area(2.0) << "\n";     // 12.5664
    greet();                            // Welcome, player!
    greet("Ada");                       // Welcome, Ada!
}""",
        "code_walkthrough": [
            "`int area(int w, int h)` and `double area(double r)` share a name but take different parameters, so they are overloads.",
            "`area(3, 4)` matches the two-`int` version and returns 12.",
            "`area(2.0)` matches the `double` version; 12.56636 prints as `12.5664` because `std::cout` shows 6 significant digits by default.",
            '`const std::string& name = "player"` passes the string without copying it and supplies a default value.',
            '`greet()` uses the default, while `greet("Ada")` overrides it.',
        ],
        "key_points": [
            "A function declares its parameter types and return type; `void` means it returns nothing.",
            "Overloads must differ in their parameter lists; a different return type alone is not enough.",
            "Pass large objects like strings by `const` reference to avoid copying them.",
        ],
        "analogy": (
            "Overloading is like a universal remote's power button: you press the same button, "
            "and it does the right thing for whichever device it is pointed at."
        ),
        "quiz": {
            "question": "Two functions named `area` can NOT be overloaded if they differ only in...",
            "options": [
                "the number of parameters",
                "the types of their parameters",
                "the order of differently typed parameters",
                "their return type",
            ],
            "correct_index": 3,
            "explanation": "The compiler chooses an overload from the arguments in the call, so the return type alone can't tell them apart.",
        },
        "try_it": {
            "prompt": "Write a function `square` that takes an `int` and returns it multiplied by itself.",
            "starter_code": r"""#include <iostream>

// write your function here

int main() {
    std::cout << square(7) << "\n";
}
""",
            "checks": [
                {
                    "pattern": r"int\s+square\s*\(\s*(const\s+)?int\s+\w+\s*\)",
                    "hint": "Start with the signature `int square(int n)`.",
                },
                {
                    "pattern": r"return\s+\(?\s*\w+\s*\*\s*\w+",
                    "hint": "Return the parameter times itself, like `return n * n;`.",
                },
            ],
            "expected_output": "49",
        },
    },
    {
        "id": "cpp6",
        "module_id": "cpp-m2",
        "title": "Aliases and Addresses: References and Pointers",
        "concept": "Pointers and references",
        "explanation": (
            "A reference (`int&`) is another name for an existing variable, so changing the reference changes the original. "
            "A pointer (`int*`) stores the memory address of a variable: `&x` gets the address and `*ptr` follows it back to the value. "
            "Unlike a reference, a pointer can be reassigned or be `nullptr`, meaning it points at nothing."
        ),
        "code_example": r"""#include <iostream>

void levelUp(int& level) { level += 1; }

int main() {
    int level = 1;
    levelUp(level);
    std::cout << level << "\n";    // 2
    int* ptr = &level;             // ptr holds level's address
    *ptr = 10;                     // change level through the pointer
    std::cout << level << "\n";    // 10
    int& alias = level;
    alias++;
    std::cout << *ptr << "\n";     // 11
}""",
        "code_walkthrough": [
            "`void levelUp(int& level)` takes a reference, so it changes the caller's variable instead of a copy.",
            "`int* ptr = &level;` stores the address of `level` in a pointer.",
            "`*ptr = 10;` dereferences the pointer and writes 10 into `level`.",
            "`int& alias = level;` makes `alias` another name for `level`, so `alias++` makes it 11.",
            "`*ptr` reads through the pointer and sees the same updated value: 11.",
        ],
        "key_points": [
            "Use references to let a function modify an argument, or `const` references to read it without copying.",
            "`&x` gives an address, and `*ptr` dereferences a pointer to reach the value.",
            "A pointer can be `nullptr`; never dereference a null or dangling pointer.",
        ],
        "analogy": (
            "A reference is a nickname for a friend, while a pointer is a slip of paper with their home address: "
            "you can rewrite the slip to point at someone else, or leave it blank."
        ),
        "quiz": {
            "question": "What is the value of `a` after this code runs?\n\nint a = 5;\nint* p = &a;\n*p = 8;",
            "options": ["5", "8", "The address of a", "13"],
            "correct_index": 1,
            "explanation": "`p` points at `a`, so `*p = 8` writes 8 directly into `a`.",
        },
    },
    {
        "id": "cpp7",
        "module_id": "cpp-m2",
        "title": "Text and Lists: std::string and std::vector",
        "concept": "Strings and vectors",
        "explanation": (
            "`std::string` holds text and grows automatically as you add to it, so you never manage its memory yourself. "
            "`std::vector` is a resizable array that keeps elements in order and adds new ones at the end with `push_back`. "
            "Both know their own `size()` and work with range-based `for` loops."
        ),
        "code_example": r"""#include <iostream>
#include <string>
#include <vector>

int main() {
    std::string hero = "Knight";
    hero += " Ada";
    std::cout << hero << " (" << hero.size() << " chars)\n";  // Knight Ada (10 chars)
    std::vector<std::string> bag{"sword", "potion"};
    bag.push_back("map");
    std::cout << bag.size() << " " << bag[0] << "\n";         // 3 sword
    for (const auto& item : bag) std::cout << item << " ";    // sword potion map
}""",
        "code_walkthrough": [
            '`hero += " Ada";` appends text, making the string "Knight Ada".',
            "`hero.size()` returns the number of characters: 10.",
            '`std::vector<std::string> bag{"sword", "potion"};` creates a vector of strings with two items.',
            '`bag.push_back("map");` adds an item to the end, so `bag.size()` is 3 and `bag[0]` is "sword".',
            "`for (const auto& item : bag)` visits each item by `const` reference, avoiding copies.",
        ],
        "key_points": [
            "Prefer `std::string` and `std::vector` over raw C arrays and `char*` strings.",
            "`push_back` adds to the end of a vector, and `size()` reports how many elements it has.",
            "`v[i]` doesn't check bounds, while `v.at(i)` throws `std::out_of_range` if `i` is invalid.",
        ],
        "analogy": (
            "A `std::vector` is like an adventurer's bag that magically grows a new pocket every time "
            "you pick up another item."
        ),
        "quiz": {
            "question": "Which expression reads element `i` of vector `v` with bounds checking?",
            "options": ["v[i]", "v.get(i)", "v.at(i)", "v(i)"],
            "correct_index": 2,
            "explanation": "`v.at(i)` checks the index and throws `std::out_of_range` if it's invalid. `v[i]` skips the check, and the other two don't exist.",
        },
    },
    {
        "id": "cpp8",
        "module_id": "cpp-m2",
        "title": "Building Your Own Types with Classes",
        "concept": "Classes and constructors",
        "explanation": (
            "A class bundles data (member variables) with the functions that work on it (member functions). "
            "A constructor runs when an object is created and sets up its members, ideally with a member initializer list. "
            "Keeping data `private` and exposing `public` functions lets the class protect its own rules."
        ),
        "code_example": r"""#include <iostream>
#include <string>
class Player {
    std::string name_;   // members are private by default
    int hp_;
public:
    Player(const std::string& name, int hp) : name_(name), hp_(hp) {}
    void takeHit(int dmg) { hp_ -= dmg; }
    void show() const { std::cout << name_ << ": " << hp_ << " HP\n"; }
};
int main() {
    Player p("Ada", 100);
    p.takeHit(30);
    p.show();   // Ada: 70 HP
}""",
        "code_walkthrough": [
            "`name_` and `hp_` come before `public:`, so they are private and only the class's own functions can touch them.",
            "`Player(...) : name_(name), hp_(hp) {}` is a constructor that initializes the members with an initializer list.",
            "`void takeHit(int dmg)` is a member function that changes the object's state.",
            "`void show() const` promises not to modify the object, so it can be called on `const` players too.",
            '`Player p("Ada", 100);` calls the constructor; after `takeHit(30)`, `show()` prints "Ada: 70 HP".',
        ],
        "key_points": [
            "A `class` defaults to `private` members; a `struct` defaults to `public`.",
            "Constructors set up an object; prefer the member initializer list (`: name_(name)`).",
            "Mark member functions that don't change the object as `const`.",
        ],
        "analogy": (
            "A class is a blueprint for a game character, and each object is a character built from it, "
            "with its own name and health bar."
        ),
        "quiz": {
            "question": "In a `class`, members are ___ unless you say otherwise.",
            "options": ["private", "public", "protected", "static"],
            "correct_index": 0,
            "explanation": "A `class` defaults to `private` access. A `struct` is identical except that it defaults to `public`.",
        },
    },
    {
        "id": "cpp9",
        "module_id": "cpp-m3",
        "title": "Family Trees of Classes: Inheritance and Polymorphism",
        "concept": "Inheritance and polymorphism",
        "explanation": (
            "Inheritance lets a derived class reuse and extend a base class, as in `struct Dragon : Enemy`. "
            "Marking a member function `virtual` lets a derived class override it, and calls through a base reference or pointer "
            "then run the derived version at runtime; this is polymorphism. "
            "A base class used this way should have a `virtual` destructor so objects are cleaned up correctly."
        ),
        "code_example": r"""#include <iostream>

struct Enemy {
    virtual ~Enemy() = default;
    virtual void attack() const { std::cout << "Enemy attacks!\n"; }
};
struct Dragon : Enemy {
    void attack() const override { std::cout << "Dragon breathes fire!\n"; }
};
void fight(const Enemy& e) { e.attack(); }
int main() {
    Dragon drake;
    fight(Enemy{});   // Enemy attacks!
    fight(drake);     // Dragon breathes fire!
}""",
        "code_walkthrough": [
            "`struct Enemy` is the base class; `virtual void attack()` allows derived classes to override it.",
            "`virtual ~Enemy() = default;` makes destruction through a base pointer safe.",
            "`struct Dragon : Enemy` inherits publicly (the default for a `struct`) and `override` asks the compiler to confirm it really overrides.",
            "`fight` takes a `const Enemy&`, so it accepts any kind of enemy.",
            "`fight(drake)` calls `Dragon::attack` at runtime even though `fight` only knows it has an `Enemy`.",
        ],
        "key_points": [
            "Derived classes inherit the members of their base class.",
            "`virtual` plus a base reference or pointer gives runtime polymorphism; always add `override` in the derived class.",
            "Give polymorphic base classes a `virtual` destructor.",
        ],
        "analogy": (
            'Polymorphism is like a general shouting "Attack!": every soldier hears the same order, '
            "but archers shoot, knights charge and dragons breathe fire."
        ),
        "quiz": {
            "question": "In the example, if you remove `virtual` from `Enemy::attack` and `override` from `Dragon::attack`, what does `fight(drake)` print?",
            "options": ["Dragon breathes fire!", "Enemy attacks!", "Both lines", "Nothing; it no longer compiles"],
            "correct_index": 1,
            "explanation": "Without `virtual`, the call is resolved at compile time using the reference's type, `Enemy`, so `Enemy::attack` runs.",
        },
    },
    {
        "id": "cpp10",
        "module_id": "cpp-m3",
        "title": "Write Once, Use Everywhere: Templates",
        "concept": "Templates",
        "explanation": (
            "A template is a recipe the compiler uses to generate code for whatever types you use it with. "
            "A function template like `template <typename T> T biggest(T a, T b)` works for `int`, `double`, `std::string` "
            "and any other type that supports the operations inside it. "
            "The compiler usually deduces `T` from the arguments, but you can also spell it out, as in `biggest<std::string>(...)`."
        ),
        "code_example": r"""#include <iostream>
#include <string>

template <typename T>
T biggest(T a, T b) {
    return (a > b) ? a : b;
}

int main() {
    std::cout << biggest(3, 9) << "\n";                       // 9
    std::cout << biggest(2.5, 1.5) << "\n";                   // 2.5
    std::cout << biggest<std::string>("ant", "bee") << "\n";  // bee
}""",
        "code_walkthrough": [
            "`template <typename T>` declares a placeholder type named `T`.",
            "`biggest(3, 9)` deduces `T` as `int` and returns 9.",
            "`biggest(2.5, 1.5)` deduces `T` as `double` and returns 2.5.",
            '`biggest<std::string>("ant", "bee")` sets `T` explicitly, so the text is compared alphabetically and "bee" wins.',
            "Without `<std::string>`, `T` would be a `const char*` and the call would compare memory addresses instead of text.",
        ],
        "key_points": [
            "Templates generate type-specific code at compile time, with no runtime cost.",
            "The standard library is built on templates: `std::vector<int>` is a class template filled in with `int`.",
            "Every argument must agree on `T`, or you need to name the type explicitly.",
        ],
        "analogy": (
            "A template is like a cookie cutter: one shape, and you can press it into chocolate, ginger or "
            "sugar dough to get the same cookie in different flavors."
        ),
        "quiz": {
            "question": "Using the `biggest` template from the example, what happens with `biggest(3, 2.5)`?",
            "options": [
                "It returns 3",
                "It returns 2.5",
                "It returns 3.0",
                "A compile error, because T can't be both int and double",
            ],
            "correct_index": 3,
            "explanation": "The compiler deduces `T` as `int` from the first argument and `double` from the second, which conflict. Write `biggest<double>(3, 2.5)` to fix it.",
        },
    },
    {
        "id": "cpp11",
        "module_id": "cpp-m3",
        "title": "The STL Toolbox: Containers and Algorithms",
        "concept": "STL containers and algorithms",
        "explanation": (
            "The Standard Template Library gives you ready-made containers such as `std::vector` and `std::map`, "
            "plus algorithms such as `std::sort` and `std::find` that work on them through iterators. "
            "`std::map` stores key-value pairs sorted by key, and `std::sort(v.begin(), v.end())` sorts a range in place. "
            "Reaching for the STL first gives you fast, well-tested code with far less effort."
        ),
        "code_example": r"""#include <algorithm>
#include <iostream>
#include <map>
#include <string>
#include <vector>

int main() {
    std::vector<int> scores{40, 90, 15, 70};
    std::sort(scores.begin(), scores.end());
    std::cout << scores.front() << " to " << scores.back() << "\n";  // 15 to 90
    std::map<std::string, int> bag{{"potion", 3}, {"arrow", 20}};
    bag["potion"] += 2;
    for (const auto& [item, count] : bag)
        std::cout << item << ": " << count << "\n";  // arrow: 20, then potion: 5
}""",
        "code_walkthrough": [
            "`std::sort(scores.begin(), scores.end())` sorts the whole vector in ascending order: 15 40 70 90.",
            "`scores.front()` and `scores.back()` read the first and last elements.",
            "`std::map<std::string, int>` maps item names to counts and keeps keys in sorted order.",
            '`bag["potion"] += 2;` updates an existing entry; with a missing key, `[]` would first insert it with value 0.',
            "`const auto& [item, count]` is a C++17 structured binding that unpacks each key-value pair.",
        ],
        "key_points": [
            "Algorithms like `std::sort` take an iterator range: `begin()` to `end()`.",
            "`std::map` keeps keys sorted; use `std::unordered_map` when you only need fast lookups.",
            "`map[key]` inserts a default value for a missing key, while `map.find(key)` and `map.count(key)` only look.",
        ],
        "analogy": (
            "The STL is like a fully stocked workshop: instead of forging your own hammer and saw, "
            "you grab well-made tools off the wall and get building."
        ),
        "quiz": {
            "question": 'What does this print?\n\nstd::map<std::string, int> m;\nstd::cout << m["gem"];',
            "options": [
                '0, and "gem" is added to the map',
                "It throws std::out_of_range",
                "A random garbage value",
                "Nothing; it doesn't compile",
            ],
            "correct_index": 0,
            "explanation": '`operator[]` inserts a missing key with a value-initialized value, which is 0 for `int`. Use `m.at("gem")` if you want an exception instead.',
        },
        "try_it": {
            "prompt": "Use `std::sort` to put `nums` in ascending order.",
            "starter_code": r"""#include <algorithm>
#include <iostream>
#include <vector>

int main() {
    std::vector<int> nums{5, 2, 8, 1};
    // sort nums here

    for (int n : nums) std::cout << n << " ";
}
""",
            "checks": [
                {
                    "pattern": r"sort\s*\(\s*(nums\s*\.\s*begin\s*\(\s*\)\s*,\s*nums\s*\.\s*end\s*\(\s*\)|nums\s*\))",
                    "hint": "Call `std::sort(nums.begin(), nums.end());`.",
                },
            ],
            "expected_output": "1 2 5 8",
        },
    },
    {
        "id": "cpp12",
        "module_id": "cpp-m3",
        "title": "Never Leak Again: Smart Pointers and RAII",
        "concept": "Smart pointers",
        "explanation": (
            "RAII (Resource Acquisition Is Initialization) means an object grabs a resource in its constructor and releases it "
            "in its destructor, which runs automatically when the object goes out of scope. "
            "Smart pointers apply RAII to heap memory: `std::unique_ptr` is the single owner of an object, "
            "and `std::shared_ptr` counts its owners and frees the object when the last one is gone. "
            "Create them with `std::make_unique` and `std::make_shared` instead of writing `new` and `delete` by hand."
        ),
        "code_example": r"""#include <iostream>
#include <memory>
struct Torch {
    Torch() { std::cout << "Torch lit\n"; }
    ~Torch() { std::cout << "Torch out\n"; }
};
int main() {
    {
        auto torch = std::make_unique<Torch>();   // Torch lit
        auto gold = std::make_shared<int>(7);
        auto copy = gold;                         // two owners now
        std::cout << *copy << " " << gold.use_count() << "\n";  // 7 2
    }   // scope ends: Torch out (freed automatically)
    std::cout << "Left the cave\n";               // Left the cave
}""",
        "code_walkthrough": [
            '`std::make_unique<Torch>()` creates a `Torch` on the heap, so its constructor prints "Torch lit".',
            "`std::make_shared<int>(7)` creates a shared integer, and `auto copy = gold;` adds a second owner.",
            "`gold.use_count()` reports how many `shared_ptr`s own the value: 2.",
            '`}` ends the inner scope, so the smart pointers are destroyed and the `Torch` destructor prints "Torch out".',
            "No `delete` is written anywhere, yet nothing leaks.",
        ],
        "key_points": [
            "Use `std::unique_ptr` by default; it can be moved but not copied.",
            "Use `std::shared_ptr` only when ownership is truly shared.",
            "RAII ties a resource's lifetime to a scope, so cleanup happens even when errors occur.",
        ],
        "analogy": (
            "A smart pointer is like a library book with an automatic return: when you leave the library (the scope), "
            "the book goes back on the shelf without you having to remember."
        ),
        "quiz": {
            "question": "Which of these pointer types can NOT be copied?",
            "options": ["std::shared_ptr", "std::weak_ptr", "A raw pointer (int*)", "std::unique_ptr"],
            "correct_index": 3,
            "explanation": "`std::unique_ptr` represents sole ownership, so it can only be moved with `std::move`, never copied.",
        },
    },
]
