"""Go Essentials: Learn modern Go, from variables to goroutines, and build fast, reliable programs."""

COURSE = {
    "id": "go-essentials",
    "title": "Go Essentials",
    "world": "Gopher Kingdom",
    "description": "Learn modern Go, from variables to goroutines, and build fast, reliable programs.",
    "language": "go",
    "modules": [
        {"id": "go-m1", "title": "Go Basics"},
        {"id": "go-m2", "title": "Data & Types"},
        {"id": "go-m3", "title": "Errors & Concurrency"},
    ],
}

ZONES = [
    {
        "id": "go-z1",
        "name": "Gopher Meadows",
        "tagline": "Variables, decisions, loops and your first functions.",
        "difficulty": "easy",
        "nodes": [
            {"id": "go1", "title": "Variables & Types", "difficulty": "easy", "xp_reward": 50, "estimated_minutes": 10},
            {"id": "go2", "title": "If & Switch", "difficulty": "easy", "xp_reward": 50, "estimated_minutes": 10},
            {"id": "go3", "title": "For Loops", "difficulty": "easy", "xp_reward": 60, "estimated_minutes": 12},
            {"id": "go4", "title": "Functions", "difficulty": "easy", "xp_reward": 60, "estimated_minutes": 12},
        ],
        "boss": {
            "id": "go-z1-boss",
            "name": "Unused Import Slime",
            "sprite": "slime",
            "challenge": "Fix 3 little programs that Go's strict compiler refuses to build",
            "stages": 3,
            "xp_reward": 250,
        },
    },
    {
        "id": "go-z2",
        "name": "Struct Canyon",
        "tagline": "Slices, maps and your own types with behavior.",
        "difficulty": "medium",
        "nodes": [
            {"id": "go5", "title": "Slices", "difficulty": "medium", "xp_reward": 90, "estimated_minutes": 18},
            {"id": "go6", "title": "Maps", "difficulty": "medium", "xp_reward": 100, "estimated_minutes": 18},
            {
                "id": "go7",
                "title": "Structs & Methods",
                "difficulty": "medium",
                "xp_reward": 100,
                "estimated_minutes": 20,
            },
            {"id": "go8", "title": "Interfaces", "difficulty": "medium", "xp_reward": 110, "estimated_minutes": 20},
        ],
        "boss": {
            "id": "go-z2-boss",
            "name": "Nil Map Beetle",
            "sprite": "bugSlime",
            "challenge": "Model a game inventory with slices, maps, structs and interfaces",
            "stages": 4,
            "xp_reward": 400,
        },
    },
    {
        "id": "go-z3",
        "name": "Goroutine Volcano",
        "tagline": "Handle errors, run code concurrently and ship real modules.",
        "difficulty": "hard",
        "nodes": [
            {"id": "go9", "title": "Error Handling", "difficulty": "hard", "xp_reward": 140, "estimated_minutes": 25},
            {"id": "go10", "title": "Goroutines", "difficulty": "hard", "xp_reward": 150, "estimated_minutes": 28},
            {"id": "go11", "title": "Channels", "difficulty": "hard", "xp_reward": 160, "estimated_minutes": 30},
            {
                "id": "go12",
                "title": "Packages & Modules",
                "difficulty": "hard",
                "xp_reward": 140,
                "estimated_minutes": 25,
            },
        ],
        "boss": {
            "id": "go-z3-boss",
            "name": "Deadlock Dragon",
            "sprite": "recursionBoss",
            "challenge": "Coordinate goroutines and channels without a single deadlock, stage by stage",
            "stages": 5,
            "xp_reward": 700,
        },
    },
]

