# Lament Standard Library

A comprehensive standard library for the Lament programming language, providing essential utilities for common programming tasks.

## Modules

### 1. core.lament - Core Utilities

Essential functions for everyday programming.

**I/O:**
- `print(value)` - Print value to stdout
- `input(prompt)` - Read input from stdin

**Higher-Order Functions:**
- `map(fn, iterable)` - Apply function to each element
- `filter(fn, iterable)` - Filter elements by predicate
- `reduce(fn, iterable, initial)` - Reduce to single value
- `foreach(fn, iterable)` - Execute for side effects

**Type Conversion:**
- `str(value)` - Convert to string
- `int(value)` - Convert to integer
- `float(value)` - Convert to float
- `bool(value)` - Convert to boolean
- `type(value)` - Get type name

**Collections:**
- `len(collection)` - Get length
- `range(start, stop, step)` - Generate numeric sequence
- `append(list, item)` - Append to list
- `extend(list1, list2)` - Extend list
- `slice(list, start, end)` - Extract slice
- `reverse(list)` - Reverse list
- `sort(list, key_fn, reverse)` - Sort list
- `enumerate(iterable, start)` - Create indexed pairs
- `zip(list1, list2)` - Zip two lists

**Predicates:**
- `all(iterable)` - Check if all truthy
- `any(iterable)` - Check if any truthy

**Utilities:**
- `identity(x)` - Return same value
- `const(value)` - Create constant function
- `compose(f, g)` - Compose functions
- `partial(fn, arg)` - Partial application
- `join(list, separator)` - Join strings
- `repeat(value, times)` - Repeat value

### 2. collections.lament - Data Structures

Advanced collection types with rich APIs.

**List:**
```lament
remember list = List_new()
list["push"](item)
remember item = list["pop"]()
remember size = list["size"]()
```

**Dict:**
```lament
remember dict = Dict_new()
dict["set"]("key", "value")
remember value = dict["get"]("key", default)
remember keys = dict["keys"]()
```

**Set:**
```lament
remember set = Set_new()
set["add"](item)
remember has = set["contains"](item)
remember union = set1["union"](set2)
remember intersection = set1["intersection"](set2)
```

**Queue (FIFO):**
```lament
remember queue = Queue_new()
queue["enqueue"](item)
remember item = queue["dequeue"]()
```

**Stack (LIFO):**
```lament
remember stack = Stack_new()
stack["push"](item)
remember item = stack["pop"]()
```

**PriorityQueue:**
```lament
remember pq = PriorityQueue_new()
pq["insert"](priority, item)
remember item = pq["extract_min"]()
```

**Deque:**
```lament
remember deque = Deque_new()
deque["push_front"](item)
deque["push_back"](item)
remember item = deque["pop_front"]()
```

**Counter:**
```lament
remember counter = Counter_new([1, 2, 2, 3, 3, 3])
remember count = counter["count"](3)  # 3
remember common = counter["most_common"](2)
```

**DefaultDict:**
```lament
sigh list_factory() { exhale [] }
remember dd = DefaultDict_new(list_factory)
remember list = dd["get"]("key")  # Auto-creates list
```

### 3. math.lament - Mathematics

Comprehensive mathematical functions and constants.

**Constants:**
- `PI = 3.14159...`
- `E = 2.71828...`
- `TAU = 6.28318...` (2π)
- `PHI = 1.61803...` (Golden ratio)

**Basic:**
- `abs(x)` - Absolute value
- `sign(x)` - Sign of number
- `max(a, b)` - Maximum
- `min(a, b)` - Minimum
- `clamp(x, min, max)` - Clamp to range

**Power/Root:**
- `pow(base, exp)` - Power
- `sqrt(x)` - Square root
- `cbrt(x)` - Cube root

**Rounding:**
- `floor(x)` - Round down
- `ceil(x)` - Round up
- `round(x, digits)` - Round to nearest
- `trunc(x)` - Truncate

**Trigonometry:**
- `sin(x)`, `cos(x)`, `tan(x)` - Trig functions
- `asin(x)`, `acos(x)`, `atan(x)` - Inverse trig
- `atan2(y, x)` - Two-argument arctangent
- `sinh(x)`, `cosh(x)`, `tanh(x)` - Hyperbolic

**Exponential/Logarithmic:**
- `exp(x)` - e^x
- `ln(x)` - Natural log
- `log(x, base)` - Logarithm
- `log10(x)`, `log2(x)` - Common logs

