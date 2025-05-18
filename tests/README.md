# Tests for Web3 Article Summarizer

This directory contains tests for the Web3 Article Summarizer API.

## Running Tests

To run the tests, execute the following command from the project root:

```bash
pytest
```

For more detailed output, you can use:

```bash
pytest -v
```

## Test Coverage

The tests cover:

1. API endpoint functionality
2. Web3 signature verification
3. Article scraping
4. Article summarization
5. Database operations

## Adding New Tests

When adding new tests, follow these conventions:
- Place test files in this directory
- Name test files with `test_` prefix
- Name test functions with `test_` prefix
- Use appropriate fixtures for database operations
