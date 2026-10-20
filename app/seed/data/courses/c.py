"""C Programming: Learn how computers really work by writing fast, close-to-the-metal C."""

COURSE = {
    "id": "c-programming",
    "title": "C Programming",
    "world": "Kernel Kingdom",
    "description": "Learn how computers really work by writing fast, close-to-the-metal C programs.",
    "language": "c",
    "modules": [
        {"id": "c-m1", "title": "Basics & Control Flow"},
        {"id": "c-m2", "title": "Functions, Arrays & Pointers"},
        {"id": "c-m3", "title": "Structs, Memory & Files"},
    ],
}

ZONES = [
    {
        "id": "c-z1",
        "name": "Bitstream Meadows",
        "tagline": "Types, input, output and the flow of a C program.",
        "difficulty": "easy",
        "nodes": [
            {"id": "c1", "title": "Variables & Types", "difficulty": "easy", "xp_reward": 50, "estimated_minutes": 10},
            {"id": "c2", "title": "printf & scanf", "difficulty": "easy", "xp_reward": 50, "estimated_minutes": 10},
            {"id": "c3", "title": "Conditionals", "difficulty": "easy", "xp_reward": 55, "estimated_minutes": 11},
            {"id": "c4", "title": "Loops", "difficulty": "easy", "xp_reward": 60, "estimated_minutes": 12},
        ],
        "boss": {
            "id": "c-z1-boss",
            "name": "Semicolon Slime",
            "sprite": "slime",
            "challenge": "Fix 3 tiny C programs that refuse to compile",
            "stages": 3,
            "xp_reward": 250,
        },
    },
    {
        "id": "c-z2",
        "name": "Pointer Labyrinth",
        "tagline": "Functions, arrays, strings and the addresses behind them.",
        "difficulty": "medium",
        "nodes": [
            {"id": "c5", "title": "Functions", "difficulty": "medium", "xp_reward": 90, "estimated_minutes": 18},
            {"id": "c6", "title": "Arrays", "difficulty": "medium", "xp_reward": 100, "estimated_minutes": 19},
            {"id": "c7", "title": "Strings", "difficulty": "medium", "xp_reward": 100, "estimated_minutes": 19},
            {"id": "c8", "title": "Pointers", "difficulty": "medium", "xp_reward": 110, "estimated_minutes": 20},
        ],
        "boss": {
            "id": "c-z2-boss",
            "name": "Segfault Sludge",
            "sprite": "bugSlime",
            "challenge": "Track down the bad pointers and off-by-one bugs before they crash the maze",
            "stages": 4,
            "xp_reward": 400,
        },
    },
    {
        "id": "c-z3",
        "name": "Heap Forge Citadel",
        "tagline": "Build your own data, manage memory and talk to files.",
        "difficulty": "hard",
        "nodes": [
            {"id": "c9", "title": "Structs", "difficulty": "hard", "xp_reward": 140, "estimated_minutes": 25},
            {"id": "c10", "title": "Dynamic Memory", "difficulty": "hard", "xp_reward": 160, "estimated_minutes": 30},
            {"id": "c11", "title": "File I/O", "difficulty": "hard", "xp_reward": 150, "estimated_minutes": 26},
            {
                "id": "c12",
                "title": "Headers & Preprocessor",
                "difficulty": "hard",
                "xp_reward": 140,
                "estimated_minutes": 25,
            },
        ],
        "boss": {
            "id": "c-z3-boss",
            "name": "Memory Leak Leviathan",
            "sprite": "recursionBoss",
            "challenge": "Plug every leak: allocate, use and free memory without a single slip",
            "stages": 5,
            "xp_reward": 700,
        },
    },
]