**Statistics:**
- `sum(numbers)` - Sum all numbers
- `product(numbers)` - Product of all
- `mean(numbers)` / `avg(numbers)` - Average
- `median(numbers)` - Median value
- `variance(numbers)` - Variance
- `stdev(numbers)` - Standard deviation

**Number Theory:**
- `gcd(a, b)` - Greatest common divisor
- `lcm(a, b)` - Least common multiple
- `factorial(n)` - Factorial
- `is_prime(n)` - Primality test
- `fibonacci(n)` - Fibonacci number

**Conversions:**
- `degrees(rad)` - Radians to degrees
- `radians(deg)` - Degrees to radians

### 4. strings.lament - String Utilities

Text processing and manipulation.

**Basic Operations:**
- `join(strings, sep)` - Join with separator
- `split(text, delim, max)` - Split by delimiter
- `strip(text, chars)` - Remove leading/trailing
- `lstrip(text, chars)` - Remove leading
- `rstrip(text, chars)` - Remove trailing

**Search/Replace:**
- `replace(text, old, new, count)` - Replace occurrences
- `contains(text, substr)` - Check if contains
- `index_of(text, substr, start)` - Find first index
- `last_index_of(text, substr)` - Find last index
- `count_occurrences(text, substr)` - Count occurrences

**Case Operations:**
- `upper(text)` - Convert to uppercase
- `lower(text)` - Convert to lowercase
- `capitalize(text)` - Capitalize first char
- `title(text)` - Title case
- `swap_case(text)` - Swap case

**Predicates:**
- `startswith(text, prefix)` - Check prefix
- `endswith(text, suffix)` - Check suffix
- `is_alpha(text)` - All alphabetic
- `is_digit(text)` - All digits
- `is_alnum(text)` - All alphanumeric
- `is_space(text)` - All whitespace

**Formatting:**
- `format(template, values)` - Format with {0}, {1}, etc.
- `pad_left(text, width, fill)` - Pad on left
- `pad_right(text, width, fill)` - Pad on right
- `center(text, width, fill)` - Center text

**Utilities:**
- `reverse(text)` - Reverse string
- `repeat(text, times)` - Repeat string
- `truncate(text, max, suffix)` - Truncate with suffix
- `lines(text)` - Split into lines
- `words(text)` - Split into words

### 5. files.lament - File I/O

File system operations and I/O.

**Reading:**
- `read_file(path)` - Read entire file
- `read_lines(path)` - Read as lines
- `read_bytes(path)` - Read binary
- `read_json(path)` - Read and parse JSON

**Writing:**
- `write_file(path, content)` - Write file
- `write_lines(path, lines)` - Write lines
- `write_bytes(path, data)` - Write binary
- `write_json(path, data)` - Write as JSON
- `append_file(path, content)` - Append to file
- `append_lines(path, lines)` - Append lines

**File Operations:**
- `exists(path)` - Check existence
- `is_file(path)` - Check if file
- `is_dir(path)` - Check if directory
- `file_size(path)` - Get file size
- `file_modified(path)` - Get modification time
- `delete(path)` - Delete file
- `rename(old, new)` - Rename/move
- `copy(source, dest)` - Copy file

**Directory Operations:**
- `mkdir(path, recursive)` - Create directory
- `rmdir(path, recursive)` - Remove directory
- `listdir(path, full_paths)` - List contents
- `walk(path)` - Recursive walk

**Path Operations:**
- `join_path(parts...)` - Join path components
- `split_path(path)` - Split into components
- `basename(path)` - Get filename
- `dirname(path)` - Get directory
- `extname(path)` - Get extension
- `stem(path)` - Filename without extension
- `abspath(path)` - Get absolute path
- `normpath(path)` - Normalize path

**Utilities:**
- `glob(pattern, recursive)` - Find files by pattern
- `temp_file(prefix, suffix)` - Create temp file

### 6. network.lament - Networking

HTTP requests and networking utilities.

**HTTP Client:**
- `http_get(url, headers, timeout)` - GET request
- `http_post(url, data, headers, timeout)` - POST request
- `http_put(url, data, headers, timeout)` - PUT request
- `http_delete(url, headers, timeout)` - DELETE request
- `http_patch(url, data, headers, timeout)` - PATCH request
- `http_head(url, headers, timeout)` - HEAD request

**URL Operations:**
- `parse_url(url)` - Parse into components
- `build_url(components)` - Build from components
- `parse_query_string(query)` - Parse query params
- `build_query_string(params)` - Build query string
- `url_encode(text)` - URL encode
- `url_decode(text)` - URL decode

