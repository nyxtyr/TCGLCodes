import time
import random
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def safe_click(driver, by, value):
    try:
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((by, value))
        )
        driver.execute_script("arguments[0].scrollIntoView();", element)
        driver.execute_script("arguments[0].click();", element)
    except TimeoutException:
        print(f"Timeout while waiting for element to be clickable: {by}={value}")
    except Exception as e:
        print(f"An error occurred while attempting to click on the element {by}={value}: {e}")

def random_sleep(min_seconds, max_seconds):
    time.sleep(random.uniform(min_seconds, max_seconds))

def move_code_to_used(code):
    with open("codes-new.txt", "r") as f:
        lines = f.readlines()

    with open("codes-new.txt", "w") as f:
        for line in lines:
            if line.strip() != code:
                f.write(line)

    with open("codes-used.txt", "a") as f:
        f.write(code + "\n")

def move_code_to_bad(code):
    with open("codes-new.txt", "r") as f:
        lines = f.readlines()

    with open("codes-new.txt", "w") as f:
        for line in lines:
            if line.strip() != code:
                f.write(line)

    with open("codes-bad.txt", "a") as f:
        f.write(code + "\n")

def main(file_path):
    with open(file_path, 'r') as file:
        text_to_input = file.read()

    text_parts = text_to_input.split('\n')
    print(f"Total {len(text_parts)} codes.")

    options = webdriver.ChromeOptions()
    options.debugger_address = "localhost:9222"
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    try:
        driver.get("https://redeem.tcg.pokemon.com/en-us/")
        random_sleep(1, 2)

        for part in text_parts:
            try:
                text_field = wait.until(EC.presence_of_element_located((By.ID, "code")))
                text_field.clear()
                text_field.send_keys(part)
                random_sleep(1, 2)

                safe_click(driver, By.CSS_SELECTOR, ".Button_blueButton__1PlZZ.VerifyModule_verifySubmitButton__3zBd-")
                random_sleep(3, 4)

                # Check if the code has already been redeemed
                elements = driver.find_elements(By.XPATH, "//td[contains(@class, 'RedeemModule_tdLocalizedName__1VWAC')]")

                if any("That code has already been redeemed." in elem.text for elem in elements):
                    print(f"This code '{part}' has already been redeemed. Moving to bad codes.")
                    move_code_to_bad(part.strip())  # Move the bad code to codes-bad.txt
                    
                    # Click the delete button for the bad code
                    delete_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".RedeemModule_tdDelete__2-YLO")))
                    safe_click(driver, By.CSS_SELECTOR, ".RedeemModule_tdDelete__2-YLO")
                    random_sleep(2, 3)
                else:
                    safe_click(driver, By.XPATH, "//button/span[text()='Redeem']")
                    print(f"Code '{part}' redeemed")
                    move_code_to_used(part.strip())  # Move the used code to codes-used.txt
                    random_sleep(4, 5)

            except Exception as e:
                print(f"An error occurred during code redemption for '{part}': {e}")

    finally:
        driver.quit()
        print('Code redemption process is complete.')

if __name__ == '__main__':
    file_path = "codes-new.txt"  # Assuming codes file path is fixed as 'codes-new.txt'
    main(file_path)
