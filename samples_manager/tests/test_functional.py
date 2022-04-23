import time
import logging
from selenium import webdriver
from django.urls import reverse
from django.test import tag
from samples_manager.models import *
from samples_manager.views import *
from samples_manager.utilities import *
from django.contrib.staticfiles.testing import (
    StaticLiveServerTestCase as SLSTestCase)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, TimeoutException

WAIT_SECONDS = 10
LONG_WAIT_SECONDS = 20


# Use this tag to skip tests: @tag('skip')


def hide_cookies_agreement(browser):
    """Hides cookies pannel if present."""
    xpath = '//div[@class = "cc-compliance"]/a'
    try:
        # This wait causes an error in tests. Don't know why yet.
        element = WebDriverWait(browser, WAIT_SECONDS).until(
        EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
    except NoSuchElementException:
        return
    except ElementNotInteractableException:
        return
    except TimeoutException:
        return
    xpath = '//div[@class = "cc-compliance"]/a'
    WebDriverWait(browser, WAIT_SECONDS).until(
        EC.invisibility_of_element_located((By.XPATH, xpath)))


def take_screenshot(browser, file_name_num=0):
    """Takes screenshot."""
    browser.save_screenshot('debug_' + str(file_name_num) + '.png')


def get_browser_console_log(browser):
    """Retrieves JS console log."""
    result = None
    try:
        result = browser.get_log('browser')
    except:
        result = "Exception when reading Browser Console log"
    return result

def scroll(browser, direction, pixels):
    """Scrolls page."""
    if direction == 'v':
        browser.execute_script('window.scrollTo(0, ' + str(pixels) + ')')
    elif direction == 'h':
        browser.execute_script('window.scrollTo(' + str(pixels) + ', 0)')

def set_user_cookies(browser, user_role):
    """Sets cookies for user."""
    browser.delete_all_cookies()
    set_user_elements_per_page(browser, 10)

    if user_role == 'Admin':
        browser.add_cookie({'name' : 'username', 'value' : 'test-admin'})
        browser.add_cookie({'name' : 'first_name', 'value' : 'Test'})
        browser.add_cookie({'name' : 'last_name', 'value' : 'Admin'})
        browser.add_cookie({'name' : 'telephone', 'value' : '1234'})
        browser.add_cookie({'name' : 'email', 'value' : 'test-admin@gmail.com'})
        browser.add_cookie({'name' : 'mobile', 'value' : '1234'})
        browser.add_cookie({'name' : 'department', 'value' : 'EP/DT'})
        browser.add_cookie({'name' : 'home_institute', 'value' : 'TU'})
    elif user_role == 'User':
        browser.add_cookie({'name' : 'username', 'value' : 'test-user'})
        browser.add_cookie({'name' : 'first_name', 'value' : 'Test'})
        browser.add_cookie({'name' : 'last_name', 'value' : 'User'})
        browser.add_cookie({'name' : 'telephone', 'value' : '1234'})
        browser.add_cookie({'name' : 'email', 'value' : 'test-user@gmail.com'})
        browser.add_cookie({'name' : 'mobile', 'value' : '1234'})
        browser.add_cookie({'name' : 'department', 'value' : 'EP/DT'})
        browser.add_cookie({'name' : 'home_institute', 'value' : 'TU'})
    
    browser.refresh()

def set_user_elements_per_page(browser, elements_per_page):
    """Sets cookies for user's elements per page."""
    browser.delete_cookie('elements_per_page')
    browser.add_cookie({'name' : 'elements_per_page', 'value' : str(elements_per_page)})
    browser.refresh()

def delayed_action(element, data):
    """Delays action by a small delay to avoid timing errors."""
    result = None
    if 'in_delay' not in data:
        data['in_delay'] = 0.1
    if 'out_delay' not in data:
        data['out_delay'] = 0
    
    time.sleep(data['in_delay'])
    if data['action'] == 'click':
        element.click()
    elif data['action'] == 'send_keys':
        if isinstance(data['keys'], list):
            for key in data['keys']:
                data_single_key = data.copy()
                data_single_key['keys'] = key
                delayed_action(element, data_single_key)
        else:
            element.send_keys(data['keys'])
    elif data['action'] == 'clear':
        element.clear()

    time.sleep(data['out_delay'])
    return result


class IndexTest(SLSTestCase):
    """Test class for index page."""

    fixtures = [
        'experiment_samples_archive.json',
        'boxes.json',
        'compound_elements.json',
        'compounds.json',
        'dosimeters.json',
        'elements.json',
        'experiment_categories.json',
        'experiments.json',
        'irradiations.json',
		'fluence_factors.json',
        'layers.json',
        'materials.json',
        'occupancies.json',
        'requested_fluences.json',
        'samples.json',
        'users.json'
        ]

    @classmethod
    def setUpClass(cls):
        """Ran once before all tests are run."""
        logging.disable(logging.CRITICAL)
        super().setUpClass()
        browser_type = 'chrome'
        if(browser_type == 'chrome'):
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--log-level=3')
            chrome_options.binary_location = '/usr/bin/chromium-browser'
            cls.browser = webdriver.Chrome(chrome_options=chrome_options)
        elif(browser_type == 'firefox'):
            firefox_options = webdriver.FirefoxOptions()
            firefox_options.set_headless()
            cls.browser = webdriver.Firefox(firefox_options=firefox_options)

        cls.experiments_url = cls.live_server_url + reverse('samples_manager:experiments_list')
        cls.url = cls.live_server_url + reverse('samples_manager:index')
        cls.new_experiment_name = 'aaa'

    @classmethod
    def tearDownClass(cls):
        """Ran once after all tests are run."""
        super().setUpClass()
        cls.browser.close()
        logging.disable(logging.NOTSET)

    def test_index_my_experiments(self):
        """Test my experiments button at index page."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        xpath = '//button[contains(@id, "user-experiments")]/..'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[contains(@class, \'breadcrumb\')]//div['\
            'contains(@class, \'active\') and contains(text(), '\
                '"Experiments")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check experiments page title
        self.assertTrue(element)

    def test_index_experiment_incomplete_form(self):
        """Test incomplete experiment form at index page."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        
        xpath = '//button[contains(@id, "create")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)
        #Last page navigation
        xpath = '//div[@id = "step-tab-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        #Submit experiment
        xpath = '//div[@id = "step-3"]//button[contains(@id, "submit")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)

    def test_index_create_experiment(self):
        """Test experiment creation at index page."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        xpath = '//button[contains(@id, "create")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)
        #Input data page 1
        xpath = '//div[@id = "step-1"]//input[@name = "title"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': self.new_experiment_name}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]//textarea[@name = "description"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': 'Test'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]//input[@name = "cern_experiment"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': 'ATLAS'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]//select[@name = "responsible"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['test-admin@gmail.com', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]//input[@name = "emergency_phone"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': '1234'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]//input[@name = "availability"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': get_aware_datetime().strftime('%d/%m/%Y')}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]//input[@name = "constraints"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': 'NA'}
        delayed_action(element, data)
        #Next page navigation
        xpath = '//div[@id = "step-tab-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        #Input data page 2
        xpath = '//div[@id = "step-2"]//input[@name = "number_samples"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': '1'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//select[@name = "category"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['Passive Standard', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "irradiation_area_5x5"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "irradiation_area_20x20"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//a[@class = "f-fs-add-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "f-fs-0-req_fluence"]'\
            '/../../..//a[@class = "f-fs-delete-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//a[@class = "f-fs-add-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//table/tbody/tr[contains(@class, "dynamic-formset-f-fs")]'
        num_rows = len(self.browser.find_elements_by_xpath(xpath))
        xpath = '//div[@id = "step-2"]//input[@name = "f-fs-' + str(num_rows-3) + '-req_fluence"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': '1'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "f-fs-' + str(num_rows-2) + '-req_fluence"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': '2'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//a[@class = "m-fs-add-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "m-fs-0-material"]'\
            '/../../..//a[@class = "m-fs-delete-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//a[@class = "m-fs-add-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//table/tbody/tr[contains(@class, "dynamic-formset-m-fs")]'
        num_rows = len(self.browser.find_elements_by_xpath(xpath))
        xpath = '//div[@id = "step-2"]//input[@name = "m-fs-' + str(num_rows-3) + '-material"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': 'material-0'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "m-fs-' + str(num_rows-2) + '-material"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': 'material-1'}
        delayed_action(element, data)
        #Next page navigation
        xpath = '//div[@id = "step-tab-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        #Input data page 3
        xpath = '//div[@id = "step-3"]//input[@name = "regulations_flag"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-3"]//input[@name = "public_experiment"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        #Submit experiment
        xpath = '//div[@id = "step-3"]//button[contains(@id, "submit")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        #Check the page remains unchanged
        xpath = '//button[contains(@id, "create")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        self.browser.get(self.experiments_url)
        xpath = '//tr/td[contains(text(), "' + self.new_experiment_name + '")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check new experiment title
        self.assertTrue(element)

    def test_index_create_experiment_form_navigation(self):
        """Test experiment creation form navigation at index page."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        xpath = '//button[contains(@id, "create")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form page one load
        self.assertTrue(element)
        xpath = '//div[@id = "step-tab-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check tab link to page two
        self.assertTrue(element)
        xpath = '//div[@id = "step-tab-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check tab link to page three
        self.assertTrue(element)
        xpath = '//div[@id = "step-tab-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check tab link to page one
        self.assertTrue(element)
        xpath = '//div[@id = "step-1"]//button[contains(text(),"Next")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check next button to page two
        self.assertTrue(element)
        xpath = '//div[@id = "step-2"]//button[contains(text(),"Next")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check next button to page three
        self.assertTrue(element)
        xpath = '//div[@id = "step-3"]//button[contains(text(),"Previous")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check previous button to page two
        self.assertTrue(element)
        xpath = '//div[@id = "step-2"]//button[contains(text(),"Previous")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check previous button to page three
        self.assertTrue(element)


class ExperimentListTest(SLSTestCase):
    """Test class experiments list."""

    fixtures = [
        'experiment_samples_archive.json',
        'boxes.json',
        'compound_elements.json',
        'compounds.json',
        'dosimeters.json',
        'elements.json',
        'experiment_categories.json',
        'experiments.json',
        'irradiations.json',
		'fluence_factors.json',
        'layers.json',
        'materials.json',
        'occupancies.json',
        'requested_fluences.json',
        'samples.json',
        'users.json'
        ]

    @classmethod
    def setUpClass(cls):
        """Ran once before all tests are run."""
        logging.disable(logging.CRITICAL)
        super().setUpClass()
        browser_type = 'chrome'
        if(browser_type == 'chrome'):
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--log-level=3')
            chrome_options.binary_location = '/usr/bin/chromium-browser'
            cls.browser = webdriver.Chrome(chrome_options=chrome_options)
        elif(browser_type == 'firefox'):
            firefox_options = webdriver.FirefoxOptions()
            firefox_options.set_headless()
            cls.browser = webdriver.Firefox(firefox_options=firefox_options)

        cls.url = cls.live_server_url + reverse('samples_manager:experiments_list')
        cls.shared_experiments_url = cls.live_server_url + reverse('samples_manager:experiments_shared_list')
        cls.new_experiment_name = 'aaa'
        cls.experiment_id = 1

    @classmethod
    def tearDownClass(cls):
        """Ran once after all tests are run."""
        super().setUpClass()
        cls.browser.close()
        logging.disable(logging.NOTSET)
        id='felters-tab'

    def test_experiment_incomplete_form(self):
        """Test incomplete experiment form."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "create")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)
        #Last page navigation
        xpath = '//div[@id = "step-tab-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        #Submit experiment
        xpath = '//div[@id = "step-3"]//button[contains(@id, "submit")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        alert = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)

    def test_create_experiment(self):
        """Test experiment creation."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "create")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        #Input data page 1
        xpath = '//div[@id = "step-1"]//input[@name = "title"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': self.new_experiment_name}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]//textarea[@name = "description"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': 'Test'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]//input[@name = "cern_experiment"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': 'ATLAS'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]//select[@name = "responsible"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['test-admin@gmail.com', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]//input[@name = "emergency_phone"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': '1234'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]//input[@name = "availability"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': get_aware_datetime().strftime('%d/%m/%Y')}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]//input[@name = "constraints"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': 'NA'}
        delayed_action(element, data)
        #Next page navigation
        xpath = '//div[@id = "step-tab-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        #Input data page 2
        xpath = '//div[@id = "step-2"]//input[@name = "number_samples"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': '1'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//select[@name = "category"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['Passive Standard', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "irradiation_area_5x5"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "irradiation_area_20x20"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//a[@class = "f-fs-add-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "f-fs-0-req_fluence"]'\
            '/../../..//a[@class = "f-fs-delete-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//a[@class = "f-fs-add-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//table/tbody/tr[contains(@class, "dynamic-formset-f-fs")]'
        num_rows = len(self.browser.find_elements_by_xpath(xpath))
        xpath = '//div[@id = "step-2"]//input[@name = "f-fs-' + str(num_rows-3) + '-req_fluence"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': '1'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "f-fs-' + str(num_rows-2) + '-req_fluence"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': '2'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//a[@class = "m-fs-add-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "m-fs-0-material"]'\
            '/../../..//a[@class = "m-fs-delete-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//a[@class = "m-fs-add-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//table/tbody/tr[contains(@class, "dynamic-formset-m-fs")]'
        num_rows = len(self.browser.find_elements_by_xpath(xpath))
        xpath = '//div[@id = "step-2"]//input[@name = "m-fs-' + str(num_rows-3) + '-material"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': 'material-0'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "m-fs-' + str(num_rows-2) + '-material"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': 'material-1'}
        delayed_action(element, data)
        #Next page navigation
        xpath = '//div[@id = "step-tab-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        #Input data page 3
        xpath = '//div[@id = "step-3"]//input[@name = "regulations_flag"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-3"]//input[@name = "public_experiment"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        #Submit experiment
        xpath = '//div[@id = "step-3"]//button[contains(@id, "submit")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        xpath = '//tr/td[contains(text(), "' + self.new_experiment_name +  '")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check new experiment title
        self.assertTrue(element)

    def test_create_experiment_form_navigation(self):
        """Test experiment creation form navigation."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "create")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form page one load
        self.assertTrue(element)
        xpath = '//div[@id = "step-tab-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check tab link to page two
        self.assertTrue(element)
        xpath = '//div[@id = "step-tab-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check tab link to page three
        self.assertTrue(element)
        xpath = '//div[@id = "step-tab-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check tab link to page one
        self.assertTrue(element)
        xpath = '//div[@id = "step-1"]//button[contains(text(),"Next")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check next button to page two
        self.assertTrue(element)
        xpath = '//div[@id = "step-2"]//button[contains(text(),"Next")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check next button to page three
        self.assertTrue(element)
        xpath = '//div[@id = "step-3"]//button[contains(text(),"Previous")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check previous button to page two
        self.assertTrue(element)
        xpath = '//div[@id = "step-2"]//button[contains(text(),"Previous")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check previous button to page three
        self.assertTrue(element)

    def test_admin_validate_experiment(self):
        """Test experiment validation."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        experiment = Experiment.objects.get(pk=1)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        xpath = '//input[@name = "checks[]" and @value="' + str(experiment.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "validate")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)
        #Navigate to page two
        xpath = '//div[@id = "step-tab-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        #Input data page 2
        xpath = '//div[@id = "step-2"]//select[@name = "category"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['Passive Custom', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//select[@name = "passive_category_type"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['Cryostat', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "passive_irradiation_area"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': '25x25mm2'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//textarea[@name = "passive_modus_operandi"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': 'NA'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//a[@class = "f-fs-add-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "f-fs-0-req_fluence"]'\
            '/../../..//a[@class = "f-fs-delete-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//a[@class = "f-fs-add-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//table/tbody/tr[contains(@class, "dynamic-formset-f-fs")]'
        num_rows = len(self.browser.find_elements_by_xpath(xpath))
        xpath = '//div[@id = "step-2"]//input[@name = "f-fs-' + str(num_rows-3) + '-req_fluence"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': '1'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "f-fs-' + str(num_rows-2) + '-req_fluence"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': '2'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//a[@class = "m-fs-add-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "m-fs-0-material"]'\
            '/../../..//a[@class = "m-fs-delete-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//a[@class = "m-fs-add-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//table/tbody/tr[contains(@class, "dynamic-formset-m-fs")]'
        num_rows = len(self.browser.find_elements_by_xpath(xpath))
        xpath = '//div[@id = "step-2"]//input[@name = "m-fs-' + str(num_rows-3) + '-material"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': 'material-0'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "m-fs-' + str(num_rows-2) + '-material"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': 'material-1'}
        delayed_action(element, data)
        #Navigate to page three
        xpath = '//div[@id = "step-tab-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-3"]//button[contains(@id, "submit")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        xpath = '//tr/td[text() = "' + str(experiment.id) + '"]/../'\
            'td[last() and contains(text(), "Validated")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check experiment validated state
        self.assertTrue(element)

    def test_admin_validate_experiment_form_navigation(self):
        """Test experiment validation form navigation."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        experiment = Experiment.objects.get(pk=1)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        xpath = '//input[@name = "checks[]" and @value="' + str(experiment.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "validate")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form page one load
        self.assertTrue(element)
        xpath = '//div[@id = "step-tab-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check tab link to page two
        self.assertTrue(element)
        xpath = '//div[@id = "step-tab-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check tab link to page three
        self.assertTrue(element)
        xpath = '//div[@id = "step-tab-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check tab link to page one
        self.assertTrue(element)
        xpath = '//div[@id = "step-1"]//button[contains(text(),"Next")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check next button to page two
        self.assertTrue(element)
        xpath = '//div[@id = "step-2"]//button[contains(text(),"Next")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check next button to page three
        self.assertTrue(element)
        xpath = '//div[@id = "step-3"]//button[contains(text(),"Previous")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check previous button to page two
        self.assertTrue(element)
        xpath = '//div[@id = "step-2"]//button[contains(text(),"Previous")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check previous button to page three
        self.assertTrue(element)

    def test_admin_update_experiment(self):
        """Test update experiment button loads form."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        experiment = Experiment.objects.get(pk=1)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        xpath = '//input[@name = "checks[]" and @value="' + str(experiment.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "update")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        #Change experiments title
        xpath = '//div[@id = "step-1"]//input[@name = "title"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': self.new_experiment_name}
        delayed_action(element, data)
        #Navigate to page two
        xpath = '//div[@id = "step-tab-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        #Input data page 2
        xpath = '//div[@id = "step-2"]//select[@name = "category"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['Passive Custom', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//select[@name = "passive_category_type"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['Cryostat', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "passive_irradiation_area"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': '25x25mm2'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//textarea[@name = "passive_modus_operandi"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': 'NA'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//a[@class = "f-fs-add-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "f-fs-0-req_fluence"]'\
            '/../../..//a[@class = "f-fs-delete-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//a[@class = "f-fs-add-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//table/tbody/tr[contains(@class, "dynamic-formset-f-fs")]'
        num_rows = len(self.browser.find_elements_by_xpath(xpath))
        xpath = '//div[@id = "step-2"]//input[@name = "f-fs-' + str(num_rows-3) + '-req_fluence"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': '1'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "f-fs-' + str(num_rows-2) + '-req_fluence"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': '2'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//a[@class = "m-fs-add-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "m-fs-0-material"]'\
            '/../../..//a[@class = "m-fs-delete-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//a[@class = "m-fs-add-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//table/tbody/tr[contains(@class, "dynamic-formset-m-fs")]'
        num_rows = len(self.browser.find_elements_by_xpath(xpath))
        xpath = '//div[@id = "step-2"]//input[@name = "m-fs-' + str(num_rows-3) + '-material"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': 'material-0'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "m-fs-' + str(num_rows-2) + '-material"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': 'material-1'}
        delayed_action(element, data)
        #Navigate to page three
        xpath = '//div[@id = "step-tab-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-3"]//button[contains(@id, "submit")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        xpath = '//tr/td[contains(text(), "' + self.new_experiment_name + '")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check new experiment title
        self.assertTrue(element)

    def test_admin_update_experiment_form_navigation(self):
        """Test experiment update form navigation."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        experiment = Experiment.objects.get(pk=1)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        xpath = '//input[@name = "checks[]" and @value="' + str(experiment.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "update")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form page one load
        self.assertTrue(element)
        xpath = '//div[@id = "step-tab-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check tab link to page two
        self.assertTrue(element)
        xpath = '//div[@id = "step-tab-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check tab link to page three
        self.assertTrue(element)
        xpath = '//div[@id = "step-tab-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check tab link to page one
        self.assertTrue(element)
        xpath = '//div[@id = "step-1"]//button[contains(text(),"Next")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check next button to page two
        self.assertTrue(element)
        xpath = '//div[@id = "step-2"]//button[contains(text(),"Next")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check next button to page three
        self.assertTrue(element)
        xpath = '//div[@id = "step-3"]//button[contains(text(),"Previous")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check previous button to page two
        self.assertTrue(element)
        xpath = '//div[@id = "step-2"]//button[contains(text(),"Previous")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check previous button to page three
        self.assertTrue(element)

    def test_admin_clone_experiment(self):
        """Test experiment cloning."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        experiment = Experiment.objects.get(pk=1)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        xpath = '//input[@name = "checks[]" and @value="' + str(experiment.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "clone")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        #Change experiments title
        xpath = '//div[@id = "step-1"]//input[@name = "title"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': self.new_experiment_name}
        delayed_action(element, data)
        #Navigate to page two
        xpath = '//div[@id = "step-tab-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        #Input data page 2
        xpath = '//div[@id = "step-2"]//select[@name = "category"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['Passive Custom', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//select[@name = "passive_category_type"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['Cryostat', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "passive_irradiation_area"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': '25x25mm2'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//textarea[@name = "passive_modus_operandi"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': 'NA'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "f-fs-0-req_fluence"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': '1'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "m-fs-0-material"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': 'Silicon'}
        delayed_action(element, data)
        #Navigate to page three
        xpath = '//div[@id = "step-tab-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-3"]//button[contains(@id, "submit")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        xpath = '//tr[1]/td[contains(text(), "' + self.new_experiment_name + '")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check new experiment title
        self.assertTrue(element)

    def test_admin_clone_experiment_form_navigation(self):
        """Test experiment cloning form navigation."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        experiment = Experiment.objects.get(pk=1)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        xpath = '//input[@name = "checks[]" and @value="' + str(experiment.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "clone")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form page one load
        self.assertTrue(element)
        xpath = '//div[@id = "step-tab-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check tab link to page two
        self.assertTrue(element)
        xpath = '//div[@id = "step-tab-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check tab link to page three
        self.assertTrue(element)
        xpath = '//div[@id = "step-tab-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check tab link to page one
        self.assertTrue(element)
        xpath = '//div[@id = "step-1"]//button[contains(text(),"Next")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check next button to page two
        self.assertTrue(element)
        xpath = '//div[@id = "step-2"]//button[contains(text(),"Next")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check next button to page three
        self.assertTrue(element)
        xpath = '//div[@id = "step-3"]//button[contains(text(),"Previous")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check previous button to page two
        self.assertTrue(element)
        xpath = '//div[@id = "step-2"]//button[contains(text(),"Previous")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check previous button to page three
        self.assertTrue(element)

    def test_contact_experiments_responsibles(self):
        """Test contact experiment responsibles action."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        experiment_0 = Experiment.objects.get(pk=1)
        experiment_1 = Experiment.objects.get(pk=2)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        xpath = '//input[@name = "checks[]" and @value="' + str(experiment_0.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@name = "checks[]" and @value="' + str(experiment_1.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "contact-responsible")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        alert = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        text = alert.text
        self.browser.switch_to.alert.accept()
        self.assertTrue('success' in text)

    def test_admin_delete_experiment(self):
        """Test experiment deletion."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        experiment = Experiment.objects.get(pk=1)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        xpath = '//input[@name = "checks[]" and @value="' + str(experiment.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "delete")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//table/tbody/tr'
        old_rows = self.browser.find_elements_by_xpath(xpath)
        xpath = '//div[@id = "modal-experiment"]//h3[text() = "Confirm experiment deletion"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)
        xpath = '//div[@id = "modal-experiment"]//button[text() = "Delete"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        #Check deleted experiment
        xpath = '//table/tbody/tr'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        new_rows = self.browser.find_elements_by_xpath(xpath)
        self.assertTrue(len(old_rows) == (len(new_rows) + 1))

    def test_admin_change_status_experiment(self):
        """Test change status experiment button loads form."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        experiment = Experiment.objects.get(pk=1)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        xpath = '//input[@name = "checks[]" and @value="' + str(experiment.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "status")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-experiment"]//h3[text() = "Update Status"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)
        xpath = '//div[@id = "modal-experiment"]//select[@name = "status"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        #Added delay to avoid timeout error
        data = {'action': 'send_keys', 'keys': ['Updated', Keys.ENTER], 'out_delay': 0.1}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-experiment"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        xpath = '//table//tr[1]/td[contains(text(), "Updated")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        #Check experiment status change
        self.assertTrue(element)

    def test_admin_users_experiment(self):
        """Test experiment users button."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        experiment = Experiment.objects.get(pk=1)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        xpath = '//input[@name = "checks[]" and @value="' + str(experiment.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "user")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[contains(@class, \'breadcrumb\')]//div['\
            'contains(@class, \'active\') and contains(text(), '\
                '"Users")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)

    def test_admin_samples_experiment(self):
        """Test experiment samples button."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        experiment = Experiment.objects.get(pk=1)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        xpath = '//input[@name = "checks[]" and @value="' + str(experiment.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "sample")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[contains(@class, \'breadcrumb\')]//div['\
            'contains(@class, \'active\') and contains(text(), '\
                '"Samples")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)

    def test_admin_search_experiment(self):
        """Test experiment search."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        experiment = Experiment.objects.get(pk=6)
        xpath = '//div[@id = "filters-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@id = "search-box"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        #Enter experiment to search
        data = {'action': 'send_keys', 'keys': str(experiment.title)}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "search")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//tbody//tr[1]/td[contains(text(), "' + str(experiment.title) + '")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check experiment is first result
        self.assertTrue(element)

    def test_admin_empty_search_experiment(self):
        """Test experiment empty search."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        xpath = '//div[@id = "filters-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "search")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//tbody//tr[1]/td[contains(text(), "e-00")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check experiment is first result
        self.assertTrue(element)

    def test_admin_experiment_completed(self):
        """Test admin experiment completed available actions."""
        experiment = Experiment.objects.get(pk=self.experiment_id)
        experiment.status = 'Completed'
        experiment.save()
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@name = "checks[]" and @value="' + str(experiment.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "update")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        alert = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        text = alert.text
        self.browser.switch_to.alert.accept()
        self.assertTrue('invalid operation' in text.lower())
        xpath = '//button[contains(@id, "validate")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        alert = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        text = alert.text
        self.browser.switch_to.alert.accept()
        self.assertTrue('invalid operation' in text.lower())
        xpath = '//button[contains(@id, "sample")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[contains(@class, \'breadcrumb\')]//div['\
            'contains(@class, \'active\') and contains(text(), '\
                '"Samples")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "archive")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//button[contains(@id, "result")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//button[contains(@id, "read-infoream")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//button[contains(@id, "sample-details")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//div[@data-tab="actions"]//button'
        num_buttons = len(self.browser.find_elements_by_xpath(xpath))
        self.assertTrue(num_buttons == 5)

    
    def test_experiment_completed(self):
        """Test user experiment completed available actions."""
        alert_str = 'invalid operation'
        experiment = Experiment.objects.get(pk=self.experiment_id)
        experiment.status = 'Completed'
        experiment.save()
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'User')
        hide_cookies_agreement(self.browser)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@name = "checks[]" and @value="' + str(experiment.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "validate")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        alert = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        text = alert.text
        self.browser.switch_to.alert.accept()
        self.assertTrue(alert_str in text.lower())
        xpath = '//button[contains(@id, "sample")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[contains(@class, \'breadcrumb\')]//div['\
            'contains(@class, \'active\') and contains(text(), '\
                '"Samples")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "archive")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//button[contains(@id, "result")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//div[@data-tab="actions"]//button'
        num_buttons = len(self.browser.find_elements_by_xpath(xpath))
        self.assertTrue(num_buttons == 3)


    def test_update_experiment(self):
        """Test update experiment button loads form."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'User')
        hide_cookies_agreement(self.browser)
        experiment = Experiment.objects.get(pk=5)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        xpath = '//input[@name = "checks[]" and @value="' + str(experiment.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "update")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        #Change experiments title
        xpath = '//div[@id = "step-1"]//input[@name = "title"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': self.new_experiment_name}
        delayed_action(element, data)
        xpath = '//div[@id = "step-tab-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        #Input data page 2
        xpath = '//div[@id = "step-2"]//select[@name = "category"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['Active', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//select[@name = "active_category_type"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['Cryostat', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "active_irradiation_area"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': '25x25mm2'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//textarea[@name = "active_modus_operandi"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': 'NA'}
        delayed_action(element, data)
        #Navigate to page three
        xpath = '//div[@id = "step-tab-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-3"]//button[contains(@id, "submit")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        xpath = '//tr[1]/td[contains(text(), "' + self.new_experiment_name + '")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check new experiment title
        self.assertTrue(element)

    def test_update_experiment_form_navigation(self):
        """Test experiment update form navigation."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'User')
        hide_cookies_agreement(self.browser)
        experiment = Experiment.objects.get(pk=5)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        xpath = '//input[@name = "checks[]" and @value="' + str(experiment.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "update")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form page one load
        self.assertTrue(element)
        xpath = '//div[@id = "step-tab-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check tab link to page two
        self.assertTrue(element)
        xpath = '//div[@id = "step-tab-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check tab link to page three
        self.assertTrue(element)
        xpath = '//div[@id = "step-tab-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check tab link to page one
        self.assertTrue(element)
        xpath = '//div[@id = "step-1"]//button[contains(text(),"Next")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check next button to page two
        self.assertTrue(element)
        xpath = '//div[@id = "step-2"]//button[contains(text(),"Next")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check next button to page three
        self.assertTrue(element)
        xpath = '//div[@id = "step-3"]//button[contains(text(),"Previous")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check previous button to page two
        self.assertTrue(element)
        xpath = '//div[@id = "step-2"]//button[contains(text(),"Previous")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check previous button to page three
        self.assertTrue(element)

    def test_clone_experiment(self):
        """Test experiment cloning."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'User')
        hide_cookies_agreement(self.browser)
        experiment = Experiment.objects.get(pk=5)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        xpath = '//input[@name = "checks[]" and @value="' + str(experiment.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "clone")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        #Change experiments title
        xpath = '//div[@id = "step-1"]//input[@name = "title"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': self.new_experiment_name}
        delayed_action(element, data)
        #Navigate to page two
        xpath = '//div[@id = "step-tab-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        #Input data page 2
        xpath = '//div[@id = "step-2"]//select[@name = "category"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['Active', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//select[@name = "active_category_type"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['Cryostat', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "active_irradiation_area"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': '25x25mm2'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//textarea[@name = "active_modus_operandi"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': 'NA'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "f-fs-0-req_fluence"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': '1'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "m-fs-0-material"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': 'Silicon'}
        delayed_action(element, data)
        #Navigate to page three
        xpath = '//div[@id = "step-tab-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-3"]//button[contains(@id, "submit")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        xpath = '//tr[1]/td[contains(text(), "' + self.new_experiment_name + '")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check new experiment title
        self.assertTrue(element)

    def test_clone_experiment_form_navigation(self):
        """Test experiment cloning form navigation."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'User')
        hide_cookies_agreement(self.browser)
        experiment = Experiment.objects.get(pk=5)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        xpath = '//input[@name = "checks[]" and @value="' + str(experiment.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "clone")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form page one load
        self.assertTrue(element)
        xpath = '//div[@id = "step-tab-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check tab link to page two
        self.assertTrue(element)
        xpath = '//div[@id = "step-tab-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check tab link to page three
        self.assertTrue(element)
        xpath = '//div[@id = "step-tab-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check tab link to page one
        self.assertTrue(element)
        xpath = '//div[@id = "step-1"]//button[contains(text(),"Next")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check next button to page two
        self.assertTrue(element)
        xpath = '//div[@id = "step-2"]//button[contains(text(),"Next")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check next button to page three
        self.assertTrue(element)
        xpath = '//div[@id = "step-3"]//button[contains(text(),"Previous")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check previous button to page two
        self.assertTrue(element)
        xpath = '//div[@id = "step-2"]//button[contains(text(),"Previous")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check previous button to page three
        self.assertTrue(element)

    def test_experiment_file_upload(self):
        """Test experiment file upload."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'User')
        hide_cookies_agreement(self.browser)
        experiment = Experiment.objects.get(pk=4)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        xpath = '//input[@name = "checks[]" and @value="' + str(experiment.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//table/tbody/tr'
        old_rows = self.browser.find_elements_by_xpath(xpath)
        xpath = '//button[contains(@id, "experiment-upload-attachment")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//h3[contains(text(), "Attachment")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        self.assertTrue(element)
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.frame_to_be_available_and_switch_to_it("iframe-upload"))
        self.assertTrue(element)
        xpath = '//input[contains(@class, "hiddenuploadfield")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.presence_of_element_located((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': '/root/Projects/samples-manager/static/images/cern.jpg'}
        delayed_action(element, data)
        xpath = '//li[contains(text(), "cern.jpg")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)

    def test_delete_experiment(self):
        """Test experiment deletion."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'User')
        hide_cookies_agreement(self.browser)
        experiment = Experiment.objects.get(pk=4)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        xpath = '//input[@name = "checks[]" and @value="' + str(experiment.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//table/tbody/tr'
        old_rows = self.browser.find_elements_by_xpath(xpath)
        xpath = '//button[contains(@id, "delete")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-experiment"]//h3[text() = "Confirm experiment deletion"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)
        xpath = '//div[@id = "modal-experiment"]//button[text() = "Delete"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        #Check deleted experiment
        xpath = '//table/tbody/tr'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        new_rows = self.browser.find_elements_by_xpath(xpath)
        self.assertTrue(len(old_rows) == (len(new_rows) + 1))

    def test_visibility_experiment(self):
        """Test experiment visibility.""" 
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        experiment = Experiment.objects.filter(public_experiment=True)[0]
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@name = "checks[]" and @value="' + str(experiment.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "visibility")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-experiment"]//h3[contains(text(), "Visibility")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check irradiation update beam status form load
        self.assertTrue(element)
        xpath = '//div[@id = "modal-experiment"]//select[@id = "id_visibility"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['Private', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-experiment"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        xpath = '//td[text() = "' + experiment.title + '"]/../td[last() - 1 and contains(text(), "Private")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        self.assertTrue(element)

    def test_form_load_users_experiment(self):
        """Test users experiment button loads form."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'User')
        hide_cookies_agreement(self.browser)
        experiment = Experiment.objects.get(pk=1)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        xpath = '//input[@name = "checks[]" and @value="' + str(experiment.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "user")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[contains(@class, \'breadcrumb\')]//div['\
            'contains(@class, \'active\') and contains(text(), '\
                '"Users")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        self.assertTrue(element)

    def test_form_load_samples_experiment(self):
        """Test samples experiment button loads form."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'User')
        hide_cookies_agreement(self.browser)
        experiment = Experiment.objects.get(pk=1)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        xpath = '//input[@name = "checks[]" and @value="' + str(experiment.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "sample")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[contains(@class, \'breadcrumb\')]//div['\
            'contains(@class, \'active\') and contains(text(), '\
                '"Samples")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        self.assertTrue(element)

    def test_details_experiment(self):
        """Test experiment details page."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        experiment = Experiment.objects.get(pk=1)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        xpath = '//input[@name = "checks[]" and @value="' + str(experiment.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "details")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[contains(@class, \'breadcrumb\')]//div['\
            'contains(@class, \'active\') and contains(text(), '\
                '"' + experiment.title + '")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        self.assertTrue(element)

    def test_search_experiment(self):
        """Test experiment search."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        set_user_elements_per_page(self.browser, 20)
        hide_cookies_agreement(self.browser)
        experiment = Experiment.objects.get(pk=6)
        xpath = '//div[@id = "filters-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@id = "search-box"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        #Enter experiment to search
        data = {'action': 'send_keys', 'keys': str(experiment.title)}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "search")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//tbody//tr[1]/td[contains(text(), "' + str(experiment.title) + '")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check experiment is first result
        self.assertTrue(element)
        #Clear search
        xpath = '//button[contains(@id, "search-clear")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click', 'out_delay': 0.5}
        delayed_action(element, data)
        #Rows with more than one column to avoid "no results" row
        xpath = '//table/tbody/tr/td[2]/..'
        all_elements = Experiment.objects.all()
        try:
            element = WebDriverWait(self.browser, WAIT_SECONDS).until(
                EC.visibility_of_element_located((By.XPATH, xpath)))
            rows = self.browser.find_elements_by_xpath(xpath)
            self.assertTrue(len(rows) == len(all_elements))
        except:
            self.assertTrue(len(all_elements) == 0)

    def test_empty_search_experiment(self):
        """Test experiment empty search."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'User')
        hide_cookies_agreement(self.browser)
        xpath = '//div[@id = "filters-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "search")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//tbody//tr[1]/td[2]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        xpath = '//tbody//tr'
        rows = self.browser.find_elements_by_xpath(xpath)
        user = User.objects.get(pk=2)
        num_experiments = write_authorised_experiments(user).count()
        #Check experiments displayed
        self.assertTrue(len(rows) == num_experiments)

    def test_experiment_completed(self):
        """Test experiment completed available actions."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'User')
        hide_cookies_agreement(self.browser)
        pass

    def test_details_shared_experiment(self):
        """Test shared experiment details page."""
        self.browser.get(self.shared_experiments_url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        experiment = Experiment.objects.get(pk=1)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        xpath = '//input[@name = "checks[]" and @value="' + str(experiment.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "details")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[contains(@class, \'breadcrumb\')]//div['\
            'contains(@class, \'active\') and contains(text(), '\
                '"' + experiment.title + '")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        self.assertTrue(element)

    def test_search_shared_experiment(self):
        """Test shared experiment search."""
        self.browser.get(self.shared_experiments_url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        experiment = Experiment.objects.get(pk=6)
        xpath = '//div[@id = "filters-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@id = "search-box"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        #Enter experiment to search
        data = {'action': 'send_keys', 'keys': str(experiment.title)}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "search")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//tbody//tr[1]/td[contains(text(), "' + str(experiment.title) + '")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check experiment is first result
        self.assertTrue(element)
        #Clear search
        xpath = '//button[contains(@id, "search-clear")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click', 'out_delay': 0.5}
        delayed_action(element, data)
        #Rows with more than one column to avoid "no results" row
        xpath = '//table/tbody/tr/td[2]/..'
        all_elements = Experiment.objects.all()
        try:
            element = WebDriverWait(self.browser, WAIT_SECONDS).until(
                EC.visibility_of_element_located((By.XPATH, xpath)))
            rows = self.browser.find_elements_by_xpath(xpath)
            self.assertTrue(len(rows) == len(all_elements))
        except:
            self.assertTrue(len(all_elements) == 0)

    def test_empty_search_shared_experiment(self):
        """Test shared experiment empty search."""
        self.browser.get(self.shared_experiments_url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        xpath = '//div[@id = "filters-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "search")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//tbody//tr'
        rows = self.browser.find_elements_by_xpath(xpath)
        user = User.objects.get(pk=1)
        num_experiments = shared_experiments(user).count()
        #Check experiments displayed
        self.assertTrue(len(rows) == num_experiments)


class SampleListTest(SLSTestCase):
    """Test class sample list."""

    fixtures = [
        'experiment_samples_archive.json',
        'boxes.json',
        'compound_elements.json',
        'compounds.json',
        'dosimeters.json',
        'elements.json',
        'experiment_categories.json',
        'experiments.json',
        'irradiations.json',
		'fluence_factors.json',
        'layers.json',
        'materials.json',
        'occupancies.json',
        'requested_fluences.json',
        'samples.json',
        'users.json'
        ]

    @classmethod
    def setUpClass(cls):
        """Ran once before all tests are run."""
        logging.disable(logging.CRITICAL)
        super().setUpClass()
        browser_type = 'chrome'
        if(browser_type == 'chrome'):
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--log-level=3')
            chrome_options.binary_location = '/usr/bin/chromium-browser'
            cls.browser = webdriver.Chrome(chrome_options=chrome_options)
        elif(browser_type == 'firefox'):
            firefox_options = webdriver.FirefoxOptions()
            firefox_options.set_headless()
            cls.browser = webdriver.Firefox(firefox_options=firefox_options)

        cls.experiment_id = 1
        cls.new_experiment_id = 3
        cls.sample_id = 1
        cls.sample_id_without_sec = 3
        cls.dosimeter_id = 1
        cls.material_id = 1
        cls.element_id_0 = 1
        cls.element_id_1 = 2
        cls.req_fluence_id = 1
        cls.new_sample_name = 'aaa'
        cls.printer_name = 'irrad-eam-printer'
        cls.printer_template_name = 'small_qr'
        cls.set_id = 'SET-003203'
        cls.url = cls.live_server_url + reverse('samples_manager:'\
            'experiment_samples_list', args=[cls.experiment_id])
        cls.url_new_experiment = cls.live_server_url + reverse('samples_manager:'\
            'experiment_samples_list', args=[cls.new_experiment_id])

    @classmethod
    def tearDownClass(cls):
        """Ran once after all tests are run."""
        super().setUpClass()
        cls.browser.close()
        logging.disable(logging.NOTSET)

    def test_sample_incomplete_form(self):
        """Test incomplete sample form."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'User')
        hide_cookies_agreement(self.browser)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "sample-create")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check sample form load
        self.assertTrue(element)
        #Last page navigation
        xpath = '//div[@id = "step-tab-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        #Submit sample
        xpath = '//div[@id = "step-3"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check sample form load
        self.assertTrue(element)

    def test_create_sample(self):
        """Test experiment creation."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'User')
        hide_cookies_agreement(self.browser)
        material = Material.objects.get(pk=self.material_id)
        req_fluence = ReqFluence.objects.get(pk=self.req_fluence_id)
        element_0 = Element.objects.get(pk=self.element_id_0)
        element_1 = Element.objects.get(pk=self.element_id_1)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "sample-create")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        #Input data page 1
        xpath = '//div[@id = "step-1"]//select[@name = "material"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [material.material, Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]//input[@name = "name"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': self.new_sample_name}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]//input[@name = "weight"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': '0.001'}
        delayed_action(element, data)
        #Next page navigation
        xpath = '//div[@id = "step-tab-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        #Input data page 2
        xpath = '//div[@id = "step-2"]//input[@name = "height"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': '0.001'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "width"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': '0.001'}
        delayed_action(element, data)
        #Create sample
        xpath = '//div[@id = "step-2"]//button[contains(@id, "create")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//h3[text() = "Create Compound"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check sample form load
        self.assertTrue(element)
        compound_name = 'test-compound'
        xpath = '//div[@id = "modal-compound"]//input[@name = "name"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': compound_name}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//input[@name = "density"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': '0.0000001'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//a[@class = "ce-fs-add-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//select[@name = "ce-fs-0-element_type"]'\
            '/../../../..//a[@class = "ce-fs-delete-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//a[@class = "ce-fs-add-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//table/tbody/tr[contains(@class, "dynamic-formset-ce-fs")]'
        num_rows = len(self.browser.find_elements_by_xpath(xpath))
        xpath = '//div[@id = "modal-compound"]//select[@name = "ce-fs-' + str(num_rows-3) + '-element_type"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [str(element_0), Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//input[@name = "ce-fs-' + str(num_rows-3) + '-percentage"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': '10'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//select[@name = "ce-fs-' + str(num_rows-2) + '-element_type"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [str(element_1), Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//input[@name = "ce-fs-' + str(num_rows-2) + '-percentage"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': '90'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
           EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {
            'action': 'click',
            'out_delay': 0.5
            }
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        #Continue input data page 2
        # TODO it seems not possible to add new rows. Maybe JS isn't loading as it should.
        xpath = '//div[@id = "step-2"]//a[@class = "layer_set-add-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click', 'out_delay': 0.75}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "layer_set-0-name"]'\
            '/../../..//a[@class = "layer_set-delete-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        data = {'action': 'click', 'out_delay': 0.75}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//a[@class = "layer_set-add-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click', 'out_delay': 0.75}
        delayed_action(element, data)
        xpath = '//table/tbody/tr[contains(@class, "dynamic-formset-layer_set")]'
        num_rows = len(self.browser.find_elements_by_xpath(xpath))
        xpath = '//div[@id = "step-2"]//input[@name = "layer_set-' + str(num_rows-3) + '-name"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': 'L-0'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "layer_set-' + str(num_rows-3) + '-length"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': '0.01'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//select[@name = "layer_set-' + str(num_rows-3) + '-compound_type"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [compound_name, Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "layer_set-' + str(num_rows-2) + '-name"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': 'L-1'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "layer_set-' + str(num_rows-2) + '-length"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': '0.01'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//select[@name = "layer_set-' + str(num_rows-2) + '-compound_type"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['c-01', Keys.ENTER]}
        delayed_action(element, data)
        #Next page navigation
        xpath = '//div[@id = "step-tab-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        #Input data page 3
        xpath = '//div[@id = "step-3"]//select[@name = "req_fluence"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [req_fluence.req_fluence, Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "step-3"]//select[@name = "category"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['Passive standard 5x', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "step-3"]//select[@name = "storage"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['Room temperature', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "step-3"]//select[@name = "current_location"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['14/R-012', Keys.ENTER], 'in_delay': 0.5}
        delayed_action(element, data)
        #Submit sample
        xpath = '//div[@id = "step-3"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        time.sleep(3)
        xpath = '//tr/td[text() = "' + self.new_sample_name + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check new experiment title
        self.assertTrue(element)

    def test_create_sample_form_navigation(self):
        """Test sample creation form navigation."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "sample-create")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form page one load
        self.assertTrue(element)
        xpath = '//div[@id = "step-tab-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check tab link to page two
        self.assertTrue(element)
        xpath = '//div[@id = "step-tab-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check tab link to page three
        self.assertTrue(element)
        xpath = '//div[@id = "step-tab-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check tab link to page one
        self.assertTrue(element)
        xpath = '//div[@id = "step-1"]//button[contains(text(),"Next")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check next button to page two
        self.assertTrue(element)
        xpath = '//div[@id = "step-2"]//button[contains(text(),"Next")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check next button to page three
        self.assertTrue(element)
        xpath = '//div[@id = "step-3"]//button[contains(text(),"Previous")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check previous button to page two
        self.assertTrue(element)
        xpath = '//div[@id = "step-2"]//button[contains(text(),"Previous")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check previous button to page three
        self.assertTrue(element)

    def test_update_sample(self):
        """Test update sample button loads form."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        sample = Sample.objects.get(pk=self.sample_id)
        prev_total_radiation_length = sample.experiment.radiation_length_occupancy + \
            sample.experiment.nu_coll_length_occupancy + \
            sample.experiment.nu_int_length_occupancy
        element_0 = Element.objects.get(pk=self.element_id_0)
        element_1 = Element.objects.get(pk=self.element_id_1)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        xpath = '//input[@name = "checks[]" and @value="' + str(sample.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "update")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        #Change experiments title
        xpath = '//div[@id = "step-1"]//input[@name = "name"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': self.new_sample_name}
        delayed_action(element, data)
        #Navigate to page two
        xpath = '//div[@id = "step-tab-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        #Input data page 2
        #Create compound
        xpath = '//div[@id = "step-2"]//button[contains(@id, "create")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//h3[text() = "Create Compound"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check compound form load
        self.assertTrue(element)
        compound_name = 'test-compound'
        xpath = '//div[@id = "modal-compound"]//input[@name = "name"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': compound_name}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//input[@name = "density"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': '0.0000001'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//a[@class = "ce-fs-add-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//select[@name = "ce-fs-0-element_type"]'\
            '/../../../..//a[@class = "ce-fs-delete-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//a[@class = "ce-fs-add-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//table/tbody/tr[contains(@class, "dynamic-formset-ce-fs")]'
        num_rows = len(self.browser.find_elements_by_xpath(xpath))
        xpath = '//div[@id = "modal-compound"]//select[@name = "ce-fs-' + str(num_rows-3) + '-element_type"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [str(element_0), Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//input[@name = "ce-fs-' + str(num_rows-3) + '-percentage"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': '10'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//select[@name = "ce-fs-' + str(num_rows-2) + '-element_type"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [str(element_1), Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//input[@name = "ce-fs-' + str(num_rows-2) + '-percentage"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': '90'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
           EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {
            'action': 'click',
            'out_delay': 0.5
            }
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        #Continue input data page 2
        xpath = '//table/tbody/tr[contains(@class, "dynamic-formset-layer_set")]'
        num_rows = len(self.browser.find_elements_by_xpath(xpath))
        #Delete last empty form
        xpath = '//div[@id = "step-2"]//input[@name = "layer_set-' + str(num_rows-2) + '-name"]'\
            '/../../..//a[@class = "layer_set-delete-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//a[@class = "layer_set-add-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "layer_set-0-name"]'\
            '/../../..//a[@class = "layer_set-delete-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//a[@class = "layer_set-add-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//table/tbody/tr[contains(@class, "dynamic-formset-layer_set")]'
        num_rows = len(self.browser.find_elements_by_xpath(xpath))
        xpath = '//div[@id = "step-2"]//input[@name = "layer_set-' + str(num_rows-3) + '-name"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': 'L-0'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "layer_set-' + str(num_rows-3) + '-length"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': '1000000'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//select[@name = "layer_set-' + str(num_rows-3) + '-compound_type"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [compound_name, Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "layer_set-' + str(num_rows-2) + '-name"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': 'L-1'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "layer_set-' + str(num_rows-2) + '-length"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': '1000000'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//select[@name = "layer_set-' + str(num_rows-2) + '-compound_type"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['c-01', Keys.ENTER]}
        delayed_action(element, data)
        #Navigate to page three
        xpath = '//div[@id = "step-tab-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        #Check form page three load
        self.assertTrue(element)
        xpath = '//div[@id = "step-3"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        #Check new sample
        xpath = '//tr/td[text() = "' + self.new_sample_name + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #A new query to the database is required to access the updated data
        sample = Sample.objects.get(pk=self.sample_id)
        total_radiation_length = sample.experiment.radiation_length_occupancy +\
            sample.experiment.nu_coll_length_occupancy + \
            sample.experiment.nu_int_length_occupancy
        self.assertTrue(element)
        self.assertTrue(prev_total_radiation_length != total_radiation_length)

    def test_update_sample_form_navigation(self):
        """Test sample update form navigation."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        sample = Sample.objects.get(pk=self.sample_id)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        xpath = '//input[@name = "checks[]" and @value="' + str(sample.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "update")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form page one load
        self.assertTrue(element)
        xpath = '//div[@id = "step-tab-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check tab link to page two
        self.assertTrue(element)
        xpath = '//div[@id = "step-tab-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check tab link to page three
        self.assertTrue(element)
        xpath = '//div[@id = "step-tab-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check tab link to page one
        self.assertTrue(element)
        xpath = '//div[@id = "step-1"]//button[contains(text(),"Next")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check next button to page two
        self.assertTrue(element)
        xpath = '//div[@id = "step-2"]//button[contains(text(),"Next")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check next button to page three
        self.assertTrue(element)
        xpath = '//div[@id = "step-3"]//button[contains(text(),"Previous")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check previous button to page two
        self.assertTrue(element)
        xpath = '//div[@id = "step-2"]//button[contains(text(),"Previous")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check previous button to page three
        self.assertTrue(element)

    def test_clone_sample(self):
        """Test sample cloning."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        sample = Sample.objects.get(pk=self.sample_id)
        element_0 = Element.objects.get(pk=self.element_id_0)
        element_1 = Element.objects.get(pk=self.element_id_1)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        xpath = '//input[@name = "checks[]" and @value="' + str(sample.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "clone")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        #Change experiments title
        xpath = '//div[@id = "step-1"]//input[@name = "name"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': self.new_sample_name}
        delayed_action(element, data)
        #Navigate to page two
        xpath = '//div[@id = "step-tab-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        #Input data page 2
        #Create compound
        xpath = '//div[@id = "step-2"]//button[contains(@id, "create")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//h3[text() = "Create Compound"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check compound form load
        self.assertTrue(element)
        compound_name = 'test-compound'
        xpath = '//div[@id = "modal-compound"]//input[@name = "name"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': compound_name}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//input[@name = "density"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': '0.0000001'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//a[@class = "ce-fs-add-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//select[@name = "ce-fs-0-element_type"]'\
            '/../../../..//a[@class = "ce-fs-delete-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//a[@class = "ce-fs-add-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//table/tbody/tr[contains(@class, "dynamic-formset-ce-fs")]'
        num_rows = len(self.browser.find_elements_by_xpath(xpath))
        xpath = '//div[@id = "modal-compound"]//select[@name = "ce-fs-' + str(num_rows-3) + '-element_type"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [str(element_0), Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//input[@name = "ce-fs-' + str(num_rows-3) + '-percentage"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': '10'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//select[@name = "ce-fs-' + str(num_rows-2) + '-element_type"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [str(element_1), Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//input[@name = "ce-fs-' + str(num_rows-2) + '-percentage"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': '90'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
           EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {
            'action': 'click',
            'out_delay': 0.5
            }
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        #Continue input data page 2
        xpath = '//table/tbody/tr[contains(@class, "formset_row dynamic-formset-layer_set")]'
        num_rows = len(self.browser.find_elements_by_xpath(xpath))
        #Delete last empty form
        xpath = '//div[@id = "step-2"]//input[@name = "layer_set-' + str(num_rows-2) + '-name"]'\
            '/../../..//a[@class = "layer_set-delete-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//a[@class = "layer_set-add-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "layer_set-' + str(num_rows-1) + '-name"]'\
            '/../../..//a[@class = "layer_set-delete-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//a[@class = "layer_set-add-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "layer_set-' + str(num_rows) + '-name"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': 'L-0'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "layer_set-' + str(num_rows) + '-length"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': '0.01'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//select[@name = "layer_set-' + str(num_rows) + '-compound_type"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [compound_name, Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "layer_set-' + str(num_rows+1) + '-name"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': 'L-1'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//input[@name = "layer_set-' + str(num_rows+1) + '-length"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': '0.01'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//select[@name = "layer_set-' + str(num_rows+1) + '-compound_type"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['c-01', Keys.ENTER]}
        delayed_action(element, data)
        #Navigate to page three
        xpath = '//div[@id = "step-tab-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-3"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        xpath = '//tr/td[text() = "' + self.new_sample_name + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check new experiment title
        self.assertTrue(element)

    def test_clone_sample_form_navigation(self):
        """Test sample cloning form navigation."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        sample = Sample.objects.get(pk=self.sample_id)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        xpath = '//input[@name = "checks[]" and @value="' + str(sample.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "clone")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form page one load
        self.assertTrue(element)
        xpath = '//div[@id = "step-tab-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check tab link to page two
        self.assertTrue(element)
        xpath = '//div[@id = "step-tab-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check tab link to page three
        self.assertTrue(element)
        xpath = '//div[@id = "step-tab-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check tab link to page one
        self.assertTrue(element)
        xpath = '//div[@id = "step-1"]//button[contains(text(),"Next")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check next button to page two
        self.assertTrue(element)
        xpath = '//div[@id = "step-2"]//button[contains(text(),"Next")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-3"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check next button to page three
        self.assertTrue(element)
        xpath = '//div[@id = "step-3"]//button[contains(text(),"Previous")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check previous button to page two
        self.assertTrue(element)
        xpath = '//div[@id = "step-2"]//button[contains(text(),"Previous")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check previous button to page three
        self.assertTrue(element)

    def test_set_id_readonly(self):
        """Test set_id disable state for admin and non-admin users."""
        #Check for non-admin users 
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'User')
        hide_cookies_agreement(self.browser)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "sample-create")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]//input[@name = "set_id"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        self.assertTrue(self.browser.execute_script('return $(\'input'\
            '[name="set_id"]\').is(\'[readonly]\')'))
        #Check for admin users 
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "sample-create")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]//input[@name = "set_id"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        self.assertTrue(self.browser.execute_script('return !$(\'input'\
            '[name="set_id"]\').is(\'[readonly]\')'))

    def test_delete_sample(self):
        """Test sample deletion."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        xpath = '//table/tbody/tr'
        old_rows = self.browser.find_elements_by_xpath(xpath)
        sample = Sample.objects.get(pk=self.sample_id)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        xpath = '//input[@name = "checks[]" and @value="' + str(sample.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "delete")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-sample"]//h3[text() = "Confirm sample deletion"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)
        xpath = '//div[@id = "modal-sample"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        #Check deleted sample
        xpath = '//table/tbody/tr'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        new_rows = self.browser.find_elements_by_xpath(xpath)
        self.assertTrue(len(old_rows) == (len(new_rows) + 1))

    def test_assign_set_id_sample(self):
        """Test sample set id assignation."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        clear_equipment_serial_number(self.set_id)
        sample = Sample.objects.get(pk=self.sample_id_without_sec)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        xpath = '//input[@name = "checks[]" and @value="' + str(sample.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "assign")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        alert = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        alert = WebDriverWait(self.browser, LONG_WAIT_SECONDS).until(
            EC.alert_is_present())
        text = alert.text
        self.browser.switch_to.alert.accept()
        self.assertTrue('success' in text)
        xpath = '//td[text() = "' + sample.name + '"]/../td[contains(text(), "SET-")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)

    def test_read_infoream_sample(self):
        """Test read sample information in infoream."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        set_user_elements_per_page(self.browser, 20)
        sample = Sample.objects.get(pk=self.sample_id)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        xpath = '//input[@name = "checks[]" and @value="' + str(sample.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "read-infoream")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[contains(@class, \'breadcrumb\')]//div['\
            'contains(@class, \'active\') and contains(text(), '\
                '"inforEAM details ' + sample.set_id + '")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check next button to page three
        self.assertTrue(element)

    def test_write_infoream_sample(self):
        """Test write sample information in infoream."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        set_user_elements_per_page(self.browser, 20)
        sample = Sample.objects.get(pk=self.sample_id)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        xpath = '//input[@name = "checks[]" and @value="' + str(sample.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "write-infoream")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-sample"]//h3[contains(text(), "Confirm")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)
        xpath = '//div[@id = "modal-sample"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        alert = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        text = alert.text
        self.browser.switch_to.alert.accept()
        self.assertTrue('success' in text)

    def test_move_sample(self):
        """Test move samples to another experiment."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        sample = Sample.objects.get(pk=self.sample_id)
        new_experiment = Experiment.objects.get(pk=self.new_experiment_id)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        xpath = '//input[@name = "checks[]" and @value="' + str(sample.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "move")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-sample"]//h3[contains(text(), "Move samples")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check irradiation update status form load
        self.assertTrue(element)
        xpath = '//div[@id = "modal-sample"]//select[@id = "id_experiment"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [new_experiment.title, Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-sample"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        alert = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        text = alert.text
        self.browser.switch_to.alert.accept()
        self.assertTrue('success' in text)
        sample = Sample.objects.get(pk=self.sample_id)
        xpath = '//button[contains(@id, "archive")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//tbody/tr/td[contains(text(), "' + sample.name + '")]/../'\
            'td/a[contains(text(), "' + sample.experiment.title + '")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        self.browser.get(self.url_new_experiment)
        xpath = '//td[contains(text(), "' + sample.name + '")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        self.assertTrue(element)

    @tag('skip')
    def test_print_sample(self):
        """Test print sample."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        sample = Sample.objects.get(pk=self.sample_id)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        xpath = '//input[@name = "checks[]" and @value="' + str(sample.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "print")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-sample"]//h3[contains(text(), "Print")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//div[@id = "modal-sample"]//select[@id = "id_printer"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [self.printer_name, Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-sample"]//select[@id = "id_template"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [self.printer_template_name, Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-sample"]//input[@id = "id_num_copies"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['0', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-sample"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        alert = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        text = alert.text
        self.browser.switch_to.alert.accept()
        self.assertTrue('success' in text)

    
    def test_print_sample_invalid_experiment(self):
        """Test print sample with invalid experiment."""
        experiment = Experiment.objects.get(pk=self.experiment_id)
        experiment.status = 'Validated'
        experiment.save()
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'User')
        hide_cookies_agreement(self.browser)
        sample = Sample.objects.get(pk=self.sample_id)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        no_print = self.browser.execute_script('return $(\'button'\
            '[id*=\\\'print\\\']\').length == 0')
        self.assertTrue(no_print)

    
    def test_print_sample_without_set_id(self):
        """Test print sample without set_id."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'User')
        hide_cookies_agreement(self.browser)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@name = "select_all"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "print")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        alert = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        text = alert.text
        self.browser.switch_to.alert.accept()
        self.assertTrue('invalid' in text)


    def test_details_sample(self):
        """Test sample details page."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        sample = Sample.objects.get(pk=self.sample_id)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        xpath = '//input[@name = "checks[]" and @value="' + str(sample.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "details")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[contains(@class, \'breadcrumb\')]//div['\
            'contains(@class, \'active\') and contains(text(), '\
                '"' + sample.name + '")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        self.assertTrue(element)

    def test_search_sample(self):
        """Test sample search."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        sample = Sample.objects.get(pk=self.sample_id)
        xpath = '//div[@id = "filters-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@id = "search-box"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        #Enter experiment to search
        data = {'action': 'send_keys', 'keys': sample.name}
        delayed_action(element, data)
        xpath = '//button[@id = "search-submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click', 'out_delay': 0.5}
        delayed_action(element, data)
        xpath = '//table/tbody/tr'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        rows = self.browser.find_elements_by_xpath(xpath)
        self.assertTrue(len(rows) == 1)
        #Clear search
        xpath = '//button[contains(@id, "search-clear")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click', 'out_delay': 0.5}
        delayed_action(element, data)
        #Rows with more than one column to avoid "no results" row
        xpath = '//table/tbody/tr/td[2]/..'
        all_elements = Sample.objects.filter(experiment=sample.experiment.id)
        try:
            element = WebDriverWait(self.browser, WAIT_SECONDS).until(
                EC.visibility_of_element_located((By.XPATH, xpath)))
            rows = self.browser.find_elements_by_xpath(xpath)
            self.assertTrue(len(rows) == len(all_elements))
        except:
            self.assertTrue(len(all_elements) == 0)

    def test_empty_search_sample(self):
        """Test sample empty search."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        experiment = Experiment.objects.get(pk=self.experiment_id)
        xpath = '//div[@id = "filters-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "search")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//tbody//tr'
        rows = self.browser.find_elements_by_xpath(xpath)
        num_samples = Sample.objects.filter(experiment=experiment).count()
        #Check samples
        self.assertTrue(len(rows) == num_samples)

class IrradiationListTest(SLSTestCase):
    """Test class irradiation list."""

    fixtures = [
        'experiment_samples_archive.json',
        'boxes.json',
        'compound_elements.json',
        'compounds.json',
        'dosimeters.json',
        'elements.json',
        'experiment_categories.json',
        'experiments.json',
        'irradiations.json',
		'fluence_factors.json',
        'layers.json',
        'materials.json',
        'occupancies.json',
        'requested_fluences.json',
        'samples.json',
        'users.json'
        ]

    @classmethod
    def setUpClass(cls):
        """Ran once before all tests are run."""
        logging.disable(logging.CRITICAL)
        super().setUpClass()
        browser_type = 'chrome'
        if(browser_type == 'chrome'):
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--log-level=3')
            chrome_options.binary_location = '/usr/bin/chromium-browser'
            cls.browser = webdriver.Chrome(chrome_options=chrome_options)
        elif(browser_type == 'firefox'):
            firefox_options = webdriver.FirefoxOptions()
            firefox_options.set_headless()
            cls.browser = webdriver.Firefox(firefox_options=firefox_options)

        cls.irradiation_id = 1
        cls.unstarted_irradiation_id = 2
        cls.experiment_id = 1
        cls.sample_id = 1
        cls.dosimeter_id = 1
        cls.past_date = get_past_aware_datetime(3).strftime('%Y/%m/%d')
        cls.current_date = get_aware_datetime().strftime('%Y/%m/%d')
        cls.initial_state = 'Registered'
        cls.in_beam_state = 'InBeam'
        cls.out_beam_state = 'OutBeam'
        cls.url = cls.live_server_url + reverse('samples_manager:irradiations_list')
        cls.sample_url = cls.live_server_url + reverse('samples_manager:'\
            'experiment_samples_list', args=[cls.experiment_id])

    @classmethod
    def tearDownClass(cls):
        """Ran once after all tests are run."""
        super().setUpClass()
        cls.browser.close()
        logging.disable(logging.NOTSET)

    def test_irradiation_incomplete_form(self):
        """Test incomplete irradiation form."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "create")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//h3[text() = "Create Irradiation"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)
        #Submit
        xpath = '//div[@id = "modal-irradiation"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        xpath = '//div[@id = "modal-irradiation"]//h3[text() = "Create Irradiation"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)

    def test_create_past_irradiation(self):
        """Test create past irradiation."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        set_user_elements_per_page(self.browser, 20)
        sample = Sample.objects.get(pk=self.sample_id)
        dosimeter = Dosimeter.objects.get(pk=self.dosimeter_id)
        set_user_elements_per_page(self.browser, 20)
        xpath = '//div[@id="partial-template"]//tbody/tr'
        old_rows = self.browser.find_elements_by_xpath(xpath)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "create")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//h3[text() = "Create Irradiation"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)
        #Fill data
        xpath = '//div[@id = "modal-irradiation"]//select[@name = "sample"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [sample.set_id, Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//select[@name = "dosimeter"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [dosimeter.dos_id, Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//select[@name = "irrad_table"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['IRRAD3', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//select[@name = "table_position"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['Center', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//input[@name = "dos_position"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': '1'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//input[@name = "date_in"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': str(self.past_date) + ' 00:00'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//input[@name = "date_out"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': str(self.current_date) + ' 09:00'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        self.browser.execute_script('console.log(\'trs \', $(\'tr\').length);')
        xpath = '//div[@id="partial-template"]//tbody/tr'
        new_rows = self.browser.find_elements_by_xpath(xpath)
        self.assertTrue(len(old_rows) == (len(new_rows) - 1))
        xpath = '//tbody/tr[1]/td[last()][contains(text(), "' + self.out_beam_state + '")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[@class="sec"][text() != "None"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[@class="estimated-fluence"][contains(text(), "E")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[@class="factor-value"][contains(text(), "E")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[7][contains(text(), "/")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[8][contains(text(), "/")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[9][contains(text(), "/")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[10][contains(text(), "/")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)

    def test_create_current_irradiation(self):
        """Test create current irradiation."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        set_user_elements_per_page(self.browser, 20)
        sample = Sample.objects.get(pk=self.sample_id)
        dosimeter = Dosimeter.objects.get(pk=self.dosimeter_id)
        xpath = '//div[@id="partial-template"]//tbody/tr'
        old_rows = self.browser.find_elements_by_xpath(xpath)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "create")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//h3[text() = "Create Irradiation"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)
        #Fill data
        xpath = '//div[@id = "modal-irradiation"]//select[@name = "sample"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [sample.set_id, Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//select[@name = "dosimeter"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [dosimeter.dos_id, Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//select[@name = "irrad_table"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['IRRAD3', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//select[@name = "table_position"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['Center', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//input[@name = "dos_position"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': '1'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//input[@name = "date_in"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': str(self.past_date) + ' 00:00'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        self.browser.execute_script('console.log(\'trs \', $(\'tr\').length);')
        xpath = '//div[@id="partial-template"]//tbody/tr'
        new_rows = self.browser.find_elements_by_xpath(xpath)
        self.assertTrue(len(old_rows) == (len(new_rows) - 1))
        xpath = '//tbody/tr[1]/td[last()][contains(text(), "' + self.in_beam_state + '")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[@class="sec"][text() != "None"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[@class="estimated-fluence"][contains(text(), "E")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[@class="factor-value"][contains(text(), "E")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[7][contains(text(), "/")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[8][contains(text(), "/")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[9][not(normalize-space(text()))]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[10][not(normalize-space(text()))]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)

    def test_create_future_irradiation(self):
        """Test create future irradiation."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        set_user_elements_per_page(self.browser, 20)
        sample = Sample.objects.get(pk=self.sample_id)
        dosimeter = Dosimeter.objects.get(pk=self.dosimeter_id)
        set_user_elements_per_page(self.browser, 20)
        xpath = '//div[@id="partial-template"]//tbody/tr'
        old_rows = self.browser.find_elements_by_xpath(xpath)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "create")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//h3[text() = "Create Irradiation"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)
        #Fill data
        xpath = '//div[@id = "modal-irradiation"]//select[@name = "sample"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [sample.set_id, Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//select[@name = "dosimeter"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [dosimeter.dos_id, Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//select[@name = "irrad_table"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['IRRAD3', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//select[@name = "table_position"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['Center', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//input[@name = "dos_position"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': '1'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, LONG_WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        self.browser.execute_script('console.log(\'trs \', $(\'tr\').length);')
        xpath = '//div[@id="partial-template"]//tbody/tr'
        new_rows = self.browser.find_elements_by_xpath(xpath)
        self.assertTrue(len(old_rows) == (len(new_rows) - 1))
        xpath = '//tbody/tr[1]/td[last()][contains(text(), "' + self.initial_state + '")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[@class="sec"][text() = "None"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[@class="estimated-fluence"][text() = "None"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[@class="factor-value"][not(normalize-space(text()))]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[7][not(normalize-space(text()))]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[8][not(normalize-space(text()))]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[9][not(normalize-space(text()))]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[10][not(normalize-space(text()))]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)

    def test_create_irradiation_group(self):
        """Test new irradiation group form."""
        self.browser.get(self.sample_url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        set_user_elements_per_page(self.browser, 20)
        sample = Sample.objects.get(pk=self.sample_id)
        dosimeter = Dosimeter.objects.get(pk=self.dosimeter_id)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@name = "checks[]" and @value="' + str(sample.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "group-irradiation")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//h3[text() = "Create Irradiation"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)
        #Fill data
        xpath = '//div[@id = "modal-irradiation"]//select[@name = "dosimeter"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [dosimeter.dos_id, Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//select[@name = "irrad_table"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['IRRAD19', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//select[@name = "table_position"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['Center', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        xpath = '//div[contains(@class, \'breadcrumb\')]//div['\
            'contains(@class, \'active\') and contains(text(), '\
                '"Irradiations")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check irradiation page redirection
        self.assertTrue(element)
        current_date = get_aware_datetime().strftime('%d/%m/%Y')
        xpath = '//tr/td[contains(text(), "' + str(current_date) + '")]/../td/a[text() = "' + dosimeter.dos_id + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check irradiation
        self.assertTrue(element)

    @tag('skip')
    def test_update_status_irradiation(self):
        """Test irradiation update status."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        set_user_elements_per_page(self.browser, 20)
        irradiation = Irradiation.objects.get(pk=self.irradiation_id)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@name = "checks[]" and @value="' + str(irradiation.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "update-status")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//h3[text() = "Update status"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check irradiation update status form load
        self.assertTrue(element)
        xpath = '//div[@id = "modal-irradiation"]//select[@id = "id_status"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['Approved', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        xpath = '//tr/td/a[text() = "' + irradiation.dosimeter.dos_id + '"]\
            /../../td[last()]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check irradiation
        self.assertTrue(element)

    def test_update_past_irradiation(self):
        """Test update past irradiation."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        set_user_elements_per_page(self.browser, 20)
        sample = Sample.objects.get(pk=self.sample_id)
        dosimeter = Dosimeter.objects.get(pk=self.dosimeter_id)
        irradiation = Irradiation.objects.get(pk=self.irradiation_id)
        set_user_elements_per_page(self.browser, 20)
        xpath = '//div[@id="partial-template"]//tbody/tr'
        old_rows = self.browser.find_elements_by_xpath(xpath)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@name = "checks[]" and @value="' + str(irradiation.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "update")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//h3[text() = "Update Irradiation"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)
        #Fill data
        xpath = '//div[@id = "modal-irradiation"]//select[@name = "sample"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [sample.set_id, Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//select[@name = "dosimeter"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [dosimeter.dos_id, Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//select[@name = "irrad_table"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['IRRAD3', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//select[@name = "table_position"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['Center', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//input[@name = "dos_position"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': '1'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//input[@name = "date_in"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': str(self.past_date) + ' 00:00'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//input[@name = "date_out"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': str(self.current_date) + ' 09:00'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        self.browser.execute_script('console.log(\'trs \', $(\'tr\').length);')
        xpath = '//div[@id="partial-template"]//tbody/tr'
        new_rows = self.browser.find_elements_by_xpath(xpath)
        self.assertTrue(len(old_rows) == len(new_rows))
        # Wait for page to load with new data
        time.sleep(2)
        # Get irradiation with updated information
        irradiation = Irradiation.objects.get(pk=self.irradiation_id)
        xpath = '//tbody/tr[1]/td[last()][contains(text(), "' + irradiation.status + '")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[@class="sec"][text() != "None"]'
        element = WebDriverWait(self.browser, LONG_WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[@class="estimated-fluence"][contains(text(), "E")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[@class="factor-value"][contains(text(), "E")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[7][contains(text(), "/")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[8][contains(text(), "/")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[9][contains(text(), "/")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[10][contains(text(), "/")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)

    def test_update_current_irradiation(self):
        """Test update current irradiation."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        set_user_elements_per_page(self.browser, 20)
        sample = Sample.objects.get(pk=self.sample_id)
        dosimeter = Dosimeter.objects.get(pk=self.dosimeter_id)
        irradiation = Irradiation.objects.get(pk=self.irradiation_id)
        set_user_elements_per_page(self.browser, 20)
        xpath = '//div[@id="partial-template"]//tbody/tr'
        old_rows = self.browser.find_elements_by_xpath(xpath)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@name = "checks[]" and @value="' + str(irradiation.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "update")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//h3[text() = "Update Irradiation"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)
        #Fill data
        xpath = '//div[@id = "modal-irradiation"]//select[@name = "sample"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [sample.set_id, Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//select[@name = "dosimeter"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [dosimeter.dos_id, Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//select[@name = "irrad_table"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['IRRAD3', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//select[@name = "table_position"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['Center', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//input[@name = "dos_position"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': '1'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//input[@name = "date_in"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': str(self.past_date) + ' 00:00'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//input[@name = "date_out"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        self.browser.execute_script('console.log(\'trs \', $(\'tr\').length);')
        xpath = '//div[@id="partial-template"]//tbody/tr'
        new_rows = self.browser.find_elements_by_xpath(xpath)
        self.assertTrue(len(old_rows) == len(new_rows))
        # Get irradiation with updated information
        irradiation = Irradiation.objects.get(pk=self.irradiation_id)
        xpath = '//tbody/tr[1]/td[last()][contains(text(), "' + irradiation.status + '")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[@class="sec"][text() != "None"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[@class="estimated-fluence"][contains(text(), "E")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[@class="factor-value"][contains(text(), "E")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[7][contains(text(), "/")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[8][contains(text(), "/")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[9][not(normalize-space(text()))]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[10][not(normalize-space(text()))]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)

    def test_update_future_irradiation(self):
        """Test update future irradiation."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        set_user_elements_per_page(self.browser, 20)
        sample = Sample.objects.get(pk=self.sample_id)
        dosimeter = Dosimeter.objects.get(pk=self.dosimeter_id)
        irradiation = Irradiation.objects.get(pk=self.irradiation_id)
        set_user_elements_per_page(self.browser, 20)
        xpath = '//div[@id="partial-template"]//tbody/tr'
        old_rows = self.browser.find_elements_by_xpath(xpath)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@name = "checks[]" and @value="' + str(irradiation.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "update")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//h3[text() = "Update Irradiation"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)
        #Fill data
        xpath = '//div[@id = "modal-irradiation"]//select[@name = "sample"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [sample.set_id, Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//select[@name = "dosimeter"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [dosimeter.dos_id, Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//select[@name = "irrad_table"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['IRRAD3', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//select[@name = "table_position"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['Center', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//input[@name = "dos_position"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': '1'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//input[@name = "date_in"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//input[@name = "date_out"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        self.browser.execute_script('console.log(\'trs \', $(\'tr\').length);')
        xpath = '//div[@id="partial-template"]//tbody/tr'
        new_rows = self.browser.find_elements_by_xpath(xpath)
        self.assertTrue(len(old_rows) == len(new_rows))
        # Get irradiation with updated information
        irradiation = Irradiation.objects.get(pk=self.irradiation_id)
        xpath = '//tbody/tr[1]/td[last()][contains(text(), "' + irradiation.status + '")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[@class="sec"][text() = "None"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[@class="estimated-fluence"][text() = "None"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[@class="factor-value"][not(normalize-space(text()))]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[7][not(normalize-space(text()))]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[8][not(normalize-space(text()))]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[9][not(normalize-space(text()))]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[10][not(normalize-space(text()))]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)

    def test_delete_irradiation(self):
        """Test irradiation deletion."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        set_user_elements_per_page(self.browser, 20)
        irradiation = Irradiation.objects.get(pk=self.irradiation_id)
        xpath = '//table/tbody/tr'
        old_rows = self.browser.find_elements_by_xpath(xpath)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@name = "checks[]" and @value="' + str(irradiation.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "delete")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//h3[text() = "Confirm irradiation deletion"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check irradiation update status form load
        self.assertTrue(element)
        xpath = '//div[@id = "modal-irradiation"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        #Check deleted irradiation
        xpath = '//table/tbody/tr'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        new_rows = self.browser.find_elements_by_xpath(xpath)
        self.assertTrue(len(old_rows) == (len(new_rows) + 1))

    def test_perform_irradiation_beam_status(self):
        """Test irradiation update beam state on and off."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        set_user_elements_per_page(self.browser, 20)
        irradiation = Irradiation.objects.filter(pk=self.unstarted_irradiation_id)[0]
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        #Set sample as in beam
        xpath = '//input[@name = "checks[]" and @value="' + str(irradiation.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "beam-status")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//h3[text() = "Update in-beam status"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check irradiation update beam status form load
        self.assertTrue(element)
        xpath = '//div[@id = "modal-irradiation"]//select[@id = "id_in_beam"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['True', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        xpath = '//td/a[text() = "' + irradiation.dosimeter.dos_id + '"]/../../td[last() and contains(text(), "InBeam")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        self.assertTrue(element)
        #Set sample as out of beam
        xpath = '//input[@name = "checks[]" and @value="' + str(irradiation.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "beam-status")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//h3[text() = "Update in-beam status"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check irradiation update beam status form load
        self.assertTrue(element)
        xpath = '//div[@id = "modal-irradiation"]//select[@id = "id_in_beam"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['False', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        time.sleep(5)
        xpath = '//td/a[text() = "' + irradiation.dosimeter.dos_id + '"]'\
            '/../../td[last() and contains(text(), "OutBeam")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[@class="sec"][text() != "None"]'
        element = WebDriverWait(self.browser, LONG_WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[@class="estimated-fluence"][contains(text(), "E")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[@class="factor-value"][contains(text(), "E")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[7][contains(text(), "/")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[10][contains(text(), "/")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        has_zero_sec = self.browser.execute_script('return '\
            '($(\'tbody tr:first-child .sec\')[0].innerText == 0)')
        if not has_zero_sec:
            xpath = '//tbody/tr[1]/td[8][contains(text(), "/")]'
            element = WebDriverWait(self.browser, WAIT_SECONDS).until(
                EC.element_to_be_clickable((By.XPATH, xpath)))
            self.assertTrue(element)
            xpath = '//tbody/tr[1]/td[9][contains(text(), "/")]'
            element = WebDriverWait(self.browser, WAIT_SECONDS).until(
                EC.element_to_be_clickable((By.XPATH, xpath)))
            self.assertTrue(element)
        else:
            xpath = '//tbody/tr[1]/td[8][not(normalize-space(text()))]'
            element = WebDriverWait(self.browser, WAIT_SECONDS).until(
                EC.element_to_be_clickable((By.XPATH, xpath)))
            self.assertTrue(element)
            xpath = '//tbody/tr[1]/td[9][not(normalize-space(text()))]'
            element = WebDriverWait(self.browser, WAIT_SECONDS).until(
                EC.element_to_be_clickable((By.XPATH, xpath)))
            self.assertTrue(element)

    @tag('skip')
    def test_perform_irradiation_status(self):
        """Test irradiation update beam state on and off using update status button."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        set_user_elements_per_page(self.browser, 20)
        irradiation = Irradiation.objects.filter(pk=self.unstarted_irradiation_id)[0]
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        #Set sample as in beam
        xpath = '//input[@name = "checks[]" and @value="' + str(irradiation.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "update-status")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//h3[text() = "Update status"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check irradiation update status form load
        self.assertTrue(element)
        xpath = '//div[@id = "modal-irradiation"]//select[@id = "id_status"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['InBeam', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        xpath = '//td/a[text() = "' + irradiation.dosimeter.dos_id + '"]/../../td[last() and contains(text(), "InBeam")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        self.assertTrue(element)
        #Set sample as out of beam
        xpath = '//input[@name = "checks[]" and @value="' + str(irradiation.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "update-status")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//h3[text() = "Update status"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check irradiation update status form load
        self.assertTrue(element)
        xpath = '//div[@id = "modal-irradiation"]//select[@id = "id_status"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['OutBeam', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-irradiation"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        time.sleep(5)
        xpath = '//td/a[text() = "' + irradiation.dosimeter.dos_id + '"]'\
            '/../../td[last() and contains(text(), "OutBeam")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[@class="sec"][text() != "None"]'
        element = WebDriverWait(self.browser, LONG_WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[@class="estimated-fluence"][contains(text(), "E")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[@class="factor-value"][contains(text(), "E")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[7][contains(text(), "/")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//tbody/tr[1]/td[10][contains(text(), "/")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        has_zero_sec = self.browser.execute_script('return '\
            '($(\'tbody tr:first-child .sec\')[0].innerText == 0)')
        if not has_zero_sec:
            xpath = '//tbody/tr[1]/td[8][contains(text(), "/")]'
            element = WebDriverWait(self.browser, WAIT_SECONDS).until(
                EC.element_to_be_clickable((By.XPATH, xpath)))
            self.assertTrue(element)
            xpath = '//tbody/tr[1]/td[9][contains(text(), "/")]'
            element = WebDriverWait(self.browser, WAIT_SECONDS).until(
                EC.element_to_be_clickable((By.XPATH, xpath)))
            self.assertTrue(element)
        else:
            xpath = '//tbody/tr[1]/td[8][not(normalize-space(text()))]'
            element = WebDriverWait(self.browser, WAIT_SECONDS).until(
                EC.element_to_be_clickable((By.XPATH, xpath)))
            self.assertTrue(element)
            xpath = '//tbody/tr[1]/td[9][not(normalize-space(text()))]'
            element = WebDriverWait(self.browser, WAIT_SECONDS).until(
                EC.element_to_be_clickable((By.XPATH, xpath)))
            self.assertTrue(element)

    def test_search_irradiation(self):
        """Test irradiation search."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        set_user_elements_per_page(self.browser, 20)
        irradiation = Irradiation.objects.get(pk=self.irradiation_id)
        xpath = '//div[@id = "filters-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@id = "search-box"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        #Enter experiment to search
        data = {'action': 'send_keys', 'keys': irradiation.dosimeter.dos_id}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "search-submit")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click', 'out_delay': 0.5}
        delayed_action(element, data)
        xpath = '//table/tbody/tr/td[2]/..'
        all_elements = Irradiation.objects.all()
        rows = self.browser.find_elements_by_xpath(xpath)
        #Check experiment is first result
        self.assertTrue(len(rows) > 0 and len(rows) < len(all_elements))
        #Clear search
        xpath = '//button[contains(@id, "search-clear")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click', 'out_delay': 0.5}
        delayed_action(element, data)
        #Rows with more than one column to avoid "no results" row
        xpath = '//table/tbody/tr/td[2]/..'
        try:
            element = WebDriverWait(self.browser, WAIT_SECONDS).until(
                EC.visibility_of_element_located((By.XPATH, xpath)))
            rows = self.browser.find_elements_by_xpath(xpath)
            self.assertTrue(len(rows) == len(all_elements))
        except:
            self.assertTrue(len(all_elements) == 0)


    def test_empty_search_irradiation(self):
        """Test irradiation empty search."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        set_user_elements_per_page(self.browser, 20)
        xpath = '//div[@id = "filters-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "search")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//tbody//tr'
        rows = self.browser.find_elements_by_xpath(xpath)
        num_irradiations = Irradiation.objects.all().count()
        #Check irradiation
        self.assertTrue(len(rows) == num_irradiations)


class FluenceFactorListTest(SLSTestCase):
    """Test class fluence factor list."""

    fixtures = [
        'experiment_samples_archive.json',
        'boxes.json',
        'compound_elements.json',
        'compounds.json',
        'dosimeters.json',
        'elements.json',
        'experiment_categories.json',
        'experiments.json',
        'irradiations.json',
		'fluence_factors.json',
        'layers.json',
        'materials.json',
        'occupancies.json',
        'requested_fluences.json',
        'samples.json',
        'users.json'
        ]

    @classmethod
    def setUpClass(cls):
        """Ran once before all tests are run."""
        logging.disable(logging.CRITICAL)
        super().setUpClass()
        browser_type = 'chrome'
        if(browser_type == 'chrome'):
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--log-level=3')
            chrome_options.binary_location = '/usr/bin/chromium-browser'
            cls.browser = webdriver.Chrome(chrome_options=chrome_options)
        elif(browser_type == 'firefox'):
            firefox_options = webdriver.FirefoxOptions()
            firefox_options.set_headless()
            cls.browser = webdriver.Firefox(firefox_options=firefox_options)

        cls.factor_id = 1
        cls.irrad_table = 'IRRAD3'
        cls.irrad_table_update = 'IRRAD5'
        cls.value = 123400
        cls.dosimeter_dim = 10
        cls.url = cls.live_server_url + reverse('samples_manager:fluence_factors_list')

    @classmethod
    def tearDownClass(cls):
        """Ran once after all tests are run."""
        super().setUpClass()
        cls.browser.close()
        logging.disable(logging.NOTSET)

    def test_fluence_factor_incomplete_form(self):
        """Test incomplete fluence factor form."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "create")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-fluence-factor"]//h3[text() = "Create Fluence Factor"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)
        #Submit
        xpath = '//div[@id = "modal-fluence-factor"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        xpath = '//div[@id = "modal-fluence-factor"]//h3[text() = "Create Fluence Factor"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)

    def test_create_fluence_factor(self):
        """Test new fluence factor form."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        set_user_elements_per_page(self.browser, 20)
        xpath = '//div[@id="partial-template"]//tbody/tr'
        old_rows = self.browser.find_elements_by_xpath(xpath)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "create")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-fluence-factor"]//h3[text() = "Create Fluence Factor"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)
        #Fill data
        xpath = '//div[@id = "modal-fluence-factor"]//input[@name = "value"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [self.value, Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-fluence-factor"]//input[@name = "dosimeter_height"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [self.dosimeter_dim, Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-fluence-factor"]//input[@name = "dosimeter_width"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [self.dosimeter_dim, Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-fluence-factor"]//select[@name = "irrad_table"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [self.irrad_table, Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-fluence-factor"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        self.browser.execute_script('console.log(\'trs \', $(\'tr\').length);')
        xpath = '//div[@id="partial-template"]//tbody/tr'
        new_rows = self.browser.find_elements_by_xpath(xpath)
        self.assertTrue(len(old_rows) == (len(new_rows) - 1))
    
    def test_update_fluence_factor(self):
        """Test update fluence factor form."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        factor = FluenceFactor.objects.get(pk=self.factor_id)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@name = "checks[]" and @value="' + str(factor.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "update")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-fluence-factor"]//h3[text() = "Update Fluence Factor"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)
        #Fill data
        xpath = '//div[@id = "modal-fluence-factor"]//select[@name = "irrad_table"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [self.irrad_table_update, Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-fluence-factor"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        xpath = '//tr/td[text() = "' + self.irrad_table_update + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check factor
        self.assertTrue(element)

    def test_delete_fluence_factor(self):
        """Test fluence factor deletion."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        factor = FluenceFactor.objects.get(pk=self.factor_id)
        xpath = '//table/tbody/tr'
        old_rows = self.browser.find_elements_by_xpath(xpath)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@name = "checks[]" and @value="' + str(factor.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "delete")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-fluence-factor"]//h3[text() = "Confirm fluence factor deletion"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check factor update status form load
        self.assertTrue(element)
        xpath = '//div[@id = "modal-fluence-factor"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        #Check deleted factor
        xpath = '//table/tbody/tr'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        new_rows = self.browser.find_elements_by_xpath(xpath)
        self.assertTrue(len(old_rows) == (len(new_rows) + 1))

    def test_search_fluence_factor(self):
        """Test fluence factor search."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        factor = FluenceFactor.objects.get(pk=self.factor_id)
        xpath = '//div[@id = "filters-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@id = "search-box"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        #Enter factor to search
        data = {'action': 'send_keys', 'keys': self.irrad_table}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "search-submit")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click', 'out_delay': 0.5}
        delayed_action(element, data)
        xpath = '//tbody//tr'
        rows = self.browser.find_elements_by_xpath(xpath)
        #Check factor is first result
        self.assertTrue(len(rows) == 1)
        #Clear search
        xpath = '//button[contains(@id, "search-clear")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click', 'out_delay': 0.5}
        delayed_action(element, data)
        #Rows with more than one column to avoid "no results" row
        xpath = '//table/tbody/tr/td[2]/..'
        all_elements = FluenceFactor.objects.all()
        try:
            element = WebDriverWait(self.browser, WAIT_SECONDS).until(
                EC.visibility_of_element_located((By.XPATH, xpath)))
            rows = self.browser.find_elements_by_xpath(xpath)
            self.assertTrue(len(rows) == len(all_elements))
        except:
            self.assertTrue(len(all_elements) == 0)

    def test_empty_search_fluence_factor(self):
        """Test fluence factor empty search."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        xpath = '//div[@id = "filters-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "search")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//tbody//tr'
        rows = self.browser.find_elements_by_xpath(xpath)
        num_elements = FluenceFactor.objects.all().count()
        #Check factor
        self.assertTrue(len(rows) == num_elements)