**JSON:**
- `parse_json(json_str)` - Parse JSON
- `to_json(data, pretty)` - Convert to JSON

**WebSocket:**
```lament
remember ws = WebSocket_connect("ws://example.com")
ws["send"]("Hello")
remember msg = ws["receive"](30)
ws["close"]()
```

**TCP Socket:**
```lament
remember sock = Socket_connect("localhost", 8080)
sock["send"]("GET / HTTP/1.0\r\n\r\n")
remember response = sock["receive"](4096)
sock["close"]()
```

**UDP Socket:**
```lament
remember sock = UDPSocket_create()
sock["send_to"]("Hello", "localhost", 9999)
remember result = sock["receive_from"](4096)
sock["close"]()
```

**Utilities:**
- `download(url, dest)` - Download file
- `upload(url, file, field)` - Upload file
- `is_url(text)` - Check if valid URL

### 7. crypto.lament - Cryptography

Security and cryptographic operations.

**Hashing:**
- `hash_md5(data)` - MD5 hash
- `hash_sha1(data)` - SHA-1 hash
- `hash_sha256(data)` - SHA-256 hash
- `hash_sha512(data)` - SHA-512 hash
- `hash(data, algo)` - Generic hash
- `hash_file(path, algo)` - Hash file

**HMAC:**
- `hmac(data, key, algo)` - Compute HMAC
- `hmac_sha256(data, key)` - HMAC-SHA256
- `verify_hmac(data, key, expected, algo)` - Verify HMAC

**Encryption:**
- `encrypt_aes(plain, key, mode)` - AES encryption
- `decrypt_aes(cipher, key, mode)` - AES decryption
- `encrypt(plain, key, algo, mode)` - Generic encrypt
- `decrypt(cipher, key, algo, mode)` - Generic decrypt

**Password Hashing:**
- `hash_password(password, salt)` - Hash password (PBKDF2)
- `verify_password(password, hash_info)` - Verify password

**Random Generation:**
- `random()` - Random float [0, 1)
- `random_int(min, max)` - Random integer
- `random_bytes(length)` - Random bytes
- `random_string(length, charset)` - Random string
- `random_hex(length)` - Random hex string
- `uuid()` - Generate UUID v4

**Encoding:**
- `base64_encode(data)` - Base64 encode
- `base64_decode(encoded)` - Base64 decode
- `hex_encode(data)` - Hex encode
- `hex_decode(hex)` - Hex decode
- `bytes_to_hex(data)` - Bytes to hex
- `hex_to_bytes(hex)` - Hex to bytes

**Key Derivation:**
- `pbkdf2(password, salt, iter, len, hash)` - PBKDF2 KDF
- `derive_key(password, salt, algo, params)` - Generic KDF

**Digital Signatures:**
- `sign_data(data, private_key, algo)` - Sign data
- `verify_signature(data, sig, public_key, algo)` - Verify signature

**Utilities:**
- `constant_time_compare(a, b)` - Timing-attack safe comparison
- `secure_random_token(length)` - Secure URL-safe token
- `checksum(data)` - Simple checksum

### 8. datetime.lament - Date and Time

Date, time, and timezone operations.

**Current Time:**
- `now()` - Current timestamp
- `today()` - Today's date as DateTime
- `utc_now()` - Current UTC timestamp

**DateTime Object:**
```lament
remember dt = DateTime_new(2025, 11, 13, 14, 30, 0)
remember formatted = dt["format"]("%Y-%m-%d %H:%M:%S")
remember later = dt["add_days"](7)
remember diff = dt1["diff"](dt2)
remember day = dt["weekday"]()
```

**Creation:**
- `DateTime_new(year, month, day, hour, min, sec)` - Create DateTime
- `from_timestamp(timestamp)` - From Unix timestamp

**TimeDelta:**
```lament
remember td = TimeDelta_new(3600)  # 1 hour in seconds
remember td = timedelta(1, 2, 30, 0)  # 1 day, 2 hours, 30 minutes
confess td["to_string"]()  # "1 days, 2:30:00"
```

**Parsing/Formatting:**
- `parse_date(date_str, format)` - Parse date string
- `format_date(dt, format)` - Format as string

Format specifiers:
- `%Y` - 4-digit year
- `%m` - 2-digit month
- `%d` - 2-digit day
- `%H` - 2-digit hour
- `%M` - 2-digit minute
- `%S` - 2-digit second
- `%B` - Full month name
- `%b` - Short month name
- `%A` - Full day name
- `%a` - Short day name