LESSONS: list[dict] = [
    {
        "id": "go1",
        "module_id": "go-m1",
        "title": "Variables, Constants and Types",
        "concept": "Variables & Types",
        "explanation": (
            "Go is statically typed: every variable has a type that is fixed when the program is compiled. "
            "Declare variables with `var name type = value` or, inside functions, the short form `name := value`, which infers the type. "
            'A variable declared without a value starts at its type\'s zero value, such as `0`, `""` or `false`, and `const` creates values that never change.'
        ),
        "code_example": """package main

import "fmt"

func main() {
\tvar name string = "Gopher"
\tage := 13
\tconst pi = 3.14
\tvar score int
\tfmt.Println(name, age, pi, score) // Gopher 13 3.14 0
\tfmt.Printf("%T %T\\n", age, pi)    // int float64
}""",
        "code_walkthrough": [
            '`var name string = "Gopher"` declares a string variable with an explicit type.',
            "`age := 13` uses the short declaration, and Go infers the type `int`.",
            "`const pi = 3.14` creates a constant that can never be reassigned.",
            "`var score int` has no value, so it starts at the zero value `0`.",
            "`%T` in `fmt.Printf` prints a value's type: `int` and `float64`.",
        ],
        "key_points": [
            "Use `:=` inside functions; use `var` at package level or when you want the zero value.",
            "An unused local variable is a compile error in Go, which keeps code tidy.",
            'Every type has a zero value: `0` for numbers, `""` for strings and `false` for booleans.',
        ],
        "analogy": (
            "A Go variable is like a labeled storage box built for one kind of item: "
            "a box made for numbers can never suddenly hold a string."
        ),
        "quiz": {
            "question": "What is the value of `s` after `var s string`?",
            "options": ["`nil`", '`""` (an empty string)', "`0`", "`undefined`"],
            "correct_index": 1,
            "explanation": 'A variable declared without a value gets its type\'s zero value, and the zero value of a string is the empty string `""`.',
        },
    },
    {
        "id": "go2",
        "module_id": "go-m1",
        "title": "Making Decisions with if and switch",
        "concept": "Conditionals & Switch",
        "explanation": (
            "Go's `if` needs no parentheses around the condition, but the curly braces are always required. "
            "Both `if` and `switch` can begin with a short statement, like `if x := 5; x > 3`, whose variable only exists inside that block. "
            "A `switch` runs the first matching `case` and then stops, so you never need to write `break`."
        ),
        "code_example": """package main

import "fmt"

func main() {
\tif score := 72; score >= 50 {
\t\tfmt.Println("Pass") // Pass
\t}
\tswitch day := "Sat"; day {
\tcase "Sat", "Sun":
\t\tfmt.Println("Weekend!") // Weekend!
\tdefault:
\t\tfmt.Println("Weekday")
\t}
}""",
        "code_walkthrough": [
            "`if score := 72; score >= 50` declares `score` and tests it in one line; `score` only exists inside the `if`.",
            'The condition is true, so "Pass" is printed.',
            '`switch day := "Sat"; day` compares `day` against each `case` from top to bottom.',
            '`case "Sat", "Sun":` matches either value, so "Weekend!" is printed.',
            "`default` runs only when no other case matches, so it is skipped here.",
        ],
        "key_points": [
            "No parentheses around conditions, but braces are mandatory.",
            "Go's `switch` doesn't fall through to the next case unless you write `fallthrough`.",
            "A `switch` with no value (`switch { case x > 5: ... }`) is a clean replacement for long if-else chains.",
        ],
        "analogy": (
            "A `switch` is like a train station's departure board: you find the first line that "
            "matches your destination, board it, and ignore the rest."
        ),
        "quiz": {
            "question": "In Go, what happens after the code in a matching `case` finishes?",
            "options": [
                "Execution falls through into the next case",
                "The program panics unless you write `break`",
                "The switch starts again from the top",
                "The switch ends, because Go doesn't fall through by default",
            ],
            "correct_index": 3,
            "explanation": "Unlike C or JavaScript, Go stops after the matching case. You only get fall-through when you explicitly write `fallthrough`.",
        },
    },
    {
        "id": "go3",
        "module_id": "go-m1",
        "title": "One Loop to Rule Them All: for",
        "concept": "For Loops",
        "explanation": (
            "`for` is Go's only loop keyword, but it covers every style of looping. "
            "The classic form has an init, a condition and a post statement, like `for i := 0; i < 3; i++`. "
            "Keep only the condition to get a while-style loop, or use `for ... range` to walk through slices, maps, strings and (since Go 1.22) integers."
        ),
        "code_example": """package main

import "fmt"

func main() {
\tfor i := 1; i <= 3; i++ {
\t\tfmt.Println("Lap", i) // Lap 1, Lap 2, Lap 3
\t}
\tn := 1
\tfor n < 100 { // Go's version of "while"
\t\tn *= 2
\t}
\tfmt.Println(n) // 128
}""",
        "code_walkthrough": [
            "`for i := 1; i <= 3; i++` starts at 1, keeps going while `i <= 3` and adds 1 after each pass.",
            '`fmt.Println("Lap", i)` prints Lap 1, Lap 2 and Lap 3 on separate lines.',
            "`for n < 100` has only a condition, so it works like a `while` loop.",
            "`n *= 2` doubles `n` (2, 4, 8 ... 64, 128); once it reaches 128 the condition is false and the loop ends.",
        ],
        "key_points": [
            "Go has no `while` or `do-while`; `for` does it all, and a bare `for { }` loops forever.",
            "`break` exits a loop early and `continue` skips to the next pass.",
            "`for i, v := range items` gives each index and value; use `_` to ignore one of them.",
        ],
        "analogy": (
            "Go's `for` is like a Swiss Army knife: one tool that folds out into whichever kind of loop you need."
        ),
        "quiz": {
            "question": "Which keyword does Go use for ALL of its loops?",
            "options": ["`for`", "`while`", "`loop`", "`repeat`"],
            "correct_index": 0,
            "explanation": "Go has just one loop keyword, `for`. A condition-only `for` replaces `while`, and a bare `for { }` loops forever.",
        },
        "try_it": {
            "prompt": "Write a classic `for` loop that prints the numbers 1 to 5, one per line.",
            "starter_code": """package main

import "fmt"

func main() {
\t// print the numbers 1 to 5, one per line
}
""",
            "checks": [
                {
                    "pattern": r"for\s+(\w+)\s*:=\s*1\s*;\s*\1\s*(<=\s*5|<\s*6)\s*;\s*\1\s*(\+\+|\+=\s*1)",
                    "hint": "Use the classic form: `for i := 1; i <= 5; i++ {`.",
                },
                {
                    "pattern": r"fmt\s*\.\s*Println\s*\(\s*\w+\s*\)",
                    "hint": "Inside the loop, print the counter with `fmt.Println(i)`.",
                },
            ],
            "expected_output": "1\n2\n3\n4\n5",
        },
    },
    {
        "id": "go4",
        "module_id": "go-m1",
        "title": "Functions That Return More Than One Value",
        "concept": "Functions & Multiple Return Values",
        "explanation": (
            "Functions are declared with `func`, and each parameter's type comes after its name, like `func add(a int, b int) int`. "
            "A Go function can return several values at once, which is how Go hands back a result together with extra information such as an error. "
            "The caller must receive every returned value, but can throw away the ones it doesn't need with the blank identifier `_`."
        ),
        "code_example": """package main

import "fmt"

func divide(a, b int) (int, int) {
\treturn a / b, a % b
}

func main() {
\tq, r := divide(17, 5)
\tfmt.Println(q, r) // 3 2
\t_, rem := divide(10, 3)
\tfmt.Println("remainder:", rem) // remainder: 1
}""",
        "code_walkthrough": [
            "`func divide(a, b int) (int, int)` takes two ints (they share a type, so `int` is written once) and returns two ints.",
            "`return a / b, a % b` returns the whole-number quotient and the remainder together.",
            "`q, r := divide(17, 5)` stores both results: 3 and 2.",
            "`_, rem := divide(10, 3)` discards the quotient and keeps the remainder, 1.",
        ],
        "key_points": [
            "Types come after names: `func greet(name string) string`.",
            "List multiple return types in parentheses, like `(int, error)`.",
            "Use `_` to ignore a returned value you don't need.",
        ],
        "analogy": (
            "A function with multiple returns is like an ATM that hands you both your cash and a receipt in one go."
        ),
        "quiz": {
            "question": "How do you ignore one of the values a function returns?",
            "options": [
                "Assign it to `nil`",
                "Just leave it out: `q := divide(17, 5)`",
                "Assign it to the blank identifier `_`",
                "Wrap the call in `ignore()`",
            ],
            "correct_index": 2,
            "explanation": "Go makes you account for every returned value, so leaving one out is a compile error. Assigning it to `_` discards it on purpose.",
        },
    },
    {
        "id": "go5",
        "module_id": "go-m2",
        "title": "Growing Lists with Slices",
        "concept": "Slices",
        "explanation": (
            "A slice is Go's flexible, growable list, written as `[]T`, such as `[]int`. "
            "The built-in `append` adds items and returns the updated slice, so you always assign the result back, and `len` tells you how many items it holds. "
            "Slicing with `s[low:high]` gives you the items from index `low` up to, but not including, `high`."
        ),
        "code_example": """package main

import "fmt"

func main() {
\tnums := []int{10, 20, 30}
\tnums = append(nums, 40)
\tfmt.Println(nums, len(nums)) // [10 20 30 40] 4
\tfmt.Println(nums[1:3])       // [20 30]
\ttotal := 0
\tfor _, n := range nums {
\t\ttotal += n
\t}
\tfmt.Println(total) // 100
}""",
        "code_walkthrough": [
            "`nums := []int{10, 20, 30}` creates a slice of three ints.",
            "`nums = append(nums, 40)` adds 40 and stores the returned slice back in `nums`.",
            "`len(nums)` is now 4, and `fmt.Println` prints slices in square brackets: `[10 20 30 40]`.",
            "`nums[1:3]` takes indexes 1 and 2, giving `[20 30]`.",
            "`for _, n := range nums` visits every value (ignoring the index) to add up a total of 100.",
        ],
        "key_points": [
            "Always write `s = append(s, x)`, because `append` may return a slice backed by a brand-new array.",
            "`s[low:high]` includes index `low` but excludes index `high`.",
            "A sub-slice shares memory with the original, so changing one can change the other.",
        ],
        "analogy": (
            "A slice is like a window onto a row of seats: you can slide the window or add seats at the end, "
            "but the seats underneath are shared."
        ),
        "quiz": {
            "question": "For `s := []int{5, 6, 7, 8}`, what is `s[1:3]`?",
            "options": ["[5 6 7]", "[6 7]", "[6 7 8]", "[7 8]"],
            "correct_index": 1,
            "explanation": "Indexes start at 0 and the end index is excluded, so `s[1:3]` contains `s[1]` and `s[2]`: 6 and 7.",
        },
        "try_it": {
            "prompt": "Use `append` to add the number 4 to the end of `nums`.",
            "starter_code": """package main

import "fmt"

func main() {
\tnums := []int{1, 2, 3}
\t// add 4 to the end of nums here

\tfmt.Println(nums, len(nums))
}
""",
            "checks": [
                {
                    "pattern": r"nums\s*=\s*append\s*\(\s*nums\s*,\s*4\s*\)",
                    "hint": "`append` returns the new slice, so assign it back: `nums = append(nums, 4)`.",
                },
            ],
            "expected_output": "[1 2 3 4] 4",
        },
    },
    {
        "id": "go6",
        "module_id": "go-m2",
        "title": "Looking Things Up with Maps",
        "concept": "Maps",
        "explanation": (
            "A map stores key-value pairs, like `map[string]int` for item names and counts, and finds values by key very quickly. "
            "You add or update an entry with `m[key] = value` and remove one with `delete(m, key)`. "
            "Reading a missing key returns the zero value, so use the two-value form `v, ok := m[key]` to check whether the key really exists."
        ),
        "code_example": """package main

import "fmt"

func main() {
\tstock := map[string]int{"apple": 5, "pear": 2}
\tstock["kiwi"] = 7
\tdelete(stock, "pear")
\tfmt.Println(len(stock), stock["apple"]) // 2 5
\tqty, ok := stock["mango"]
\tfmt.Println(qty, ok) // 0 false
\tfmt.Println(stock)   // map[apple:5 kiwi:7]
}""",
        "code_walkthrough": [
            '`map[string]int{"apple": 5, "pear": 2}` creates a map with two entries.',
            '`stock["kiwi"] = 7` adds a new key, and `delete(stock, "pear")` removes one.',
            '`len(stock)` is now 2, and `stock["apple"]` is 5.',
            '`qty, ok := stock["mango"]` gives `0` and `false` because "mango" isn\'t in the map.',
            "`fmt.Println` prints maps with their keys sorted, but a `range` loop over a map visits keys in random order.",
        ],
        "key_points": [
            "Create maps with a literal or `make(map[string]int)`; writing to a nil map panics.",
            "Use `v, ok := m[key]` to tell a missing key apart from a stored zero value.",
            "Never rely on the order of a `range` loop over a map.",
        ],
        "analogy": (
            "A map is like a coat check: hand over your ticket (the key) and you get back exactly your coat (the value)."
        ),
        "quiz": {
            "question": 'For `m := map[string]int{}`, what does `v, ok := m["missing"]` give you?',
            "options": [
                "`v` is 0 and `ok` is false",
                "A runtime panic",
                "`v` is nil and `ok` is false",
                "`v` is -1 and `ok` is true",
            ],
            "correct_index": 0,
            "explanation": "A missing key returns the value type's zero value (0 for `int`) and `ok` is false. Reading never panics; only writing to a nil map does.",
        },
    },
    {
        "id": "go7",
        "module_id": "go-m2",
        "title": "Building Your Own Types with Structs",
        "concept": "Structs & Methods",
        "explanation": (
            "A struct groups related fields into one custom type, like a `Player` with a `Name` and `XP`. "
            "A method is a function attached to a type through a receiver, written before the method name: `func (p Player) Greet()`. "
            "Use a pointer receiver (`*Player`) when the method needs to change the original value, because a value receiver only works on a copy."
        ),
        "code_example": """package main

import "fmt"

type Player struct {
\tName string
\tXP   int
}

func (p *Player) Gain(xp int) { p.XP += xp }

func main() {
\tp := Player{Name: "Ada", XP: 10}
\tp.Gain(40)
\tfmt.Printf("%+v\\n", p) // {Name:Ada XP:50}
}""",
        "code_walkthrough": [
            "`type Player struct { ... }` defines a new type with a `Name` field and an `XP` field.",
            "`func (p *Player) Gain(xp int)` is a method with a pointer receiver, so it can modify the player.",
            '`Player{Name: "Ada", XP: 10}` creates a struct value using field names.',
            "`p.Gain(40)` works on `p` directly: Go passes `&p` for you, so `XP` becomes 50.",
            "The `%+v` verb prints a struct with its field names: `{Name:Ada XP:50}`.",
        ],
        "key_points": [
            "Struct fields are read and written with a dot: `p.Name`.",
            "Pointer receivers can modify the value; value receivers get a copy.",
            "Go has no classes: structs plus methods cover the same ground.",
        ],
        "analogy": (
            "A struct is like a character sheet in a game, and its methods are the moves that character knows how to perform."
        ),
        "quiz": {
            "question": "Why does `Gain` use a pointer receiver `(p *Player)`?",
            "options": [
                "Pointer receivers are required for every method",
                "So the method can only be called on nil players",
                "Because structs can't have value receivers",
                "So the method can modify the original struct instead of a copy",
            ],
            "correct_index": 3,
            "explanation": "With a value receiver, `Gain` would update a copy and the original player's XP wouldn't change. A pointer receiver lets the method modify the real struct.",
        },
        "try_it": {
            "prompt": "Add an `Area` method on `Rect` that returns `W` times `H` as an `int`.",
            "starter_code": """package main

import "fmt"

type Rect struct {
\tW, H int
}

// add an Area method here

func main() {
\tr := Rect{W: 3, H: 4}
\tfmt.Println(r.Area())
}
""",
            "checks": [
                {
                    "pattern": r"func\s*\(\s*\w+\s+\*?Rect\s*\)\s*Area\s*\(\s*\)\s*int",
                    "hint": "Declare the method with a receiver: `func (r Rect) Area() int {`.",
                },
                {
                    "pattern": r"return\s+(\w+)\.W\s*\*\s*\1\.H|return\s+(\w+)\.H\s*\*\s*\2\.W",
                    "hint": "Return the product of the fields: `return r.W * r.H`.",
                },
            ],
            "expected_output": "12",
        },
    },
    {
        "id": "go8",
        "module_id": "go-m2",
        "title": "Interfaces: Behavior Over Inheritance",
        "concept": "Interfaces",
        "explanation": (
            "An interface lists method signatures, describing what a type can do rather than what it is. "
            "Any type that has all of those methods satisfies the interface automatically; there is no `implements` keyword. "
            "This lets you write functions that accept many different types, as long as they share the behavior you need."
        ),
        "code_example": """package main

import "fmt"

type Shape interface{ Area() float64 }

type Square struct{ Side float64 }

func (s Square) Area() float64 { return s.Side * s.Side }

func main() {
\tvar sh Shape = Square{Side: 3}
\tfmt.Println(sh.Area()) // 9
}""",
        "code_walkthrough": [
            "`type Shape interface{ Area() float64 }` says a Shape is anything with an `Area` method that returns a `float64`.",
            "`type Square struct{ Side float64 }` is an ordinary struct.",
            "`func (s Square) Area() float64` gives `Square` an `Area` method, so it satisfies `Shape` automatically.",
            "`var sh Shape = Square{Side: 3}` stores a `Square` in a variable of interface type `Shape`.",
            "`sh.Area()` calls the Square's method and prints 9.",
        ],
        "key_points": [
            "Interfaces are satisfied implicitly, just by having the right methods.",
            "Keep interfaces small; many standard ones have a single method, like `fmt.Stringer` or `io.Reader`.",
            "The empty interface `any` can hold a value of any type.",
        ],
        "analogy": (
            'An interface is like a job posting that says "must be able to drive": anyone with that skill qualifies, '
            "no matter who they are."
        ),
        "quiz": {
            "question": "How does a type implement an interface in Go?",
            "options": [
                "By writing `implements Shape` after the type name",
                "By embedding the interface inside the struct",
                "By simply having all the methods the interface lists",
                "By registering the type with the interface at startup",
            ],
            "correct_index": 2,
            "explanation": "Go interfaces are satisfied implicitly: if a type has every method in the interface, it can be used wherever that interface is expected.",
        },
    },
    {
        "id": "go9",
        "module_id": "go-m3",
        "title": "Handling Errors the Go Way",
        "concept": "Error Handling",
        "explanation": (
            "Go has no exceptions; a function that can fail returns an `error` as its last return value. "
            "If nothing went wrong, that error is `nil`, so you check it right away with `if err != nil`. "
            'You can create your own errors with `errors.New("message")`, or with `fmt.Errorf`, which also lets you add details and wrap another error using `%w`.'
        ),
        "code_example": """package main

import (
\t"fmt"
\t"strconv"
)

func main() {
\tn, err := strconv.Atoi("42")
\tfmt.Println(n, err) // 42 <nil>
\tif _, err := strconv.Atoi("abc"); err != nil {
\t\tfmt.Println("Error:", err) // Error: strconv.Atoi: parsing "abc": invalid syntax
\t}
}""",
        "code_walkthrough": [
            '`strconv.Atoi("42")` converts a string to an int and returns `(int, error)`.',
            "The conversion succeeds, so `n` is 42 and `err` is `nil`, which prints as `<nil>`.",
            '`if _, err := strconv.Atoi("abc"); err != nil` tries a bad conversion and checks the error in one line.',
            'The error message explains exactly what failed: `strconv.Atoi: parsing "abc": invalid syntax`.',
        ],
        "key_points": [
            "Return `error` as the last value, and `nil` when everything worked.",
            "Check errors immediately with `if err != nil`, then handle them or return them.",
            'Wrap errors with `fmt.Errorf("loading config: %w", err)` to add context.',
        ],
        "analogy": (
            "A Go error is like a delivery driver handing you a note that says the package was damaged, "
            "instead of quietly leaving an empty box: you always know to check."
        ),
        "quiz": {
            "question": "What is the idiomatic way to check for an error in Go?",
            "options": [
                "`if err != nil { ... }`",
                "`try { ... } catch (err) { ... }`",
                "`if err == true { ... }`",
                "`on error resume next`",
            ],
            "correct_index": 0,
            "explanation": "Go functions return errors as ordinary values, and `nil` means success, so you compare the error with `nil` right after the call.",
        },
        "try_it": {
            "prompt": 'Finish `checkAge` so it returns `errors.New("age cannot be negative")` when `age` is less than 0, and `nil` otherwise.',
            "starter_code": """package main

import (
\t"errors"
\t"fmt"
)

func checkAge(age int) error {
\t// TODO: return an error for negative ages
\treturn nil
}

func main() {
\tfmt.Println(checkAge(-5))
}
""",
            "checks": [
                {
                    "pattern": r"if\s+\(?\s*(age\s*<\s*0|0\s*>\s*age)",
                    "hint": "Test for a negative age with `if age < 0 {`.",
                },
                {
                    "pattern": r"return\s+errors\s*\.\s*New\s*\(\s*[\"`]age cannot be negative[\"`]\s*\)",
                    "hint": 'Inside the `if`, write `return errors.New("age cannot be negative")`.',
                },
            ],
            "expected_output": "age cannot be negative",
        },
    },
    {
        "id": "go10",
        "module_id": "go-m3",
        "title": "Doing Things at Once with Goroutines",
        "concept": "Goroutines",
        "explanation": (
            "A goroutine is a lightweight function that runs concurrently with the rest of your program; you start one by putting `go` before a function call. "
            "Goroutines are cheap enough to run thousands at once, but the program exits as soon as `main` returns, even if they are still working. "
            "A `sync.WaitGroup` lets `main` wait until every goroutine has finished."
        ),
        "code_example": """package main

import (
\t"fmt"
\t"sync"
)

func main() {
\tvar wg sync.WaitGroup
\tsquares := make([]int, 3)
\tfor i := range 3 {
\t\twg.Add(1)
\t\tgo func() { defer wg.Done(); squares[i] = i * i }()
\t}
\twg.Wait()
\tfmt.Println(squares) // [0 1 4]
}""",
        "code_walkthrough": [
            "`var wg sync.WaitGroup` creates a counter of goroutines that are still running.",
            "`squares := make([]int, 3)` makes a slice of three zeros to hold the results.",
            "`for i := range 3` counts 0, 1, 2 (Go 1.22+), and `wg.Add(1)` bumps the counter before each goroutine starts.",
            "`go func() { ... }()` starts a goroutine, and `defer wg.Done()` lowers the counter when it finishes.",
            "Each goroutine writes only its own slot, `squares[i]`, so they never step on each other.",
            "`wg.Wait()` blocks until the counter reaches zero, then `[0 1 4]` is printed.",
        ],
        "key_points": [
            "`go f()` starts `f` concurrently and returns immediately.",
            "When `main` returns the program ends, even if goroutines haven't finished.",
            "Since Go 1.22, each loop iteration gets its own copy of the loop variable, so goroutines capture the right `i`.",
        ],
        "analogy": (
            "Goroutines are like kitchen helpers working side by side on different dishes, "
            "and the WaitGroup is the head chef who waits until every plate is ready."
        ),
        "quiz": {
            "question": "What happens to goroutines that are still running when `main` returns?",
            "options": [
                "`main` automatically waits for them to finish",
                "They keep running in the background forever",
                "They pause and resume the next time the program runs",
                "The program exits and they are stopped",
            ],
            "correct_index": 3,
            "explanation": "A Go program ends when `main` returns, without waiting for other goroutines. Use a `sync.WaitGroup` or channels to wait for them.",
        },
    },
    {
        "id": "go11",
        "module_id": "go-m3",
        "title": "Passing Messages with Channels",
        "concept": "Channels",
        "explanation": (
            "A channel is a typed pipe that goroutines use to send and receive values safely, created with `make(chan T)`. "
            "`ch <- v` sends a value and `v := <-ch` receives one; on an unbuffered channel, each send waits until another goroutine is ready to receive it. "
            "When the sender is done it can `close` the channel, and a `for v := range ch` loop keeps receiving until the channel is closed."
        ),
        "code_example": """package main

import "fmt"

func main() {
\tch := make(chan string)
\tgo func() {
\t\tch <- "ping"
\t\tch <- "pong"
\t\tclose(ch)
\t}()
\tfor msg := range ch {
\t\tfmt.Println(msg) // ping, then pong
\t}
}""",
        "code_walkthrough": [
            "`ch := make(chan string)` creates an unbuffered channel that carries strings.",
            '`go func() { ... }()` starts a goroutine that sends "ping" and then "pong".',
            "Each `ch <- ...` waits until `main` is ready to receive, which keeps the two goroutines in step.",
            "`close(ch)` signals that no more values are coming.",
            "`for msg := range ch` receives the values in the order they were sent and stops once the channel is closed.",
        ],
        "key_points": [
            "Don't communicate by sharing memory; share memory by communicating.",
            "Only the sender should close a channel, because sending on a closed channel panics.",
            "`make(chan int, 10)` creates a buffered channel whose sends don't block until 10 values are waiting.",
        ],
        "analogy": (
            "A channel is like a pneumatic tube between two offices: one side drops in a message, the other pulls it out, "
            "and nobody has to fight over a shared desk."
        ),
        "quiz": {
            "question": "What does `for v := range ch` do once `ch` is closed and empty?",
            "options": [
                "It blocks forever",
                "The loop ends",
                "It panics",
                "It keeps receiving zero values forever",
            ],
            "correct_index": 1,
            "explanation": "Ranging over a channel receives values until the channel is closed and drained, then the loop exits normally.",
        },
    },
    {
        "id": "go12",
        "module_id": "go-m3",
        "title": "Organizing Code with Packages and Modules",
        "concept": "Packages & Modules",
        "explanation": (
            "Every Go file belongs to a package, and `package main` with a `func main` builds a runnable program. "
            "A module is a collection of packages with a `go.mod` file, created by `go mod init`, that records the module's path and its dependencies. "
            "Only names that start with a capital letter, like `strings.ToUpper`, are exported and usable from other packages."
        ),
        "code_example": """// main.go, in a module created with: go mod init example.com/hello
package main

import (
\t"fmt"
\t"strings"
)

func main() {
\tfmt.Println(strings.ToUpper("gopher"))          // GOPHER
\tfmt.Println(strings.Repeat("go", 3))            // gogogo
\tfmt.Println(strings.Contains("golang", "lang")) // true
}""",
        "code_walkthrough": [
            "`go mod init example.com/hello` (run once in the terminal) creates a `go.mod` file that names your module.",
            "`package main` marks this file as part of an executable program.",
            "The `import` block brings in the standard library packages `fmt` and `strings`.",
            "`strings.ToUpper`, `strings.Repeat` and `strings.Contains` are usable here because their names start with a capital letter.",
            "`go run .` runs the program, and `go get` adds third-party dependencies to `go.mod`.",
        ],
        "key_points": [
            "Capitalized names are exported; lowercase names stay private to their package.",
            "`go.mod` records your module path and dependency versions, and `go.sum` stores their checksums.",
            "Importing a package you don't use is a compile error, so remove unused imports.",
        ],
        "analogy": (
            "A module is like a library building, its packages are the rooms inside, "
            "and capitalized names are the doors left open to visitors."
        ),
        "quiz": {
            "question": "Which of these names can be used from outside its package?",
            "options": ["`total`", "`_total`", "`Total`", "`total_`"],
            "correct_index": 2,
            "explanation": "In Go, an identifier is exported when it starts with an uppercase letter, so only `Total` is visible to other packages.",
        },
    },
]
