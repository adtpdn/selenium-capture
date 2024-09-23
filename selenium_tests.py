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
    "https://adengroup.com",
    "https://nx-park.com",
    "https://adenenergies.com"
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
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Load existing results
    if os.path.exists('test_results.json'):
        with open('test_results.json', 'r') as f:
            all_results = json.load(f)
    else:
        all_results = []
    
    # Add new results
    all_results.insert(0, {"timestamp": current_date, "results": results})
    
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
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        h1, h2 {
            text-align: center;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        .screenshot {
            width: 200px;
            height: auto;
            cursor: pointer;
        }
        .modal {
            display: none;
            position: fixed;
            z-index: 1;
            padding-top: 50px;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            overflow: auto;
            background-color: rgba(0,0,0,0.9);
        }
        .modal-content {
            margin: auto;
            display: block;
            max-width: 90%;
            max-height: 90%;
        }
        .close {
            position: absolute;
            top: 15px;
            right: 35px;
            color: #f1f1f1;
            font-size: 40px;
            font-weight: bold;
            transition: 0.3s;
        }
        .close:hover,
        .close:focus {
            color: #bbb;
            text-decoration: none;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <h1>Selenium Test Results</h1>
    <div id="testResults"></div>

    <div id="myModal" class="modal">
        <span class="close">&times;</span>
        <img class="modal-content" id="modalImg">
    </div>

    <script>
        const testResults = {json_data};

        function createTable(results) {
            const urls = [...new Set(results.map(r => r.url))];
            const browserDevices = ['chrome desktop', 'chrome mobile', 'firefox desktop', 'firefox mobile', 'edge desktop', 'edge mobile'];
            
            let tableHtml = '<table><tr><th>URL</th>';
            browserDevices.forEach(bd => {
                tableHtml += `<th>${bd}</th>`;
            });
            tableHtml += '</tr>';

            urls.forEach(url => {
                tableHtml += `<tr><td>${url}</td>`;
                browserDevices.forEach(bd => {
                    const [browser, device] = bd.split(' ');
                    const result = results.find(r => r.url === url && r.browser === browser && r.device === device);
                    if (result) {
                        tableHtml += `<td><img src="${result.screenshot}" alt="Screenshot" class="screenshot" onclick="openModal(this.src)"></td>`;
                    } else {
                        tableHtml += '<td>N/A</td>';
                    }
                });
                tableHtml += '</tr>';
            });

            tableHtml += '</table>';
            return tableHtml;
        }

        function renderResults() {
            const testResultsDiv = document.getElementById('testResults');
            let resultsHtml = '';

            testResults.forEach((testRun, index) => {
                resultsHtml += `
                    <h2>${testRun.timestamp}${index === 0 ? ' (Latest)' : ''}</h2>
                    ${createTable(testRun.results)}
                `;
            });
            testResultsDiv.innerHTML = resultsHtml;
        }

        // Modal functionality
        const modal = document.getElementById("myModal");
        const modalImg = document.getElementById("modalImg");
        const closeBtn = document.getElementsByClassName("close")[0];
        let scale = 1;
        let panning = false;
        let pointX = 0;
        let pointY = 0;
        let start = { x: 0, y: 0 };

        function openModal(imgSrc) {
            modal.style.display = "block";
            modalImg.src = imgSrc;
            scale = 1;
            modalImg.style.transform = `scale(${scale})`;
        }

        closeBtn.onclick = function() {
            modal.style.display = "none";
        }

        modalImg.onmousedown = function(e) {
            e.preventDefault();
            start = { x: e.clientX - pointX, y: e.clientY - pointY };
            panning = true;
        }

        modalImg.onmouseup = function(e) {
            panning = false;
        }

        modalImg.onmousemove = function(e) {
            e.preventDefault();
            if (!panning) {
                return;
            }
            pointX = (e.clientX - start.x);
            pointY = (e.clientY - start.y);
            modalImg.style.transform = `translate(${pointX}px, ${pointY}px) scale(${scale})`;
        }

        modalImg.onwheel = function(e) {
            e.preventDefault();
            let xs = (e.clientX - pointX) / scale;
            let ys = (e.clientY - pointY) / scale;
            let delta = (e.wheelDelta ? e.wheelDelta : -e.deltaY);
            (delta > 0) ? (scale *= 1.2) : (scale /= 1.2);
            pointX = e.clientX - xs * scale;
            pointY = e.clientY - ys * scale;

            modalImg.style.transform = `translate(${pointX}px, ${pointY}px) scale(${scale})`;
        }

        // Touch events for mobile pinch zoom
        let evCache = [];
        let prevDiff = -1;

        modalImg.ontouchstart = function(e) {
            e.preventDefault();
            for (let i = 0; i < e.touches.length; i++) {
                evCache.push(e.touches[i]);
            }
        }

        modalImg.ontouchmove = function(e) {
            e.preventDefault();
            if (e.touches.length === 2) {
                let curDiff = Math.abs(e.touches[0].clientX - e.touches[1].clientX);

                if (prevDiff > 0) {
                    if (curDiff > prevDiff) {
                        scale *= 1.02;
                    }
                    if (curDiff < prevDiff) {
                        scale /= 1.02;
                    }
                    modalImg.style.transform = `translate(${pointX}px, ${pointY}px) scale(${scale})`;
                }

                prevDiff = curDiff;
            }
        }

        modalImg.ontouchend = function(e) {
            evCache = [];
            prevDiff = -1;
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