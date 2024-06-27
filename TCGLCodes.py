import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def safe_click(driver, by, value):
    try:
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((by, value))
        )
        driver.execute_script("arguments[0].scrollIntoView();", element)
        driver.execute_script("arguments[0].click();", element)
    except Exception as e:
        print(f"An error occurred while attempting to click on the element: {e}")

def random_sleep(min_seconds, max_seconds):
    time.sleep(random.uniform(min_seconds, max_seconds))

# Read text from text file
with open("codes.txt", "r") as file:
    text_to_input = file.read()

text_parts = text_to_input.split("\n")
print(f"Total {len(text_parts)} codes.")

user_decision = input("Would you like to continue? (y/n): ")

if user_decision.lower() != 'y':
    print("Terminating the script.")
    exit(0)

# Get username and password from user
username = input("Enter your username: ")
password = input("Enter your password: ")

# Initialize undetected Chrome driver
options = uc.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
driver = uc.Chrome(options=options)
wait = WebDriverWait(driver, 10)

# Initialize counters
i = 0
j = 0

try:
    # Navigate to the login page
    driver.get("https://redeem.tcg.pokemon.com/en-us/")
    random_sleep(1, 2)

    # Find the username and password fields
    username_elem = wait.until(EC.presence_of_element_located((By.ID, "email")))
    password_elem = wait.until(EC.presence_of_element_located((By.ID, "password")))

    username_elem.send_keys(username)
    password_elem.send_keys(password)
    random_sleep(1, 2)

    # Find and click the login button
    safe_click(driver, By.ID, 'accept')
    random_sleep(10, 12)

    # Wait for the cookie popup's "Accept" button to appear and click
    safe_click(driver, By.XPATH, "//button[text()='Accept All']")
    random_sleep(2, 3)

    for part in text_parts:
        try:
            text_field = wait.until(EC.presence_of_element_located((By.ID, "code")))
            text_field.clear()
            text_field.send_keys(part)
            random_sleep(1, 2)

            # Submit the code
            safe_click(driver, By.CSS_SELECTOR, ".Button_blueButton__1PlZZ.VerifyModule_verifySubmitButton__3zBd-")
            random_sleep(3, 4)

            elements = driver.find_elements(By.XPATH, "//td[text()='This code has already been redeemed by this account. ']")

            if len(elements) == 0:
                # Click the Redeem button
                safe_click(driver, By.XPATH, "//button/span[text()='Redeem']")
                i += 1
                print(f"{i} codes redeemed")
                random_sleep(4, 5)
            else:
                print("This code has already been redeemed. Skipping.")
                driver.refresh()
                j += 1
                print(f"{j} codes failed")
                elements = []
                random_sleep(2, 3)
        except Exception as e:
            print(f"An error occurred during code redemption: {e}")

finally:
    driver.quit()
    print("Complete")
    print(f"{i} total codes redeemed")
    print(f"{j} total codes failed")
