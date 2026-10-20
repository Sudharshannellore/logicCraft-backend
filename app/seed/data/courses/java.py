"""Java Foundations: Learn the language behind Android apps, enterprise backends and big data tools."""

COURSE = {
    "id": "java-foundations",
    "title": "Java Foundations",
    "world": "Java Kingdom",
    "description": "Learn core Java, from variables and classes to collections, generics and streams.",
    "language": "java",
    "modules": [
        {"id": "java-m1", "title": "Java Basics"},
        {"id": "java-m2", "title": "Methods & Objects"},
        {"id": "java-m3", "title": "The Modern Java Toolkit"},
    ],
}

ZONES = [
    {
        "id": "java-z1",
        "name": "Coffee Bean Coast",
        "tagline": "Variables, text and the flow of a program.",
        "difficulty": "easy",
        "nodes": [
            {
                "id": "java1",
                "title": "Variables & Types",
                "difficulty": "easy",
                "xp_reward": 50,
                "estimated_minutes": 10,
            },
            {"id": "java2", "title": "Strings", "difficulty": "easy", "xp_reward": 50, "estimated_minutes": 10},
            {"id": "java3", "title": "if & switch", "difficulty": "easy", "xp_reward": 55, "estimated_minutes": 11},
            {"id": "java4", "title": "Loops", "difficulty": "easy", "xp_reward": 60, "estimated_minutes": 12},
        ],
        "boss": {
            "id": "java-z1-boss",
            "name": "Semicolon Slime",
            "sprite": "slime",
            "challenge": "Fix 3 little programs that refuse to compile",
            "stages": 3,
            "xp_reward": 250,
        },
    },
    {
        "id": "java-z2",
        "name": "Object Oak Forest",
        "tagline": "Methods, arrays and the classes that shape your world.",
        "difficulty": "medium",
        "nodes": [
            {"id": "java5", "title": "Methods", "difficulty": "medium", "xp_reward": 90, "estimated_minutes": 18},
            {"id": "java6", "title": "Arrays", "difficulty": "medium", "xp_reward": 100, "estimated_minutes": 19},
            {
                "id": "java7",
                "title": "Classes & Objects",
                "difficulty": "medium",
                "xp_reward": 100,
                "estimated_minutes": 20,
            },
            {
                "id": "java8",
                "title": "Inheritance & Interfaces",
                "difficulty": "medium",
                "xp_reward": 110,
                "estimated_minutes": 20,
            },
        ],
        "boss": {
            "id": "java-z2-boss",
            "name": "Inheritance Hydra",
            "sprite": "bugSlime",
            "challenge": "Untangle a class hierarchy so every subclass behaves",
            "stages": 4,
            "xp_reward": 400,
        },
    },
    {
        "id": "java-z3",
        "name": "Lambda Lava Peaks",
        "tagline": "Collections, generics, exceptions and stream power.",
        "difficulty": "hard",
        "nodes": [
            {
                "id": "java9",
                "title": "Lists & Maps",
                "difficulty": "hard",
                "xp_reward": 140,
                "estimated_minutes": 25,
            },
            {"id": "java10", "title": "Generics", "difficulty": "hard", "xp_reward": 150, "estimated_minutes": 26},
            {"id": "java11", "title": "Exceptions", "difficulty": "hard", "xp_reward": 150, "estimated_minutes": 28},
            {
                "id": "java12",
                "title": "Streams & Lambdas",
                "difficulty": "hard",
                "xp_reward": 160,
                "estimated_minutes": 30,
            },
        ],
        "boss": {
            "id": "java-z3-boss",
            "name": "Stack Trace Titan",
            "sprite": "recursionBoss",
            "challenge": "Survive five rounds of stream pipelines and thrown exceptions",
            "stages": 5,
            "xp_reward": 700,
        },
    },
]

