"""TypeScript Essentials: Add static types to JavaScript and catch bugs before your code ever runs."""

COURSE = {
    "id": "typescript-essentials",
    "title": "TypeScript Essentials",
    "world": "TypeScript Citadel",
    "description": "Add static types to your JavaScript and catch bugs before your code ever runs.",
    "language": "typescript",
    "modules": [
        {"id": "ts-m1", "title": "Types & Functions"},
        {"id": "ts-m2", "title": "Shaping Data"},
        {"id": "ts-m3", "title": "Advanced Types & Async"},
    ],
}

ZONES = [
    {
        "id": "ts-z1",
        "name": "Annotation Outpost",
        "tagline": "Label your values and let the compiler guard the gates.",
        "difficulty": "easy",
        "nodes": [
            {
                "id": "ts1",
                "title": "Types & Annotations",
                "difficulty": "easy",
                "xp_reward": 50,
                "estimated_minutes": 10,
            },
            {"id": "ts2", "title": "Type Inference", "difficulty": "easy", "xp_reward": 50, "estimated_minutes": 10},
            {"id": "ts3", "title": "Arrays & Tuples", "difficulty": "easy", "xp_reward": 60, "estimated_minutes": 12},
            {"id": "ts4", "title": "Typed Functions", "difficulty": "easy", "xp_reward": 60, "estimated_minutes": 12},
        ],
        "boss": {
            "id": "ts-z1-boss",
            "name": "The Any Slime",
            "sprite": "slime",
            "challenge": "Replace every sneaky `any` with a real type before the slime spreads",
            "stages": 3,
            "xp_reward": 250,
        },
    },
    {
        "id": "ts-z2",
        "name": "Interface Keep",
        "tagline": "Shape your objects, juggle unions and narrow them safely.",
        "difficulty": "medium",
        "nodes": [
            {
                "id": "ts5",
                "title": "Interfaces & Type Aliases",
                "difficulty": "medium",
                "xp_reward": 90,
                "estimated_minutes": 18,
            },
            {
                "id": "ts6",
                "title": "Union & Literal Types",
                "difficulty": "medium",
                "xp_reward": 100,
                "estimated_minutes": 20,
            },
            {"id": "ts7", "title": "Type Narrowing", "difficulty": "medium", "xp_reward": 100, "estimated_minutes": 20},
            {
                "id": "ts8",
                "title": "Classes & Access Modifiers",
                "difficulty": "medium",
                "xp_reward": 110,
                "estimated_minutes": 20,
            },
        ],
        "boss": {
            "id": "ts-z2-boss",
            "name": "Union Hydra",
            "sprite": "bugSlime",
            "challenge": "Narrow a many-headed union until every case is handled",
            "stages": 4,
            "xp_reward": 400,
        },
    },
    {
        "id": "ts-z3",
        "name": "Generic Spire",
        "tagline": "Reusable types, smart utilities and typed async code.",
        "difficulty": "hard",
        "nodes": [
            {"id": "ts9", "title": "Generics", "difficulty": "hard", "xp_reward": 140, "estimated_minutes": 25},
            {"id": "ts10", "title": "Utility Types", "difficulty": "hard", "xp_reward": 150, "estimated_minutes": 28},
            {
                "id": "ts11",
                "title": "Enums & as const",
                "difficulty": "hard",
                "xp_reward": 150,
                "estimated_minutes": 25,
            },
            {
                "id": "ts12",
                "title": "Async/Await with Types",
                "difficulty": "hard",
                "xp_reward": 160,
                "estimated_minutes": 30,
            },
        ],
        "boss": {
            "id": "ts-z3-boss",
            "name": "The Generic Overlord",
            "sprite": "recursionBoss",
            "challenge": "Forge type-safe helpers that work for any data, round by round",
            "stages": 5,
            "xp_reward": 700,
        },
    },
]

