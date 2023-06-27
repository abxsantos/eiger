from typing import Tuple

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


def fill_registration_form(
    browser: webdriver.Remote,
    email: str,
    password: str,
    confirmation_password: str,
) -> None:
    email_inputbox = browser.find_element(by=By.ID, value='id_email')
    email_inputbox.send_keys(email)

    password_inputbox = browser.find_element(by=By.ID, value='id_password1')
    password_inputbox.send_keys(password)

    password_confirmation_inputbox = browser.find_element(
        by=By.ID, value='id_password2'
    )
    password_confirmation_inputbox.send_keys(confirmation_password)


def submit_registration_form(browser: webdriver.Remote) -> None:
    register_button = browser.find_element(by=By.ID, value='register-input')
    register_button.click()


def retrieve_error_components(
    browser: webdriver.Remote,
) -> Tuple[WebElement, WebElement]:
    error_note = browser.find_element(by=By.CLASS_NAME, value='errornote')
    error_list = browser.find_element(by=By.CLASS_NAME, value='errorlist')
    return error_note, error_list


@pytest.mark.xfail(reason='Trainer registration flow not yet implemented')
def test_trainer_accesses_the_registration_page(
    live_server_url: str, browser: webdriver.Remote
) -> None:
    """
    Feature: Trainer Registration
    Scenario: Trainer accesses the registration page
    """
    # Given I'm on the website's homepage
    browser.get(f'{live_server_url}/')
    assert browser.title == 'Climb Hard | Trainer Management'
    # When I click on the "Register" button
    register_button = browser.find_element(by=By.ID, value='register-button')
    register_button.click()
    # Then I should be redirected to the registration page
    assert browser.title == 'Register | Trainer Management'


@pytest.mark.xfail(reason='Trainer registration flow not yet implemented')
def test_trainer_enters_valid_registration_details(
    live_server_url: str, browser: webdriver.Remote
) -> None:
    """
    Feature: Trainer Registration
    Scenario: Trainer enters valid registration details
    """
    browser.get(f'{live_server_url}/register/')
    # Given I am on the registration page
    assert browser.title == 'Register | Trainer Management'

    # When I fill in the following details:
    # | Email            | trainer@example.com |
    # | Password         | StrongPass123!      |
    # | Confirm Password | StrongPass123!      |
    email = 'trainer@example.com'
    password = 'StrongPass123!'
    fill_registration_form(
        browser=browser,
        email=email,
        password=password,
        confirmation_password=password,
    )

    # And I click on the register button
    submit_registration_form(browser=browser)

    # Then I should be redirected to the admin index page
    assert browser.title == 'Home | Trainer Management'


@pytest.mark.xfail(reason='Trainer registration flow not yet implemented')
def test_trainer_enters_mismatched_password(
    live_server_url: str, browser: webdriver.Remote
) -> None:
    """
    Feature: Trainer Registration
    Scenario: Trainer enters mismatched password
    """
    browser.get(f'{live_server_url}/register/')
    # Given I am on the registration page
    assert browser.title == 'Register | Trainer Management'
    # When I fill in the following details:
    # | Email            | trainer@example.com |
    # | Password         | StrongPass123!      |
    # | Confirm Password | DifferentPass456!   |
    email = 'trainer@example.com'
    password = 'StrongPass123!'
    mismatched_confirmation_password = 'DifferentPass456!'
    fill_registration_form(
        browser=browser,
        email=email,
        password=password,
        confirmation_password=mismatched_confirmation_password,
    )
    # And I click on the "Register" button
    submit_registration_form(browser=browser)
    # Then I should see an error message indicating password mismatch
    error_note, error_list = retrieve_error_components(browser)
    assert error_note.text == 'Error'
    assert error_list.text == 'Password mismatch'
    # And the trainer's account should not be created.
    # assert Trainer.objects.filter(email=email).exists() is False


@pytest.mark.xfail(reason='Trainer registration flow not yet implemented')
def test_trainer_enters_invalid_registration_details(
    live_server_url: str, browser: webdriver.Remote
) -> None:
    """
    Feature: Trainer Registration
    Scenario: Trainer enters invalid registration details
    """
    browser.get(f'{live_server_url}/register/')
    # Given I am on the registration page
    assert browser.title == 'Register | Trainer Management'
    # When I fill in the following details:
    # | Email            | invalid_email       |
    # | Password         | StrongPass123!      |
    # | Confirm Password | StrongPass123!      |
    email = 'invalid_email'
    password = 'weakpassword'
    fill_registration_form(
        browser=browser,
        email=email,
        password=password,
        confirmation_password=password,
    )
    # And I click on the "Register" button
    submit_registration_form(browser=browser)
    # Then I should see an error message indicating invalid email format
    error_note, error_list = retrieve_error_components(browser)
    assert error_note.text == 'Error'
    assert error_list.text == 'Invalid email format'
    # And the trainer's account should not be created.
    # assert Trainer.objects.filter(email=email).exists() is False


@pytest.mark.xfail(reason='Trainer registration flow not yet implemented')
def test_trainer_leaves_email_field_empty(
    live_server_url: str, browser: webdriver.Remote
) -> None:
    """
    Feature: Trainer Registration
    Scenario: Trainer leaves email field empty
    """
    browser.get(f'{live_server_url}/register/')
    # Given I am on the registration page
    assert browser.title == 'Register | Trainer Management'
    # When I fill in the following details:
    # | Email            |                     |
    # | Password         | weakpassword        |
    # | Confirm Password | weakpassword        |
    email = 'invalid_email'
    password = 'weakpassword'
    fill_registration_form(
        browser=browser,
        email=email,
        password=password,
        confirmation_password=password,
    )
    # And I click on the "Register" button
    submit_registration_form(browser=browser)
    # Then I should see an error message indicating the
    # email field is required
    error_note, error_list = retrieve_error_components(browser)
    assert error_note.text == 'Error'
    assert error_list.text == 'Email field is required'
    # And the trainer's account should not be created.
    # assert Trainer.objects.filter(email=email).exists() is False


@pytest.mark.xfail(reason='Trainer registration flow not yet implemented')
def test_trainer_registering_an_email_that_already_been_used(
    live_server_url: str, browser: webdriver.Remote
) -> None:
    """
    Feature: Trainer Registration
    Scenario: Trainer registering an email that already been used
    """
    browser.get(f'{live_server_url}/register/')
    # Given I am on the registration page
    assert browser.title == 'Register | Trainer Management'
    # When I enter an email that is already registered:
    # | Email            | trainer@example.com |
    # And I fill in the passwords:
    # | Password         | StrongPass123!      |
    # | Confirm Password | StrongPass123!      |
    email = 'trainer@example.com'
    password = 'StrongPass123!'
    fill_registration_form(
        browser=browser,
        email=email,
        password=password,
        confirmation_password=password,
    )
    # And I click on the "Register" button
    submit_registration_form(browser=browser)
    # Then I should see an error message indicating that
    # an account with that email already exists
    error_note, error_list = retrieve_error_components(browser)
    assert error_note.text == 'Error'
    assert error_list.text == 'Account with this email already exists'
    # And the trainer's account should not be created.
    # assert Trainer.objects.filter(email=email).exists() is False