LESSONS: list[dict] = [
    {
        "id": "java1",
        "module_id": "java-m1",
        "title": "Storing Values in Typed Variables",
        "concept": "Java Variables and Primitive Data Types",
        "explanation": (
            "Java is statically typed: every variable has a type, such as `int`, `double`, `boolean` or `long`, "
            "and the compiler checks that you only store matching values in it. "
            "These primitive types hold simple values directly, and dividing two `int` values throws away the remainder. "
            "Since Java 10 you can also write `var` for local variables and let the compiler infer the type."
        ),
        "code_example": """public class Main {
    public static void main(String[] args) {
        int lives = 3;
        double speed = 1.5;
        boolean hasKey = true;
        long coins = 9_000_000_000L;
        var level = 7;                  // compiler infers int
        lives = lives - 1;
        System.out.println(lives);      // 2
        System.out.println(speed * 2);  // 3.0
        System.out.println(7 / 2);      // 3 (integer division)
        System.out.println(hasKey + " " + coins + " " + level); // true 9000000000 7
    }
}""",
        "code_walkthrough": [
            "`int lives = 3;` declares a whole-number variable and gives it a starting value.",
            "`double speed = 1.5;` stores a decimal number, and `boolean hasKey = true;` stores true or false.",
            "`long coins = 9_000_000_000L;` needs `long` because the value is too big for an `int`; the `L` marks a long literal and the underscores are just for readability.",
            "`var level = 7;` lets the compiler work out that `level` is an `int`.",
            "`7 / 2` prints 3 because dividing two integers drops the decimal part.",
        ],
        "key_points": [
            "Every variable has a fixed type; you can change its value but not its type.",
            "Use `int` for whole numbers, `double` for decimals and `boolean` for true/false.",
            "Integer division truncates: `7 / 2` is 3, but `7 / 2.0` is 3.5.",
        ],
        "analogy": (
            "A typed variable is like a labeled storage box: a box marked `int` only accepts whole numbers, "
            "and the compiler is the strict shopkeeper who checks every item you put in."
        ),
        "quiz": {
            "question": "What value ends up in `avg` after `double avg = 5 / 2;`?",
            "options": ["2.5", "2.0", "3.0", "A compile error"],
            "correct_index": 1,
            "explanation": "`5 / 2` is calculated first as integer division, giving 2. That `int` is then widened to the `double` 2.0. Write `5 / 2.0` to get 2.5.",
        },
    },
    {
        "id": "java2",
        "module_id": "java-m1",
        "title": "Working with Text",
        "concept": "Java Strings",
        "explanation": (
            "A `String` is an object that holds a sequence of characters, written in double quotes. "
            "Strings come with handy methods like `length()`, `toUpperCase()` and `contains()`, and you can join them with `+`. "
            "Strings are immutable, so methods return new strings, and you compare their text with `equals()`, not `==`."
        ),
        "code_example": """public class Main {
    public static void main(String[] args) {
        String hero = "Duke";
        String greeting = "Hello, " + hero + "!";
        System.out.println(greeting);                  // Hello, Duke!
        System.out.println(hero.length());             // 4
        System.out.println(hero.toUpperCase());        // DUKE
        System.out.println(greeting.contains("Duke")); // true
        String copy = new String("Duke");
        System.out.println(hero == copy);              // false (different objects)
        System.out.println(hero.equals(copy));         // true (same text)
    }
}""",
        "code_walkthrough": [
            '`"Hello, " + hero + "!"` joins three pieces of text into one new string.',
            "`hero.length()` counts the characters: 4.",
            '`hero.toUpperCase()` returns a new string "DUKE"; `hero` itself is unchanged.',
            "`hero == copy` is false because `==` checks whether both variables point to the same object.",
            "`hero.equals(copy)` is true because it compares the actual characters.",
        ],
        "key_points": [
            "Strings use double quotes; single quotes are for a single `char`.",
            "Strings are immutable: methods like `toUpperCase()` return a new string.",
            "Always compare text with `equals()` (or `equalsIgnoreCase()`), never `==`.",
        ],
        "analogy": (
            "A String is like a printed name tag: you can't change the ink, but you can print "
            "a new tag based on the old one."
        ),
        "quiz": {
            "question": "What is the reliable way to check whether two strings `a` and `b` hold the same text?",
            "options": ["a == b", "a.length() == b.length()", "a.compareTo(b) > 0", "a.equals(b)"],
            "correct_index": 3,
            "explanation": "`equals()` compares the characters. `==` only checks whether both variables refer to the same object, so it can be false for identical text.",
        },
        "try_it": {
            "prompt": "Print how many characters are in `name` using the `length()` method.",
            "starter_code": (
                "public class Main {\n"
                "    public static void main(String[] args) {\n"
                '        String name = "Logicraft";\n'
                "        // print the number of characters in name\n"
                "\n"
                "    }\n"
                "}\n"
            ),
            "checks": [
                {
                    "pattern": r"name\s*\.\s*length\s*\(\s*\)",
                    "hint": "Call `name.length()` to count the characters.",
                },
                {
                    "pattern": r"System\s*\.\s*out\s*\.\s*println\s*\(",
                    "hint": "Print the result with `System.out.println(...)`.",
                },
            ],
            "expected_output": "9",
        },
    },
    {
        "id": "java3",
        "module_id": "java-m1",
        "title": "Making Decisions with if and switch",
        "concept": "Java if-else and switch Statements",
        "explanation": (
            "`if`, `else if` and `else` run different blocks of code depending on whether a `boolean` condition is true. "
            "When you are choosing between many fixed values, a `switch` is often cleaner. "
            "Modern Java (14+) has switch expressions with `case ... ->` arrows that return a value and never fall through to the next case."
        ),
        "code_example": """public class Main {
    public static void main(String[] args) {
        int level = 2;
        if (level >= 3) {
            System.out.println("Boss unlocked");
        } else if (level == 2) {
            System.out.println("Almost there");  // Almost there
        }
        String zone = switch (level) {
            case 1, 2 -> "Starter Plains";
            default -> "Boss Peaks";
        };
        System.out.println(zone);                // Starter Plains
    }
}""",
        "code_walkthrough": [
            "`if (level >= 3)` is false, so its block is skipped.",
            '`else if (level == 2)` is true, so "Almost there" is printed.',
            "`switch (level)` compares `level` against each `case`.",
            '`case 1, 2 -> "Starter Plains";` matches either value and produces that string.',
            "`default` covers every other value, and the chosen string is stored in `zone`.",
        ],
        "key_points": [
            "Conditions must be `boolean`; use `==` for numbers and `equals()` for strings.",
            "Add a final `else` to catch every case the earlier conditions missed.",
            "Arrow-style `switch` expressions return a value and don't fall through.",
        ],
        "analogy": (
            "An `if` chain is like a series of gates you try one by one, while a `switch` is like "
            "an elevator panel: press a number and go straight to that floor."
        ),
        "quiz": {
            "question": "What does the arrow form of switch (`case 1 -> ...`) prevent compared with the old colon form (`case 1:`)?",
            "options": [
                "Accidentally falling through into the next case",
                "Switching on String values",
                "Having a default branch",
                "Listing more than one value per case",
            ],
            "correct_index": 0,
            "explanation": "With the old colon form, forgetting `break` makes execution fall through into the next case. Arrow cases run only their own code.",
        },
    },
    {
        "id": "java4",
        "module_id": "java-m1",
        "title": "Repeating Work with Loops",
        "concept": "Java Loops",
        "explanation": (
            "A `for` loop repeats code a set number of times using a counter with a start, a condition and an update. "
            "A `while` loop keeps going for as long as its condition stays true, which suits cases where you don't know the count in advance. "
            "`break` exits a loop early and `continue` skips to the next pass."
        ),
        "code_example": """public class Main {
    public static void main(String[] args) {
        for (int i = 1; i <= 3; i++) {
            System.out.println("Round " + i);  // Round 1, Round 2, Round 3
        }
        int energy = 10;
        int steps = 0;
        while (energy > 0) {
            energy -= 3;
            steps++;
        }
        System.out.println(steps + " steps"); // 4 steps
    }
}""",
        "code_walkthrough": [
            "`int i = 1` starts the counter, `i <= 3` is checked before each pass, and `i++` runs after each pass.",
            "The `for` body prints Round 1, Round 2 and Round 3.",
            "`while (energy > 0)` repeats as long as there is energy left.",
            "Each pass subtracts 3 with `energy -= 3` and counts a step with `steps++`.",
            "Energy goes 10, 7, 4, 1, -2, so the loop runs 4 times.",
        ],
        "key_points": [
            "Use `for` when you know how many times to repeat.",
            "Use `while` when you repeat until something changes.",
            "Make sure the condition eventually becomes false, or the loop never ends.",
        ],
        "analogy": (
            "A `for` loop is like running exactly three laps of a track, while a `while` loop is "
            "like running until you're out of breath."
        ),
        "quiz": {
            "question": "How many times does the body of `for (int i = 0; i < 5; i += 2)` run?",
            "options": ["2", "5", "3", "4"],
            "correct_index": 2,
            "explanation": "`i` takes the values 0, 2 and 4. When it reaches 6, `i < 5` is false, so the body runs 3 times.",
        },
        "try_it": {
            "prompt": "Write a `for` loop that prints the numbers 1 to 5, one per line.",
            "starter_code": (
                "public class Main {\n"
                "    public static void main(String[] args) {\n"
                "        // write your loop here\n"
                "\n"
                "    }\n"
                "}\n"
            ),
            "checks": [
                {
                    "pattern": r"for\s*\(\s*(int|var)\s+\w+\s*=\s*[01]\s*;",
                    "hint": "Start with `for (int i = 1; ...; ...)`.",
                },
                {
                    "pattern": r"System\s*\.\s*out\s*\.\s*println\s*\(",
                    "hint": "Print each number inside the loop with `System.out.println(i)`.",
                },
            ],
            "expected_output": "1\n2\n3\n4\n5",
        },
    },
    {
        "id": "java5",
        "module_id": "java-m2",
        "title": "Packaging Code into Methods",
        "concept": "Java Methods",
        "explanation": (
            "A method is a named block of code that can take parameters and return a value, so you can reuse logic instead of repeating it. "
            "Its declaration states the return type (or `void` if it returns nothing), the name and the typed parameters. "
            "`static` methods belong to the class itself, so `main` can call them directly."
        ),
        "code_example": """public class Main {
    static int add(int a, int b) {
        return a + b;
    }

    static String greet(String name) {
        return "Welcome, " + name + "!";
    }

    public static void main(String[] args) {
        System.out.println(add(2, 3));      // 5
        System.out.println(add(10, -4));    // 6
        System.out.println(greet("Duke"));  // Welcome, Duke!
    }
}""",
        "code_walkthrough": [
            "`static int add(int a, int b)` declares a method that takes two `int` parameters and returns an `int`.",
            "`return a + b;` sends the sum back to whoever called the method.",
            "`static String greet(String name)` returns a new `String` built from its parameter.",
            "`add(2, 3)` and `add(10, -4)` reuse the same method with different arguments.",
        ],
        "key_points": [
            "A method declares its return type, name and parameter types.",
            "Use `void` when a method does work but returns nothing.",
            "Methods can share a name if their parameter lists differ (overloading).",
        ],
        "analogy": (
            "A method is like a recipe card: write it once, then follow it whenever you need "
            "that dish, swapping in different ingredients each time."
        ),
        "quiz": {
            "question": "What does `void` mean in `static void log(String msg)`?",
            "options": [
                "The method takes no parameters",
                "The method returns no value",
                "The method is private",
                "The method cannot be called from main",
            ],
            "correct_index": 1,
            "explanation": "`void` is the return type, meaning the method doesn't return a value. It still takes the `msg` parameter.",
        },
    },
    {
        "id": "java6",
        "module_id": "java-m2",
        "title": "Storing Many Values in Arrays",
        "concept": "Java Arrays",
        "explanation": (
            "An array holds a fixed number of values of the same type, each reached by an index starting at 0. "
            "Its size is set when it's created and is available as `array.length`. "
            "New arrays are filled with default values, such as 0 for numbers and `null` for objects."
        ),
        "code_example": """import java.util.Arrays;

public class Main {
    public static void main(String[] args) {
        int[] scores = {72, 95, 88};
        System.out.println("first: " + scores[0] + ", size: " + scores.length); // first: 72, size: 3
        int total = 0;
        for (int s : scores) {
            total += s;
        }
        System.out.println(total);                  // 255
        int[] slots = new int[3];
        System.out.println(Arrays.toString(slots)); // [0, 0, 0]
    }
}""",
        "code_walkthrough": [
            "`int[] scores = {72, 95, 88};` creates an array with three values.",
            "`scores[0]` reads the first element, and `scores.length` is 3.",
            "`for (int s : scores)` is an enhanced for loop that visits each element in turn.",
            "`new int[3]` creates an array of three zeros.",
            "`Arrays.toString(slots)` turns the array into readable text for printing.",
        ],
        "key_points": [
            "Indexes run from 0 to `length - 1`.",
            "An array's size can't change after it's created.",
            "Printing an array directly shows a memory code, so use `Arrays.toString()`.",
        ],
        "analogy": (
            "An array is like a row of numbered lockers: the number of lockers is fixed, and the first one is locker 0."
        ),
        "quiz": {
            "question": "What happens when you read `scores[3]` from an array of length 3?",
            "options": [
                "It returns 0",
                "It returns null",
                "It returns the last element",
                "It throws an ArrayIndexOutOfBoundsException",
            ],
            "correct_index": 3,
            "explanation": "The valid indexes are 0, 1 and 2. Reading index 3 throws an `ArrayIndexOutOfBoundsException` at runtime.",
        },
    },
    {
        "id": "java7",
        "module_id": "java-m2",
        "title": "Building Your Own Types with Classes",
        "concept": "Java Classes and Objects",
        "explanation": (
            "A class is a blueprint that bundles data (fields) with behavior (methods), and each object made from it with `new` has its own copy of the fields. "
            "A constructor sets up a new object, and `this` refers to the object being built. "
            "Marking fields `private` hides them so other code has to go through your methods (encapsulation)."
        ),
        "code_example": """class Hero {
    private final String name;
    private int level = 1;
    Hero(String name) { this.name = name; }
    void levelUp() { level++; }
    String status() { return name + " is level " + level; }
}
public class Main {
    public static void main(String[] args) {
        Hero duke = new Hero("Duke");
        duke.levelUp();
        System.out.println(duke.status());                // Duke is level 2
        System.out.println(new Hero("Ada").status());     // Ada is level 1
    }
}""",
        "code_walkthrough": [
            "`class Hero` defines a new type with two `private` fields: `name` and `level`.",
            "`Hero(String name) { this.name = name; }` is the constructor; `this.name` is the field and `name` is the parameter.",
            '`new Hero("Duke")` creates an object and stores a reference to it in `duke`.',
            "`duke.levelUp()` changes only Duke's `level`, so the separate Ada object created later starts at level 1.",
        ],
        "key_points": [
            "A class is the blueprint; objects are instances created with `new`.",
            "Constructors share the class's name and have no return type.",
            "Keep fields `private` and expose behavior through methods.",
        ],
        "analogy": (
            "A class is like a cookie cutter and objects are the cookies: same shape, "
            "but each cookie can have its own frosting."
        ),
        "quiz": {
            "question": "What is the relationship between a class and an object?",
            "options": [
                "A class is a blueprint; an object is an instance created from it",
                "They are two names for exactly the same thing",
                "An object is a blueprint; a class is an instance of it",
                "A class holds only data, and an object holds only methods",
            ],
            "correct_index": 0,
            "explanation": "The class describes the fields and methods. Each `new` call builds an object from that blueprint with its own field values.",
        },
    },
    {
        "id": "java8",
        "module_id": "java-m2",
        "title": "Sharing Behavior with Inheritance and Interfaces",
        "concept": "Java Inheritance and Interfaces",
        "explanation": (
            "With `extends`, a subclass inherits the fields and methods of a parent class and can override methods to change their behavior. "
            "An `interface` is a contract listing methods a class promises to provide, and a class signs it with `implements`. "
            "Code written against a parent type or interface works with any subclass, which is called polymorphism."
        ),
        "code_example": """interface Attacker { int damage(); }

class Monster implements Attacker {
    public int damage() { return 5; }
}
class Dragon extends Monster {
    @Override public int damage() { return super.damage() * 10; }
}
public class Main {
    public static void main(String[] args) {
        for (Attacker foe : new Attacker[] {new Monster(), new Dragon()}) {
            System.out.println(foe.damage());  // 5, then 50
        }
    }
}""",
        "code_walkthrough": [
            "`interface Attacker` declares a `damage()` method without saying how it works.",
            "`class Monster implements Attacker` keeps the promise by providing `damage()`.",
            "`class Dragon extends Monster` inherits from `Monster`, and `@Override` replaces its `damage()`.",
            "`super.damage() * 10` calls the parent's version (5) and multiplies it.",
            "The loop treats both objects as `Attacker`, yet each runs its own `damage()`: 5, then 50.",
        ],
        "key_points": [
            "A class can `extend` only one class but `implement` many interfaces.",
            "Use `@Override` so the compiler checks you really are overriding a method.",
            "Program to interfaces so new types can slot in without changing existing code.",
        ],
        "analogy": (
            "An interface is like a job description, and inheritance is like a family recipe: "
            "the child gets the parent's recipe and can add their own twist."
        ),
        "quiz": {
            "question": "How many classes can a Java class directly `extend`?",
            "options": [
                "None; Java has no inheritance",
                "As many as it likes",
                "Exactly one",
                "Exactly two",
            ],
            "correct_index": 2,
            "explanation": "Java allows single class inheritance, so a class extends at most one class. It can implement any number of interfaces.",
        },
    },
    {
        "id": "java9",
        "module_id": "java-m3",
        "title": "Flexible Storage with Lists and Maps",
        "concept": "Java Collections: ArrayList and HashMap",
        "explanation": (
            "The Collections Framework gives you resizable data structures, unlike fixed-size arrays. "
            "A `List` such as `ArrayList` keeps items in order and grows as you `add`, while a `Map` such as `HashMap` stores key-value pairs for fast lookup by key. "
            "You declare variables with the interface type (`List`, `Map`) and choose the implementation with `new`."
        ),
        "code_example": """import java.util.*;

public class Main {
    public static void main(String[] args) {
        List<String> party = new ArrayList<>();
        party.add("Duke");
        party.add("Ada");
        System.out.println(party + " " + party.size());   // [Duke, Ada] 2
        Map<String, Integer> gold = new HashMap<>();
        gold.put("Duke", 40);
        gold.put("Duke", 50);                             // replaces 40
        System.out.println(gold.get("Duke"));             // 50
        System.out.println(gold.getOrDefault("Ada", 0));  // 0
    }
}""",
        "code_walkthrough": [
            "`import java.util.*;` brings in `List`, `ArrayList`, `Map` and `HashMap`.",
            "`List<String> party = new ArrayList<>();` creates an empty, growable list of strings.",
            "`party.add(...)` appends items, and `party.size()` reports how many there are.",
            '`gold.put("Duke", 50)` overwrites the old value because each key appears only once in a map.',
            '`gold.getOrDefault("Ada", 0)` returns 0 because there is no "Ada" key.',
        ],
        "key_points": [
            "`List` keeps order and allows duplicates; access items with `get(index)`.",
            "`Map` links unique keys to values; `put` adds or replaces, `get` looks up.",
            "Collections hold objects, so use wrapper types like `Integer` instead of `int`.",
        ],
        "analogy": (
            "A `List` is like a queue of players waiting in line, and a `Map` is like a "
            "coat check where each ticket number gets you exactly one coat."
        ),
        "quiz": {
            "question": 'What does `gold.get("Zed")` return if the `HashMap` has no "Zed" key?',
            "options": ["0", "null", "An empty string", "It throws an exception"],
            "correct_index": 1,
            "explanation": "`get` returns `null` for a missing key. Use `getOrDefault` or `containsKey` when a key might not be there.",
        },
        "try_it": {
            "prompt": 'Create a `Map<String, Integer>` named `stock`, put "potion" with the value 3, then print `stock.get("potion")`.',
            "starter_code": (
                "import java.util.*;\n"
                "\n"
                "public class Main {\n"
                "    public static void main(String[] args) {\n"
                "        // create a map called stock here\n"
                "\n"
                "        // print how many potions are in stock\n"
                "    }\n"
                "}\n"
            ),
            "checks": [
                {
                    "pattern": r"stock\s*=\s*new\s+(Hash|Tree|LinkedHash)Map\s*<",
                    "hint": "Create it with `Map<String, Integer> stock = new HashMap<>();`.",
                },
                {
                    "pattern": r"stock\s*\.\s*put\s*\(\s*\"potion\"\s*,\s*3\s*\)",
                    "hint": 'Add the entry with `stock.put("potion", 3);`.',
                },
                {
                    "pattern": r"stock\s*\.\s*get\s*\(\s*\"potion\"\s*\)",
                    "hint": 'Look the value up with `stock.get("potion")` and print it.',
                },
            ],
            "expected_output": "3",
        },
    },
    {
        "id": "java10",
        "module_id": "java-m3",
        "title": "Reusable, Type-Safe Code with Generics",
        "concept": "Java Generics",
        "explanation": (
            "Generics let you write a class or method once with a type parameter like `<T>`, then use it with many types safely. "
            "The compiler fills in `T` (for example `String` or `Integer`), so it catches type mistakes early and you never need risky casts. "
            "That's why collections are written as `List<String>` or `Map<String, Integer>`."
        ),
        "code_example": """class Box<T> {
    private final T item;
    Box(T item) { this.item = item; }
    T open() { return item; }
}

public class Main {
    public static void main(String[] args) {
        Box<String> scroll = new Box<>("Fireball");
        Box<Integer> chest = new Box<>(100);
        String spell = scroll.open();             // no cast needed
        System.out.println(spell.toUpperCase());  // FIREBALL
        System.out.println(chest.open() + 1);     // 101
    }
}""",
        "code_walkthrough": [
            "`class Box<T>` declares a type parameter `T` that stands in for a real type.",
            "`private final T item;` and `T open()` use `T`, so they work with whatever type the box holds.",
            '`Box<String> scroll = new Box<>("Fireball");` fixes `T` as `String`; the empty `<>` (diamond) lets Java infer it.',
            "`scroll.open()` returns a `String` directly, so `toUpperCase()` works without a cast.",
            "`chest.open() + 1` works because that box's `T` is `Integer`.",
        ],
        "key_points": [
            "A type parameter like `<T>` is a placeholder filled in when the class is used.",
            "Generics move type errors from runtime to compile time.",
            "Type arguments must be reference types: write `List<Integer>`, not `List<int>`.",
        ],
        "analogy": (
            "A generic class is like a labeled storage jar: the jar design is the same, but once "
            'you label it "cookies", nobody can sneak in a sock.'
        ),
        "quiz": {
            "question": "Why can't you write `List<int>` in Java?",
            "options": [
                "Lists can only hold Strings",
                "int values are too big to store in a list",
                "You can; List<int> is valid but slower",
                "Type arguments must be reference types, so you use List<Integer>",
            ],
            "correct_index": 3,
            "explanation": "Generics only work with object types. Each primitive has a wrapper class (`int` to `Integer`), and Java converts between them automatically (autoboxing).",
        },
    },
    {
        "id": "java11",
        "module_id": "java-m3",
        "title": "Handling Errors with Exceptions",
        "concept": "Java Exception Handling",
        "explanation": (
            "When something goes wrong at runtime, Java throws an exception object that stops normal flow until some code catches it. "
            "You wrap risky code in `try`, handle specific problems in `catch`, and put cleanup that must always run in `finally`. "
            "Checked exceptions, such as `IOException`, must be caught or declared with `throws`, while unchecked ones extend `RuntimeException`."
        ),
        "code_example": """public class Main {
    public static void main(String[] args) {
        String[] inputs = {"42", "abc"};
        for (String input : inputs) {
            try {
                int n = Integer.parseInt(input);
                System.out.println("Got " + n);               // Got 42
            } catch (NumberFormatException e) {
                System.out.println("Not a number: " + input); // Not a number: abc
            } finally {
                System.out.println("Done with " + input);     // Done with 42, Done with abc
            }
        }
    }
}""",
        "code_walkthrough": [
            '`Integer.parseInt(input)` turns "42" into the number 42 but throws a `NumberFormatException` for "abc".',
            'For "42" the `try` block finishes normally and prints Got 42.',
            'For "abc" the exception jumps straight to the matching `catch` block, skipping the rest of `try`.',
            "The `finally` block runs in both cases, so it's the place for cleanup.",
            "Because the error was caught, the program keeps running instead of crashing.",
        ],
        "key_points": [
            "Catch the most specific exception type you can handle.",
            "`finally` runs whether or not an exception was thrown.",
            'Use `throw new IllegalArgumentException("...")` to signal bad input in your own methods.',
        ],
        "analogy": (
            "Exceptions are like a fire alarm: normal work stops, everyone heads to the "
            "designated exit (`catch`), and the building still gets locked up afterwards (`finally`)."
        ),
        "quiz": {
            "question": "Which of these is a checked exception that the compiler forces you to catch or declare?",
            "options": [
                "IOException",
                "NullPointerException",
                "ArithmeticException",
                "IllegalArgumentException",
            ],
            "correct_index": 0,
            "explanation": "`IOException` is checked. The other three extend `RuntimeException`, so they are unchecked and the compiler doesn't force you to handle them.",
        },
    },
    {
        "id": "java12",
        "module_id": "java-m3",
        "title": "Processing Data with Streams and Lambdas",
        "concept": "Java Streams and Lambda Expressions",
        "explanation": (
            "A lambda like `s -> s >= 50` is a short, unnamed function you can pass to another method. "
            "The Stream API uses lambdas to process collections as a pipeline: `filter` keeps matching items, `map` transforms them, and a terminal step like `toList()` or `sum()` produces the result. "
            "Streams don't modify the original collection."
        ),
        "code_example": """import java.util.List;

public class Main {
    public static void main(String[] args) {
        List<Integer> scores = List.of(45, 82, 67, 91, 30);
        List<Integer> boosted = scores.stream()
                .filter(s -> s >= 50)
                .map(s -> s + 5)
                .toList();
        System.out.println(boosted);  // [87, 72, 96]
        int total = scores.stream().mapToInt(Integer::intValue).sum();
        System.out.println(total);    // 315
    }
}""",
        "code_walkthrough": [
            "`List.of(...)` creates a fixed list, and `scores.stream()` starts a pipeline over it.",
            "`.filter(s -> s >= 50)` keeps only 82, 67 and 91.",
            "`.map(s -> s + 5)` adds 5 to each remaining score.",
            "`.toList()` collects the results into a new list (Java 16+).",
            "`mapToInt(Integer::intValue).sum()` uses a method reference to turn the scores into `int` values and add them up.",
        ],
        "key_points": [
            "A lambda is written `parameters -> expression`.",
            "Stream pipelines are lazy and only run when a terminal operation is called.",
            "Streams leave the original collection unchanged.",
        ],
        "analogy": (
            "A stream is like a conveyor belt in a factory: items pass through stations that "
            "inspect (`filter`) and repaint (`map`) them, and the last station boxes them up."
        ),
        "quiz": {
            "question": "What does `List.of(1, 2, 3, 4).stream().filter(n -> n % 2 == 0).map(n -> n * 10).toList()` return?",
            "options": ["[10, 30]", "[2, 4]", "[20, 40]", "[10, 20, 30, 40]"],
            "correct_index": 2,
            "explanation": "`filter` keeps the even numbers 2 and 4, then `map` multiplies each by 10, giving [20, 40].",
        },
        "try_it": {
            "prompt": 'Use a stream with `filter` to keep only the names that start with "A", then print the list.',
            "starter_code": (
                "import java.util.List;\n"
                "\n"
                "public class Main {\n"
                "    public static void main(String[] args) {\n"
                '        List<String> names = List.of("Ada", "Bob", "Alan", "Cy");\n'
                "        List<String> aNames = names; // replace with a stream pipeline\n"
                "        System.out.println(aNames);\n"
                "    }\n"
                "}\n"
            ),
            "checks": [
                {
                    "pattern": r"names\s*\.\s*stream\s*\(\s*\)",
                    "hint": "Start the pipeline with `names.stream()`.",
                },
                {
                    "pattern": r"\.\s*filter\s*\(\s*\(?\s*\w+\s*\)?\s*->",
                    "hint": "Pass a lambda to filter, like `.filter(n -> ...)`.",
                },
                {
                    "pattern": r"startsWith\s*\(\s*\"A\"\s*\)",
                    "hint": 'Test each name with `n.startsWith("A")`.',
                },
            ],
            "expected_output": "[Ada, Alan]",
        },
    },
]
