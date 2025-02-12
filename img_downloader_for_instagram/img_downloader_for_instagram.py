import time
import requests
import logging
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Configure logging for detailed output.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# URL for the public Instagram account.
INSTAGRAM_URL = "https://www.instagram.com/grapeot/"

def setup_driver() -> webdriver.Chrome:
    """
    Set up the Selenium Chrome driver with options.
    Ensure that you have downloaded the correct version of ChromeDriver and it is in your PATH.
    """
    chrome_options = Options()
    # Run headless to avoid opening a browser window.
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    # Optionally reduce Chrome logging:
    chrome_options.add_argument("--log-level=3")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def scroll_until_no_new_images(driver: webdriver.Chrome, pause_time: float = 2.0, max_attempts: int = 5) -> None:
    """
    Scrolls down the Instagram page repeatedly until no new images are loaded after several attempts.
    
    Args:
        driver: The Selenium WebDriver instance.
        pause_time: Time (in seconds) to wait after each scroll.
        max_attempts: Number of consecutive scrolls without new images before stopping.
    """
    attempts = 0
    prev_count = 0
    while attempts < max_attempts:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_time)
        image_elements = driver.find_elements(By.TAG_NAME, "img")
        current_count = len(image_elements)
        logging.info(f"Found {current_count} images so far.")
        if current_count == prev_count:
            attempts += 1
            logging.info(f"No new images loaded; attempt {attempts} of {max_attempts}.")
        else:
            attempts = 0  # Reset counter if new images are loaded.
            prev_count = current_count
    logging.info("No new images loaded after several attempts; scrolling complete.")

def extract_image_urls(driver: webdriver.Chrome) -> list:
    """
    Extracts the URLs of images from the loaded Instagram page.
    
    Returns:
        A list of unique image URLs.
    """
    image_elements = driver.find_elements(By.TAG_NAME, "img")
    image_urls = set()
    for img in image_elements:
        src = img.get_attribute("src")
        if src:
            image_urls.add(src)
    return list(image_urls)

def download_image(url: str, folder: Path, file_name: str) -> None:
    """
    Downloads a single image from the given URL and saves it to the specified folder with the provided file name.
    
    Args:
        url: The URL of the image.
        folder: The folder path where the image will be saved.
        file_name: The name to save the image as.
    """
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/90.0.4430.93 Safari/537.36"
            )
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        image_path = folder / file_name
        with open(image_path, "wb") as f:
            f.write(response.content)
        logging.info(f"Downloaded image: {file_name}")
    except Exception as e:
        logging.error(f"Failed to download {url}: {e}")

def main() -> None:
    # Set up the output directory.
    output_folder = Path(__file__).parent / "img"
    output_folder.mkdir(parents=True, exist_ok=True)
    logging.info(f"Images will be saved to: {output_folder.resolve()}")

    # Set up Selenium and load the Instagram page.
    driver = setup_driver()
    logging.info(f"Navigating to {INSTAGRAM_URL}")
    driver.get(INSTAGRAM_URL)
    time.sleep(5)  # Allow time for the page to initially load.

    # Scroll down until no new images are loaded.
    logging.info("Scrolling through the page to load images...")
    scroll_until_no_new_images(driver, pause_time=2)

    # Extract image URLs.
    logging.info("Extracting image URLs...")
    image_urls = extract_image_urls(driver)
    logging.info(f"Found {len(image_urls)} unique images.")

    driver.quit()

    # Download each image.
    for idx, url in enumerate(image_urls, start=1):
        # Attempt to determine the file extension from the URL.
        file_extension = url.split("?")[0].split(".")[-1]
        file_name = f"img_{idx:03d}.{file_extension}"
        download_image(url, output_folder, file_name)
        time.sleep(1)  # Brief delay between downloads.

if __name__ == "__main__":
    main()