class CompoundListTest(SLSTestCase):
    """Test class compounds list."""

    fixtures = [
        'experiment_samples_archive.json',
        'boxes.json',
        'compound_elements.json',
        'compounds.json',
        'dosimeters.json',
        'elements.json',
        'experiment_categories.json',
        'experiments.json',
        'irradiations.json',
		'fluence_factors.json',
        'layers.json',
        'materials.json',
        'occupancies.json',
        'requested_fluences.json',
        'samples.json',
        'users.json'
        ]

    @classmethod
    def setUpClass(cls):
        """Ran once before all tests are run."""
        logging.disable(logging.CRITICAL)
        super().setUpClass()
        browser_type = 'chrome'
        if(browser_type == 'chrome'):
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--log-level=3')
            chrome_options.binary_location = '/usr/bin/chromium-browser'
            cls.browser = webdriver.Chrome(chrome_options=chrome_options)
        elif(browser_type == 'firefox'):
            firefox_options = webdriver.FirefoxOptions()
            firefox_options.set_headless()
            cls.browser = webdriver.Firefox(firefox_options=firefox_options)

        cls.compound_id = 1
        cls.compound_with_associated_sample_id = 2
        cls.element_id_0 = 1
        cls.element_id_1 = 2
        cls.new_compound_name = 'aaa-test-compound'
        cls.url = cls.live_server_url + reverse('samples_manager:compounds_list')

    @classmethod
    def tearDownClass(cls):
        """Ran once after all tests are run."""
        super().setUpClass()
        cls.browser.close()
        logging.disable(logging.NOTSET)

    def test_compound_incomplete_form(self):
        """Test incomplete compound form."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "create")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//h3[text() = "Create Compound"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check compound form load
        self.assertTrue(element)
        #Submit
        xpath = '//div[@id = "modal-compound"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
           EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        xpath = '//div[@id = "modal-compound"]//h3[text() = "Create Compound"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check compound form load
        self.assertTrue(element)

    def test_create_compound(self):
        """Test compound creation."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        element_0 = Element.objects.get(pk=self.element_id_0)
        element_1 = Element.objects.get(pk=self.element_id_1)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "create")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//h3[text() = "Create Compound"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check compound form load
        self.assertTrue(element)
        xpath = '//div[@id = "modal-compound"]//input[@name = "name"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': self.new_compound_name}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//input[@name = "density"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': '0.0000001'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//a[@class = "ce-fs-add-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//select[@name = "ce-fs-0-element_type"]'\
            '/../../../..//a[@class = "ce-fs-delete-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//a[@class = "ce-fs-add-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//table/tbody/tr[contains(@class, "dynamic-formset-ce-fs")]'
        num_rows = len(self.browser.find_elements_by_xpath(xpath))
        xpath = '//div[@id = "modal-compound"]//select[@name = "ce-fs-' + str(num_rows-3) + '-element_type"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [str(element_0), Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//input[@name = "ce-fs-' + str(num_rows-3) + '-percentage"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': '10'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//select[@name = "ce-fs-' + str(num_rows-2) + '-element_type"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [str(element_1), Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//input[@name = "ce-fs-' + str(num_rows-2) + '-percentage"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': '90'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
           EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        xpath = '//div[@id = "partial-template-table"]//tbody/tr[1]/td[text() = "' + self.new_compound_name + '"]'
        #Wait time needed for WebDriverWait
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        self.assertTrue(element)


    def test_update_compound(self):
        """Test compound update."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        compound = Compound.objects.get(pk=self.compound_id)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@name = "checks[]" and @value="' + str(compound.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "update")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//h3[text() = "Update Compound"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check compound form load
        self.assertTrue(element)
        xpath = '//div[@id = "modal-compound"]//input[@name = "name"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': self.new_compound_name}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        xpath = '//td[text() = "' + self.new_compound_name + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check compound form load
        self.assertTrue(element)

    def test_delete_compound(self):
        """Test compound deletion."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        set_user_elements_per_page(self.browser, 20)
        hide_cookies_agreement(self.browser)
        compound = Compound.objects.get(pk=self.compound_id)
        xpath = '//table/tbody/tr'
        old_rows = self.browser.find_elements_by_xpath(xpath)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@name = "checks[]" and @value="' + str(compound.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "delete")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//h3[text() = "Confirm compound deletion"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)
        xpath = '//div[@id = "modal-compound"]//button[text() = "Delete"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        #Check deleted compound
        xpath = '//table/tbody/tr'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        new_rows = self.browser.find_elements_by_xpath(xpath)
        self.assertTrue(len(old_rows) == (len(new_rows) + 1))


    def test_delete_compound_with_associated_sample(self):
        """
        Test compound deletion when it has an associated sample. The 
        action should not be allowed.
        """
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        set_user_elements_per_page(self.browser, 20)
        hide_cookies_agreement(self.browser)
        compound = Compound.objects.get(pk=\
            self.compound_with_associated_sample_id)
        xpath = '//input[@name = "checks[]" and @value="' + str(compound.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "delete")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        self.assertTrue(element)

    def test_search_compound(self):
        """Test experiment user search."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        set_user_elements_per_page(self.browser, 50)
        hide_cookies_agreement(self.browser)
        xpath = '//div[@id = "filters-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@id = "search-box"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        #Enter user to search
        name = Compound.objects.get(pk=self.compound_id).name
        data = {'action': 'send_keys', 'keys': name}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "search")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//table/tbody/tr'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        rows = self.browser.find_elements_by_xpath(xpath)
        self.assertTrue(len(rows) == 1)
        #Clear search
        xpath = '//button[contains(@id, "search-clear")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click', 'out_delay': 0.5}
        delayed_action(element, data)
        #Rows with more than one column to avoid "no results" row
        xpath = '//table/tbody/tr/td[2]/..'
        all_elements = Compound.objects.all()
        try:
            element = WebDriverWait(self.browser, WAIT_SECONDS).until(
                EC.visibility_of_element_located((By.XPATH, xpath)))
            rows = self.browser.find_elements_by_xpath(xpath)
            self.assertTrue(len(rows) == len(all_elements))
        except:
            self.assertTrue(len(all_elements) == 0)

    def test_empty_search_compound(self):
        """Test experiment user empty search."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        xpath = '//table/tbody/tr'
        old_rows = self.browser.find_elements_by_xpath(xpath)
        xpath = '//div[@id = "filters-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "search")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//table/tbody/tr'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        new_rows = self.browser.find_elements_by_xpath(xpath)
        self.assertTrue(len(old_rows) == len(new_rows))

