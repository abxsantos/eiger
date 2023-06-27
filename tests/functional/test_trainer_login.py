from typing import Tuple

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


def fill_login_form(
    browser: webdriver.Remote,
    email: str,
    password: str,
) -> None:
    email_inputbox = browser.find_element(by=By.ID, value='id_email')
    email_inputbox.send_keys(email)

    password_inputbox = browser.find_element(by=By.ID, value='id_password')
    password_inputbox.send_keys(password)


def submit_registration_form(browser: webdriver.Remote) -> None:
    register_button = browser.find_element(by=By.ID, value='login-input')
    register_button.click()


def retrieve_error_components(
    browser: webdriver.Remote,
) -> Tuple[WebElement, WebElement]:
    error_note = browser.find_element(by=By.CLASS_NAME, value='errornote')
    error_list = browser.find_element(by=By.CLASS_NAME, value='errorlist')
    return error_note, error_list


@pytest.mark.xfail(reason='Trainer registration flow not yet implemented')
def test_trainer_accesses_the_login_page(
    live_server_url: str, browser: webdriver.Remote
) -> None:
    """
    Feature: Trainer Login
    Scenario: Trainer accesses the login page
    """
    # Given I'm on the website's homepage
    browser.get(f'{live_server_url}/')
    assert browser.title == 'Climb Hard | Trainer Management'
    # When I click on the "Login" button
    submit_registration_form(browser=browser)
    # Then I should be redirected to the login page
    assert browser.title == 'Log In | Trainer Management'


@pytest.mark.xfail(reason='Trainer registration flow not yet implemented')
def test_trainer_enters_valid_login_details(
    live_server_url: str, browser: webdriver.Remote
) -> None:
    """
    Feature: Trainer Login
    Scenario: Trainer enters valid login credentials
    """
    # baker.make(
    # Trainer, email='trainer@example.com',
    # hashed_password=hash_password('StrongPass123!'))
    # Given I'm on the login page
    browser.get(f'{live_server_url}/login/')
    assert browser.title == 'Log In | Trainer Management'
    # When the trainer fills in the following details:
    # | Email            | trainer@example.com |
    # | Password         | StrongPass123!      |
    email = 'trainer@example.com'
    password = 'StrongPass123!'
    fill_login_form(
        browser=browser,
        email=email,
        password=password,
    )
    # And I click on the "Login" button
    submit_registration_form(browser=browser)
    # Then I should be redirected to the trainer management home
    assert browser.title == 'Home | Trainer Management'


@pytest.mark.xfail(reason='Trainer registration flow not yet implemented')
def test_trainer_enters_non_registered_credentials(
    live_server_url: str, browser: webdriver.Remote
) -> None:
    """
    Feature: Trainer login
    Scenario: Trainer submits non-registered credentials
    """
    # Given I'm on the login page
    browser.get(f'{live_server_url}/login/')
    assert browser.title == 'Log In | Trainer Management'
    # When I fill in the following details:
    # | Email            | trainer@example.com |
    # | Password         | StrongPass123!      |
    email = 'trainer@example.com'
    password = 'StrongPass123!'
    fill_login_form(
        browser=browser,
        email=email,
        password=password,
    )
    # And I click on the "Login" button
    submit_registration_form(browser=browser)
    # Then I should see an error message
    error_note, error_list = retrieve_error_components(browser)
    # And the message should indicate that the credentials are invalid
    assert error_note.text == 'Error'
    assert error_list.text == 'Password mismatch'
    # And I should remain on the login page
    assert browser.title == 'Log In | Trainer Management'


@pytest.mark.xfail(reason='Trainer login flow not yet implemented')
def test_trainer_tries_to_access_staff_admin_page(
    live_server_url: str, browser: webdriver.Remote
) -> None:
    """
    Feature: Trainer login
    Scenario: Trainer tries to access staff admin page
    """
    # Given I'm on the staff login page
    browser.get(f'{live_server_url}/admin/')
    assert browser.title == 'Log In | Django Admin'
    # When I fill in the following details:
    # | Email            | trainer@example.com |
    # | Password         | StrongPass123!      |
    email = 'trainer@example.com'
    password = 'StrongPass123!'
    fill_login_form(
        browser=browser,
        email=email,
        password=password,
    )
    # And I click on the "Login" button
    submit_registration_form(browser=browser)
    # Then I should see an error message
    error_note, error_list = retrieve_error_components(browser)
    # And the message should indicate that I've invalid login credentials.
    assert error_note.text == 'Error'
    assert error_list.text == 'Invalid login credentials'
