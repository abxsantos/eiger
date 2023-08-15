import pytest
from django.contrib.auth.models import User
from selenium import webdriver
from selenium.webdriver.common.by import By


def fill_registration_form(
    browser: webdriver.Remote,
    username: str,
    password: str,
    confirmation_password: str,
) -> None:
    username_inputbox = browser.find_element(
        by=By.ID, value='register-component'
    ).find_element(by=By.ID, value='id_username')
    username_inputbox.send_keys(username)

    password_inputbox = browser.find_element(by=By.ID, value='id_password1')
    password_inputbox.send_keys(password)

    password_confirmation_inputbox = browser.find_element(
        by=By.ID, value='id_password2'
    )
    password_confirmation_inputbox.send_keys(confirmation_password)


def submit_registration_form(browser: webdriver.Remote) -> None:
    register_input = browser.find_element(by=By.ID, value='register-input')
    register_input.click()


def retrieve_error_list(
    browser: webdriver.Remote,
) -> str:
    return browser.find_element(by=By.CLASS_NAME, value='errorlist').text


@pytest.mark.ignore_template_errors()
@pytest.mark.django_db(transaction=True)
def test_trainer_enters_valid_registration_details(
    live_server_url: str, browser: webdriver.Remote
) -> None:
    """
    Feature: Trainer Registration
    Scenario: Trainer enters valid registration details
    """
    browser.get(live_server_url)
    # Given I am on the registration page
    assert browser.title == 'Climb Hard - Trainers'

    # When I fill in the following details:
    # | Username            | trainer |
    # | Password         | StrongPass123!      |
    # | Confirm Password | StrongPass123!      |
    username = 'trainer'
    password = 'StrongPass123!'
    fill_registration_form(
        browser=browser,
        username=username,
        password=password,
        confirmation_password=password,
    )

    # And I click on the register button
    submit_registration_form(browser=browser)

    # Then I should be redirected to the management home page
    assert browser.title == 'Climb Hard - Home'


@pytest.mark.ignore_template_errors()
@pytest.mark.django_db(transaction=True)
def test_trainer_enters_mismatched_password(
    live_server_url: str, browser: webdriver.Remote
) -> None:
    """
    Feature: Trainer Registration
    Scenario: Trainer enters mismatched password
    """
    browser.get(live_server_url)
    # Given I am on the registration page
    assert browser.title == 'Climb Hard - Trainers'
    # When I fill in the following details:
    # | username         | trainer |
    # | Password         | StrongPass123!      |
    # | Confirm Password | DifferentPass456!   |
    username = 'trainer'
    password = 'StrongPass123!'
    mismatched_confirmation_password = 'DifferentPass456!'
    fill_registration_form(
        browser=browser,
        username=username,
        password=password,
        confirmation_password=mismatched_confirmation_password,
    )
    # And I click on the "Register" button
    submit_registration_form(browser=browser)
    # Then I should see an error message indicating password mismatch
    assert (
        retrieve_error_list(browser) == 'The two password fields didn’t match.'
    )
    # And the trainer's account should not be created.
    assert User.objects.filter(username=username).exists() is False


@pytest.mark.ignore_template_errors()
@pytest.mark.django_db(transaction=True)
def test_trainer_enters_invalid_registration_details(
    live_server_url: str, browser: webdriver.Remote
) -> None:
    """
    Feature: Trainer Registration
    Scenario: Trainer enters invalid registration details
    """
    browser.get(live_server_url)
    # Given I am on the registration page
    assert browser.title == 'Climb Hard - Trainers'
    # When I fill in the following details:
    # | Email            | weak       |
    # | Password         | weakpass      |
    # | Confirm Password | weakpass      |
    username = '1'
    password = '1'
    fill_registration_form(
        browser=browser,
        username=username,
        password=password,
        confirmation_password=password,
    )
    # And I click on the "Register" button
    submit_registration_form(browser=browser)
    # Then I should see an error message indicating invalid username format
    assert (
        retrieve_error_list(browser)
        == 'The password is too similar to the username.\n'
        'This password is too short. It must contain at least 8 characters.\n'
        'This password is too common.\n'
        'This password is entirely numeric.'
    )
    # And the trainer's account should not be created.
    assert User.objects.filter(username=username).exists() is False


@pytest.mark.ignore_template_errors()
@pytest.mark.django_db(transaction=True)
def test_trainer_registering_an_email_that_already_been_used(
    live_server_url: str, browser: webdriver.Remote
) -> None:
    """
    Feature: Trainer Registration
    Scenario: Trainer registering an email that already been used
    """
    username = 'trainer'
    password = 'StrongPass123!'
    User.objects.create_user(username=username, password=password)
    browser.get(live_server_url)
    # Given I am on the registration page
    assert browser.title == 'Climb Hard - Trainers'
    # When I enter an email that is already registered:
    # | Username         | trainer             |
    # And I fill in the passwords:
    # | Password         | StrongPass123!      |
    # | Confirm Password | StrongPass123!      |

    fill_registration_form(
        browser=browser,
        username=username,
        password=password,
        confirmation_password=password,
    )
    # And I click on the "Register" button
    submit_registration_form(browser=browser)
    # Then I should see an error message indicating that
    # an account with that email already exists
    assert (
        retrieve_error_list(browser)
        == 'A user with that username already exists.'
    )
