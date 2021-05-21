import logging
import time
import traceback

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException


def _value_to_key(search_dict: dict, value: int) -> str:
    for key, val in search_dict.items():
        if val == value:
            return key
    return ""


_number_dict = {
    "First": 1,
    "Second": 2,
    "Third": 3,
    "Fourth": 4,
    "Fifth": 5,
    "Sixth": 6,
    "Seventh": 7,
    "Eighth": 8,
    "Ninth": 9,
    "Tenth": 10
}


def _click(item):
    item.click()
    time.sleep(2)


# noinspection PyBroadException
class UofGSession:
    print_available = True

    def __init__(self,
                 driver,
                 email,
                 password,
                 login_address,
                 home_address,
                 basket_address):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(driver, options=chrome_options)
        self.email = email
        self.password = password
        self.login_address = login_address
        self.home_address = home_address
        self.basket_address = basket_address
        self.log = logging.getLogger("UofG")

    def __del__(self):
        self.driver.close()

    def empty_basket(self):
        self.log.info("Emptying basket...")
        try:
            self.driver.get(self.basket_address)
            _click(self.driver.find_element_by_id("sc-button-empty"))
            return self.driver.find_element_by_id(
                "sc-label-basket").text == "Your basket is empty."
        except:
            self.log.error("Error emptying basket...")
            self.log.error(traceback.format_exc())
            return False

    def go_home(self):
        try:
            self.driver.get(self.home_address)
            if not self.driver.title == "UofG Sport":
                self.log.critical("Cannot load page " + self.login_address)
                return False
            return True
        except:
            return False

    def login(self) -> bool:
        self.log.info("Attempting to log into {}".format(self.login_address))
        self.driver.get(self.login_address)
        if not self.driver.title == "UofG Sport":
            self.log.critical("Cannot load page " + self.login_address)
            return False

        community_login = self.driver.find_element_by_id("sc-button-userlogin")
        _click(community_login)

        email_input = self.driver.find_element_by_id("sc-input-email")
        email_input.clear()
        email_input.send_keys(self.email)

        pw1 = self.driver.find_element_by_id("sc-input-password1-container-id")
        pw1_input = pw1.find_element_by_id("sc-input-password1")
        pw1_label = str(pw1.find_element_by_tag_name("label").get_attribute(
            'textContent')).split(" ")
        pw1_index = _number_dict[pw1_label[0]]

        pw2 = self.driver.find_element_by_id("sc-input-password2-container-id")
        pw2_input = pw2.find_element_by_id("sc-input-password2")
        pw2_label = str(pw2.find_element_by_tag_name("label").get_attribute(
            'textContent')).split(" ")
        pw2_index = _number_dict[pw2_label[0]]

        pw3 = self.driver.find_element_by_id("sc-input-password3-container-id")
        pw3_input = pw3.find_element_by_id("sc-input-password3")
        pw3_label = str(pw3.find_element_by_tag_name("label").get_attribute(
            'textContent')).split(" ")
        pw3_index = _number_dict[pw3_label[0]]

        self.log.info(
            "Using letters {}({}), {}({}) and {}({}) from the password".format(
                pw1_index, _value_to_key(_number_dict, pw1_index),
                pw2_index, _value_to_key(_number_dict, pw2_index),
                pw3_index, _value_to_key(_number_dict, pw3_index)))

        pw1_input.send_keys(self.password[pw1_index - 1])
        pw2_input.send_keys(self.password[pw2_index - 1])
        pw3_input.send_keys(self.password[pw3_index - 1])

        _click(self.driver.find_element_by_id("sc-submit-login"))
        try:
            self.driver.find_element_by_id("sc-div-bookcaptiontext")
            return True
        except:
            self.log.error(
                "Failed to log in with credentials: {}:{}"
                    .format(self.email,
                            self.password))
            self.log.error(traceback.format_exc())
            return False

    def book_class(self, session_name: str) -> bool:
        self.log.info("Attempting booking: " + session_name)

        self.driver.find_element_by_id("sc-button-bookclass").click()

        try:
            days = self.driver.find_element_by_id(
                "sc-combo-classdate").find_elements_by_tag_name("option")
        except:
            self.log.error(
                "Error: No options found, unable to make booking")
            self.log.error(traceback.format_exc())
            return False

        last_day = days[-1]
        last_day.click()
        time.sleep(3)

        try:
            class_list = WebDriverWait(self.driver, 10).until(
                expected_conditions.presence_of_element_located(
                    (By.ID, "sc-listview-classlist"))
            )
        except:
            self.log.error(
                "Error: Class list unavailable, unable to make booking")
            self.log.error(traceback.format_exc())
            return False

        sessions = class_list.find_elements_by_tag_name("a")

        if self.print_available:
            self.log.info("Available sessions:")
        to_book = list()
        for sesh in sessions:
            if "FULLY BOOKED" not in sesh.text:
                if self.print_available:
                    self.log.info(sesh.text)
                if session_name in sesh.text:
                    to_book.append(sesh)
        self.print_available = False

        if len(to_book) > 1:
            self.log.error(
                "Too many sessions match session name: " + session_name)
            return False

        if len(to_book) < 1:
            self.log.error(
                "Error: No available sessions match session name: "
                + session_name)
            return False

        to_book[0].click()

        try:
            self.driver.find_element_by_id("sc-button-classdetail").click()
            self.driver.find_element_by_id("sc-button-classdetail").click()
            self.driver.find_element_by_id("sc-button-confirm").click()
        except:
            self.log.error("Confirming booking failed")
            self.log.error(traceback.format_exc())
            return False

        try:
            confirmed = self.driver.find_element_by_id("sc-div-sentemailtext")
            return confirmed is not None
        except:
            self.log.error("Error when confirming booking, assuming failed.")
            self.log.error(traceback.format_exc())
            self.empty_basket()
            return False