class DosimeterListTest(SLSTestCase):
    """Test class dosimeter list."""

    fixtures = [
        'experiment_samples_archive.json',
        'boxes.json',
        'compound_elements.json',
        'compounds.json',
        'dosimeters.json',
        'elements.json',
        'experiment_categories.json',
        'experiments.json',
        'irradiations.json',
		'fluence_factors.json',
        'layers.json',
        'materials.json',
        'occupancies.json',
        'requested_fluences.json',
        'samples.json',
        'users.json'
        ]

    @classmethod
    def setUpClass(cls):
        """Ran once before all tests are run."""
        logging.disable(logging.CRITICAL)
        super().setUpClass()
        browser_type = 'chrome'
        if(browser_type == 'chrome'):
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--log-level=3')
            chrome_options.binary_location = '/usr/bin/chromium-browser'
            cls.browser = webdriver.Chrome(chrome_options=chrome_options)
        elif(browser_type == 'firefox'):
            firefox_options = webdriver.FirefoxOptions()
            firefox_options.set_headless()
            cls.browser = webdriver.Firefox(firefox_options=firefox_options)

        cls.experiment_id = 1
        cls.dosimeter_id = 1
        cls.dosimeter_with_children_id = 1
        cls.dosimeter_without_children_id = 2
        cls.dosimeter_id_details = 1
        cls.new_dosimeter_name = 'DOS-004009'
        cls.new_dosimeter_child_name = 'DOS-004001.999'
        cls.user_id = 1
        cls.printer_name = 'irrad-eam-printer'
        cls.printer_template_name = 'small_qr'
        cls.url = cls.live_server_url + reverse('samples_manager:'\
            'dosimeters_list')

    @classmethod
    def tearDownClass(cls):
        """Ran once after all tests are run."""
        super().setUpClass()
        cls.browser.close()
        logging.disable(logging.NOTSET)

    def test_dosimeter_incomplete_form(self):
        """Test incomplete dosimeter form."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "create")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check dosimeter form load
        self.assertTrue(element)
        #Next page navigation
        xpath = '//div[@id = "step-tab-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        #Submit dosimeter
        xpath = '//div[@id = "step-2"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check dosimeter form load
        self.assertTrue(element)

    def test_create_dosimeter(self):
        """Test experiment creation."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        user = User.objects.get(pk=self.user_id)
        parent_dosimeter = Dosimeter.objects.get(pk=self.dosimeter_with_children_id)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "create")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check dosimeter form load
        self.assertTrue(element)
        #Input data page 1
        xpath = '//div[@id = "step-1"]//input[@name = "dos_id"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': self.new_dosimeter_child_name}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]//input[@name = "length"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': '0.000001'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]//input[@name = "height"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': '0.000001'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]//input[@name = "width"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': '0.000001'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]//input[@name = "weight"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': '0.000001'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]//input[@name = "foils_number"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': '1'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]//select[@name = "dos_type"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['Aluminium', Keys.ENTER]}
        delayed_action(element, data)
        #Next page navigation
        xpath = '//div[@id = "step-tab-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        #Input data page 2
        xpath = '//div[@id = "step-2"]//select[@name = "responsible"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [user.email, Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//select[@name = "current_location"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['14/R-012', Keys.ENTER], 'in_delay': 0.5}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]//select[@name = "parent_dosimeter"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [parent_dosimeter.dos_id, Keys.ENTER]}
        delayed_action(element, data)
        #Submit dosimeter
        xpath = '//div[@id = "step-2"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        xpath = '//tr/td[text() = "' + self.new_dosimeter_child_name + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check new dosimeter
        self.assertTrue(element)

    def test_create_dosimeter_form_navigation(self):
        """Test dosimeter creation form navigation."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "create")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form page one load
        self.assertTrue(element)
        xpath = '//div[@id = "step-tab-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check tab link to page two
        self.assertTrue(element)
        xpath = '//div[@id = "step-tab-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check tab link to page one
        self.assertTrue(element)
        xpath = '//div[@id = "step-1"]//button[contains(text(),"Next")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check next button to page two
        self.assertTrue(element)
        xpath = '//div[@id = "step-2"]//button[contains(text(),"Previous")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check previous button to page three
        self.assertTrue(element)

    def test_update_dosimeter(self):
        """Test update dosimeter button loads form."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        dosimeter = Dosimeter.objects.get(pk=self.dosimeter_id)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@name = "checks[]" and @value="' + str(dosimeter.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "update")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check dosimeter form load
        self.assertTrue(element)
        #Input data page 1
        xpath = '//div[@id = "step-1"]//input[@name = "dos_id"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': self.new_dosimeter_name}
        delayed_action(element, data)
        #Next page navigation
        xpath = '//div[@id = "step-tab-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        #Submit dosimeter
        xpath = '//div[@id = "step-2"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        xpath = '//tr/td[text() = "' + self.new_dosimeter_name + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check new dosimeter
        self.assertTrue(element)

    def test_update_dosimeter_form_navigation(self):
        """Test dosimeter update form navigation."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        dosimeter = Dosimeter.objects.get(pk=self.dosimeter_id)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@name = "checks[]" and @value="' + str(dosimeter.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "update")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check dosimeter form load
        self.assertTrue(element)
        xpath = '//div[@id = "step-tab-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check tab link to page two
        self.assertTrue(element)
        xpath = '//div[@id = "step-tab-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check tab link to page one
        self.assertTrue(element)
        xpath = '//div[@id = "step-1"]//button[contains(text(),"Next")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check next button to page two
        self.assertTrue(element)
        xpath = '//div[@id = "step-2"]//button[contains(text(),"Previous")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check previous button to page three
        self.assertTrue(element)

    def test_clone_dosimeter(self):
        """Test dosimeter cloning."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        parent_dosimeter = Dosimeter.objects.get(pk=self.dosimeter_with_children_id)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@name = "checks[]" and @value="' + str(parent_dosimeter.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "clone")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check dosimeter form load
        self.assertTrue(element)
        #Input data page 1
        xpath = '//div[@id = "step-1"]//input[@name = "dos_id"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': self.new_dosimeter_child_name}
        delayed_action(element, data)
        #Next page navigation
        xpath = '//div[@id = "step-tab-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        #Input data page 2
        xpath = '//div[@id = "step-2"]//select[@name = "parent_dosimeter"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [parent_dosimeter.dos_id, Keys.ENTER]}
        delayed_action(element, data)
        #Submit dosimeter
        xpath = '//div[@id = "step-2"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        xpath = '//tr/td[text() = "' + self.new_dosimeter_child_name + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check new dosimeter
        self.assertTrue(element)

    def test_clone_dosimeter_form_navigation(self):
        """Test dosimeter cloning form navigation."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        dosimeter = Dosimeter.objects.get(pk=self.dosimeter_id)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@name = "checks[]" and @value="' + str(dosimeter.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "clone")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check dosimeter form load
        self.assertTrue(element)
        xpath = '//div[@id = "step-tab-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check tab link to page two
        self.assertTrue(element)
        xpath = '//div[@id = "step-tab-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check tab link to page one
        self.assertTrue(element)
        xpath = '//div[@id = "step-1"]//button[contains(text(),"Next")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-2"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check next button to page two
        self.assertTrue(element)
        xpath = '//div[@id = "step-2"]//button[contains(text(),"Previous")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "step-1"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check previous button to page three
        self.assertTrue(element)
    
    @tag('skip')
    def test_print_dosimeter(self):
        """Test print dosimeter."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        dosimeter = Dosimeter.objects.get(pk=self.dosimeter_id)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        xpath = '//input[@name = "checks[]" and @value="' + str(dosimeter.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "print")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-dosimeter"]//h3[contains(text(), "Print")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//div[@id = "modal-dosimeter"]//select[@id = "id_printer"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [self.printer_name, Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-dosimeter"]//select[@id = "id_template"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [self.printer_template_name, Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-dosimeter"]//input[@id = "id_num_copies"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['0', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-dosimeter"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        alert = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        text = alert.text
        self.browser.switch_to.alert.accept()
        self.assertTrue('success' in text)

    def test_delete_dosimeter_and_children(self):
        """Test dosimeter deletion including children."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        set_user_elements_per_page(self.browser, 20)
        xpath = '//table/tbody/tr'
        old_rows = self.browser.find_elements_by_xpath(xpath)
        dosimeter = Dosimeter.objects.get(pk=self.dosimeter_with_children_id)
        xpath = '//td[contains(text(), "' + dosimeter.dos_id + '")]'
        related_dosimeters = self.browser.find_elements_by_xpath(xpath)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@name = "checks[]" and @value="' + str(dosimeter.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "delete")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-dosimeter"]//h3[text() = "Confirm dosimeter deletion"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)
        xpath = '//div[@id = "modal-dosimeter"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        #Check deleted dosimeter
        xpath = '//table/tbody/tr'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        new_rows = self.browser.find_elements_by_xpath(xpath)
        self.assertTrue(len(old_rows) == (len(new_rows) + len(related_dosimeters)))

    def test_delete_dosimeter(self):
        """Test dosimeter deletion."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        set_user_elements_per_page(self.browser, 20)
        xpath = '//table/tbody/tr'
        old_rows = self.browser.find_elements_by_xpath(xpath)
        dosimeter = Dosimeter.objects.get(pk=self.dosimeter_without_children_id)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@name = "checks[]" and @value="' + str(dosimeter.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "delete")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-dosimeter"]//h3[text() = "Confirm dosimeter deletion"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)
        xpath = '//div[@id = "modal-dosimeter"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        #Check deleted dosimeter
        xpath = '//table/tbody/tr'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        new_rows = self.browser.find_elements_by_xpath(xpath)
        self.assertTrue(len(old_rows) == (len(new_rows) + 1))

    def test_details_dosimeter(self):
        """Test dosimeter details page."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        dosimeter = Dosimeter.objects.get(pk=self.dosimeter_id_details)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        xpath = '//input[@name = "checks[]" and @value="' + str(dosimeter.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "details")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[contains(@class, \'breadcrumb\')]//div['\
            'contains(@class, \'active\') and contains(text(), '\
                '"' + dosimeter.dos_id + '")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        self.assertTrue(element)

    def test_new_dosimeter_ids(self):
        """Test new dosimeter ids function."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        set_user_elements_per_page(self.browser, 20)
        xpath = '//table/tbody/tr'
        old_rows = self.browser.find_elements_by_xpath(xpath)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "ids")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-dosimeter"]//h3[text() = "Create dosimeter entries"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)
        num = 3
        xpath = '//div[@id = "modal-dosimeter"]//input[@name = "num_ids"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': num}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-dosimeter"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        #Check deleted dosimeter
        xpath = '//table/tbody/tr'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        new_rows = self.browser.find_elements_by_xpath(xpath)
        self.assertTrue(len(old_rows) == (len(new_rows) - num))

    def test_read_infoream_dosimeter(self):
        """Test read dosimeter information in infoream."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        set_user_elements_per_page(self.browser, 20)
        dosimeter = Dosimeter.objects.get(pk=self.dosimeter_id)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@name = "checks[]" and @value="' + str(dosimeter.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "read-infoream")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[contains(@class, \'breadcrumb\')]//div['\
            'contains(@class, \'active\') and contains(text(), '\
                '"inforEAM details ' + dosimeter.dos_id + '")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check next button to page three
        self.assertTrue(element)

    def test_write_infoream_dosimeter(self):
        """Test write dosimeter information in infoream."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        set_user_elements_per_page(self.browser, 20)
        dosimeter = Dosimeter.objects.get(pk=self.dosimeter_id)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@name = "checks[]" and @value="' + str(dosimeter.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "write-infoream")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-dosimeter"]//h3[contains(text(), "Confirm")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)
        xpath = '//div[@id = "modal-dosimeter"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        alert = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        text = alert.text
        self.browser.switch_to.alert.accept()
        self.assertTrue('success' in text)

    def test_search_dosimeter(self):
        """Test dosimeter search."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        set_user_elements_per_page(self.browser, 20)
        hide_cookies_agreement(self.browser)
        dosimeter = Dosimeter.objects.get(pk=2)
        xpath = '//div[@id = "filters-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@id = "search-box"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        #Enter experiment to search
        data = {'action': 'send_keys', 'keys': str(dosimeter.dos_id)}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "search-submit")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        # Delay needed to observe change in table rows.
        data = {'action': 'click', 'out_delay': 0.5}
        delayed_action(element, data)
        xpath = '//table/tbody/tr'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        rows = self.browser.find_elements_by_xpath(xpath)
        self.assertTrue(len(rows) == 1)
        #Clear search
        xpath = '//button[contains(@id, "search-clear")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click', 'out_delay': 0.5}
        delayed_action(element, data)
        #Rows with more than one column to avoid "no results" row
        xpath = '//table/tbody/tr/td[2]/..'
        all_elements = Dosimeter.objects.all()
        try:
            element = WebDriverWait(self.browser, WAIT_SECONDS).until(
                EC.visibility_of_element_located((By.XPATH, xpath)))
            rows = self.browser.find_elements_by_xpath(xpath)
            self.assertTrue(len(rows) == len(all_elements))
        except:
            self.assertTrue(len(all_elements) == 0)

    def test_empty_search_dosimeter(self):
        """Test dosimeter empty search."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        xpath = '//div[@id = "filters-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//table/tbody/tr'
        old_rows = self.browser.find_elements_by_xpath(xpath)
        xpath = '//button[contains(@id, "search")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//table/tbody/tr'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        new_rows = self.browser.find_elements_by_xpath(xpath)
        self.assertTrue(len(old_rows) == len(new_rows))