LESSONS: list[dict] = [
    {
        "id": "ts1",
        "module_id": "ts-m1",
        "title": "Labeling Values with Types",
        "concept": "Type Annotations",
        "explanation": (
            "TypeScript is JavaScript plus static types: you can label a variable with `: type` to say what it may hold. "
            "The compiler checks these labels before your code runs and reports a mistake, such as putting text into a number variable, as an error. "
            "The types are erased when TypeScript compiles to JavaScript, so they cost nothing at runtime."
        ),
        "code_example": """let username: string = "Ada";
let level: number = 3;
let isOnline: boolean = true;
level = level + 1;
// level = "four"; // Error: Type 'string' is not assignable to type 'number'.
console.log(`${username} is level ${level}`); // Ada is level 4
console.log(typeof isOnline);                 // boolean""",
        "code_walkthrough": [
            "`let username: string` tells TypeScript that `username` may only ever hold text.",
            "`level: number` and `isOnline: boolean` use the other two everyday primitive types.",
            "`level = level + 1;` is fine because the result is still a number.",
            'Uncommenting `level = "four";` makes the compiler refuse to build your code.',
            "At runtime the types are gone, so `typeof isOnline` is plain JavaScript and prints `boolean`.",
        ],
        "key_points": [
            "Annotate with `name: type`, for example `let age: number = 30;`.",
            "Type errors are caught at compile time, before the code ever runs.",
            "Avoid `any`: it switches type checking off for that value.",
        ],
        "analogy": (
            "Type annotations are like labels on storage boxes: once a box says 'Books', the compiler "
            "stops anyone from packing shoes into it."
        ),
        "quiz": {
            "question": 'What happens when TypeScript sees `let count: number = "5";`?',
            "options": [
                "It compiles fine and count holds the string",
                "It reports a compile-time type error",
                'It silently converts "5" to the number 5',
                "Nothing until the line runs, then it throws",
            ],
            "correct_index": 1,
            "explanation": "A string isn't assignable to a `number` variable, so the compiler reports an error before the code runs.",
        },
    },
    {
        "id": "ts2",
        "module_id": "ts-m1",
        "title": "Letting TypeScript Figure It Out",
        "concept": "Type Inference",
        "explanation": (
            "You don't have to annotate everything: TypeScript infers a type from the value you assign. "
            "`let` variables get a general type like `number`, while `const` variables get the exact literal value as their type. "
            "Inference also flows into callbacks, so array methods know the type of each item automatically."
        ),
        "code_example": """let score = 10;            // inferred as number
const greeting = "hello";  // inferred as the literal type "hello"
const items = [1, 2, 3];   // inferred as number[]
const doubled = items.map((n) => n * 2); // n is a number
console.log(doubled);      // [ 2, 4, 6 ]
score += 5;
// score = "high"; // Error: Type 'string' is not assignable to type 'number'.
console.log(score, greeting.toUpperCase()); // 15 HELLO""",
        "code_walkthrough": [
            "`let score = 10;` has no annotation, but TypeScript infers `number` from the value.",
            '`const greeting = "hello";` can never change, so its type is the literal `"hello"`.',
            "`[1, 2, 3]` is inferred as `number[]`, and `map` knows each `n` is a number.",
            "Inferred types are just as strict: assigning a string to `score` would be an error.",
            "`greeting.toUpperCase()` is allowed because TypeScript knows `greeting` is a string.",
        ],
        "key_points": [
            "Let inference handle obvious local variables; annotate function parameters and public APIs.",
            "`let` infers a wide type (`number`); `const` infers a literal type (`10`).",
            "Hover over a variable in your editor to see the type TypeScript inferred.",
        ],
        "analogy": (
            "Inference is like a smart librarian: you hand over a cookbook and they file it under "
            "'Cooking' without you writing a label."
        ),
        "quiz": {
            "question": "What type does TypeScript infer for `let x = 42;`?",
            "options": ["any", "42", "number", "unknown"],
            "correct_index": 2,
            "explanation": "`let` variables can be reassigned, so TypeScript widens the value to `number`. Only `const x = 42` would get the literal type `42`.",
        },
    },
    {
        "id": "ts3",
        "module_id": "ts-m1",
        "title": "Typed Lists and Fixed-Size Tuples",
        "concept": "Tuples",
        "explanation": (
            "An array type like `number[]` (or `Array<number>`) holds any number of items of the same type. "
            "A tuple like `[string, number]` is an array with a fixed length where each position has its own type. "
            "Adding `readonly` stops an array or tuple from being changed."
        ),
        "code_example": """const scores: number[] = [90, 75, 88];
const names: Array<string> = ["Ada", "Linus"];
scores.push(100);
// scores.push("A+"); // Error: 'string' is not assignable to 'number'.
const player: [string, number] = ["Ada", 42];
const [hero, hp] = player;
console.log(scores.length, names[1]); // 4 Linus
console.log(`${hero} has ${hp} HP`);  // Ada has 42 HP
const point: readonly [number, number] = [3, 4];
console.log(point[0] + point[1]);     // 7""",
        "code_walkthrough": [
            "`number[]` and `Array<string>` are two ways to write an array type.",
            "`scores.push(100)` is fine, but pushing a string would be a compile error.",
            "`[string, number]` is a tuple: position 0 is a string and position 1 is a number.",
            "Destructuring `const [hero, hp] = player;` gives `hero` type `string` and `hp` type `number`.",
            "`readonly [number, number]` makes the pair unchangeable, so `point[0] = 9` would be an error.",
        ],
        "key_points": [
            "Use `T[]` for lists of any length where every item has the same type.",
            "Use tuples for small fixed-shape groups, like a coordinate or a key-value pair.",
            "`readonly` arrays and tuples block `push`, `pop` and index assignment.",
        ],
        "analogy": (
            "An array is like an egg carton that only takes eggs, however many you have; a tuple "
            "is like a lunchbox with one slot for a sandwich and one slot for an apple."
        ),
        "quiz": {
            "question": "Which type describes exactly two items: a string followed by a number?",
            "options": ["[string, number]", "string[] | number[]", "Array<string | number>", "{ string, number }"],
            "correct_index": 0,
            "explanation": "A tuple type `[string, number]` fixes both the length and the type at each position. `Array<string | number>` allows any mix and any length.",
        },
    },
    {
        "id": "ts4",
        "module_id": "ts-m1",
        "title": "Functions with Typed Inputs and Outputs",
        "concept": "Function Types",
        "explanation": (
            "In TypeScript you annotate each function parameter and, optionally, the return type after the parameter list. "
            "A `?` after a parameter name makes it optional, and rest parameters collect extra arguments into a typed array. "
            "Functions that don't return anything use the `void` return type."
        ),
        "code_example": """function add(a: number, b: number): number {
  return a + b;
}
const greet = (name: string, title?: string): string =>
  title ? `Hello, ${title} ${name}` : `Hello, ${name}`;
function logAll(...msgs: string[]): void {
  console.log(msgs.join(" | "));
}
console.log(add(2, 3));           // 5
console.log(greet("Ada"));        // Hello, Ada
console.log(greet("Ada", "Dr.")); // Hello, Dr. Ada
logAll("start", "load", "done");  // start | load | done
// add("2", 3); // Error: 'string' is not assignable to parameter of type 'number'.""",
        "code_walkthrough": [
            "`add(a: number, b: number): number` types both inputs and promises a number back.",
            "`title?: string` is optional, so inside the function its type is `string | undefined`.",
            "`...msgs: string[]` gathers any number of string arguments into one array.",
            "`: void` says `logAll` doesn't return a useful value.",
            'Calling `add("2", 3)` would be rejected by the compiler instead of quietly returning "23".',
        ],
        "key_points": [
            "Always annotate parameters; TypeScript can usually infer the return type, but writing it documents intent.",
            "Optional parameters (`x?: T`) must come after required ones.",
            "Use `void` for functions that only perform side effects.",
        ],
        "analogy": (
            "A typed function is like a vending machine that only accepts coins of the right size "
            "and promises exactly what will drop out."
        ),
        "quiz": {
            "question": "What does the `?` mean in `function show(label?: string)`?",
            "options": [
                "label can be any type",
                "label must be passed",
                "label must be null",
                "label is optional and may be undefined",
            ],
            "correct_index": 3,
            "explanation": "A `?` marks the parameter as optional. If the caller leaves it out, its value is `undefined`, so its type is `string | undefined`.",
        },
        "try_it": {
            "prompt": "Add types so `area` takes two numbers, `width` and `height`, and returns a number.",
            "starter_code": "function area(width, height) {\n  return width * height;\n}\n\nconsole.log(area(3, 4));\n",
            "checks": [
                {
                    "pattern": r"width\s*:\s*number",
                    "hint": "Annotate the first parameter as `width: number`.",
                },
                {
                    "pattern": r"height\s*:\s*number",
                    "hint": "Annotate the second parameter as `height: number`.",
                },
                {
                    "pattern": r"\)\s*:\s*number\s*\{",
                    "hint": "Add the return type after the parameter list: `): number {`.",
                },
            ],
            "expected_output": "12",
        },
    },
    {
        "id": "ts5",
        "module_id": "ts-m2",
        "title": "Describing Object Shapes",
        "concept": "Interfaces",
        "explanation": (
            "An `interface` describes the shape of an object: which properties it has and what type each one is. "
            "A `type` alias can name any type, including object shapes, unions and tuples. "
            "Mark properties with `?` to make them optional and with `readonly` to stop them from being reassigned."
        ),
        "code_example": """interface Player {
  readonly id: number;   // can't change after creation
  name: string;
  level: number;
  guild?: string;        // optional
}
type Point = { x: number; y: number };
const hero: Player = { id: 1, name: "Ada", level: 5 };
const spawn: Point = { x: 0, y: 10 };
hero.level += 1;
// hero.id = 2; // Error: Cannot assign to 'id' because it is a read-only property.
console.log(`${hero.name} Lv.${hero.level}`); // Ada Lv.6
console.log(hero.guild ?? "no guild");        // no guild
console.log(spawn);                           // { x: 0, y: 10 }""",
        "code_walkthrough": [
            "`interface Player { ... }` lists the properties every player object must have.",
            "`readonly id` can be set when the object is created but never reassigned.",
            "`guild?: string` is optional, so `hero` is valid without it and its value is `undefined`.",
            "`type Point = { x: number; y: number };` names an object shape with a type alias.",
            '`hero.guild ?? "no guild"` supplies a fallback because `guild` is missing.',
        ],
        "key_points": [
            "Interfaces can `extend` other interfaces; type aliases combine shapes with `&`.",
            "Use `type` for unions, tuples and other non-object types; either works for object shapes.",
            "Object literals with extra, unknown properties are flagged, which catches typos.",
        ],
        "analogy": (
            "An interface is like a form with labeled fields: any object that fills in every "
            "required field correctly is accepted."
        ),
        "quiz": {
            "question": "Which keyword lets one interface build on another, as in `interface Admin ___ User { ... }`?",
            "options": ["implements", "inherits", "extends", "with"],
            "correct_index": 2,
            "explanation": "`interface Admin extends User` gives `Admin` all of `User`'s properties plus its own. `implements` is used by classes.",
        },
        "try_it": {
            "prompt": "Write an interface named `Item` with a `name` property (string) and a `price` property (number).",
            "starter_code": '// Define the Item interface here\n\nconst sword: Item = { name: "Sword", price: 150 };\nconsole.log(sword.name, sword.price);\n',
            "checks": [
                {
                    "pattern": r"interface\s+Item\s*\{",
                    "hint": "Start with `interface Item {`.",
                },
                {
                    "pattern": r"name\s*\??\s*:\s*string",
                    "hint": "Add `name: string;` inside the interface.",
                },
                {
                    "pattern": r"price\s*\??\s*:\s*number",
                    "hint": "Add `price: number;` inside the interface.",
                },
            ],
            "expected_output": "Sword 150",
        },
    },
    {
        "id": "ts6",
        "module_id": "ts-m2",
        "title": "This or That: Unions and Literals",
        "concept": "Union Types",
        "explanation": (
            "A union type like `number | string` means a value can be one of several types. "
            'Literal types pin a value to exact options, so `"up" | "down"` accepts only those two strings. '
            "Combining unions with literals is a lightweight way to model a fixed set of choices."
        ),
        "code_example": """type Id = number | string;
type Direction = "up" | "down" | "left" | "right";
function formatId(id: Id): string {
  return `#${id}`;
}
function move(dir: Direction): string {
  return `Moving ${dir}`;
}
console.log(formatId(42));   // #42
console.log(formatId("a7")); // #a7
console.log(move("left"));   // Moving left
// move("jump"); // Error: '"jump"' is not assignable to parameter of type 'Direction'.""",
        "code_walkthrough": [
            "`type Id = number | string;` accepts either a number or a string.",
            '`type Direction = "up" | "down" | "left" | "right";` allows only those four exact strings.',
            "`formatId` works with both kinds of `Id` because template literals accept either one.",
            '`move("left")` compiles, but a typo like `move("jump")` is caught by the compiler.',
        ],
        "key_points": [
            "Read `A | B` as 'A or B'.",
            "String literal unions give you autocomplete and catch typos in fixed options.",
            "With a union you may only use members common to every type until you narrow it.",
        ],
        "analogy": (
            "A literal union is like a drink menu: you can order coffee, tea or juice, but asking "
            "for 'lava' gets politely refused."
        ),
        "quiz": {
            "question": 'Given `type Size = "S" | "M" | "L";`, which line compiles?',
            "options": [
                'const s: Size = "M";',
                'const s: Size = "XL";',
                'const s: Size = "m";',
                "const s: Size = 2;",
            ],
            "correct_index": 0,
            "explanation": 'Only the exact strings "S", "M" and "L" are allowed. Literal types are case-sensitive, so "m" fails too.',
        },
    },
    {
        "id": "ts7",
        "module_id": "ts-m2",
        "title": "Narrowing Down What a Value Is",
        "concept": "Type Narrowing",
        "explanation": (
            "When a value has a union type, TypeScript lets you use type-specific features only after you check which type it is. "
            "Checks like `typeof`, `instanceof`, `in` and comparing a shared `kind` property narrow the type inside that branch. "
            "A union of objects that share a literal `kind` field is called a discriminated union."
        ),
        "code_example": """type Shape =
  | { kind: "circle"; radius: number }
  | { kind: "square"; side: number };
function area(shape: Shape): number {
  if (shape.kind === "circle") {
    return Math.PI * shape.radius ** 2; // shape is the circle here
  }
  return shape.side ** 2;               // so here it must be the square
}
function clean(value: string | number): string {
  return typeof value === "number" ? value.toFixed(1) : value.trim();
}
console.log(area({ kind: "square", side: 3 }));              // 9
console.log(area({ kind: "circle", radius: 1 }).toFixed(2)); // 3.14
console.log(clean(5), clean("  hi  "));                      // 5.0 hi""",
        "code_walkthrough": [
            "`Shape` is a discriminated union: both members have a `kind` field with a different literal value.",
            '`if (shape.kind === "circle")` narrows `shape` to the circle, so `shape.radius` is allowed.',
            "After the `if` returns, only the square is left, so `shape.side` is allowed.",
            '`typeof value === "number"` narrows `value`, so `toFixed` and `trim` are each used on the right type.',
        ],
        "key_points": [
            "Use `typeof` for primitives and `instanceof` for class instances.",
            "Give related object types a shared literal `kind` field and check it to narrow.",
            "TypeScript tracks `return` and `else` branches, so the remaining type shrinks as you go.",
        ],
        "analogy": (
            "Narrowing is like a detective ruling out suspects: each clue you check shrinks the "
            "list until only one possibility is left."
        ),
        "quiz": {
            "question": 'If `x: string | number`, what is the type of `x` inside `if (typeof x === "string") { ... }`?',
            "options": ["string | number", "unknown", "number", "string"],
            "correct_index": 3,
            "explanation": 'The `typeof x === "string"` check narrows the union, so inside that block TypeScript knows `x` is a `string`.',
        },
        "try_it": {
            "prompt": "Finish `measure`: if `value` is a string, return its length; otherwise return the number doubled.",
            "starter_code": 'function measure(value: string | number): number {\n  // narrow the type here\n  return 0;\n}\n\nconsole.log(measure("hello"), measure(21));\n',
            "checks": [
                {
                    "pattern": r"typeof\s+value\s*===?\s*[\"'`](string|number)[\"'`]",
                    "hint": 'Check the type with `typeof value === "string"`.',
                },
                {
                    "pattern": r"value\s*\.\s*length",
                    "hint": "Return `value.length` for strings.",
                },
                {
                    "pattern": r"value\s*\*\s*2|2\s*\*\s*value",
                    "hint": "Return `value * 2` for numbers.",
                },
            ],
            "expected_output": "5 42",
        },
    },
    {
        "id": "ts8",
        "module_id": "ts-m2",
        "title": "Classes with Public and Private Parts",
        "concept": "Access Modifiers",
        "explanation": (
            "TypeScript classes work like JavaScript classes but let you type their fields and methods. "
            "Access modifiers control who can use a member: `public` (anyone, the default), `protected` (the class and its subclasses) and `private` (only the class itself). "
            "Parameter properties like `constructor(public name: string)` declare and assign a field in one step."
        ),
        "code_example": """class BankAccount {
  private balance = 0;
  constructor(public readonly owner: string) {}
  deposit(amount: number): void {
    if (amount <= 0) throw new Error("Deposit must be positive");
    this.balance += amount;
  }
  getBalance(): number {
    return this.balance;
  }
}
const account = new BankAccount("Ada");
account.deposit(50);
console.log(account.owner, account.getBalance()); // Ada 50
// account.balance = 1e6; // Error: Property 'balance' is private.""",
        "code_walkthrough": [
            "`private balance = 0;` can only be read or changed by code inside `BankAccount`.",
            "`constructor(public readonly owner: string) {}` creates a public, read-only `owner` field automatically.",
            "`deposit` is the only way to add money, so it can reject invalid amounts.",
            "`getBalance()` exposes the balance for reading without allowing outside writes.",
            "Writing `account.balance` from outside the class is a compile-time error.",
        ],
        "key_points": [
            "Members are `public` unless you say otherwise.",
            "`private` and `protected` are checked at compile time; use JavaScript `#field` for runtime privacy.",
            "Parameter properties remove the boilerplate of declaring and assigning constructor fields.",
        ],
        "analogy": (
            "A class with private fields is like an ATM: you press public buttons like 'deposit', "
            "but you can't reach inside and grab the cash drawer."
        ),
        "quiz": {
            "question": "Which modifier allows access inside the class and its subclasses, but not from outside?",
            "options": ["public", "protected", "private", "readonly"],
            "correct_index": 1,
            "explanation": "`protected` members are visible to the class and any class that extends it. `private` members are visible only to the class itself.",
        },
    },
    {
        "id": "ts9",
        "module_id": "ts-m3",
        "title": "Reusable Code with Generics",
        "concept": "Generics",
        "explanation": (
            "Generics let you write one function, interface or class that works with many types while keeping full type safety. "
            "A type parameter such as `<T>` is a placeholder that gets filled in, usually by inference, each time the code is used. "
            "Constraints like `<T extends { length: number }>` limit which types are allowed."
        ),
        "code_example": """function first<T>(items: T[]): T | undefined {
  return items[0];
}
interface Box<T> {
  value: T;
}
const n = first([10, 20, 30]); // T is number
const s = first(["a", "b"]);   // T is string
const box: Box<boolean> = { value: true };
console.log(n, s, box.value);  // 10 a true
function longest<T extends { length: number }>(a: T, b: T): T {
  return a.length >= b.length ? a : b;
}
console.log(longest("hi", "hello")); // hello
console.log(longest([1, 2], [3]));   // [ 1, 2 ]""",
        "code_walkthrough": [
            "`first<T>(items: T[]): T | undefined` returns the same type that the array holds.",
            "`first([10, 20, 30])` infers `T` as `number`, so `n` is typed `number | undefined`.",
            "`Box<T>` is a generic interface, and `Box<boolean>` fills in `T` explicitly.",
            "`T extends { length: number }` only accepts types with a `length`, such as strings and arrays.",
            "`longest` returns whichever argument is longer, keeping its original type.",
        ],
        "key_points": [
            "Generics keep the link between input and output types, unlike `any`.",
            "TypeScript usually infers type arguments, so you rarely write `first<number>(...)`.",
            "Use `extends` to constrain a type parameter to what your code needs.",
        ],
        "analogy": (
            "A generic is like a cookie cutter: the shape stays the same, but you choose the dough "
            "(the type) each time you use it."
        ),
        "quiz": {
            "question": "Given `function wrap<T>(x: T): T[] { return [x]; }`, what type does `wrap(true)` return?",
            "options": ["any[]", "T[]", "boolean[]", "boolean"],
            "correct_index": 2,
            "explanation": "TypeScript infers `T` as `boolean` from the argument, so the return type `T[]` becomes `boolean[]`.",
        },
        "try_it": {
            "prompt": "Make `last` generic with a type parameter named `T`, so it returns the last item of any array with the right type.",
            "starter_code": 'function last(items: number[]): number | undefined {\n  return items[items.length - 1];\n}\n\nconsole.log(last(["a", "b", "c"]));\n',
            "checks": [
                {
                    "pattern": r"last\s*<\s*T\s*>",
                    "hint": "Declare the type parameter right after the name: `function last<T>(...)`.",
                },
                {
                    "pattern": r"items\s*:\s*(T\s*\[\s*\]|Array\s*<\s*T\s*>)",
                    "hint": "Type the parameter as `items: T[]`.",
                },
            ],
            "expected_output": "c",
        },
    },
    {
        "id": "ts10",
        "module_id": "ts-m3",
        "title": "Transforming Types with Utility Types",
        "concept": "Utility Types",
        "explanation": (
            "TypeScript ships with built-in utility types that build new types from existing ones. "
            "`Partial<T>` makes every property optional, `Pick<T, K>` keeps only some properties, `Omit<T, K>` removes some, and `Record<K, V>` describes an object whose keys map to values of one type. "
            "They help you avoid copying the same shape over and over."
        ),
        "code_example": """interface User {
  id: number;
  name: string;
  email: string;
}
type UserUpdate = Partial<User>;              // every field optional
type UserPreview = Pick<User, "id" | "name">; // only id and name
type PublicUser = Omit<User, "email">;        // everything except email
const patch: UserUpdate = { name: "Ada L." };
const preview: UserPreview = { id: 1, name: "Ada" };
const pub: PublicUser = { id: 2, name: "Linus" };
const roles: Record<string, number> = { admin: 3, editor: 2 };
console.log(Object.keys(patch));        // [ 'name' ]
console.log(preview.name, roles.admin); // Ada 3
console.log(pub);                       // { id: 2, name: 'Linus' }""",
        "code_walkthrough": [
            "`Partial<User>` lets `patch` contain just the fields being updated.",
            '`Pick<User, "id" | "name">` keeps only the listed keys.',
            '`Omit<User, "email">` keeps every key except `email`, which is handy for public data.',
            "`Record<string, number>` types an object whose keys are strings and whose values are numbers.",
            "Utility types exist only at compile time; at runtime these are ordinary objects.",
        ],
        "key_points": [
            "`Partial`, `Required` and `Readonly` change every property at once.",
            "`Pick` and `Omit` select or drop properties by key name.",
            "`Record<K, V>` is a quick way to type dictionaries and lookup tables.",
        ],
        "analogy": (
            "Utility types are like photo filters: you start with one picture (your type) and "
            "quickly produce variations without redrawing it."
        ),
        "quiz": {
            "question": "Which utility type makes every property of `T` optional?",
            "options": ["Partial<T>", "Required<T>", "Pick<T, K>", "Readonly<T>"],
            "correct_index": 0,
            "explanation": "`Partial<T>` adds `?` to every property. `Required<T>` does the opposite, and `Readonly<T>` makes them unchangeable.",
        },
    },
    {
        "id": "ts11",
        "module_id": "ts-m3",
        "title": "Named Constants with Enums and as const",
        "concept": "Enums",
        "explanation": (
            "An `enum` gives friendly names to a set of related constants; numeric enums count up from 0 by default, and string enums use the values you assign. "
            "The `as const` assertion makes an object or array deeply read-only and keeps its exact literal values. "
            "Many teams use `as const` with a union type as a lighter alternative to enums."
        ),
        "code_example": """enum Status {
  Idle,
  Running,
  Done,
}
enum Color {
  Red = "RED",
  Green = "GREEN",
}
const DIRECTIONS = ["north", "south"] as const;
type Direction = (typeof DIRECTIONS)[number]; // "north" | "south"
const heading: Direction = "north";
console.log(Status.Running, Status[2]);  // 1 Done
console.log(Color.Green);                // GREEN
console.log(heading, DIRECTIONS.length); // north 2""",
        "code_walkthrough": [
            "`enum Status { Idle, Running, Done }` numbers its members 0, 1 and 2.",
            'Numeric enums also map backwards, so `Status[2]` gives the name `"Done"`.',
            '`Color.Green` is a string enum member with the value `"GREEN"`.',
            '`as const` turns the array into `readonly ["north", "south"]` instead of `string[]`.',
            '`(typeof DIRECTIONS)[number]` turns that array into the union `"north" | "south"`.',
        ],
        "key_points": [
            "Numeric enums start at 0 unless you assign values.",
            "String enums are easier to read in logs and API responses.",
            "`as const` plus a derived union type gives enum-like safety using plain JavaScript values.",
        ],
        "analogy": (
            "An enum is like the labeled buttons on an elevator: you press 'Lobby' instead of "
            "remembering that the lobby is floor 0."
        ),
        "quiz": {
            "question": "What is the value of `Status.Idle` in `enum Status { Idle, Running }`?",
            "options": ['"Idle"', "1", "undefined", "0"],
            "correct_index": 3,
            "explanation": "Numeric enum members start at 0 by default, so `Idle` is 0 and `Running` is 1.",
        },
    },
    {
        "id": "ts12",
        "module_id": "ts-m3",
        "title": "Typed Promises with async/await",
        "concept": "Async/Await",
        "explanation": (
            "An `async` function always returns a Promise, and in TypeScript you describe what it resolves to with `Promise<T>`. "
            "`await` unwraps that Promise, so the result gets the inner type `T` automatically. "
            "In strict mode a caught error has type `unknown`, so you check it, for example with `instanceof Error`, before using it."
        ),
        "code_example": """interface Quest { id: number; title: string }
async function fetchQuest(id: number): Promise<Quest> {
  if (id <= 0) throw new Error("Invalid quest id");
  return { id, title: `Quest #${id}` }; // pretend this came from an API
}
async function main(): Promise<void> {
  const quest = await fetchQuest(7); // quest is typed as Quest
  console.log(quest.title);          // Quest #7
  try {
    await fetchQuest(0);
  } catch (err) {                    // err is 'unknown' in strict mode
    if (err instanceof Error) console.log(err.message); // Invalid quest id
  }
}
main();""",
        "code_walkthrough": [
            "`Promise<Quest>` declares that `fetchQuest` eventually produces a `Quest`.",
            "Throwing inside an `async` function rejects the Promise it returns.",
            "`await fetchQuest(7)` unwraps the Promise, so `quest` has the type `Quest`.",
            "`catch (err)` gives `err` the type `unknown`, so `err instanceof Error` narrows it before `err.message` is read.",
        ],
        "key_points": [
            "Annotate async functions with `Promise<T>`, never just `T`.",
            "`await` turns a `Promise<T>` into a `T`.",
            "Narrow `unknown` errors in `catch` before using their properties.",
        ],
        "analogy": (
            "A `Promise<Quest>` is like a parcel tracking number that's guaranteed to deliver a "
            "quest scroll: you don't have it yet, but you know exactly what will arrive."
        ),
        "quiz": {
            "question": "What is the inferred return type of `async function getCount() { return 5; }`?",
            "options": ["number", "Promise<number>", "Promise<void>", "number | undefined"],
            "correct_index": 1,
            "explanation": "An `async` function always wraps its result in a Promise, so returning a number gives `Promise<number>`.",
        },
    },
]
