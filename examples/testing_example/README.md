# Lament Testing Framework Example

This directory contains a complete example of using Lament's testing framework.

## Structure

- `test_basic.lament` - Basic assertion tests
- `test_math.lament` - Mathematical operation tests
- `test_temporal.lament` - Temporal feature tests
- `test_fixtures.lament` - Test fixtures and setup/teardown
- `test_mocks.lament` - Mock object testing
- `test_benchmarks.lament` - Performance benchmarks
- `calculator.lament` - Example module to test

## Running Tests

### Run all tests:
```bash
lament-test examples/testing_example/
```

### Run specific test file:
```bash
lament-test examples/testing_example/test_basic.lament
```

### Run with coverage:
```bash
lament-test --coverage examples/testing_example/
```

### Run in parallel:
```bash
lament-test --parallel 4 examples/testing_example/
```

### Generate reports:
```bash
lament-test --xml report.xml --json report.json examples/testing_example/
```

### Filter tests:
```bash
lament-test --filter "test_add*" examples/testing_example/
```

## Coverage

### Generate coverage report:
```bash
lament-coverage examples/testing_example/calculator.lament
```

### Generate HTML coverage:
```bash
lament-coverage --html coverage_report examples/testing_example/calculator.lament
```

### Enforce minimum coverage:
```bash
lament-coverage --min 80 examples/testing_example/calculator.lament
```

## Documentation

### Generate test documentation:
```bash
lament-doc --auto examples/testing_example/
```

### Serve documentation:
```bash
lament-doc --auto --serve --port 8000 examples/testing_example/
```

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