LESSONS: list[dict] = [
    {
        "id": "c1",
        "module_id": "c-m1",
        "title": "Storing Values with C Types",
        "concept": "Variables & Data Types",
        "explanation": (
            "In C, every variable has a fixed type that you declare up front, such as `int` for whole numbers, "
            "`double` for decimals and `char` for a single character. "
            "The type decides how much memory the variable uses and how operations behave. "
            "For example, dividing two `int` values throws away the fractional part, so `7 / 2` is `3`."
        ),
        "code_example": r"""#include <stdio.h>

int main(void) {
    int lives = 3;
    double speed = 2.5;
    char grade = 'A';
    printf("%d\n", lives);     // 3
    printf("%.1f\n", speed);   // 2.5
    printf("%c\n", grade);     // A
    printf("%d\n", 7 / 2);     // 3
    printf("%.1f\n", 7 / 2.0); // 3.5
    return 0;
}""",
        "code_walkthrough": [
            "`#include <stdio.h>` brings in `printf` from the standard input/output library.",
            "`int lives = 3;` declares a whole-number variable and gives it a starting value.",
            "`double speed = 2.5;` stores a decimal number, and `char grade = 'A';` stores one character in single quotes.",
            "`%d`, `%.1f` and `%c` tell `printf` to print an int, a double with one decimal place, and a char.",
            "`7 / 2` is integer division (3), but `7 / 2.0` involves a double, so the result is 3.5.",
        ],
        "key_points": [
            "Declare a variable's type before using it: `int`, `double`, `char` and friends.",
            "Always initialize variables; an uninitialized local holds garbage.",
            "Dividing two ints truncates toward zero; use a `double` when you need decimals.",
        ],
        "analogy": (
            "A C variable is like a labeled storage box of a fixed size: an `int` box only holds "
            "whole numbers, and a `char` box only fits one letter."
        ),
        "quiz": {
            "question": "What is the value of `7 / 2` in C when both numbers are `int`?",
            "options": ["3.5", "4", "3", "A compile error"],
            "correct_index": 2,
            "explanation": "Integer division discards the fractional part, so `7 / 2` is `3`. Write `7 / 2.0` to get 3.5.",
        },
    },
    {
        "id": "c2",
        "module_id": "c-m1",
        "title": "Talking to the Player with printf and scanf",
        "concept": "printf and scanf",
        "explanation": (
            "`printf` prints formatted text, replacing format specifiers like `%d` (int), `%f` (double), "
            "`%c` (char) and `%s` (string) with the values you pass. "
            "`scanf` reads input using the same specifiers, but it needs the address of each variable "
            "(written with `&`) so it can store the value there. "
            "`scanf` returns how many values it read successfully, which you should check."
        ),
        "code_example": r"""#include <stdio.h>

int main(void) {
    int age;
    printf("Pi is about %.2f\n", 3.14159);  // Pi is about 3.14
    printf("Enter your age: ");
    if (scanf("%d", &age) == 1) {            // you type: 20
        printf("Next year: %d\n", age + 1);  // Next year: 21
    } else {
        printf("That wasn't a number!\n");
    }
    return 0;
}""",
        "code_walkthrough": [
            "`%.2f` prints a double rounded to two decimal places, so 3.14159 becomes 3.14.",
            r"`\n` is the newline character; without it, the next output continues on the same line.",
            '`scanf("%d", &age)` reads a whole number and stores it at the address of `age`.',
            "`== 1` checks that exactly one value was read before we trust `age`.",
            "If the player types 20, `age + 1` prints as 21.",
        ],
        "key_points": [
            "Match each format specifier to its value's type: `%d` int, `%f` double, `%c` char, `%s` string.",
            "Pass addresses to `scanf` with `&` (except for char arrays, which already act as addresses).",
            "Check `scanf`'s return value so bad input doesn't leave variables uninitialized.",
        ],
        "analogy": (
            "A `printf` format string is like a fill-in-the-blanks form: each `%` specifier is a blank, "
            "and the values you pass fill them in order."
        ),
        "quiz": {
            "question": 'Why do you write `&age` instead of `age` in `scanf("%d", &age)`?',
            "options": [
                "scanf needs the address of age so it can store the value there",
                "It makes age a constant",
                "The & tells scanf to read a decimal number",
                "It prints age after reading it",
            ],
            "correct_index": 0,
            "explanation": "C passes arguments by value, so `scanf` needs a pointer (the address from `&`) to write into your variable.",
        },
        "try_it": {
            "prompt": "Use `printf` with the `%d` specifier and the `score` variable to print `Score: 42`.",
            "starter_code": r"""#include <stdio.h>

int main(void) {
    int score = 42;
    // print "Score: 42" using score

    return 0;
}
""",
            "checks": [
                {
                    "pattern": r"printf\s*\(\s*\"Score:\s*%d(\\n)?\"\s*,\s*score\s*\)",
                    "hint": 'Write `printf("Score: %d\\n", score);` so `%d` is replaced by `score`.',
                },
            ],
            "expected_output": "Score: 42",
        },
    },
    {
        "id": "c3",
        "module_id": "c-m1",
        "title": "Making Decisions with if and else",
        "concept": "Conditional Statements",
        "explanation": (
            "`if`, `else if` and `else` run different blocks of code depending on a condition. "
            "In C, a condition is just a number: `0` means false and any non-zero value means true. "
            "The ternary operator `condition ? a : b` picks between two values in a single expression."
        ),
        "code_example": r"""#include <stdio.h>

int main(void) {
    int hp = 35;
    if (hp > 50) {
        printf("Healthy\n");
    } else if (hp > 20) {
        printf("Wounded\n");                    // Wounded
    } else {
        printf("Critical\n");
    }
    printf("%s\n", hp % 2 == 0 ? "even" : "odd"); // odd
    return 0;
}""",
        "code_walkthrough": [
            "`hp > 50` is false for 35, so the first block is skipped.",
            '`hp > 20` is true, so "Wounded" is printed and the rest of the chain is skipped.',
            "The final `else` only runs when no earlier condition was true.",
            '`hp % 2 == 0 ? "even" : "odd"` checks the remainder; 35 is odd, so it picks "odd".',
        ],
        "key_points": [
            "C treats `0` as false and every non-zero value as true.",
            "Use `==` to compare; a single `=` assigns and is a classic bug inside `if`.",
            "`&&` (and), `||` (or) and `!` (not) combine conditions.",
        ],
        "analogy": (
            "An `if`/`else if` chain is like a castle gate with several guards: you go through "
            "the first gate whose guard says yes and skip all the others."
        ),
        "quiz": {
            "question": "Which of these values counts as false in a C `if` condition?",
            "options": ["1", "-1", "'0'", "0"],
            "correct_index": 3,
            "explanation": "Only zero is false. `-1` is non-zero, and the character `'0'` has the code 48, so both are true.",
        },
    },
    {
        "id": "c4",
        "module_id": "c-m1",
        "title": "Repeating Actions with Loops",
        "concept": "Loops",
        "explanation": (
            "A `for` loop bundles a start, a condition and a step, which makes it ideal for counting. "
            "A `while` loop keeps going as long as its condition is true, and `do ... while` always runs at least once. "
            "`break` exits a loop early and `continue` skips to the next pass."
        ),
        "code_example": r"""#include <stdio.h>

int main(void) {
    for (int i = 1; i <= 3; i++) {
        printf("Level %d\n", i);   // Level 1, Level 2, Level 3
    }
    int coins = 10;
    while (coins > 0) {
        coins -= 4;
    }
    printf("coins = %d\n", coins); // coins = -2
    return 0;
}""",
        "code_walkthrough": [
            "`int i = 1` runs once, `i <= 3` is checked before each pass, and `i++` runs after each pass.",
            "The `for` body prints Level 1, Level 2 and Level 3 on separate lines.",
            "`while (coins > 0)` keeps subtracting 4: 10, 6, 2, then -2.",
            "Once `coins` is -2 the condition is false, so the loop stops and the value is printed.",
        ],
        "key_points": [
            "Use `for` when you know how many times to repeat, and `while` when you repeat until something changes.",
            "Make sure something in the loop moves it toward ending, or it runs forever.",
            "`break` leaves the loop immediately; `continue` jumps to the next iteration.",
        ],
        "analogy": (
            "A `for` loop is like running laps with a lap counter; a `while` loop is like spending "
            "coins until your pouch is empty."
        ),
        "quiz": {
            "question": "How many times does the body of `for (int i = 0; i < 5; i += 2)` run?",
            "options": ["2", "3", "5", "It never stops"],
            "correct_index": 1,
            "explanation": "`i` takes the values 0, 2 and 4. When it reaches 6, `i < 5` is false, so the body runs 3 times.",
        },
        "try_it": {
            "prompt": "Write a `for` loop that prints the numbers 1 to 5, one per line, using `printf`.",
            "starter_code": r"""#include <stdio.h>

int main(void) {
    // print 1 to 5 with a for loop

    return 0;
}
""",
            "checks": [
                {
                    "pattern": r"for\s*\([^;]*;[^;]*(<=\s*5|<\s*6)\s*;",
                    "hint": "Start with `for (int i = 1; i <= 5; i++)`.",
                },
                {
                    "pattern": r"printf\s*\(\s*\"%d\\n\"\s*,",
                    "hint": 'Print each number with `printf("%d\\n", i);`.',
                },
            ],
            "expected_output": "1\n2\n3\n4\n5",
        },
    },
    {
        "id": "c5",
        "module_id": "c-m2",
        "title": "Building Reusable Functions",
        "concept": "Functions",
        "explanation": (
            "A function has a return type, a name and a list of typed parameters, and it hands back a value with `return`. "
            "A prototype (declaration) before `main` lets you call a function that is defined further down the file. "
            "C passes arguments by value, so a function gets its own copy and can't change the caller's variable directly."
        ),
        "code_example": r"""#include <stdio.h>

int square(int n);                   // prototype (declaration)

void try_change(int x) { x = 100; }  // changes only its own copy

int main(void) {
    int a = 7;
    try_change(a);
    printf("%d %d\n", a, square(a)); // 7 49
    return 0;
}

int square(int n) { return n * n; }""",
        "code_walkthrough": [
            "`int square(int n);` tells the compiler the function's signature before it is used.",
            "`void try_change(int x)` returns nothing; `void` means no return value.",
            "`try_change(a)` copies 7 into `x`, so setting `x = 100` leaves `a` untouched.",
            "`square(a)` returns `7 * 7`, so the line prints 7 49.",
            "The full definition of `square` can live after `main` thanks to the prototype.",
        ],
        "key_points": [
            "Declare the return type and every parameter type.",
            "Use a prototype (or define the function first) before calling it.",
            "Arguments are copied; to let a function change a variable, pass its address (coming up in Pointers).",
        ],
        "analogy": (
            "Calling a function is like handing a photocopy of your notes to a friend: they can "
            "scribble on the copy, but your original stays clean."
        ),
        "quiz": {
            "question": "After `void bump(int x) { x++; }` and `int a = 5; bump(a);`, what is `a`?",
            "options": ["6", "0", "5", "It is undefined"],
            "correct_index": 2,
            "explanation": "`bump` receives a copy of `a`, so incrementing `x` does not affect `a`, which stays 5.",
        },
    },
    {
        "id": "c6",
        "module_id": "c-m2",
        "title": "Lining Up Values in Arrays",
        "concept": "Arrays",
        "explanation": (
            "An array stores a fixed number of values of the same type side by side in memory, indexed from 0. "
            "`sizeof array / sizeof array[0]` gives the element count, as long as you use it where the array was declared. "
            "C does not check bounds, so reading or writing past the end is undefined behavior."
        ),
        "code_example": r"""#include <stdio.h>

int main(void) {
    int scores[] = {90, 75, 60, 85};
    int n = sizeof scores / sizeof scores[0];
    int total = 0;
    for (int i = 0; i < n; i++) {
        total += scores[i];
    }
    printf("count = %d\n", n);         // count = 4
    printf("first = %d\n", scores[0]); // first = 90
    printf("total = %d\n", total);     // total = 310
    return 0;
}""",
        "code_walkthrough": [
            "`int scores[] = {90, 75, 60, 85};` lets the compiler size the array from its four values.",
            "`sizeof scores / sizeof scores[0]` divides the array's total bytes by one element's bytes, giving 4.",
            "The loop runs `i` from 0 to 3 and adds each `scores[i]` to `total`.",
            "`scores[0]` is the first element, 90, and the total is 90 + 75 + 60 + 85 = 310.",
        ],
        "key_points": [
            "Indexes run from 0 to length - 1.",
            "C never checks bounds for you, so keep your loop conditions tight.",
            "When an array is passed to a function it becomes a pointer, so pass its length too.",
        ],
        "analogy": (
            "An array is like a row of numbered lockers: every locker is the same size, and you open "
            "one by its number, starting from locker 0."
        ),
        "quiz": {
            "question": "For `int a[5];`, which is the last valid element?",
            "options": ["a[4]", "a[5]", "a[0]", "a[6]"],
            "correct_index": 0,
            "explanation": "Indexes start at 0, so five elements are `a[0]` to `a[4]`. Accessing `a[5]` is out of bounds.",
        },
        "try_it": {
            "prompt": "Finish the loop so it adds every element of `nums` into `sum`.",
            "starter_code": r"""#include <stdio.h>

int main(void) {
    int nums[] = {4, 8, 15, 16};
    int sum = 0;
    for (int i = 0; i < 4; i++) {
        // add nums[i] to sum
    }
    printf("%d\n", sum);
    return 0;
}
""",
            "checks": [
                {
                    "pattern": r"sum\s*(\+=|=\s*sum\s*\+)\s*nums\s*\[\s*i\s*\]",
                    "hint": "Inside the loop, write `sum += nums[i];`.",
                },
            ],
            "expected_output": "43",
        },
    },
    {
        "id": "c7",
        "module_id": "c-m2",
        "title": "Working with Text as char Arrays",
        "concept": "Strings in C",
        "explanation": (
            "C has no built-in string type: a string is an array of `char` that ends with the null character `'\\0'`. "
            "The `<string.h>` library provides helpers such as `strlen` (length), `strcmp` (compare) and `strcat` (append). "
            "Always make sure the destination array is big enough, including room for the final `'\\0'`."
        ),
        "code_example": r"""#include <stdio.h>
#include <string.h>

int main(void) {
    char name[20] = "Ada";
    printf("%s has %zu letters\n", name, strlen(name)); // Ada has 3 letters
    strcat(name, " L.");
    printf("%s\n", name);                               // Ada L.
    printf("%d\n", strcmp(name, "Ada L.") == 0);        // 1
    printf("%c\n", name[0]);                            // A
    return 0;
}""",
        "code_walkthrough": [
            r"""`char name[20] = "Ada";` reserves 20 bytes and stores 'A', 'd', 'a' and a terminating `\0`.""",
            "`strlen(name)` counts characters up to the `\\0`, giving 3; `%zu` prints its `size_t` result.",
            '`strcat(name, " L.")` appends to the end, which fits because `name` has room for 20 bytes.',
            "`strcmp` returns 0 when two strings are equal, so `== 0` evaluates to 1 (true).",
            "`name[0]` is a single `char`, printed with `%c`.",
        ],
        "key_points": [
            "A C string is a `char` array ending in `'\\0'`, so it needs length + 1 bytes.",
            "Compare strings with `strcmp`, never with `==` (that compares addresses).",
            "Prefer bounded functions like `snprintf` to avoid overflowing a buffer.",
        ],
        "analogy": (
            "A C string is like a train of letter cars with a special caboose (`'\\0'`) at the end: "
            "functions keep reading cars until they reach the caboose."
        ),
        "quiz": {
            "question": 'How many bytes does `char word[] = "hi";` take up?',
            "options": ["1", "2", "4", "3"],
            "correct_index": 3,
            "explanation": "The array holds 'h', 'i' and the terminating `'\\0'`, so it is 3 bytes.",
        },
    },
    {
        "id": "c8",
        "module_id": "c-m2",
        "title": "Following Addresses with Pointers",
        "concept": "Pointers",
        "explanation": (
            "A pointer is a variable that stores the memory address of another variable. "
            "`&x` gives the address of `x`, and `*p` (dereferencing) reads or writes the value the pointer points to. "
            "Passing a pointer to a function lets that function change the caller's variable."
        ),
        "code_example": r"""#include <stdio.h>

void add_bonus(int *score) {
    *score += 10;
}

int main(void) {
    int score = 50;
    int *p = &score;
    printf("%d\n", *p);          // 50
    add_bonus(&score);
    printf("%d\n", score);       // 60
    printf("%d\n", p == &score); // 1
    return 0;
}""",
        "code_walkthrough": [
            "`int *p = &score;` declares a pointer to an int and stores the address of `score` in it.",
            "`*p` follows the address and reads the value there, which is 50.",
            "`add_bonus(&score)` passes the address, so `*score += 10` changes the original variable to 60.",
            "`p == &score` is true (1) because `p` still holds the address of `score`.",
        ],
        "key_points": [
            "`&` gets an address; `*` follows one.",
            "Initialize pointers to a valid address or `NULL`, and never dereference `NULL`.",
            "Pointers let functions modify the caller's data and avoid copying big values.",
        ],
        "analogy": (
            "A pointer is like a treasure map: it isn't the treasure itself, but it tells you exactly "
            "where to dig to find (or swap) it."
        ),
        "quiz": {
            "question": "Given `int x = 5; int *p = &x;`, what does `*p = 9;` do?",
            "options": [
                "Makes p point to address 9",
                "Sets x to 9",
                "Creates a new variable holding 9",
                "Causes a compile error",
            ],
            "correct_index": 1,
            "explanation": "`*p` refers to the variable `p` points to, which is `x`, so the assignment sets `x` to 9.",
        },
    },
    {
        "id": "c9",
        "module_id": "c-m3",
        "title": "Grouping Data with Structs",
        "concept": "Structures",
        "explanation": (
            "A `struct` groups related values of different types under one name, like a player's name and level. "
            "You access fields with the dot operator (`hero.level`), or with the arrow operator (`p->level`) "
            "when you have a pointer to the struct. "
            "`typedef` gives the struct type a short name so you don't have to write `struct` every time."
        ),
        "code_example": r"""#include <stdio.h>

typedef struct {
    char name[16];
    int level;
} Player;

int main(void) {
    Player hero = {"Link", 3};
    Player *p = &hero;
    p->level++;
    printf("%s is level %d\n", hero.name, hero.level); // Link is level 4
    return 0;
}""",
        "code_walkthrough": [
            "`typedef struct { ... } Player;` defines a new type with a `name` and a `level` field.",
            '`Player hero = {"Link", 3};` fills the fields in order.',
            "`Player *p = &hero;` makes a pointer to the struct.",
            "`p->level++` is shorthand for `(*p).level++`, raising the level from 3 to 4.",
            "`hero.name` and `hero.level` read the fields with the dot operator.",
        ],
        "key_points": [
            "Use `.` on a struct variable and `->` on a pointer to a struct.",
            "Structs are copied by value when assigned or passed, so pass a pointer for large structs.",
            "`typedef` creates a convenient alias for a struct type.",
        ],
        "analogy": (
            "A struct is like a character sheet in a game: one card that holds the name, level and stats together."
        ),
        "quiz": {
            "question": "Given a pointer `Player *p`, how do you access its `level` field?",
            "options": ["p.level", "&p.level", "p->level", "p[level]"],
            "correct_index": 2,
            "explanation": "The arrow operator `p->level` follows the pointer and picks the field; it means `(*p).level`.",
        },
    },
    {
        "id": "c10",
        "module_id": "c-m3",
        "title": "Borrowing Memory with malloc and free",
        "concept": "Dynamic Memory Allocation",
        "explanation": (
            "`malloc` from `<stdlib.h>` reserves memory on the heap at runtime and returns a pointer to it, "
            "or `NULL` if it fails. "
            "This lets you create arrays whose size you only know while the program runs. "
            "Every block you `malloc` must be released exactly once with `free`, or your program leaks memory."
        ),
        "code_example": r"""#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int n = 5;
    int *squares = malloc(n * sizeof *squares);
    if (squares == NULL) return 1;     // always check!
    for (int i = 0; i < n; i++) squares[i] = i * i;
    printf("%d\n", squares[4]);        // 16
    free(squares);                     // give the memory back
    squares = NULL;                    // avoid a dangling pointer
    return 0;
}""",
        "code_walkthrough": [
            "`malloc(n * sizeof *squares)` asks for room for 5 ints; `sizeof *squares` stays correct if the type changes.",
            "`if (squares == NULL) return 1;` stops safely if the allocation failed.",
            "The loop fills the block like a normal array: 0, 1, 4, 9, 16.",
            "`free(squares)` returns the memory to the system once we're done with it.",
            "Setting `squares = NULL` makes accidental reuse easy to spot instead of silently corrupting memory.",
        ],
        "key_points": [
            "Check `malloc`'s result for `NULL` before using it.",
            "Every `malloc` needs exactly one matching `free`; never use memory after freeing it.",
            "Use `sizeof` to compute byte counts instead of hard-coding sizes.",
        ],
        "analogy": (
            "`malloc` is like renting a storage unit: you get a key (the pointer) to space you asked for, "
            "and `free` is handing the key back so someone else can use it."
        ),
        "quiz": {
            "question": "What must every successful `malloc` eventually be paired with?",
            "options": ["A call to free", "A call to printf", "A second malloc", "A cast to void"],
            "correct_index": 0,
            "explanation": "Heap memory stays reserved until you call `free`. Forgetting it causes a memory leak.",
        },
        "try_it": {
            "prompt": (
                "Allocate room for 3 ints with `malloc`, store 7 in the first slot, print it, "
                "then release the memory with `free`."
            ),
            "starter_code": r"""#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int *nums = NULL;
    // 1. allocate space for 3 ints
    // 2. set the first slot to 7 and print it
    // 3. give the memory back
    return 0;
}
""",
            "checks": [
                {
                    "pattern": r"nums\s*=\s*(\(\s*int\s*\*\s*\)\s*)?malloc\s*\([^;]*sizeof",
                    "hint": "Allocate with `nums = malloc(3 * sizeof(int));`.",
                },
                {
                    "pattern": r"nums\s*\[\s*0\s*\]\s*=\s*7\s*;",
                    "hint": "Store the value with `nums[0] = 7;`.",
                },
                {
                    "pattern": r"free\s*\(\s*nums\s*\)",
                    "hint": "Release the memory with `free(nums);` when you're done.",
                },
            ],
            "expected_output": "7",
        },
    },
    {
        "id": "c11",
        "module_id": "c-m3",
        "title": "Saving and Loading Files",
        "concept": "File Handling",
        "explanation": (
            "`fopen` opens a file and returns a `FILE *`, or `NULL` if it can't. "
            'The mode string chooses what you can do: `"r"` reads, `"w"` writes (erasing old contents) and `"a"` appends. '
            "`fprintf` and `fscanf` work like `printf` and `scanf` but on a file, and `fclose` finishes the job."
        ),
        "code_example": r"""#include <stdio.h>

int main(void) {
    FILE *f = fopen("save.txt", "w");
    if (f == NULL) return 1;
    fprintf(f, "level %d\n", 7);
    fclose(f);

    f = fopen("save.txt", "r");
    if (f == NULL) return 1;
    int level;
    if (fscanf(f, "level %d", &level) == 1) printf("Loaded level %d\n", level); // Loaded level 7
    fclose(f);
    return 0;
}""",
        "code_walkthrough": [
            '`fopen("save.txt", "w")` creates (or empties) the file for writing.',
            "`if (f == NULL) return 1;` handles the case where the file couldn't be opened.",
            '`fprintf(f, "level %d\\n", 7)` writes the text "level 7" into the file.',
            "`fclose(f)` flushes the data to disk and releases the file handle.",
            '`fscanf(f, "level %d", &level)` reads the number back and returns 1 on success.',
        ],
        "key_points": [
            "Always check whether `fopen` returned `NULL`.",
            'Pick the right mode: `"r"` read, `"w"` overwrite, `"a"` append.',
            "Close every file you open with `fclose`.",
        ],
        "analogy": (
            "A file is like a save slot in a game: `fopen` picks the slot, `fprintf` writes your progress, "
            "and `fclose` makes sure the save is really stored."
        ),
        "quiz": {
            "question": 'What happens when you open an existing file with mode `"w"`?',
            "options": [
                "New text is added to the end",
                "fopen returns NULL",
                "The file opens read-only",
                "Its old contents are erased",
            ],
            "correct_index": 3,
            "explanation": '`"w"` truncates the file to zero length (or creates it). Use `"a"` to add to the end instead.',
        },
    },
    {
        "id": "c12",
        "module_id": "c-m3",
        "title": "Sharing Code with Headers and the Preprocessor",
        "concept": "C Preprocessor",
        "explanation": (
            "Before compiling, the preprocessor handles lines starting with `#`: `#include` pastes in a file, "
            "and `#define` creates constants and macros by text replacement. "
            "Header files (`.h`) hold declarations that several `.c` files share, while the definitions live in one `.c` file. "
            "An include guard (`#ifndef` / `#define` / `#endif`) stops a header from being pasted in twice."
        ),
        "code_example": r"""#include <stdio.h>
#ifndef GAME_H                       // include guard, normally inside game.h
#define GAME_H
#define MAX_LEVEL 99
#define SQUARE(x) ((x) * (x))
int clamp_level(int level);          // declaration a header would share
#endif

int main(void) {
    printf("%d\n", clamp_level(120)); // 99
    printf("%d\n", SQUARE(3 + 1));    // 16
    return 0;
}

int clamp_level(int level) { return level > MAX_LEVEL ? MAX_LEVEL : level; }""",
        "code_walkthrough": [
            "`#include <stdio.h>` pastes in the standard header that declares `printf`.",
            "`#ifndef GAME_H` / `#define GAME_H` / `#endif` is an include guard: the block is only used the first time.",
            "`#define MAX_LEVEL 99` replaces every `MAX_LEVEL` with 99 before compiling.",
            "`SQUARE(3 + 1)` expands to `((3 + 1) * (3 + 1))`, which is 16 thanks to the extra parentheses.",
            "`clamp_level(120)` returns `MAX_LEVEL`, so it prints 99.",
        ],
        "key_points": [
            'Use `#include <...>` for system headers and `#include "..."` for your own.',
            "Put declarations in `.h` files, definitions in `.c` files, and guard every header.",
            "Wrap macro parameters and bodies in parentheses to avoid surprising expansions.",
        ],
        "analogy": (
            "A header file is like a restaurant menu: it lists what's available (declarations), "
            "while the kitchen (`.c` file) actually cooks it (definitions)."
        ),
        "quiz": {
            "question": "What problem does an include guard (`#ifndef X_H` / `#define X_H` / `#endif`) solve?",
            "options": [
                "It makes the program run faster",
                "It stops a header's contents from being included twice in one file",
                "It hides functions from other files",
                "It links the standard library",
            ],
            "correct_index": 1,
            "explanation": "Including a header twice would repeat its type and macro definitions and cause redefinition errors; the guard skips the contents the second time.",
        },
    },
]
