import pytest
from django.contrib.auth.models import User
from selenium import webdriver
from selenium.webdriver.common.by import By


def fill_login_form(
    browser: webdriver.Remote,
    username: str,
    password: str,
) -> None:
    username_inputbox = browser.find_element(
        by=By.ID, value='login-component'
    ).find_element(by=By.ID, value='id_username')
    username_inputbox.send_keys(username)

    password_inputbox = browser.find_element(by=By.ID, value='id_password')
    password_inputbox.send_keys(password)


def fill_admin_login_form(
    browser: webdriver.Remote,
    username: str,
    password: str,
) -> None:
    username_inputbox = browser.find_element(by=By.ID, value='id_username')
    username_inputbox.send_keys(username)

    password_inputbox = browser.find_element(by=By.ID, value='id_password')
    password_inputbox.send_keys(password)


def submit_admin_registration_form(browser: webdriver.Remote) -> None:
    register_button = browser.find_element(
        by=By.CSS_SELECTOR, value='.submit-row > input:nth-child(1)'
    )
    register_button.click()


def submit_registration_form(browser: webdriver.Remote) -> None:
    register_button = browser.find_element(by=By.ID, value='login-input')
    register_button.click()


def retrieve_error_text(
    browser: webdriver.Remote,
) -> str:
    return browser.find_element(by=By.CLASS_NAME, value='errornote').text


@pytest.mark.xfail(reason='Home page not yet implemented.')
@pytest.mark.ignore_template_errors()
@pytest.mark.django_db(transaction=True)
def test_trainer_enters_valid_login_details(
    live_server_url: str, browser: webdriver.Remote
) -> None:
    """
    Feature: Trainer Login
    Scenario: Trainer enters valid login credentials
    """
    username = 'trainer'
    password = 'StrongPass123!'
    User.objects.create_user(username=username, password=password)
    # Given I'm on the login page
    browser.get(live_server_url)
    assert browser.title == 'Climb Hard - Trainers'
    # When the trainer fills in the following details:
    # | Email            | trainer             |
    # | Password         | StrongPass123!      |
    fill_login_form(
        browser=browser,
        username=username,
        password=password,
    )
    # And I click on the "Login" button
    submit_registration_form(browser=browser)
    # Then I should be redirected to the trainer management home
    assert browser.title == 'Climb Hard - Home'


@pytest.mark.ignore_template_errors()
@pytest.mark.django_db(transaction=True)
def test_trainer_enters_non_registered_credentials(
    live_server_url: str, browser: webdriver.Remote
) -> None:
    """
    Feature: Trainer login
    Scenario: Trainer submits non-registered credentials
    """
    # Given I'm on the login page
    browser.get(live_server_url)
    assert browser.title == 'Climb Hard - Trainers'
    # When I fill in the following details:
    # | Email            | trainer |
    # | Password         | StrongPass123!      |
    username = 'trainer'
    password = 'StrongPass123!'
    fill_login_form(
        browser=browser,
        username=username,
        password=password,
    )
    # And I click on the "Login" button
    submit_registration_form(browser=browser)
    # Then I should see an error message indicating that the credentials are invalid
    assert (
        retrieve_error_text(browser)
        == 'Please enter a correct username and password. Note that both'
        ' fields may be case-sensitive.'
    )
    # And I should remain on the login page
    assert browser.title == 'Climb Hard - Trainers'


@pytest.mark.ignore_template_errors()
@pytest.mark.django_db(transaction=True)
def test_trainer_tries_to_access_staff_admin_page(
    live_server_url: str, browser: webdriver.Remote
) -> None:
    """
    Feature: Trainer login
    Scenario: Trainer tries to access staff admin page
    """
    username = 'trainer'
    password = 'StrongPass123!'
    User.objects.create_user(username=username, password=password)
    # Given I'm on the staff login page
    browser.get(f'{live_server_url}/admin/')
    assert browser.title == 'Log in | Django site admin'
    # When I fill in the following details:
    # | Email            | trainer |
    # | Password         | StrongPass123!      |
    fill_admin_login_form(
        browser=browser,
        username=username,
        password=password,
    )
    # And I click on the "Login" button
    submit_admin_registration_form(browser=browser)
    # Then I should see an error message indicating that I've invalid login credentials.
    assert (
        retrieve_error_text(browser)
        == 'Please enter the correct username and password for a staff'
        ' account. Note that both fields may be case-sensitive.'
    )
