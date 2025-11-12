#!/usr/bin/env python3

import re
import json
import logging
import requests
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from webdriver_manager.chrome import ChromeDriverManager

_LOGGER = logging.getLogger(__name__)
HOST = "churchofjesuschrist.org"
BETA_HOST = f"beta.{HOST}"
LCR_DOMAIN = f"lcr.{HOST}"
CHROME_OPTIONS = webdriver.chrome.options.Options()
CHROME_OPTIONS.add_argument("--headless")
TIMEOUT = 10

if _LOGGER.getEffectiveLevel() <= logging.DEBUG:
    import http.client as http_client
    http_client.HTTPConnection.debuglevel = 1


class InvalidCredentialsError(Exception):
    pass


class API():
    def __init__(
            self, username, password, unit_number, beta=False,
            driver = webdriver.Chrome(ChromeDriverManager().install(), options=CHROME_OPTIONS)):
        driver
        self.unit_number = unit_number
        self.session = requests.Session()
        self.driver = driver
        self.beta = beta
        self.host = BETA_HOST if beta else HOST

        self._login(username, password)

    def _login(self, user, password):
        _LOGGER.info("Logging in")

        # Navigate to the login page
        self.driver.get(f"https://{LCR_DOMAIN}")

        _LOGGER.info("Entering username")

        # Enter the username
        login_input = WebDriverWait(self.driver, TIMEOUT).until(
                        ec.presence_of_element_located(
                            (By.XPATH, "//input[@autocomplete='username']") # Have to use another field, they keep changing the ID
                            )
                        )
        login_input.send_keys(user)

        # Find the "Next" button and click it
        next_button = self.driver.find_element(By.ID, "button-primary")
        next_button.click()

        _LOGGER.info("Entering password")

         # Enter password
        password_input = WebDriverWait(self.driver, TIMEOUT).until(
                ec.presence_of_element_located(
                        (By.CSS_SELECTOR, "input#password-input")  # or input.eden-form-part-input__control
                    )
                )
        password_input.send_keys(password)
        
        # Find the "Verify" button and click it
        verify_password_button = self.driver.find_element(By.ID, "button-primary")
        verify_password_button.click()

        # Wait until the page is loaded
        WebDriverWait(self.driver, TIMEOUT).until(
                ec.presence_of_element_located(
                    (By.CSS_SELECTOR, "platform-header.PFshowHeader")
                    )
                )
        
        time.sleep(5) # Unable to find a better item above to wait on, but the above still needs some of the page to load.

        _LOGGER.info("Successfully logged in, getting cookies")

        # Get authState parameter.  Copy all cookies from the session rather than looking for a specific one.
        cookies = self.driver.get_cookies()
        for cookie in cookies:
            self.session.cookies.set(cookie['name'], cookie['value'])

        self.driver.close()
        self.driver.quit()

    def _make_request(self, request):
        if self.beta:
            request['cookies'] = {'clerk-resources-beta-terms': '4.1',
                                  'clerk-resources-beta-eula': '4.2'}

        response = self.session.get(**request)
        response.raise_for_status()  # break on any non 200 status
        return response

    def birthday_list(self, month, months=1):
        _LOGGER.info("Getting birthday list")
        request = {
                'url': 'https://{}/api/report/birthday-list'.format(
                    LCR_DOMAIN
                    ),
                'params': {
                    'lang': 'eng',
                    'month': month,
                    'months': months
                    }
                }

        result = self._make_request(request)
        return result.json()

    def members_moved_in(self, months):
        _LOGGER.info("Getting members moved in")
        request = {'url': 'https://{}/api/report/members-moved-in/unit/{}/{}'.format(LCR_DOMAIN,
                                                                                                  self.unit_number,
                                                                                                  months),
                   'params': {'lang': 'eng'}}

        result = self._make_request(request)
        return result.json()


    def members_moved_out(self, months):
        _LOGGER.info("Getting members moved out")
        request = {'url': 'https://{}/api/report/members-moved-out/unit/{}/{}'.format(LCR_DOMAIN,
                                                                                                   self.unit_number,
                                                                                                   months),
                   'params': {'lang': 'eng'}}

        result = self._make_request(request)
        return result.json()


    def member_list(self):
        _LOGGER.info("Getting member list")
        request = {'url': 'https://{}/api/umlu/report/member-list'.format(LCR_DOMAIN),
                   'params': {'lang': 'eng',
                              'unitNumber': self.unit_number}}

        result = self._make_request(request)
        return result.json()


    def individual_photo(self, member_id):
        """
        member_id is not the same as Mrn
        """
        _LOGGER.info("Getting photo for {}".format(member_id))
        request = {'url': 'https://{}/individual-photo/{}'.format(LCR_DOMAIN, member_id),
                   'params': {'lang': 'eng',
                              'status': 'APPROVED'}}

        result = self._make_request(request)
        scdn_url = result.json()['tokenUrl']
        return self._make_request({'url': scdn_url}).content


    def callings(self):
        _LOGGER.info("Getting callings for all organizations")
        request = {'url': 'https://{}/api/orgs/sub-orgs-with-callings'.format(LCR_DOMAIN),
                   'params': {'lang': 'eng'}}

        result = self._make_request(request)
        return result.json()


    def members_with_callings_list(self):
        _LOGGER.info("Getting callings for all organizations")
        request = {'url': 'https://{}/api/report/members-with-callings'.format(LCR_DOMAIN),
                   'params': {'lang': 'eng'}}

        result = self._make_request(request)
        return result.json()


    def ministering(self):
        """
        API parameters known to be accepted are lang type unitNumber and quarter.
        """
        _LOGGER.info("Getting ministering data")
        request = {'url': 'https://{}/api/umlu/v1/ministering/data-full'.format(LCR_DOMAIN),
                   'params': {'lang': 'eng',
                              'unitNumber': self.unit_number}}

        result = self._make_request(request)
        return result.json()


    def access_table(self):
        """
        Once the users role id is known this table could be checked to selectively enable or disable methods for API endpoints.
        """
        _LOGGER.info("Getting info for data access")
        request = {'url': 'https://{}/api/access-table'.format(LCR_DOMAIN),
                   'params': {'lang': 'eng'}}

        result = self._make_request(request)
        return result.json()


    def recommend_status(self):
        """
        Obtain member information on recommend status
        """
        _LOGGER.info("Getting recommend status")
        request = {
                'url': 'https://{}/api/recommend/recommend-status'.format(LCR_DOMAIN),
                'params': {
                    'lang': 'eng',
                    'unitNumber': self.unit_number
                    }
                }
        result = self._make_request(request)
        return result.json()


class MemberData():
    def __init__(self, legacyMemberId, fullName, sex, birthdate, callings, recommendStatus):
        self.legacyMemberId = legacyMemberId
        self.fullName = fullName
        self.sex = sex
        self.birthdate = birthdate
        self.callings = callings
        self.recommendStatus = recommendStatus

    def __iter__(self):
        return iter([self.legacyMemberId, self.fullName, self.sex, self.birthdate, self.callings, self.recommendStatus])
