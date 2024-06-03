import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from webdriver_manager.chrome import ChromeDriverManager

_LOGGER = logging.getLogger(__name__)
CHROME_OPTIONS = webdriver.chrome.options.Options()
CHROME_OPTIONS.add_argument("--headless")
TIMEOUT = 10

def login(api, user, password):
        _LOGGER.info("Logging in")

        if api.driver is None:
          api.driver =webdriver.Chrome(ChromeDriverManager().install(), options=CHROME_OPTIONS)

        # Navigate to the login page
        api.driver.get(f"https://{LCR_DOMAIN}")

        _LOGGER.info("Entering username")

        # Enter the username
        login_input = WebDriverWait(api.driver, TIMEOUT).until(
                        ec.presence_of_element_located(
                            (By.XPATH, "//input[@autocomplete='username']") # Have to use another field, they keep changing the ID
                            )
                        )
        login_input.send_keys(user)
        login_input.submit()

        _LOGGER.info("Entering password")

        # Enter password
        password_input = WebDriverWait(api.driver, TIMEOUT).until(
                ec.presence_of_element_located(
                    (By.CSS_SELECTOR, "input.password-with-toggle")
                    )
                )
        password_input.send_keys(password)
        password_input.submit()

        # Wait until the page is loaded
        WebDriverWait(api.driver, TIMEOUT).until(
                ec.presence_of_element_located(
                    (By.CSS_SELECTOR, "platform-header.PFshowHeader")
                    )
                )
        
        time.sleep(5) # Unable to find a better item above to wait on, but the above still needs some of the page to load.

        _LOGGER.info("Successfully logged in, getting cookies")

        # Get authState parameter.  Copy all cookies from the session rather than looking for a specific one.
        cookies = api.driver.get_cookies()
        for cookie in cookies:
            api.session.cookies.set(cookie['name'], cookie['value'])

        api.driver.close()
        api.driver.quit()