class UserListTest(SLSTestCase):
    """Test class user list."""

    fixtures = [
        'experiment_samples_archive.json',
        'boxes.json',
        'compound_elements.json',
        'compounds.json',
        'dosimeters.json',
        'elements.json',
        'experiment_categories.json',
        'experiments.json',
        'irradiations.json',
		'fluence_factors.json',
        'layers.json',
        'materials.json',
        'occupancies.json',
        'requested_fluences.json',
        'samples.json',
        'users.json'
        ]

    @classmethod
    def setUpClass(cls):
        """Ran once before all tests are run."""
        logging.disable(logging.CRITICAL)
        super().setUpClass()
        browser_type = 'chrome'
        if(browser_type == 'chrome'):
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--log-level=3')
            chrome_options.binary_location = '/usr/bin/chromium-browser'
            cls.browser = webdriver.Chrome(chrome_options=chrome_options)
        elif(browser_type == 'firefox'):
            firefox_options = webdriver.FirefoxOptions()
            firefox_options.set_headless()
            cls.browser = webdriver.Firefox(firefox_options=firefox_options)

        cls.experiment_without_users_id = 2
        cls.experiment_with_users_id = 1
        cls.user_admin_id = 1
        cls.user_id = 2
        cls.url = cls.live_server_url + reverse('samples_manager:'\
            'users_list')
        cls.experiment_without_users_url = cls.live_server_url + reverse('samples_manager:'\
            'experiment_users_list', args=[cls.experiment_without_users_id])
        cls.experiment_with_users_url = cls.live_server_url + reverse('samples_manager:'\
            'experiment_users_list', args=[cls.experiment_with_users_id])

    @classmethod
    def tearDownClass(cls):
        """Ran once after all tests are run."""
        super().setUpClass()
        cls.browser.close()
        logging.disable(logging.NOTSET)

    def test_user_incomplete_form(self):
        """Test incomplete user form."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "create")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-user"]//h3[text() = "Create User"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check user form load
        self.assertTrue(element)
        #Submit user
        xpath = '//div[@id = "modal-user"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        xpath = '//div[@id = "modal-user"]//h3[text() = "Create User"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check user form load
        self.assertTrue(element)

    def test_create_user(self):
        """Test user creation."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "create")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-user"]//h3[text() = "Create User"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check user form load
        self.assertTrue(element)
        #Input data
        email = 'test-user-temp@gmail.com'
        xpath = '//div[@id = "modal-user"]//input[@name = "name"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': 'Test'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-user"]//input[@name = "surname"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': 'User  Temp'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-user"]//input[@name = "email"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': email}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-user"]//input[@name = "telephone"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': '1234'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-user"]//select[@name = "role"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['User', Keys.ENTER]}
        delayed_action(element, data)
        #Submit user
        xpath = '//div[@id = "modal-user"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        xpath = '//tr/td[text() = "' + email + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check user email
        self.assertTrue(element)

    def test_update_user(self):
        """Test update user button loads form."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        user = User.objects.get(pk=1)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@name = "checks[]" and @value="' + str(user.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "update")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-user"]//h3[text() = "Update User"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check user form load
        self.assertTrue(element)
        #Input data page 1
        email = 'test-user-temp-updated@gmail.com'
        xpath = '//div[@id = "modal-user"]//input[@name = "email"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': email}
        delayed_action(element, data)
        #Submit user
        xpath = '//div[@id = "modal-user"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        xpath = '//tr/td[text() = "' + email + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check new user title
        self.assertTrue(element)

    def test_delete_user(self):
        """Test user deletion."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        xpath = '//table/tbody/tr'
        old_rows = self.browser.find_elements_by_xpath(xpath)
        user = User.objects.get(pk=self.user_id)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@name = "checks[]" and @value="' + str(user.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "delete")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-user"]//h3[text() = "Confirm user deletion"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)
        xpath = '//div[@id = "modal-user"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        #Check deleted user
        xpath = '//table/tbody/tr//input[@type="checkbox"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        new_rows = self.browser.find_elements_by_xpath(xpath)
        self.assertTrue(len(old_rows) == (len(new_rows) + 1))

    def test_experiment_user_incomplete_form(self):
        """Test incomplete experiment user form."""
        self.browser.get(self.experiment_with_users_url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "add")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-user"]//h3[text() = "Add User"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check user form load
        self.assertTrue(element)
        #Submit user
        xpath = '//div[@id = "modal-user"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        xpath = '//div[@id = "modal-user"]//h3[text() = "Add User"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check user form load
        self.assertTrue(element)

    def test_add_experiment_user(self):
        """Test experiment user adding."""
        self.browser.get(self.experiment_without_users_url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "add")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-user"]//h3[text() = "Add User"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check user form load
        self.assertTrue(element)
        #Input data
        email = User.objects.get(pk=self.user_id).email
        xpath = '//div[@id = "modal-user"]//input[@name = "email"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': email}
        delayed_action(element, data)
        #Submit user
        xpath = '//div[@id = "modal-user"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        xpath = '//tr/td[text() = "' + email + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check user email
        self.assertTrue(element)

    def test_remove_experiment_user(self):
        """Test experiment user removal."""
        self.browser.get(self.experiment_with_users_url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        xpath = '//table/tbody/tr'
        old_rows = self.browser.find_elements_by_xpath(xpath)
        user = User.objects.get(pk=self.user_id)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@name = "checks[]" and @value="' + str(user.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "remove")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-user"]//h3[text() = "Confirm user removal"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)
        xpath = '//div[@id = "modal-user"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        #Check deleted user
        xpath = '//table/tbody/tr//input[@type="checkbox"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        new_rows = self.browser.find_elements_by_xpath(xpath)
        self.assertTrue(len(old_rows) == (len(new_rows) + 1))

    def test_search_user(self):
        """Test user search."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        user = User.objects.get(pk=1)
        xpath = '//div[@id = "filters-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@id = "search-box"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        #Enter user to search
        data = {'action': 'send_keys', 'keys': str(user.email)}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "search")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//table/tbody/tr'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        rows = self.browser.find_elements_by_xpath(xpath)
        self.assertTrue(len(rows) == 1)
        #Clear search
        xpath = '//button[contains(@id, "search-clear")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click', 'out_delay': 0.5}
        delayed_action(element, data)
        #Rows with more than one column to avoid "no results" row
        xpath = '//table/tbody/tr/td[2]/..'
        all_elements = User.objects.all()
        try:
            element = WebDriverWait(self.browser, WAIT_SECONDS).until(
                EC.visibility_of_element_located((By.XPATH, xpath)))
            rows = self.browser.find_elements_by_xpath(xpath)
            self.assertTrue(len(rows) == len(all_elements))
        except:
            self.assertTrue(len(all_elements) == 0)

    def test_empty_search_user(self):
        """Test user empty search."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        xpath = '//table/tbody/tr'
        old_rows = self.browser.find_elements_by_xpath(xpath)
        xpath = '//div[@id = "filters-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "search")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//table/tbody/tr'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        new_rows = self.browser.find_elements_by_xpath(xpath)
        self.assertTrue(len(old_rows) == len(new_rows))

    def test_search_experiment_user(self):
        """Test experiment user search."""
        self.browser.get(self.experiment_with_users_url)
        experiment = Experiment.objects.get(pk=self.experiment_with_users_id)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        xpath = '//div[@id = "filters-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@id = "search-box"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        #Enter user to search
        email = User.objects.get(pk=self.user_id).email
        data = {'action': 'send_keys', 'keys': str(email)}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "search")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//table/tbody/tr'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        rows = self.browser.find_elements_by_xpath(xpath)
        self.assertTrue(len(rows) == 1)
        #Clear search
        xpath = '//button[contains(@id, "search-clear")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click', 'out_delay': 0.5}
        delayed_action(element, data)
        #Rows with more than one column to avoid "no results" row
        xpath = '//table/tbody/tr/td[2]/..'
        all_elements = get_experiment_users(experiment)
        try:
            element = WebDriverWait(self.browser, WAIT_SECONDS).until(
                EC.visibility_of_element_located((By.XPATH, xpath)))
            rows = self.browser.find_elements_by_xpath(xpath)
            self.assertTrue(len(rows) == len(all_elements))
        except:
            self.assertTrue(len(all_elements) == 0)

    def test_empty_search_experiment_user(self):
        """Test experiment user empty search."""
        self.browser.get(self.experiment_with_users_url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        xpath = '//table/tbody/tr'
        old_rows = self.browser.find_elements_by_xpath(xpath)
        xpath = '//div[@id = "filters-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "search")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//table/tbody/tr'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        new_rows = self.browser.find_elements_by_xpath(xpath)
        self.assertTrue(len(old_rows) == len(new_rows))


class DosimetryResultListTest(SLSTestCase):
    """Test class dosimetry results list."""

    fixtures = [
        'experiment_samples_archive.json',
        'boxes.json',
        'compound_elements.json',
        'compounds.json',
        'dosimeters.json',
        'elements.json',
        'experiment_categories.json',
        'experiments.json',
        'irradiations.json',
		'fluence_factors.json',
        'layers.json',
        'materials.json',
        'occupancies.json',
        'requested_fluences.json',
        'samples.json',
        'users.json'
        ]

    @classmethod
    def setUpClass(cls):
        """Ran once before all tests are run."""
        logging.disable(logging.CRITICAL)
        super().setUpClass()
        browser_type = 'chrome'
        if(browser_type == 'chrome'):
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--log-level=3')
            chrome_options.binary_location = '/usr/bin/chromium-browser'
            cls.browser = webdriver.Chrome(chrome_options=chrome_options)
        elif(browser_type == 'firefox'):
            firefox_options = webdriver.FirefoxOptions()
            firefox_options.set_headless()
            cls.browser = webdriver.Firefox(firefox_options=firefox_options)

        cls.experiment_id = 1
        cls.url = cls.live_server_url + reverse('samples_manager:'\
            'dosimetry_results_list')

    @classmethod
    def tearDownClass(cls):
        """Ran once after all tests are run."""
        super().setUpClass()
        cls.browser.close()
        logging.disable(logging.NOTSET)

    def test_search_dosimetry_result(self):
        """Test dosimetry result search."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        irradiation = Irradiation.objects.get(pk=4)
        xpath = '//div[@id = "filters-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@id = "search-box"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        #Enter user to search
        data = {'action': 'send_keys', 'keys': str(irradiation.dosimeter.dos_id)}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "search-submit")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click', 'out_delay': 0.5}
        delayed_action(element, data)
        #Rows with more than one column to avoid "no results" row
        xpath = '//table/tbody/tr/td[contains(text(), "' + irradiation.dosimeter.dos_id + '")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        rows = self.browser.find_elements_by_xpath(xpath)
        self.assertTrue(len(rows) == 1)
        #Clear search
        xpath = '//button[contains(@id, "search-clear")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click', 'out_delay': 0.5}
        delayed_action(element, data)
        #Rows with more than one column to avoid "no results" row
        xpath = '//table/tbody/tr/td[2]/..'
        all_elements = Irradiation.objects.filter(Q(status='Completed'))
        try:
            element = WebDriverWait(self.browser, WAIT_SECONDS).until(
                EC.visibility_of_element_located((By.XPATH, xpath)))
            rows = self.browser.find_elements_by_xpath(xpath)
            self.assertTrue(len(rows) == len(all_elements))
        except:
            self.assertTrue(len(all_elements) == 0)


    def test_empty_search_dosimetry_result(self):
        """Test dosimetry result empty search."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        xpath = '//table/tbody/tr'
        old_rows = self.browser.find_elements_by_xpath(xpath)
        xpath = '//div[@id = "filters-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "search")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//table/tbody/tr'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        new_rows = self.browser.find_elements_by_xpath(xpath)
        self.assertTrue(len(old_rows) == len(new_rows))


class PaginationTest(SLSTestCase):
    """Test pages pagination."""

    fixtures = [
        'experiment_samples_archive.json',
        'boxes.json',
        'compound_elements.json',
        'compounds.json',
        'dosimeters.json',
        'elements.json',
        'experiment_categories.json',
        'experiments.json',
        'irradiations.json',
		'fluence_factors.json',
        'layers.json',
        'materials.json',
        'occupancies.json',
        'requested_fluences.json',
        'samples.json',
        'users.json'
        ]

    @classmethod
    def setUpClass(cls):
        """Ran once before all tests are run."""
        logging.disable(logging.CRITICAL)
        super().setUpClass()
        browser_type = 'chrome'
        if(browser_type == 'chrome'):
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--log-level=3')
            chrome_options.binary_location = '/usr/bin/chromium-browser'
            cls.browser = webdriver.Chrome(chrome_options=chrome_options)
        elif(browser_type == 'firefox'):
            firefox_options = webdriver.FirefoxOptions()
            firefox_options.set_headless()
            cls.browser = webdriver.Firefox(firefox_options=firefox_options)

        cls.experiment_id = 1
        cls.compound_id = 11
        cls.url = cls.live_server_url + reverse('samples_manager:'\
            'compounds_list')
        cls.elements_per_page_url = cls.live_server_url + \
            reverse('samples_manager:experiments_list')
        cls.index_url = cls.live_server_url + reverse('samples_manager:index')

    @classmethod
    def tearDownClass(cls):
        """Ran once after all tests are run."""
        super().setUpClass()
        cls.browser.close()
        logging.disable(logging.NOTSET)

    def test_last_item_deletion(self):
        """Test deletion of last and only item in list."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        set_user_elements_per_page(self.browser, 50)
        hide_cookies_agreement(self.browser)
        compound = Compound.objects.get(pk=self.compound_id)
        xpath = '//tbody//tr'
        num_rows = len(self.browser.find_elements_by_xpath(xpath))
        #Check if maximum number of rows is 11.
        self.assertTrue(num_rows == 11)
        #Switch to one element per page.
        set_user_elements_per_page(self.browser, 1)
        xpath = '//a[@class = "item" and contains(text(), "last")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//a[@class = "item active" and contains(text(), "11")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
        #Delete last and only item in list
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@name = "checks[]" and @value="' + str(compound.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "delete")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-compound"]//h3[text() = "Confirm compound deletion"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)
        xpath = '//div[@id = "modal-compound"]//button[text() = "Delete"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
         #Check correct page load of off limits page number to closest page.
        xpath = '//a[@class = "item active" and contains(text(), "10")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        self.assertTrue(element)
    
    def test_elements_per_page(self):
        """Test elements per page."""
        self.browser.get(self.elements_per_page_url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        set_user_elements_per_page(self.browser, 5)
        xpath = '//div[contains(@id, "partial-template-pagination-bottom")]'\
            '//div[contains(@class, "ui dropdown elements-per-page selection")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = xpath + '//div[@data-value = "50"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        self.browser.get(self.index_url)
        xpath = '//h1[text() = "IRRAD Data Manager"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        self.browser.get(self.elements_per_page_url)
        num_experiments = Experiment.objects.all().count()
        xpath = '//table/tbody/tr'
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        new_rows = self.browser.find_elements_by_xpath(xpath)
        self.assertTrue(len(new_rows) == num_experiments)

    def test_elements_per_page_filtered_list(self):
        """Test elements per page for filtered list."""
        self.browser.get(self.elements_per_page_url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        set_user_elements_per_page(self.browser, 5)
        xpath = '//div[@id = "filters-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@id = "search-box"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        #Enter user to search
        title = Experiment.objects.get(pk=self.experiment_id).title
        data = {'action': 'send_keys', 'keys': str(title)}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "search")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//table/tbody/tr'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        rows = self.browser.find_elements_by_xpath(xpath)
        self.assertTrue(len(rows) == 1)
        xpath = '//div[contains(@id, "partial-template-pagination-bottom")]'\
            '//div[contains(@class, "update-elements-per-page")]/div'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click', 'out_delay': 0.5}
        delayed_action(element, data)
        xpath = xpath + '//div[@data-value = "10"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click', 'out_delay': 0.5}
        delayed_action(element, data)
        xpath = '//table/tbody/tr'
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        new_rows = self.browser.find_elements_by_xpath(xpath)
        self.assertTrue(len(new_rows) == 1)


class BoxListTest(SLSTestCase):
    """Test class box list."""

    fixtures = [
        'experiment_samples_archive.json',
        'boxes.json',
        'compound_elements.json',
        'compounds.json',
        'dosimeters.json',
        'elements.json',
        'experiment_categories.json',
        'experiments.json',
        'irradiations.json',
		'fluence_factors.json',
        'layers.json',
        'materials.json',
        'occupancies.json',
        'requested_fluences.json',
        'samples.json',
        'users.json'
        ]

    @classmethod
    def setUpClass(cls):
        """Ran once before all tests are run."""
        logging.disable(logging.CRITICAL)
        super().setUpClass()
        browser_type = 'chrome'
        if(browser_type == 'chrome'):
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--log-level=3')
            chrome_options.binary_location = '/usr/bin/chromium-browser'
            cls.browser = webdriver.Chrome(chrome_options=chrome_options)
        elif(browser_type == 'firefox'):
            firefox_options = webdriver.FirefoxOptions()
            firefox_options.set_headless()
            cls.browser = webdriver.Firefox(firefox_options=firefox_options)

        cls.experiment_id = 1
        cls.box_id = 1
        cls.box_id_incorrect = 2
        cls.remove_sample_id_item = 1
        cls.new_sample_id_item = 2
        cls.new_dosimeter_id_item = 5
        cls.sample_with_box = 1
        cls.dosimeter_with_box = 1
        cls.dosimeter_id_incorrect_format = 3
        cls.user_id = 1
        cls.printer_name = 'irrad-eam-printer'
        cls.printer_template_name = 'small_qr'
        cls.new_box_name = 'BOX-000303'
        cls.url = cls.live_server_url + reverse('samples_manager:'\
            'boxes_list')
        cls.box_items_url = cls.live_server_url + reverse('samples_manager:'\
            'box_items_list', args=[cls.box_id])
        cls.dosimeters_url = cls.live_server_url + reverse('samples_manager:'\
            'dosimeters_list')
        cls.samples_url = cls.live_server_url + reverse('samples_manager:'\
            'experiment_samples_list', args=[cls.experiment_id])

    @classmethod
    def tearDownClass(cls):
        """Ran once after all tests are run."""
        super().setUpClass()
        cls.browser.close()
        logging.disable(logging.NOTSET)

    def test_box_incomplete_form(self):
        """Test incomplete box form."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "create")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-box"]//h3[text() = "Create Box"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check dosimeter form load
        self.assertTrue(element)
        #Submit dosimeter
        xpath = '//div[@id = "modal-box"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        xpath = '//div[@id = "modal-box"]//h3[text() = "Create Box"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check dosimeter form load
        self.assertTrue(element)

    def test_create_box(self):
        """Test box creation."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        set_user_elements_per_page(self.browser, 20)
        user = User.objects.get(pk=self.user_id)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "create")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-box"]//h3[text() = "Create Box"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check box form load
        self.assertTrue(element)
        #Input data
        xpath = '//div[@id = "modal-box"]//input[@name = "box_id"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': self.new_box_name}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-box"]//input[@name = "description"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': 'description'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-box"]//select[@name = "responsible"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [user.email, Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-box"]//select[@name = "current_location"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['14/R-012', Keys.ENTER], 'in_delay': 0.5}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-box"]//input[@name = "length"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': '100'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-box"]//input[@name = "height"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': '100'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-box"]//input[@name = "width"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': '100'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-box"]//input[@name = "weight"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': '100'}
        delayed_action(element, data)
        #Submit box
        xpath = '//div[@id = "modal-box"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        xpath = '//tr/td[text() = "' + self.new_box_name + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check new dosimeter
        self.assertTrue(element)

    def test_update_box(self):
        """Test update box button loads form."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        set_user_elements_per_page(self.browser, 20)
        box = Box.objects.get(pk=self.box_id)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@name = "checks[]" and @value="' + str(box.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "update")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-box"]//h3[text() = "Update Box"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check box form load
        self.assertTrue(element)
        #Input data
        xpath = '//div[@id = "modal-box"]//input[@name = "box_id"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': self.new_box_name}
        delayed_action(element, data)
        #Submit box
        xpath = '//div[@id = "modal-box"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        xpath = '//tr/td[text() = "' + self.new_box_name + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check new dosimeter
        self.assertTrue(element)

    def test_clone_box(self):
        """Test box cloning."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        set_user_elements_per_page(self.browser, 20)
        box = Box.objects.get(pk=self.box_id)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@name = "checks[]" and @value="' + str(box.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "clone")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-box"]//h3[text() = "Clone Box"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check box form load
        self.assertTrue(element)
        #Input data
        xpath = '//div[@id = "modal-box"]//input[@name = "box_id"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'clear'}
        delayed_action(element, data)
        data = {'action': 'send_keys', 'keys': self.new_box_name}
        delayed_action(element, data)
        #Submit box
        xpath = '//div[@id = "modal-box"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        xpath = '//tr/td[text() = "' + self.new_box_name + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check new dosimeter
        self.assertTrue(element)

    @tag('skip')
    def test_print_box(self):
        """Test print box."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        box = Box.objects.get(pk=self.box_id)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        xpath = '//input[@name = "checks[]" and @value="' + str(box.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "print")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-box"]//h3[contains(text(), "Print")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        self.assertTrue(element)
        xpath = '//div[@id = "modal-box"]//select[@id = "id_printer"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [self.printer_name, Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-box"]//select[@id = "id_template"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [self.printer_template_name, Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-box"]//input[@id = "id_num_copies"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['0', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-box"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        alert = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        text = alert.text
        self.browser.switch_to.alert.accept()
        self.assertTrue('success' in text)

    def test_delete_box(self):
        """Test box deletion."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        set_user_elements_per_page(self.browser, 20)
        xpath = '//table/tbody/tr'
        old_rows = self.browser.find_elements_by_xpath(xpath)
        box = Box.objects.get(pk=self.box_id)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@name = "checks[]" and @value="' + str(box.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "delete")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-box"]//h3[text() = "Confirm box deletion"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)
        xpath = '//div[@id = "modal-box"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        #Check deleted dosimeter
        xpath = '//table/tbody/tr//input[@type = "checkbox"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        new_rows = self.browser.find_elements_by_xpath(xpath)
        self.assertTrue(len(old_rows) == (len(new_rows) + 1))

    def test_details_box(self):
        """Test box details page."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        box = Box.objects.get(pk=self.box_id)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        xpath = '//input[@name = "checks[]" and @value="' + str(box.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "details")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[contains(@class, \'breadcrumb\')]//div['\
            'contains(@class, \'active\') and contains(text(), '\
                '"' + box.box_id + '")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        self.assertTrue(element)

    def test_assign_box_to_dosimeter(self):
        """Test assign box to dosimeter function."""
        self.browser.get(self.dosimeters_url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        set_user_elements_per_page(self.browser, 20)
        box_id = Box.objects.get(pk=self.box_id).box_id
        dosimeter = Dosimeter.objects.get(pk=self.new_dosimeter_id_item)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@name = "checks[]" and @value="' + str(dosimeter.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "box")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-dosimeter"]//h3[text() = "Assign Box"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)
        xpath = '//div[@id = "modal-dosimeter"]//select[@name = "box_id"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [box_id, Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-dosimeter"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        #Check assigned Box
        xpath = '//td[text() = "' + dosimeter.dos_id + '"]/../td[last() - 1]/a[text() = "' + box_id + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        self.assertTrue(element)

    def test_revoke_box_from_dosimeter(self):
        """Test revoking box from dosimeter by assigning 'None'."""
        self.browser.get(self.dosimeters_url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        set_user_elements_per_page(self.browser, 20)
        dosimeter = Dosimeter.objects.get(pk=self.dosimeter_with_box)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@name = "checks[]" and @value="' + str(dosimeter.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "box")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-dosimeter"]//h3[text() = "Assign Box"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)
        xpath = '//div[@id = "modal-dosimeter"]//select[@name = "box_id"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['No box', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-dosimeter"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        #Check box revokement
        xpath = '//td[text() = "' + dosimeter.dos_id + '"]/../td[last() - 1 and text() = "Not assigned"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        self.assertTrue(element)

    def test_assign_box_to_sample(self):
        """Test assign box to sample function."""
        self.browser.get(self.samples_url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        box_id = Box.objects.get(pk=self.box_id).box_id
        sample = Sample.objects.get(pk=self.new_sample_id_item)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@name = "checks[]" and @value="' + str(sample.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "box")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-sample"]//h3[text() = "Assign Box"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)
        xpath = '//div[@id = "modal-sample"]//select[@name = "box_id"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': [box_id, Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-sample"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        #Check assigned Box
        xpath = '//td[text() = "' + sample.set_id + '"]/../td[last()]/a[text() = "' + box_id + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        self.assertTrue(element)

    def test_revoke_box_from_sample(self):
        """Test revoking box from sample by assigning 'None'."""
        self.browser.get(self.samples_url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        set_user_elements_per_page(self.browser, 20)
        sample = Sample.objects.get(pk=self.sample_with_box)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@name = "checks[]" and @value="' + str(sample.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "box")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-sample"]//h3[text() = "Assign Box"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)
        xpath = '//div[@id = "modal-sample"]//select[@name = "box_id"]/../input'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': ['None', Keys.ENTER]}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-sample"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        #Check box revokement
        xpath = '//td[text() = "' + sample.set_id + '"]/../td[last() and text() = "Not assigned"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        self.assertTrue(element)

    def test_read_infoream_box(self):
        """Test read box information in infoream."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        set_user_elements_per_page(self.browser, 20)
        box = Box.objects.get(pk=self.box_id)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@name = "checks[]" and @value="' + str(box.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "read-infoream")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[contains(@class, \'breadcrumb\')]//div['\
            'contains(@class, \'active\') and contains(text(), '\
                '"inforEAM details ' + box.box_id + '")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check next button to page three
        self.assertTrue(element)

    def test_write_infoream_box(self):
        """Test write box information in infoream."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        set_user_elements_per_page(self.browser, 20)
        box = Box.objects.get(pk=self.box_id)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@name = "checks[]" and @value="' + str(box.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "write-infoream")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-box"]//h3[contains(text(), "Confirm")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)
        xpath = '//div[@id = "modal-box"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        alert = WebDriverWait(self.browser, (WAIT_SECONDS*4)).until(
            EC.alert_is_present())
        text = alert.text
        self.browser.switch_to.alert.accept()
        self.assertTrue('success' in text)

    def test_write_infoream_box_incorrect_id(self):
        """
        Test write box information in infoream 
        using incorrect id.
        """
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        set_user_elements_per_page(self.browser, 20)
        box = Box.objects.get(pk=self.box_id_incorrect)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@name = "checks[]" and @value="' + str(box.id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "write-infoream")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-box"]//h3[contains(text(), "Confirm")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)
        xpath = '//div[@id = "modal-box"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        alert = WebDriverWait(self.browser, (WAIT_SECONDS*4)).until(
            EC.alert_is_present())
        text = alert.text
        self.browser.switch_to.alert.accept()
        self.assertTrue('inforEAM ID doesn\'t exist.' in text)

    def test_search_box(self):
        """Test box search."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        box = Box.objects.get(pk=self.box_id)
        xpath = '//div[@id = "filters-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@id = "search-box"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        #Enter box to search
        data = {'action': 'send_keys', 'keys': str(box.box_id)}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "search")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//table/tbody/tr'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        rows = self.browser.find_elements_by_xpath(xpath)
        self.assertTrue(len(rows) == 1)

    def test_empty_search_box(self):
        """Test box empty search."""
        self.browser.get(self.url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        xpath = '//table/tbody/tr'
        old_rows = self.browser.find_elements_by_xpath(xpath)
        xpath = '//div[@id = "filters-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "search")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//table/tbody/tr'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        new_rows = self.browser.find_elements_by_xpath(xpath)
        self.assertTrue(len(old_rows) == len(new_rows))

    def test_add_box_item(self):
        """Test box item addition."""
        self.browser.get(self.box_items_url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        set_user_elements_per_page(self.browser, 20)
        sample = Sample.objects.get(pk=self.new_sample_id_item)
        dosimeter = Dosimeter.objects.get(pk=self.new_dosimeter_id_item)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "add")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-box-item"]//h3[text() = "Add items to box"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check box form load
        self.assertTrue(element)
        #Input data
        xpath = '//div[@id = "modal-box-item"]//a[@class = "i-fs-add-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-box-item"]//input[@name = "i-fs-0-box_item_id"]'\
            '/../../..//a[@class = "i-fs-delete-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-box-item"]//a[@class = "i-fs-add-row"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//table/tbody/tr[contains(@class, "dynamic-formset-i-fs")]'
        num_rows = len(self.browser.find_elements_by_xpath(xpath))
        xpath = '//div[@id = "modal-box-item"]//input[@name = "i-fs-' + str(num_rows-3) + '-box_item_id"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': sample.set_id}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-box-item"]//input[@name = "i-fs-' + str(num_rows-2) + '-box_item_id"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'send_keys', 'keys': dosimeter.dos_id}
        delayed_action(element, data)
        #Submit box items
        xpath = '//div[@id = "modal-box-item"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        xpath = '//tr/td/a[text() = "' + sample.set_id + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check new box item
        self.assertTrue(element)
        xpath = '//tr/td/a[text() = "' + dosimeter.dos_id + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check new box item
        self.assertTrue(element)

    def test_remove_box_item(self):
        """Test box item removal."""
        self.browser.get(self.box_items_url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        set_user_elements_per_page(self.browser, 20)
        xpath = '//table/tbody/tr'
        old_rows = self.browser.find_elements_by_xpath(xpath)
        sample = Sample.objects.get(pk=self.remove_sample_id_item)
        xpath = '//div[@id = "actions-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@name = "checks[]" and @value="' + str(sample.set_id) + '"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "remove")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//div[@id = "modal-box-item"]//h3[text() = "Confirm item removal"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        #Check form load
        self.assertTrue(element)
        xpath = '//div[@id = "modal-box-item"]//button[@type = "submit"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.alert_is_present())
        self.browser.switch_to.alert.accept()
        #Check removed item
        xpath = '//table/tbody/tr//input[@type="checkbox"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        new_rows = self.browser.find_elements_by_xpath(xpath)
        self.assertTrue(len(old_rows) == (len(new_rows) + 1))

    def test_search_box_item(self):
        """Test box item search."""
        self.browser.get(self.box_items_url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        set_user_elements_per_page(self.browser, 20)
        sample = Sample.objects.get(pk=self.remove_sample_id_item)
        xpath = '//div[@id = "filters-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//input[@id = "search-box"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        #Enter item to search
        data = {'action': 'send_keys', 'keys': str(sample.set_id)}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "search")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//table/tbody/tr'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        rows = self.browser.find_elements_by_xpath(xpath)
        self.assertTrue(len(rows) == 1)

    def test_empty_search_box_item(self):
        """Test box item empty search."""
        self.browser.get(self.box_items_url)
        set_user_cookies(self.browser, 'Admin')
        hide_cookies_agreement(self.browser)
        set_user_elements_per_page(self.browser, 20)
        xpath = '//table/tbody/tr'
        old_rows = self.browser.find_elements_by_xpath(xpath)
        xpath = '//div[@id = "filters-tab"]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//button[contains(@id, "search")]'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.element_to_be_clickable((By.XPATH, xpath)))
        data = {'action': 'click'}
        delayed_action(element, data)
        xpath = '//table/tbody/tr'
        element = WebDriverWait(self.browser, WAIT_SECONDS).until(
            EC.visibility_of_element_located((By.XPATH, xpath)))
        new_rows = self.browser.find_elements_by_xpath(xpath)
        self.assertTrue(len(old_rows) == len(new_rows))
