import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


def value_to_key(search_dict: dict, value: int) -> str:
    for key, val in search_dict.items():
        if val == value:
            return key
    return ""


# noinspection PyBroadException
class UofGSession:
    number_dict = {
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

    def __init__(self, driver, email, password, login_address, home_address):
        self.driver = webdriver.Chrome(driver)
        self.email = email
        self.password = password
        self.login_address = login_address
        self.home_address = home_address
        self.log = logging.getLogger("UofG")

    def __del__(self):
        self.driver.close()

    def go_home(self):
        self.driver.get(self.home_address)
        if not self.driver.title == "UofG Sport":
            self.log.critical("Cannot load page " + self.login_address)
            return False
        return True

    def login(self) -> bool:
        self.log.info("Attempting to log into {}".format(self.login_address))
        self.driver.get(self.login_address)
        if not self.driver.title == "UofG Sport":
            self.log.critical("Cannot load page " + self.login_address)
            return False

        community_login = self.driver.find_element_by_id("sc-button-userlogin")
        community_login.click()

        email_input = self.driver.find_element_by_id("sc-input-email")
        email_input.clear()
        email_input.send_keys(self.email)

        pw1 = self.driver.find_element_by_id("sc-input-password1-container-id")
        pw1_input = pw1.find_element_by_id("sc-input-password1")
        pw1_label = str(pw1.find_element_by_tag_name("label").get_attribute(
            'textContent')).split(" ")
        pw1_index = self.number_dict[pw1_label[0]]

        pw2 = self.driver.find_element_by_id("sc-input-password2-container-id")
        pw2_input = pw2.find_element_by_id("sc-input-password2")
        pw2_label = str(pw2.find_element_by_tag_name("label").get_attribute(
            'textContent')).split(" ")
        pw2_index = self.number_dict[pw2_label[0]]

        pw3 = self.driver.find_element_by_id("sc-input-password3-container-id")
        pw3_input = pw3.find_element_by_id("sc-input-password3")
        pw3_label = str(pw3.find_element_by_tag_name("label").get_attribute(
            'textContent')).split(" ")
        pw3_index = self.number_dict[pw3_label[0]]

        self.log.info(
            "Using letters {}({}), {}({}) and {}({}) from the password".format(
                pw1_index, value_to_key(self.number_dict, pw1_index),
                pw2_index, value_to_key(self.number_dict, pw2_index),
                pw3_index, value_to_key(self.number_dict, pw3_index)))

        pw1_input.send_keys(self.password[pw1_index - 1])
        pw2_input.send_keys(self.password[pw2_index - 1])
        pw3_input.send_keys(self.password[pw3_index - 1])

        self.driver.find_element_by_id("sc-submit-login").click()
        try:
            self.driver.find_element_by_id("sc-div-bookcaptiontext")
            return True
        except:
            self.log.error(
                "Failed to log in with credentials: {}:{}"
                    .format(self.email,
                            self.password))
            return False

    def book_class(self, session_name: str) -> bool:
        self.log.info("Attempting booking: " + session_name)

        book = self.driver.find_element_by_id("sc-button-bookclass")
        book.click()

        try:
            days = self.driver.find_element_by_id(
                "sc-combo-classdate").find_elements_by_tag_name("option")
        except:
            self.log.error(
                "Error: No options found, unable to make booking")
            return False

        last_day = days[-1]
        last_day.click()

        try:
            class_list = WebDriverWait(self.driver, 10).until(
                expected_conditions.presence_of_element_located(
                    (By.ID, "sc-listview-classlist"))
            )
        except:
            self.log.error(
                "Error: Class list unavailable, unable to make booking")
            return False

        sessions = class_list.find_elements_by_tag_name("a")

        self.log.info("Available sessions:")
        to_book = list()
        for sesh in sessions:
            if "FULLY BOOKED" not in sesh.text:
                self.log.info(sesh.text)
                if session_name in sesh.text:
                    to_book.append(sesh)

        if len(to_book) > 1:
            self.log.error(
                "Too many sessions match session name: " + session_name)
            return False

        if len(to_book) < 1:
            self.log.error(
                "Error: No available sessions match session name: "
                + session_name)
            return False

        var = to_book[0]
        var.click()

        self.driver.find_element_by_id("sc-button-classdetail").click()
        self.driver.find_element_by_id("sc-button-classdetail").click()
        self.driver.find_element_by_id("sc-button-confirm").click()

        try:
            confirmed = self.driver.find_element_by_id("sc-div-sentemailtext")
            return confirmed is not None
        except:
            return False
