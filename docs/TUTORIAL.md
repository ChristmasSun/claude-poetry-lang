# Lament Tutorial

A complete step-by-step guide to learning Lament from zero to hero.

---

## Table of Contents

1. [Introduction](#introduction)
2. [Lesson 1: Hello, World](#lesson-1-hello-world)
3. [Lesson 2: Variables and Types](#lesson-2-variables-and-types)
4. [Lesson 3: Functions](#lesson-3-functions)
5. [Lesson 4: Control Flow](#lesson-4-control-flow)
6. [Lesson 5: Collections](#lesson-5-collections)
7. [Lesson 6: Timeline Features](#lesson-6-timeline-features)
8. [Lesson 7: Time-Travel Debugging](#lesson-7-time-travel-debugging)
9. [Lesson 8: Causal Debugging](#lesson-8-causal-debugging)
10. [Lesson 9: Temporal Contracts](#lesson-9-temporal-contracts)
11. [Lesson 10: Reality Branching](#lesson-10-reality-branching)
12. [Lesson 11: Neural Networks](#lesson-11-neural-networks)
13. [Lesson 12: Metaprogramming](#lesson-12-metaprogramming)
14. [Lesson 13: File I/O](#lesson-13-file-io)
15. [Lesson 14: Building a Real Project](#lesson-14-building-a-real-project)

---

## Introduction

Welcome to Lament! This tutorial will teach you everything you need to know.

### Prerequisites
- Basic programming knowledge
- Python 3.8+ installed
- Lament installed ([Installation Guide](../INSTALL.md))

### What You'll Learn
- Lament syntax and semantics
- Timeline variables and temporal programming
- Causal debugging and why it matters
- Reality branching for parallel execution
- Neural networks as language primitives
- Building real projects in Lament

### How to Follow Along

Start the Lament REPL:
```bash
python3 lament/cli.py repl
```

Or create `.lament` files and run them:
```bash
python3 lament/cli.py run myprogram.lament
```

Let's begin!

---

## Lesson 1: Hello, World

### Your First Program

Create a file called `hello.lament`:

```lament
confess "Hello, World!"
```

Run it:
```bash
python3 lament/cli.py run hello.lament
```

Output:
```
Hello, World!
```

### Understanding `confess`

In Lament, `confess` is how you output to the console. It's not just print—it's a confession with emotional weight. The output pauses for 0.3 seconds to give your words gravitas.

```lament
confess "This is important"
confess "Every word matters"
```

### Comments

```lament
# This is a single-line comment

/* This is a
   multi-line
   comment */

confess "Hello, World!"  # Inline comment
```

**Exercise 1.1**: Create a program that confesses your name and favorite programming language.

<details>
<summary>Solution</summary>

```lament
confess "My name is Alice"
confess "I love learning Lament!"
```
</details>

---

## Lesson 2: Variables and Types

### Declaring Variables

Use `remember` to create variables:

```lament
remember age = 25
remember name = "Alice"
remember is_student = true
remember nothing = void
```

### Types

Lament has emotional types:

```lament
remember count = 42           # numb (integer)
remember pain = 3.14          # ache (float)
remember message = "hi"       # whisper (string)
remember decision = true      # maybe (boolean)
remember absence = void       # void (null)
```

### Type Checking

```lament
remember x = 42

if is_numb(x) {
    confess "x is a number"
}

remember t = typeof(x)
confess t  # "numb"
```

### Reassignment

```lament
remember x = 1
confess x  # 1

x = 2
confess x  # 2

x = 3
confess x  # 3
```

**Exercise 2.1**: Create variables for your name, age, and whether you like programming. Check their types.

<details>
<summary>Solution</summary>

```lament
remember my_name = "Alice"
remember my_age = 25
remember likes_programming = true

confess "Name type: " + typeof(my_name)
confess "Age type: " + typeof(my_age)
confess "Likes programming type: " + typeof(likes_programming)
```
</details>

---

## Lesson 3: Functions

### Defining Functions

Functions in Lament are called "sighs" (regretful computations):

```lament
sigh greet(name) {
    confess "Hello, " + name
}

greet("Alice")
greet("Bob")
```

### Return Values

Use `exhale` to return:

```lament
sigh add(a, b) {
    exhale a + b
}

remember sum = add(5, 3)
confess sum  # 8
```

### Multiple Parameters

```lament
sigh calculate_total(price, quantity, tax_rate) {
    remember subtotal = price * quantity
    remember tax = subtotal * tax_rate
    remember total = subtotal + tax
    exhale total
}

remember result = calculate_total(100, 5, 0.1)
confess result  # 550
```

### Recursion

```lament
sigh factorial(n) {
    if n <= 1 {
        exhale 1
    }
    exhale n * factorial(n - 1)
}

confess factorial(5)  # 120
```

**Exercise 3.1**: Write a function that calculates the area of a rectangle.

<details>
<summary>Solution</summary>

```lament
sigh area(width, height) {
    exhale width * height
}

confess area(10, 5)  # 50
```
</details>

**Exercise 3.2**: Write a recursive function to calculate Fibonacci numbers.

<details>
<summary>Solution</summary>

```lament
sigh fibonacci(n) {
    if n <= 1 {
        exhale n
    }
    exhale fibonacci(n - 1) + fibonacci(n - 2)
}

for i in range(10) {
    confess fibonacci(i)
}
```
</details>

---

## Lesson 4: Control Flow

### If-Else

```lament
remember x = 42

if x > 50 {
    confess "Large"
} else if x > 20 {
    confess "Medium"
} else {
    confess "Small"
}
```

### While Loops

```lament
remember i = 0

while i < 5 {
    confess i
    i = i + 1
}
```

### For Loops

```lament
# Range
for i in range(5) {
    confess i
}

# List
remember fruits = ["apple", "banana", "cherry"]
for fruit in fruits {
    confess fruit
}
```

### Break and Continue

```lament
remember i = 0
while i < 10 {
    i = i + 1

    if i == 3 {
        continue  # Skip 3
    }

    if i == 7 {
        break  # Stop at 7
    }

    confess i
}
```

**Exercise 4.1**: Write a program that prints all even numbers from 1 to 20.

<details>
<summary>Solution</summary>

```lament
for i in range(1, 21) {
    if i % 2 == 0 {
        confess i
    }
}
```
</details>

**Exercise 4.2**: Write FizzBuzz (1-30: print "Fizz" for multiples of 3, "Buzz" for 5, "FizzBuzz" for both).

<details>
<summary>Solution</summary>

```lament
for i in range(1, 31) {
    if i % 15 == 0 {
        confess "FizzBuzz"
    } else if i % 3 == 0 {
        confess "Fizz"
    } else if i % 5 == 0 {
        confess "Buzz"
    } else {
        confess i
    }
}
```
</details>

---

## Lesson 5: Collections

### Lists

```lament
# Creation
remember numbers = [1, 2, 3, 4, 5]
remember names = ["Alice", "Bob", "Charlie"]
remember mixed = [1, "two", true, void]

# Access
confess numbers[0]  # 1
confess names[2]    # "Charlie"

# Modification
numbers[0] = 10
confess numbers  # [10, 2, 3, 4, 5]

# Length
confess length_of(numbers)  # 5

# Iteration
for num in numbers {
    confess num
}
```

### Dictionaries

```lament
# Creation
remember person = {
    "name": "Alice",
    "age": 30,
    "city": "NYC"
}

# Access
confess person["name"]  # "Alice"

# Modification
person["age"] = 31

# Add new key
person["email"] = "alice@example.com"

# Iteration
for key in person {
    confess key + ": " + person[key]
}
```

**Exercise 5.1**: Create a list of your top 5 favorite books and print them with numbers.

<details>
<summary>Solution</summary>

```lament
remember books = [
    "1984",
    "Brave New World",
    "Foundation",
    "Dune",
    "Neuromancer"
]

remember i = 1
for book in books {
    confess i + ". " + book
    i = i + 1
}
```
</details>

**Exercise 5.2**: Create a dictionary representing a car (make, model, year) and print each property.

<details>
<summary>Solution</summary>

```lament
remember car = {
    "make": "Tesla",
    "model": "Model 3",
    "year": 2023
}

for key in car {
    confess key + ": " + car[key]
}
```
</details>

---

## Lesson 6: Timeline Features

This is where Lament becomes revolutionary!

### Timeline Variables

Every variable in Lament is a timeline:

```lament
remember x = 1
x = 2
x = 3

confess x           # 3 (current)
confess x@past      # 2 (previous)
confess x@past(2)   # 1 (two steps back)
confess x@origin    # 1 (first value)
confess x@age       # 3 (assignment count)
```

### Tracking History

```lament
remember balance = 1000

balance = balance - 100  # Withdrew $100
balance = balance - 50   # Withdrew $50
balance = balance + 200  # Deposited $200

confess "Current: " + balance          # 1050
confess "Before deposit: " + balance@past     # 850
confess "Original: " + balance@origin         # 1000
confess "Transactions: " + balance@age        # 3
```

**Exercise 6.1**: Track a player's score through 5 rounds of a game.

<details>
<summary>Solution</summary>

```lament
remember score = 0

score = score + 10  # Round 1
score = score + 25  # Round 2
score = score + 15  # Round 3
score = score - 5   # Round 4 (penalty)
score = score + 30  # Round 5

confess "Final score: " + score
confess "After round 4: " + score@past
confess "After round 3: " + score@past(2)
confess "Initial score: " + score@origin
confess "Total rounds: " + score@age
```
</details>

---

## Lesson 7: Time-Travel Debugging

### Creating Snapshots

```lament
remember x = 1
remember s1 = snapshot()  # Save state

x = 2
remember s2 = snapshot()  # Save state

x = 3
remember s3 = snapshot()  # Save state

confess list_snapshots()  # Show all snapshots
```

### Rewinding Execution

```lament
remember x = 1
x = 2
x = 3

confess x  # 3

rewind(1)
confess x  # 2

rewind(1)
confess x  # 1
```

### Practical Use Case

```lament
remember balance = 1000

balance = balance - 100
confess "After withdrawal: " + balance

balance = balance - 950  # Oops! Overdraft

# Rewind to before the mistake
rewind(1)
confess "Balance restored: " + balance

# Try again correctly
balance = balance - 50
confess "Correct balance: " + balance
```

**Exercise 7.1**: Write a program that makes mistakes and uses rewind to fix them.

<details>
<summary>Solution</summary>

```lament
remember x = 10

x = x * 5   # Should have been * 2
confess "Oops: " + x  # 50

rewind(1)  # Go back

x = x * 2  # Correct operation
confess "Fixed: " + x  # 20
```
</details>

---

## Lesson 8: Causal Debugging

### The `why()` Function

Ask WHY a variable has its current value:

```lament
remember price = 100
remember quantity = 5
remember subtotal = price * quantity
remember tax = subtotal * 0.1
remember total = subtotal + tax

confess why(total)
```

Output:
```
╔══════════════════════════════════════════════════════════╗
║  🔍 CAUSAL TRACE: total                                  ║
╚══════════════════════════════════════════════════════════╝

Current value: 550
Last assigned: subtotal + tax
Dependencies:
  • subtotal = 500
    Last assigned: price * quantity
    Dependencies:
      • price = 100
      • quantity = 5
  • tax = 50
    Last assigned: subtotal * 0.1
```

### Debugging Complex Calculations

```lament
sigh calculate_shipping(weight, distance, is_express) {
    remember base_cost = weight * 0.5
    remember distance_cost = distance * 0.1
    remember express_fee = if is_express { 20 } else { 0 }
    remember total = base_cost + distance_cost + express_fee
    exhale total
}

remember shipping = calculate_shipping(10, 500, true)
confess why(shipping)
# See complete dependency tree!
```

**Exercise 8.1**: Create a complex calculation and use why() to understand it.

<details>
<summary>Solution</summary>

```lament
remember hours_worked = 40
remember hourly_rate = 25
remember overtime_hours = 10
remember overtime_rate = hourly_rate * 1.5

remember regular_pay = hours_worked * hourly_rate
remember overtime_pay = overtime_hours * overtime_rate
remember total_pay = regular_pay + overtime_pay

confess why(total_pay)
```
</details>

---

## Lesson 9: Temporal Contracts

### Invariants

Conditions that must ALWAYS be true:

```lament
invariant balance >= 0

remember balance = 1000

balance = balance - 500  # OK
confess "Balance: " + balance  # 500

balance = balance - 600  # VIOLATION!
# Beautiful error with full context
```

### Ensures

Post-conditions for functions:

```lament
sigh withdraw(amount) {
    ensures balance >= 0
    balance = balance - amount
}

remember balance = 1000
withdraw(500)  # OK
withdraw(600)  # VIOLATION!
```

### Eventually

Conditions that must become true within N steps:

```lament
eventually(10) balance > 1000

remember balance = 500

# ... within 10 assignments, balance must exceed 1000
balance = balance + 600  # Now balance = 1100, contract satisfied!
```

**Exercise 9.1**: Create a bank account system with invariants.

<details>
<summary>Solution</summary>

```lament
invariant balance >= 0
invariant balance <= 1000000  # Max balance

remember balance = 1000

sigh deposit(amount) {
    ensures amount > 0
    balance = balance + amount
}

sigh withdraw(amount) {
    ensures amount > 0
    ensures balance >= 0
    balance = balance - amount
}

deposit(500)
confess "Balance: " + balance

withdraw(200)
confess "Balance: " + balance
```
</details>

---

## Lesson 10: Reality Branching

### Forking Reality

Execute multiple timelines in parallel:

```lament
remember result = void

fork reality {
    on timeline("approach1") {
        result = 100 + 200
    }

    on timeline("approach2") {
        result = 150 * 2
    }
} collapse observe result

confess result  # Value from the winning timeline
confess "Winner: " + current_timeline()
```

### Practical Use: Algorithm Racing

```lament
remember data = [5, 2, 8, 1, 9, 3, 7, 4, 6]
remember sorted_data = void

fork reality {
    on timeline("quick") {
        sorted_data = quick_sort(data)
    }

    on timeline("merge") {
        sorted_data = merge_sort(data)
    }

    on timeline("bubble") {
        sorted_data = bubble_sort(data)
    }
} collapse observe sorted_data

confess "Sorted: " + sorted_data
confess "Winner: " + current_timeline()
```

**Exercise 10.1**: Use reality branching to find the fastest way to calculate something.

<details>
<summary>Solution</summary>

```lament
remember n = 10
remember result = void

fork reality {
    on timeline("iterative") {
        # Iterative factorial
        remember temp = 1
        for i in range(1, n + 1) {
            temp = temp * i
        }
        result = temp
    }

    on timeline("recursive") {
        # Recursive factorial
        result = factorial(n)
    }
} collapse observe result

confess "Factorial(" + n + ") = " + result
confess "Fastest method: " + current_timeline()
```
</details>

---

## Lesson 11: Neural Networks

### Creating Tensors

```lament
# Basic tensor
remember x = Tensor([[1, 2], [3, 4]])
remember y = Tensor([[5, 6], [7, 8]])

# Operations
remember sum = x + y
remember product = x * y
remember matrix_mul = x @ y

confess sum
```

### With Gradients

```lament
remember a = Tensor([[2, 3]], requires_grad=true)
remember b = Tensor([[4], [5]], requires_grad=true)
remember c = a @ b

# Backpropagation
c.backward()

confess "a.grad: " + a.grad
confess "b.grad: " + b.grad
```

### Building a Network

```lament
# Create network
remember model = NeuralNetwork("brain")
model.add(Dense(2, 4, "hidden"))
model.add(Dense(4, 1, "output"))

# Summary
model.summary()
```

### Training

```lament
# XOR problem
remember X = [
    Tensor([[0, 0]]),
    Tensor([[0, 1]]),
    Tensor([[1, 0]]),
    Tensor([[1, 1]])
]

remember y = [
    Tensor([[0]]),
    Tensor([[1]]),
    Tensor([[1]]),
    Tensor([[0]])
]

remember train_data = zip(X, y)

# Create optimizer and loss
remember optimizer = Adam(model.parameters(), lr=0.1)
remember loss_fn = MSELoss()

# Train
train(model, train_data, optimizer, loss_fn, epochs=100)

# Test
model.eval()
for i in range(4) {
    remember pred = model(X[i])
    confess "Input: " + X[i] + " -> Prediction: " + pred
}
```

**Exercise 11.1**: Train a network to learn the AND gate.

<details>
<summary>Solution</summary>

```lament
remember X = [
    Tensor([[0, 0]]),
    Tensor([[0, 1]]),
    Tensor([[1, 0]]),
    Tensor([[1, 1]])
]

remember y = [
    Tensor([[0]]),
    Tensor([[0]]),
    Tensor([[0]]),
    Tensor([[1]])
]

remember model = NeuralNetwork("AND_gate")
model.add(Dense(2, 4))
model.add(Dense(4, 1))

remember optimizer = Adam(model.parameters(), lr=0.1)
remember loss_fn = MSELoss()

train(model, zip(X, y), optimizer, loss_fn, epochs=100)
```
</details>

---

## Lesson 12: Metaprogramming

### Quoting Code

```lament
# Capture code as data
remember code = quote(confess "hello")

# Inspect AST
confess ast_of(code)

# Evaluate later
eval_ast(code)  # Prints "hello"
```

### Macros

```lament
# Define macro
macro unless(condition, body) {
    exhale quote(
        if not unquote(condition) {
            unquote(body)
        }
    )
}

# Use macro
unless(x == 0, {
    confess "x is not zero"
})
```

**Exercise 12.1**: Create a macro that repeats code N times.

<details>
<summary>Solution</summary>

```lament
macro repeat(n, body) {
    remember code = quote(
        for _i in range(unquote(n)) {
            unquote(body)
        }
    )
    exhale code
}

repeat(5, {
    confess "Hello!"
})
```
</details>

---

## Lesson 13: File I/O

### Writing Files

```lament
write_file("/tmp/message.txt", "Hello from Lament!")
confess "File written"
```

### Reading Files

```lament
remember content = read_file("/tmp/message.txt")
confess content
```

### Checking Existence

```lament
if file_exists("/tmp/message.txt") {
    confess "File exists"
} else {
    confess "File not found"
}
```

### Directory Operations

```lament
create_dir("/tmp/mydir")
confess "Directory created"

remember files = list_dir("/tmp/mydir")
confess "Files: " + files
```

**Exercise 13.1**: Write a program that saves and loads a shopping list.

<details>
<summary>Solution</summary>

```lament
remember shopping_list = ["milk", "eggs", "bread", "cheese"]

# Save to file
remember content = ""
for item in shopping_list {
    content = content + item + "\n"
}
write_file("/tmp/shopping.txt", content)

# Load from file
remember loaded = read_file("/tmp/shopping.txt")
confess "Shopping list:"
confess loaded
```
</details>

---

## Lesson 14: Building a Real Project

### Project: Bank Account System

Let's build a complete bank account system with all Lament features!

```lament
# bank_account.lament

# Invariants
invariant balance >= 0
invariant balance <= 1000000

# State
remember balance = 0
remember transactions = []

# Functions
sigh create_account(initial_balance) {
    ensures initial_balance >= 0
    balance = initial_balance
    remember tx = {
        "type": "create",
        "amount": initial_balance,
        "time": now()
    }
    # transactions.append(tx)  # Future feature
}

sigh deposit(amount) {
    ensures amount > 0
    remember old_balance = balance
    balance = balance + amount
    confess "Deposited " + amount + ". New balance: " + balance
}

sigh withdraw(amount) {
    ensures amount > 0
    ensures balance >= amount

    remember old_balance = balance
    balance = balance - amount
    confess "Withdrew " + amount + ". New balance: " + balance
}

sigh check_balance() {
    confess "Current balance: " + balance
    confess "Previous balance: " + balance@past
    confess "Original balance: " + balance@origin
}

sigh audit() {
    confess "=== Account Audit ==="
    confess "Current balance: " + balance
    confess "Total transactions: " + balance@age
    confess why(balance)
}

# Main program
create_account(1000)
check_balance()

deposit(500)
deposit(250)
withdraw(200)

check_balance()
audit()

# Save account state
remember account_data = "Balance: " + balance
write_file("/tmp/account.txt", account_data)
confess "Account saved"
```

Run it:
```bash
python3 lament/cli.py run bank_account.lament
```

### Project: To-Do List Manager

```lament
# todo.lament

remember todos = []
remember next_id = 1

sigh add_todo(description) {
    remember todo = {
        "id": next_id,
        "description": description,
        "completed": false
    }
    # todos.append(todo)  # Future feature
    next_id = next_id + 1
    confess "Added: " + description
}

sigh list_todos() {
    confess "=== To-Do List ==="
    for todo in todos {
        remember status = if todo["completed"] { "[X]" } else { "[ ]" }
        confess status + " " + todo["id"] + ". " + todo["description"]
    }
}

sigh complete_todo(id) {
    # Mark as complete (simplified)
    confess "Completed task " + id
}

# Usage
add_todo("Learn Lament")
add_todo("Build a project")
add_todo("Master temporal programming")
list_todos()
```

---

## Congratulations!

You've completed the Lament tutorial! You now know:

✅ Basic syntax and types
✅ Functions and control flow
✅ Collections (lists and dicts)
✅ Timeline variables
✅ Time-travel debugging
✅ Causal debugging
✅ Temporal contracts
✅ Reality branching
✅ Neural networks
✅ Metaprogramming
✅ File I/O
✅ Building real projects

---

## Next Steps

1. 📖 Read the [Language Guide](LANGUAGE_GUIDE.md) for complete reference
2. 🔬 Check the [API Reference](API_REFERENCE.md) for detailed docs
3. 💪 Try the [advanced examples](../examples/)
4. 🏗️ Learn about [Architecture](../ARCHITECTURE.md)
5. 🤝 Join the [Community](https://discord.gg/lament)
6. 🚀 Build something amazing!

---

## Practice Projects

Try building these projects to solidify your knowledge:

1. **Calculator** with history (use timeline variables)
2. **Note-taking app** with file persistence
3. **Simple game** with state tracking
4. **Expense tracker** with invariants
5. **ML model** for simple classification
6. **Web scraper** with parallel timelines
7. **Code analyzer** using metaprogramming

---

**Remember: In Lament, every variable is a timeline, every execution is negotiable, and every error is a teacher. Code with feeling.**

Happy Lamenting! 💜
