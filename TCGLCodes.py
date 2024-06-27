import sys
import time
import random
import undetected_chromedriver as uc
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QFileDialog, QVBoxLayout, QMessageBox
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pygetwindow as gw

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

class RedeemApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Code Redemption Tool')

        layout = QVBoxLayout()

        self.username_label = QLabel('Username:')
        self.username_input = QLineEdit(self)
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)

        self.password_label = QLabel('Password:')
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        self.file_label = QLabel('Select Codes File:')
        self.file_button = QPushButton('Browse', self)
        self.file_button.clicked.connect(self.showFileDialog)
        layout.addWidget(self.file_label)
        layout.addWidget(self.file_button)

        self.start_button = QPushButton('Start', self)
        self.start_button.clicked.connect(self.start_redemption)
        layout.addWidget(self.start_button)

        self.setLayout(layout)

    def showFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Codes File", "", "Text Files (*.txt);;All Files (*)", options=options)
        if fileName:
            self.file_label.setText(fileName)

    def start_redemption(self):
        username = self.username_input.text()
        password = self.password_input.text()
        file_path = self.file_label.text()

        if not username or not password or not file_path:
            QMessageBox.warning(self, 'Input Error', 'Please provide all inputs.')
            return

        with open(file_path, 'r') as file:
            text_to_input = file.read()
        
        text_parts = text_to_input.split('\n')
        print(f"Total {len(text_parts)} codes.")

        options = uc.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        driver = uc.Chrome(options=options)
        wait = WebDriverWait(driver, 10)

        try:
            driver.get("https://redeem.tcg.pokemon.com/en-us/")
            random_sleep(1, 2)

            username_elem = wait.until(EC.presence_of_element_located((By.ID, "email")))
            password_elem = wait.until(EC.presence_of_element_located((By.ID, "password")))

            username_elem.send_keys(username)
            password_elem.send_keys(password)
            random_sleep(1, 2)

            safe_click(driver, By.ID, 'accept')
            random_sleep(10, 12)

            safe_click(driver, By.XPATH, "//button[text()='Accept All']")
            random_sleep(2, 3)

            for part in text_parts:
                try:
                    text_field = wait.until(EC.presence_of_element_located((By.ID, "code")))
                    text_field.clear()
                    text_field.send_keys(part)
                    random_sleep(1, 2)

                    safe_click(driver, By.CSS_SELECTOR, ".Button_blueButton__1PlZZ.VerifyModule_verifySubmitButton__3zBd-")
                    random_sleep(3, 4)

                    elements = driver.find_elements(By.XPATH, "//td[text()='This code has already been redeemed by this account. ']")

                    if len(elements) == 0:
                        safe_click(driver, By.XPATH, "//button/span[text()='Redeem']")
                        print("Code redeemed")
                        random_sleep(4, 5)
                    else:
                        print("This code has already been redeemed. Skipping.")
                        driver.refresh()
                        random_sleep(2, 3)
                except Exception as e:
                    print(f"An error occurred during code redemption: {e}")

        finally:
            driver.quit()
            QMessageBox.information(self, 'Redemption Complete', 'Code redemption process is complete.')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = RedeemApp()
    ex.show()
    sys.exit(app.exec_())
