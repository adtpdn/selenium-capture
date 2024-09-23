import os
import json
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

def generate_html_report(results):
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Load existing results
    if os.path.exists('test_results.json'):
        with open('test_results.json', 'r') as f:
            all_results = json.load(f)
    else:
        all_results = []
    
    # Add new results
    all_results.insert(0, {"date": current_date, "results": results})
    
    # Save all results
    with open('test_results.json', 'w') as f:
        json.dump(all_results, f)
    
    # Generate HTML
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Selenium Test Results</title>
    <style>
        /* ... (keep the same CSS as before) ... */
    </style>
</head>
<body>
    <h1>Selenium Test Results</h1>
    <div id="allResults"></div>

    <div id="myModal" class="modal">
        <span class="close">&times;</span>
        <img class="modal-content" id="modalImg">
        <div id="zoomControls">
            <button id="zoomIn">+</button>
            <button id="zoomOut">-</button>
        </div>
    </div>

    <script>
        const testResults = {json_data};

        function createTable(results) {
            // ... (keep the same createTable function as before) ...
        }

        function renderResults() {
            const allResultsDiv = document.getElementById('allResults');
            let allResultsHtml = '';

            testResults.forEach((testRun, index) => {
                allResultsHtml += `
                    <button class="accordion ${index === 0 ? 'active' : ''}">${testRun.date}${index === 0 ? ' (Latest)' : ''}</button>
                    <div class="panel" style="display: ${index === 0 ? 'block' : 'none'}">
                        ${createTable(testRun.results)}
                    </div>
                `;
            });
            allResultsDiv.innerHTML = allResultsHtml;

            // Set up accordion functionality
            const acc = document.getElementsByClassName("accordion");
            for (let i = 0; i < acc.length; i++) {
                acc[i].addEventListener("click", function() {
                    this.classList.toggle("active");
                    const panel = this.nextElementSibling;
                    if (panel.style.display === "block") {
                        panel.style.display = "none";
                    } else {
                        panel.style.display = "block";
                    }
                });
            }
        }

        // Modal functionality
        const modal = document.getElementById("myModal");
        const modalImg = document.getElementById("modalImg");
        const closeBtn = document.getElementsByClassName("close")[0];
        const zoomInBtn = document.getElementById("zoomIn");
        const zoomOutBtn = document.getElementById("zoomOut");
        let zoomLevel = 1;

        function openModal(imgSrc) {
            modal.style.display = "block";
            modalImg.src = imgSrc;
            zoomLevel = 1;
            modalImg.style.transform = `scale(${zoomLevel})`;
        }

        closeBtn.onclick = function() {
            modal.style.display = "none";
        }

        zoomInBtn.onclick = function() {
            zoomLevel += 0.1;
            modalImg.style.transform = `scale(${zoomLevel})`;
        }

        zoomOutBtn.onclick = function() {
            zoomLevel = Math.max(0.1, zoomLevel - 0.1);
            modalImg.style.transform = `scale(${zoomLevel})`;
        }

        // Initial render
        renderResults();
    </script>
</body>
</html>
    """
    
    # Replace {json_data} with the actual JSON data
    html = html.replace('{json_data}', json.dumps(all_results))
    
    # Write HTML to file
    with open('index.html', 'w') as f:
        f.write(html)

if __name__ == "__main__":
    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")
    
    results = run_tests()
    generate_html_report(results)
    
    print("Tests completed. Check index.html for results.")