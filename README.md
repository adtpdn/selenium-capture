# Selenium URL Testing with GitHub Actions

This repository contains a Selenium test suite that checks multiple URLs across different browsers and device types. The tests are run automatically using GitHub Actions, and the results are published to GitHub Pages.

## Test Results

You can view the latest test results and screenshots on our [GitHub Pages site](https://yourusername.github.io/your-repo-name/).

The page includes:
- A table of historical test results
- A gallery of screenshots that can be clicked to view full-size

## Running Tests Locally

To run the tests locally:

1. Clone this repository
2. Install the required dependencies
3. Install the necessary browser drivers (Chrome, Firefox, Edge, Safari)
4. Run the tests

## Modifying the Test Suite

To modify the URLs being tested, edit the `urls` list in `tests/test_urls.py`.

## GitHub Actions Workflow

The tests are automatically run on push to the `main` branch, on pull requests to the `main` branch, and daily at midnight UTC. You can modify this schedule by editing the `.github/workflows/selenium_test.yml` file.