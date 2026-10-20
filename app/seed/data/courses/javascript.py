"""JavaScript Essentials: Master modern JavaScript and the fundamentals of web development."""

COURSE = {
    "id": "javascript-essentials",
    "title": "JavaScript Essentials",
    "world": "JavaScript World",
    "description": "Master modern JavaScript and the fundamentals of web development.",
    "language": "javascript",
    "modules": [
        {"id": "jm1", "title": "Syntax & Types"},
        {"id": "jm2", "title": "Functions & Scope"},
        {"id": "jm3", "title": "Async JavaScript"},
    ],
}

ZONES = [
    {
        "id": "js-z1",
        "name": "Syntax Plains",
        "tagline": "Values, operators and the flow of a program.",
        "difficulty": "easy",
        "nodes": [
            {"id": "js1", "title": "Variables & Types", "difficulty": "easy", "xp_reward": 50, "estimated_minutes": 10},
            {"id": "js2", "title": "Operators", "difficulty": "easy", "xp_reward": 50, "estimated_minutes": 10},
            {"id": "js3", "title": "Conditionals", "difficulty": "easy", "xp_reward": 60, "estimated_minutes": 12},
            {"id": "js4", "title": "Loops", "difficulty": "easy", "xp_reward": 70, "estimated_minutes": 15},
            {"id": "js5", "title": "Functions", "difficulty": "easy", "xp_reward": 70, "estimated_minutes": 15},
        ],
        "boss": {
            "id": "js-z1-boss",
            "name": "Syntax Slime",
            "sprite": "slime",
            "challenge": "Clean up 3 broken snippets of everyday JavaScript",
            "stages": 3,
            "xp_reward": 250,
        },
    },
    {
        "id": "js-z2",
        "name": "Closure Caves",
        "tagline": "Scope, objects and the array toolbox.",
        "difficulty": "medium",
        "nodes": [
            {
                "id": "js6",
                "title": "Scope & Closures",
                "difficulty": "medium",
                "xp_reward": 90,
                "estimated_minutes": 18,
            },
            {
                "id": "js7",
                "title": "Arrays & Objects",
                "difficulty": "medium",
                "xp_reward": 100,
                "estimated_minutes": 20,
            },
            {"id": "js8", "title": "Array Methods", "difficulty": "medium", "xp_reward": 100, "estimated_minutes": 20},
            {"id": "js9", "title": "Promises", "difficulty": "medium", "xp_reward": 120, "estimated_minutes": 22},
        ],
        "boss": {
            "id": "js-z2-boss",
            "name": "Callback Kraken",
            "sprite": "bugSlime",
            "challenge": "Untangle nested callbacks into clean promise chains",
            "stages": 4,
            "xp_reward": 400,
        },
    },
    {
        "id": "js-z3",
        "name": "Async Peaks",
        "tagline": "Talk to servers and bring web pages to life.",
        "difficulty": "hard",
        "nodes": [
            {"id": "js10", "title": "Async / Await", "difficulty": "hard", "xp_reward": 140, "estimated_minutes": 25},
            {"id": "js11", "title": "DOM Basics", "difficulty": "hard", "xp_reward": 160, "estimated_minutes": 30},
            {"id": "js12", "title": "Events", "difficulty": "hard", "xp_reward": 150, "estimated_minutes": 25},
            {"id": "js13", "title": "Modules", "difficulty": "hard", "xp_reward": 140, "estimated_minutes": 22},
        ],
        "boss": {
            "id": "js-z3-boss",
            "name": "Event Loop Lich",
            "sprite": "recursionBoss",
            "challenge": "Predict the output of tricky async code, round by round",
            "stages": 5,
            "xp_reward": 800,
        },
    },
]

