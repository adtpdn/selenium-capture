import os
import time
import json
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# List of URLs to test
urls = [
    "https://www.example.com",
    "https://www.github.com",
    # Add more URLs here
]

# List of browsers to test
browsers = ["chrome", "firefox", "edge", "safari"]

# List of device types
device_types = ["desktop", "mobile"]

# Function to set up the webdriver for a specific browser and device type
def setup_driver(browser, device_type):
    if browser == "chrome":
        options = ChromeOptions()
        if device_type == "mobile":
            options.add_argument("--window-size=375,812")  # iPhone X dimensions
        driver = webdriver.Chrome(options=options)
    elif browser == "firefox":
        options = FirefoxOptions()
        if device_type == "mobile":
            options.add_argument("--width=375")
            options.add_argument("--height=812")
        driver = webdriver.Firefox(options=options)
    elif browser == "edge":
        options = EdgeOptions()
        if device_type == "mobile":
            options.add_argument("--window-size=375,812")
        driver = webdriver.Edge(options=options)
    elif browser == "safari":
        options = SafariOptions()
        driver = webdriver.Safari(options=options)
        if device_type == "mobile":
            driver.set_window_size(375, 812)
    else:
        raise ValueError(f"Unsupported browser: {browser}")
    
    return driver

# Function to capture full page screenshot
def capture_full_page_screenshot(driver, file_name):
    total_height = driver.execute_script("return document.body.scrollHeight")
    driver.set_window_size(driver.get_window_size()['width'], total_height)
    time.sleep(2)  # Wait for the page to adjust
    driver.save_screenshot(file_name)

# Main test function
def run_tests():
    results = []
    screenshots = []
    for url in urls:
        for browser in browsers:
            for device_type in device_types:
                try:
                    driver = setup_driver(browser, device_type)
                    driver.get(url)
                    
                    # Wait for the page to load
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                    
                    # Create directory for screenshots if it doesn't exist
                    os.makedirs(f"screenshots/{browser}/{device_type}", exist_ok=True)
                    
                    # Capture full page screenshot
                    file_name = f"screenshots/{browser}/{device_type}/{url.replace('https://', '').replace('http://', '').replace('/', '_')}.png"
                    capture_full_page_screenshot(driver, file_name)
                    
                    results.append({
                        "url": url,
                        "browser": browser,
                        "device_type": device_type,
                        "status": "success",
                        "screenshot": file_name
                    })
                    screenshots.append(file_name)
                except Exception as e:
                    results.append({
                        "url": url,
                        "browser": browser,
                        "device_type": device_type,
                        "status": "failure",
                        "error": str(e)
                    })
                finally:
                    driver.quit()
    
    return results, screenshots

# Run the tests and save results
if __name__ == "__main__":
    test_results, screenshots = run_tests()
    
    # Generate a timestamp for the test run (GMT+8)
    timestamp = (datetime.utcnow() + timedelta(hours=8)).strftime("%Y%m%d_%H%M%S")
    formatted_timestamp = (datetime.utcnow() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S (GMT+8)")
    
    # Save results as JSON
    result_data = {
        "timestamp": formatted_timestamp,
        "results": test_results,
        "screenshots": screenshots
    }
    
    with open(f"results_{timestamp}.json", "w") as f:
        json.dump(result_data, f, indent=2)
    
    print(f"Test results saved to results_{timestamp}.json")

    # Print results to console
    print(f"Test run completed at: {formatted_timestamp}")
    for result in test_results:
        print(f"URL: {result['url']}")
        print(f"Browser: {result['browser']}")
        print(f"Device: {result['device_type']}")
        print(f"Status: {result['status']}")
        if result['status'] == 'failure':
            print(f"Error: {result['error']}")
        else:
            print(f"Screenshot: {result['screenshot']}")
        print("---")