import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime

# List of URLs to test
urls = [
    "https://example.com",
    "https://example.org",
    # Add more URLs as needed
]

# Browser configurations
browsers = [
    {"name": "chrome", "options": ChromeOptions()},
    {"name": "firefox", "options": FirefoxOptions()},
    {"name": "edge", "options": EdgeOptions()}
]

# Device configurations
devices = [
    {"name": "desktop", "width": 1920, "height": 1080},
    {"name": "mobile", "width": 375, "height": 812}
]

def setup_driver(browser, device):
    if browser["name"] == "chrome":
        options = webdriver.ChromeOptions()
    elif browser["name"] == "firefox":
        options = webdriver.FirefoxOptions()
    elif browser["name"] == "edge":
        options = webdriver.EdgeOptions()
    
    options.add_argument(f"--window-size={device['width']},{device['height']}")
    options.add_argument("--headless")
    
    if browser["name"] == "chrome":
        return webdriver.Chrome(options=options)
    elif browser["name"] == "firefox":
        return webdriver.Firefox(options=options)
    elif browser["name"] == "edge":
        return webdriver.Edge(options=options)

def capture_full_page_screenshot(driver, url, browser, device):
    driver.get(url)
    
    # Wait for the page to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    
    # Scroll to capture full page
    total_height = driver.execute_script("return document.body.scrollHeight")
    viewport_height = driver.execute_script("return window.innerHeight")
    
    for i in range(0, total_height, viewport_height):
        driver.execute_script(f"window.scrollTo(0, {i})")
        time.sleep(0.5)
    
    # Scroll back to top
    driver.execute_script("window.scrollTo(0, 0)")
    
    # Take screenshot
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshots/{url.replace('https://', '').replace('/', '_')}_{browser['name']}_{device['name']}_{timestamp}.png"
    driver.save_screenshot(filename)
    return filename

def run_tests():
    results = []
    
    for url in urls:
        for browser in browsers:
            for device in devices:
                driver = setup_driver(browser, device)
                try:
                    screenshot = capture_full_page_screenshot(driver, url, browser, device)
                    results.append({
                        "url": url,
                        "browser": browser["name"],
                        "device": device["name"],
                        "screenshot": screenshot,
                        "status": "Pass"
                    })
                except Exception as e:
                    results.append({
                        "url": url,
                        "browser": browser["name"],
                        "device": device["name"],
                        "screenshot": None,
                        "status": f"Fail: {str(e)}"
                    })
                finally:
                    driver.quit()
    
    return results

if __name__ == "__main__":
    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")
    
    results = run_tests()
    
    # Generate report
    with open("report.md", "w") as f:
        f.write("# Test Report\n\n")
        for result in results:
            f.write(f"## {result['url']} - {result['browser']} - {result['device']}\n\n")
            f.write(f"Status: {result['status']}\n\n")
            if result['screenshot']:
                f.write(f"![Screenshot]({result['screenshot']})\n\n")
    
    print("Tests completed. Check report.md for results.")