LESSONS: list[dict] = [
    {
        "id": "js1",
        "module_id": "jm1",
        "title": "let, const and JavaScript Types",
        "concept": "Variables & Types",
        "explanation": (
            "Modern JavaScript declares variables with `const` (can't be reassigned) and `let` (can be reassigned). "
            "Values have types such as string, number, boolean, undefined, null and object. "
            "The `typeof` operator tells you a value's type at runtime."
        ),
        "code_example": """const name = "Ada";        // can't be reassigned
let score = 10;            // can change
score += 5;
console.log(typeof name);  // string
console.log(typeof score); // number
console.log(typeof null);  // object (a famous quirk)""",
        "code_walkthrough": [
            '`const name = "Ada";` creates a constant binding that can\'t be reassigned.',
            "`let score = 10;` creates a variable that can change.",
            "`score += 5;` updates `score` to 15.",
            '`typeof name` and `typeof score` report "string" and "number".',
            '`typeof null` returns "object", a long-standing JavaScript quirk.',
        ],
        "key_points": [
            "Default to `const`; use `let` only when you need to reassign.",
            "Avoid the old `var` keyword in modern code.",
            '`typeof` reveals a value\'s type, but reports `null` as "object".',
        ],
        "analogy": (
            "`const` is like a name engraved on a trophy, while `let` is like a name written "
            "on a whiteboard that you can erase and rewrite."
        ),
        "quiz": {
            "question": "What happens when you run `const x = 1; x = 2;`?",
            "options": ["x becomes 2", "x stays 1 silently", "A TypeError is thrown", "x becomes undefined"],
            "correct_index": 2,
            "explanation": "Reassigning a `const` throws `TypeError: Assignment to constant variable.`",
        },
    },
    {
        "id": "js2",
        "module_id": "jm1",
        "title": "Doing Math and Comparisons",
        "concept": "Operators",
        "explanation": (
            "Operators perform math (`+ - * / % **`), comparisons (`===`, `<`, `>=`) and logic (`&&`, `||`, `!`). "
            "Always prefer strict equality `===`, because loose `==` converts types before comparing and can surprise you. "
            "The `??` operator gives a fallback only when a value is `null` or `undefined`."
        ),
        "code_example": """console.log(7 % 3);             // 1
console.log(2 ** 3);            // 8
console.log("5" == 5);          // true (converts types)
console.log("5" === 5);         // false (strict)
console.log(true && false);     // false
console.log(null ?? "default"); // default""",
        "code_walkthrough": [
            "`7 % 3` is the remainder after division: 1.",
            "`2 ** 3` raises 2 to the power of 3: 8.",
            '`"5" == 5` is true because `==` converts the string to a number first.',
            '`"5" === 5` is false because the types differ.',
            '`null ?? "default"` falls back to "default" because the left side is `null`.',
        ],
        "key_points": [
            "Use `===` and `!==` to compare without type conversion.",
            "`%` gives the remainder, handy for checking even or odd numbers.",
            "`&&` and `||` combine conditions; `??` supplies defaults for null or undefined.",
        ],
        "analogy": (
            "`==` is like a bouncer who lets in anyone who looks roughly right; `===` checks "
            "both the name and the photo ID."
        ),
        "quiz": {
            "question": 'What does `"5" + 3` evaluate to in JavaScript?',
            "options": ["8", '"53"', "NaN", "A TypeError"],
            "correct_index": 1,
            "explanation": 'When either side of `+` is a string, JavaScript converts the other side to a string and concatenates, giving "53".',
        },
    },
    {
        "id": "js3",
        "module_id": "jm1",
        "title": "Choosing a Path with if and Ternaries",
        "concept": "Conditionals",
        "explanation": (
            "`if`, `else if` and `else` run different code depending on whether a condition is truthy. "
            "The ternary operator `condition ? a : b` is a compact way to choose between two values. "
            'Falsy values (`false`, `0`, `""`, `null`, `undefined`, `NaN`) count as false; everything else is truthy.'
        ),
        "code_example": """const age = 20;
if (age >= 18) {
  console.log("Adult");     // Adult
} else {
  console.log("Minor");
}
const label = age >= 18 ? "can vote" : "too young";
console.log(label);         // can vote""",
        "code_walkthrough": [
            "`const age = 20;` sets the value to test.",
            '`if (age >= 18)` is true, so "Adult" is logged.',
            "The `else` block is skipped.",
            '`age >= 18 ? "can vote" : "too young"` picks the first value because the condition is true.',
        ],
        "key_points": [
            "Conditions go in parentheses and code blocks go in curly braces.",
            "Use a ternary for simple either/or values, and `if` for bigger blocks of logic.",
            'Know the falsy values: `false`, `0`, `""`, `null`, `undefined` and `NaN`.',
        ],
        "analogy": (
            "A conditional is like a fork in a hiking trail: a sign (the condition) tells you which path to take."
        ),
        "quiz": {
            "question": "Which of these values is falsy in JavaScript?",
            "options": ['"0"', "[]", "{}", "0"],
            "correct_index": 3,
            "explanation": 'The number `0` is falsy. The string "0", an empty array and an empty object are all truthy.',
        },
        "try_it": {
            "prompt": 'Use a ternary to set `result` to "pass" if `score` is 50 or more, otherwise "fail".',
            "starter_code": "const score = 72;\n// const result = ...\n\nconsole.log(result);\n",
            "checks": [
                {
                    "pattern": r"(const|let)\s+result\s*=",
                    "hint": "Declare `result` with `const`.",
                },
                {
                    "pattern": r"score\s*>=\s*50\s*\?\s*[\"'`]pass[\"'`]\s*:\s*[\"'`]fail[\"'`]",
                    "hint": 'Use the form `score >= 50 ? "pass" : "fail"`.',
                },
            ],
            "expected_output": "pass",
        },
    },
    {
        "id": "js4",
        "module_id": "jm1",
        "title": "Looping in JavaScript",
        "concept": "Loops",
        "explanation": (
            "The classic `for` loop uses a counter with a start, a condition and a step. "
            "`for...of` walks through the values of an array (or any iterable) without needing an index. "
            "`while` loops repeat as long as a condition stays true."
        ),
        "code_example": """for (let i = 0; i < 3; i++) {
  console.log(i);            // 0, 1, 2
}
const colors = ["red", "green"];
for (const c of colors) {
  console.log(c);            // red, green
}""",
        "code_walkthrough": [
            "`let i = 0` starts the counter, `i < 3` is checked before each pass, and `i++` runs after each pass.",
            "`console.log(i)` logs 0, 1 and 2.",
            '`const colors = ["red", "green"];` creates an array to loop over.',
            '`for (const c of colors)` gives each value in turn: "red", then "green".',
        ],
        "key_points": [
            "Use a classic `for` loop when you need the index.",
            "Use `for...of` to loop over array values.",
            "`for...in` loops over keys (property names), so avoid it for arrays.",
        ],
        "analogy": (
            "A `for` loop is like doing laps around a track with a lap counter; `for...of` is like "
            "walking down a line of people and greeting each one."
        ),
        "quiz": {
            "question": "Which loop gives you each value of an array directly?",
            "options": ["for...of", "for...in", "do...while", "if...else"],
            "correct_index": 0,
            "explanation": '`for...of` iterates over values. `for...in` iterates over keys, which for arrays are index strings like "0".',
        },
    },
    {
        "id": "js5",
        "module_id": "jm2",
        "title": "Declaring and Calling Functions",
        "concept": "Functions",
        "explanation": (
            "Functions are reusable blocks of code that take parameters and can return a value. "
            "You can write them as function declarations or as shorter arrow functions. "
            "An arrow function with no curly braces returns its expression automatically."
        ),
        "code_example": """function add(a, b) {
  return a + b;
}
const multiply = (a, b) => a * b;
const greet = (name = "friend") => `Hi, ${name}!`;
console.log(add(2, 3));       // 5
console.log(multiply(4, 5));  // 20
console.log(greet());         // Hi, friend!""",
        "code_walkthrough": [
            "`function add(a, b) { return a + b; }` is a function declaration with an explicit return.",
            "`const multiply = (a, b) => a * b;` is an arrow function that returns `a * b` implicitly.",
            '`(name = "friend")` gives the parameter a default value.',
            "The template literal `` `Hi, ${name}!` `` inserts the value of `name` into the string.",
            '`greet()` is called with no argument, so the default "friend" is used.',
        ],
        "key_points": [
            "Functions return `undefined` unless you `return` something.",
            "Arrow functions without braces return their expression automatically.",
            "Default parameters cover missing arguments.",
        ],
        "analogy": (
            "A function is like a vending machine: put in inputs (coins and a choice), and it hands back a result."
        ),
        "quiz": {
            "question": "What does `f(3)` return?\n\nconst f = (x) => { x * 2 };",
            "options": ["6", '"x * 2"', "undefined", "A SyntaxError"],
            "correct_index": 2,
            "explanation": "With curly braces, an arrow function needs an explicit `return`. Without it, the function returns `undefined`.",
        },
    },
    {
        "id": "js6",
        "module_id": "jm2",
        "title": "Where Variables Live: Scope and Closures",
        "concept": "Scope & Closures",
        "explanation": (
            "Scope decides where a variable can be used: `let` and `const` are visible only inside the block `{}` where they're declared. "
            "Inner functions can read variables from the functions around them. "
            "A closure happens when an inner function keeps remembering those outer variables even after the outer function has finished."
        ),
        "code_example": """function makeCounter() {
  let count = 0;              // private to makeCounter
  return () => ++count;       // inner function remembers count
}
const counter = makeCounter();
console.log(counter());       // 1
console.log(counter());       // 2""",
        "code_walkthrough": [
            "`let count = 0;` lives inside `makeCounter`, so code outside can't touch it directly.",
            "`return () => ++count;` returns an inner function that increments and returns `count`.",
            "`const counter = makeCounter();` runs the outer function once and keeps the returned function.",
            "Each `counter()` call updates the same remembered `count`: 1, then 2.",
        ],
        "key_points": [
            "`let` and `const` are block-scoped.",
            "Inner functions can access variables from outer scopes.",
            "Closures let functions keep private state between calls.",
        ],
        "analogy": (
            "A closure is like a backpack: when a function leaves home, it carries the "
            "variables it needs along with it."
        ),
        "quiz": {
            "question": "What happens here?\n\nif (true) { let x = 1; }\nconsole.log(x);",
            "options": ["It logs 1", "It throws a ReferenceError", "It logs undefined", "It logs null"],
            "correct_index": 1,
            "explanation": "`let` is block-scoped, so `x` doesn't exist outside the `if` block and accessing it throws a ReferenceError.",
        },
    },
    {
        "id": "js7",
        "module_id": "jm1",
        "title": "Grouping Data in Arrays and Objects",
        "concept": "Arrays & Objects",
        "explanation": (
            "Arrays hold ordered lists of values accessed by index, while objects hold named properties as key-value pairs. "
            "Both can be changed even when declared with `const`, because `const` only stops reassignment of the variable itself. "
            "Destructuring lets you pull values out into variables in one step."
        ),
        "code_example": """const user = { name: "Sam", age: 25 };
user.email = "sam@example.com";
console.log(user.name);           // Sam
const nums = [10, 20, 30];
nums.push(40);
console.log(nums.length);         // 4
const { name, age } = user;       // destructuring
console.log(`${name} is ${age}`); // Sam is 25""",
        "code_walkthrough": [
            '`const user = { name: "Sam", age: 25 };` creates an object with two properties.',
            "`user.email = ...` adds a new property using dot notation.",
            "`nums.push(40)` adds an item to the end of the array, so its length becomes 4.",
            "`const { name, age } = user;` copies the `name` and `age` properties into variables.",
        ],
        "key_points": [
            "Arrays use numeric indexes starting at 0; objects use named keys.",
            'Access properties with `obj.key` or `obj["key"]`.',
            "`const` arrays and objects can still be modified; they just can't be reassigned.",
        ],
        "analogy": (
            "An array is like a numbered row of lockers; an object is like a filing cabinet with labeled folders."
        ),
        "quiz": {
            "question": "What happens when you run `const nums = [1]; nums.push(2);`?",
            "options": [
                "A TypeError, because nums is const",
                "nums stays [1]",
                "nums becomes [2]",
                "It works, and nums becomes [1, 2]",
            ],
            "correct_index": 3,
            "explanation": "`const` prevents reassigning `nums`, but the array itself can still be modified, so `push` works.",
        },
    },
    {
        "id": "js8",
        "module_id": "jm2",
        "title": "Transforming Arrays with map, filter and reduce",
        "concept": "Array Methods",
        "explanation": (
            "Array methods take a callback function and apply it to each element. "
            "`map` transforms every item, `filter` keeps items that pass a test, and `reduce` combines everything into a single value. "
            "`map` and `filter` return new arrays and leave the original unchanged."
        ),
        "code_example": """const prices = [5, 12, 8, 20];
const doubled = prices.map(p => p * 2);
const big = prices.filter(p => p > 10);
const total = prices.reduce((sum, p) => sum + p, 0);
console.log(doubled);  // [10, 24, 16, 40]
console.log(big);      // [12, 20]
console.log(total);    // 45""",
        "code_walkthrough": [
            "`prices.map(p => p * 2)` creates a new array with every price doubled.",
            "`prices.filter(p => p > 10)` keeps only prices above 10.",
            "`prices.reduce((sum, p) => sum + p, 0)` starts at 0 and adds each price to the running sum.",
            "The original `prices` array is not changed by any of these calls.",
        ],
        "key_points": [
            "`map` returns a new array of the same length.",
            "`filter` returns a new array with only the items whose callback returns true.",
            "`reduce` boils an array down to one value; always pass a starting value.",
        ],
        "analogy": (
            "Think of a factory line: `map` paints every item, `filter` removes the faulty ones, "
            "and `reduce` packs everything into one box."
        ),
        "quiz": {
            "question": "What does `[1, 2, 3].map(n => n * 10)` return?",
            "options": ["[10, 20, 30]", "60", "[1, 2, 3]", "[10]"],
            "correct_index": 0,
            "explanation": "`map` applies the callback to every element and returns a new array of results.",
        },
        "try_it": {
            "prompt": "Use `filter` to keep only the even numbers from `nums`.",
            "starter_code": 'const nums = [1, 2, 3, 4, 5, 6];\nconst evens = // your code here\n\nconsole.log(evens.join(", "));\n',
            "checks": [
                {
                    "pattern": r"nums\s*\.\s*filter\s*\(",
                    "hint": "Call `nums.filter(...)` with a callback.",
                },
                {
                    "pattern": r"%\s*2\s*===?\s*0",
                    "hint": "A number is even when `n % 2 === 0`.",
                },
            ],
            "expected_output": "2, 4, 6",
        },
    },
    {
        "id": "js9",
        "module_id": "jm3",
        "title": "Promises: Values from the Future",
        "concept": "Promises",
        "explanation": (
            "A Promise represents a value that isn't ready yet, such as the result of a network request or a timer. "
            "It starts pending and then either fulfills with a value or rejects with an error. "
            "You react to the outcome with `.then()` for success and `.catch()` for errors."
        ),
        "code_example": """const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
wait(500)
  .then(() => {
    console.log("Half a second later");
    return 42;
  })
  .then((value) => console.log(value))  // 42
  .catch((err) => console.error(err));""",
        "code_walkthrough": [
            "`new Promise((resolve) => setTimeout(resolve, ms))` creates a Promise that fulfills after `ms` milliseconds.",
            "`wait(500).then(...)` schedules code to run once the Promise fulfills.",
            "`return 42;` passes a value to the next `.then()` in the chain.",
            "`.then((value) => console.log(value))` receives 42 and logs it.",
            "`.catch(...)` handles an error from any earlier step in the chain.",
        ],
        "key_points": [
            "A Promise is pending, then either fulfilled or rejected.",
            "Returning a value from `.then()` passes it down the chain.",
            "One `.catch()` at the end handles errors from the whole chain.",
        ],
        "analogy": (
            "A Promise is like a restaurant buzzer: you get it right away, and it goes off "
            "later when your food is ready (or tells you something went wrong)."
        ),
        "quiz": {
            "question": "Which of these is NOT a state a Promise can be in?",
            "options": ["pending", "fulfilled", "rejected", "paused"],
            "correct_index": 3,
            "explanation": "Promises are only ever pending, fulfilled or rejected. There is no paused state.",
        },
    },
    {
        "id": "js10",
        "module_id": "jm3",
        "title": "Writing Async Code with async/await",
        "concept": "Async / Await",
        "explanation": (
            "`async` and `await` let you write Promise-based code that reads top to bottom like normal code. "
            "Inside an `async` function, `await` pauses that function until a Promise settles, without freezing the rest of the page. "
            "An `async` function always returns a Promise, and you handle errors with an ordinary `try`/`catch`."
        ),
        "code_example": """const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
async function run() {
  console.log("Start");
  await wait(1000);          // pauses run(), not the whole page
  console.log("1 second later");
  return "done";
}
run().then((msg) => console.log(msg)); // done""",
        "code_walkthrough": [
            "`wait(ms)` returns a Promise that fulfills after a delay.",
            "`async function run()` marks the function as asynchronous.",
            "`await wait(1000);` pauses `run` for one second until the Promise fulfills.",
            '`return "done";` fulfills the Promise that `run()` returns.',
            '`run().then(...)` receives "done" once the function finishes.',
        ],
        "key_points": [
            "`await` only works inside `async` functions (or at the top level of modules).",
            "An `async` function always returns a Promise.",
            "Wrap `await` calls in `try`/`catch` to handle rejected Promises.",
        ],
        "analogy": (
            "`await` is like putting a pot on to boil and checking your phone: you pause that "
            "task, but the rest of your kitchen keeps running."
        ),
        "quiz": {
            "question": "What does an `async` function always return?",
            "options": ["undefined", "A Promise", "The awaited value directly", "A callback function"],
            "correct_index": 1,
            "explanation": "Whatever you return from an `async` function is wrapped in a Promise, so callers use `await` or `.then()` to get the value.",
        },
    },
    {
        "id": "js11",
        "module_id": "jm3",
        "title": "Changing the Page with the DOM",
        "concept": "DOM Basics",
        "explanation": (
            "The DOM (Document Object Model) is the browser's tree of objects representing your HTML page. "
            "JavaScript can find elements with `document.querySelector()` and then change their text, classes or styles. "
            "You can also create new elements and add them to the page."
        ),
        "code_example": """const title = document.querySelector("#title");
title.textContent = "Welcome to Logicraft!";
title.classList.add("highlight");
const item = document.createElement("li");
item.textContent = "New item";
document.querySelector("ul").appendChild(item);""",
        "code_walkthrough": [
            '`document.querySelector("#title")` finds the first element with `id="title"`.',
            "`title.textContent = ...` replaces the element's text.",
            '`title.classList.add("highlight")` adds a CSS class without removing others.',
            '`document.createElement("li")` builds a new list item in memory.',
            "`appendChild(item)` inserts it into the first `<ul>` on the page.",
        ],
        "key_points": [
            "`querySelector` uses CSS selectors and returns the first match (or `null`).",
            "Prefer `textContent` over `innerHTML` for plain text; it's safer.",
            "Use `classList` to add, remove or toggle CSS classes.",
        ],
        "analogy": (
            "The DOM is like a puppet on strings: your HTML builds the puppet, and JavaScript "
            "pulls the strings to change it live."
        ),
        "quiz": {
            "question": 'If a page has three elements with class `card`, what does `document.querySelector(".card")` return?',
            "options": [
                "The first matching element",
                "All three elements",
                "The last matching element",
                "null, because there is more than one match",
            ],
            "correct_index": 0,
            "explanation": "`querySelector` returns only the first match. Use `querySelectorAll` to get all of them.",
        },
    },
    {
        "id": "js12",
        "module_id": "jm3",
        "title": "Responding to Clicks and Other Events",
        "concept": "Events",
        "explanation": (
            "Events are signals the browser sends when something happens, like a click, a key press or a form submit. "
            "You respond by attaching a handler function with `addEventListener`. "
            "The handler receives an event object with details, and `event.preventDefault()` stops the browser's default action."
        ),
        "code_example": """const button = document.querySelector("#save");
button.addEventListener("click", (event) => {
  console.log("Saved!");
  console.log(event.target.id);   // save
});
const form = document.querySelector("form");
form.addEventListener("submit", (e) => e.preventDefault());""",
        "code_walkthrough": [
            '`document.querySelector("#save")` finds the button.',
            '`addEventListener("click", ...)` runs the handler every time the button is clicked.',
            '`event.target` is the element that triggered the event, so its `id` is "save".',
            "`e.preventDefault()` stops the form from submitting and reloading the page.",
        ],
        "key_points": [
            "Use `addEventListener(type, handler)` to react to events.",
            "The event object describes what happened, including `event.target`.",
            "`preventDefault()` cancels default browser behavior like form submission.",
        ],
        "analogy": (
            "An event listener is like a doorbell: nothing happens until someone presses it, "
            "and then your chosen action runs."
        ),
        "quiz": {
            "question": "What does calling `event.preventDefault()` in a form's submit handler do?",
            "options": [
                "Removes the form from the page",
                "Stops other listeners from running",
                "Stops the browser from submitting the form and reloading the page",
                "Clears all of the form's inputs",
            ],
            "correct_index": 2,
            "explanation": "`preventDefault()` cancels the browser's default action for the event, which for a submit is sending the form and reloading.",
        },
    },
    {
        "id": "js13",
        "module_id": "jm2",
        "title": "Organizing Code with Modules",
        "concept": "Modules",
        "explanation": (
            "ES modules let you split code across files and share only what you choose. "
            "Use `export` to make values available and `import` to bring them into another file. "
            "A module can have many named exports but only one default export."
        ),
        "code_example": """// math.js
export const PI = 3.14159;
export default function area(r) {
  return PI * r * r;
}
// main.js
import area, { PI } from "./math.js";
console.log(area(2).toFixed(2));  // 12.57""",
        "code_walkthrough": [
            "`export const PI = 3.14159;` is a named export from `math.js`.",
            "`export default function area(r)` is the module's single default export.",
            '`import area, { PI } from "./math.js";` imports the default (any name works) and the named export (exact name in braces).',
            '`area(2).toFixed(2)` computes 3.14159 * 2 * 2 and rounds it to "12.57".',
        ],
        "key_points": [
            "Named exports are imported with curly braces and must match the exported name.",
            "Each module has at most one default export, imported without braces.",
            "Modules keep their variables private unless they're exported.",
        ],
        "analogy": (
            "Modules are like rooms in a house: each has its own stuff, and you choose what "
            "to pass through the doorway to other rooms."
        ),
        "quiz": {
            "question": "How many default exports can a single module have?",
            "options": ["Unlimited", "One", "Two", "None; only named exports are allowed"],
            "correct_index": 1,
            "explanation": "A module can have only one `export default`, but as many named exports as it needs.",
        },
    },
]