**Arithmetic:**
- `add_days(dt, days)` - Add days
- `add_hours(dt, hours)` - Add hours
- `add_minutes(dt, minutes)` - Add minutes
- `add_seconds(dt, seconds)` - Add seconds
- `subtract_dates(dt1, dt2)` - Get difference

**Utilities:**
- `is_leap_year(year)` - Check leap year
- `days_in_month(year, month)` - Days in month
- `weekday(dt)` - Day of week (0-6)
- `weekday_name(dt, short)` - Name of day
- `month_name(month, short)` - Name of month
- `is_weekend(dt)` - Check if weekend
- `is_weekday(dt)` - Check if weekday

**Timezone:**
```lament
remember tz = Timezone_new("EST", -5)
remember converted = tz["convert"](dt)
remember utc = utc_timezone()
```

**Constants:**
- `MONTH_NAMES` - Full month names
- `MONTH_NAMES_SHORT` - Short month names
- `DAY_NAMES` - Full day names
- `DAY_NAMES_SHORT` - Short day names

## Usage Examples

### Example 1: File Processing
```lament
import { read_lines, write_lines } from "files.lament"
import { map, filter } from "core.lament"
import { strip, upper } from "strings.lament"

# Read file, process lines, write back
remember lines = read_lines("input.txt")

sigh process_line(line) {
    exhale upper(strip(line))
}

remember processed = map(process_line, lines)
write_lines("output.txt", processed)
```

### Example 2: HTTP API Client
```lament
import { http_get, http_post, parse_json, to_json } from "network.lament"

# GET request
remember response = http_get("https://api.example.com/users")
remember users = parse_json(response["body"])

# POST request
remember new_user = {"name": "Alice", "email": "alice@example.com"}
remember result = http_post(
    "https://api.example.com/users",
    new_user,
    void,
    30
)
```

### Example 3: Data Analysis
```lament
import { mean, median, stdev, sum } from "math.lament"
import { Counter_new } from "collections.lament"

remember data = [23, 45, 12, 67, 34, 23, 56, 23, 89, 12]

confess "Mean: ${mean(data)}"
confess "Median: ${median(data)}"
confess "Std Dev: ${stdev(data)}"
confess "Sum: ${sum(data)}"

remember counter = Counter_new(data)
remember common = counter["most_common"](3)
confess "Most common: ${common}"
```

### Example 4: Security
```lament
import { hash_password, verify_password, random_string } from "crypto.lament"
import { base64_encode } from "crypto.lament"

# Hash password
remember salt = random_string(32)
remember hash_info = hash_password("my_password", salt)

# Verify password
remember is_valid = verify_password("my_password", hash_info)

# Generate secure token
remember token = secure_random_token(32)
```

### Example 5: Date Handling
```lament
import { today, add_days, format_date, parse_date } from "datetime.lament"

# Get today
remember dt = today()
confess "Today: ${dt["to_string"]()}"

# Add 7 days
remember next_week = add_days(dt, 7)
confess "Next week: ${next_week["to_string"]()}"

# Format date
remember formatted = format_date(dt, "%B %d, %Y")
confess formatted

# Parse date
remember parsed = parse_date("2025-12-25", "%Y-%m-%d")
confess "Christmas: ${parsed["to_string"]()}"
```

## Import Syntax

All modules support selective imports:

```lament
# Import specific functions
import { map, filter, reduce } from "core.lament"

# Import from nested modules
import { http_get, parse_json } from "network.lament"
import { read_file, write_file } from "files.lament"

# Use imported functions
remember numbers = [1, 2, 3, 4, 5]
sigh square(x) { exhale x * x }
remember squared = map(square, numbers)
```

## Module Dependencies

The standard library modules have minimal dependencies:
- **core**: No dependencies (foundational)
- **collections**: Depends on core
- **math**: No dependencies
- **strings**: No dependencies
- **files**: Depends on strings, core
- **network**: Depends on strings
- **crypto**: Depends on strings
- **datetime**: No dependencies

## Performance Notes

- Functions are implemented in pure Lament code
- Some operations may require built-in runtime support
- Cryptographic operations should use native implementations when available
- File I/O operations use buffered reads/writes for efficiency

## Contributing

To add new functions to the standard library:
1. Add implementation to appropriate module
2. Export in the `expose { }` block
3. Document in this README
4. Add usage examples

## License

Part of the Lament programming language standard library.
