from typing import Optional

import pytest
from django.contrib.auth import get_user_model
from model_bakery import baker
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from eiger.trainers.models import Category, Exercise, SubCategory


@pytest.fixture()
def strength_category() -> Category:
    return baker.make(Category, name='Strength')


@pytest.fixture()
def finger_strength_sub_categories(strength_category: Category) -> SubCategory:
    return baker.make(
        SubCategory, name='Finger strength', category=strength_category
    )


@pytest.fixture()
def pending_review_exercise(
    finger_strength_sub_categories: SubCategory,
) -> Exercise:
    return baker.make(
        Exercise,
        name='Bouldering circuit',
        description='Bouldering circuit at 2 grades bellow onsight level.',
        sub_category=finger_strength_sub_categories,
        created_by=get_user_model().objects.get(),
        reviewed=False,
    )


@pytest.fixture()
def already_existing_exercise() -> Exercise:
    return baker.make(
        Exercise,
        name='Project boulders',
        description=(
            'Bouldering at near maximum intensity. Should focus on 1 to 3'
            ' moves only at limit level.'
        ),
        reviewed=False,
    )


def fill_in_exercise_input(
    authenticated_browser: webdriver.Remote,
    name: Optional[str] = None,
    sub_category: Optional[str] = None,
    description: Optional[str] = None,
) -> None:
    if name:
        name_input = authenticated_browser.find_element(
            by=By.ID, value='id_name'
        )
        name_input.clear()
        name_input.send_keys(name)
    if sub_category:
        select = Select(
            authenticated_browser.find_element(
                by=By.ID, value='id_sub_categories'
            )
        )
        select.select_by_visible_text(sub_category)
    if description:
        description_input = authenticated_browser.find_element(
            by=By.ID, value='id_description'
        )
        description_input.clear()
        description_input.send_keys(description)


def click_on_save_button(authenticated_browser: webdriver.Remote) -> None:
    save_button = authenticated_browser.find_element(
        by=By.CSS_SELECTOR,
        value='body > div > main > div > div > form > button',
    )
    save_button.click()


def assert_that_has_displayed_a_successful_update_message(
    authenticated_browser: webdriver.Remote,
    message: str,
    name: Optional[str] = None,
    sub_category: Optional[str] = None,
    description: Optional[str] = None,
) -> None:
    """
    TODO: Implement this functionality!
    """


def assert_that_has_error_update_message(
    authenticated_browser: webdriver.Remote,
    error_message: str,
) -> None:
    error_list = authenticated_browser.find_element(
        by=By.CLASS_NAME, value='errorlist'
    )
    assert error_message == error_list.text


def assert_pending_review_exercise_must_be_updated(
    authenticated_browser: webdriver.Remote,
    exercise: Exercise,
    name: Optional[str] = None,
    sub_category: Optional[str] = None,
    description: Optional[str] = None,
) -> None:
    exercise.refresh_from_db()
    if name:
        name_text = authenticated_browser.find_element(
            by=By.CSS_SELECTOR,
            value=(
                'body > div > main > div > div > div > div:nth-child(1) >'
                ' div:nth-child(2) > div.exercise-header > h4'
            ),
        ).text
        assert name_text == exercise.name
        assert name_text == name
    if sub_category:
        sub_categories_text = authenticated_browser.find_element(
            by=By.CSS_SELECTOR,
            value=(
                'body > div > main > div > div > div > div:nth-child(1) >'
                ' div:nth-child(2) > div.exercise-tags > span'
            ),
        ).text
        assert sub_categories_text == str(exercise.sub_category)
        assert sub_categories_text == sub_category
    if description:
        description_text = authenticated_browser.find_element(
            by=By.CSS_SELECTOR,
            value=(
                'body > div > main > div > div > div > div:nth-child(1) >'
                ' div:nth-child(2) > p.exercise-description'
            ),
        ).text
        assert description_text == exercise.description
        assert description_text == description


def assert_pending_exercise_was_not_updated(
    exercise: Exercise,
    old_name: str,
    old_sub_categories: str,
    old_description: str,
) -> None:
    assert old_name == exercise.name
    assert old_sub_categories == str(exercise.sub_category)
    assert old_description == exercise.description


@pytest.mark.ignore_template_errors()
@pytest.mark.django_db(transaction=True)
def test_trainer_must_be_redirected_to_index_given_non_authenticated_access(
    live_server_url: str,
    browser: webdriver.Remote,
) -> None:
    """
    Feature: Trainer editing an exercise
    Scenario: Trainer tries to access an exercise update page without being logged in
    """
    exercise = baker.make(Exercise)
    # Given I didn't log in
    browser.get(live_server_url)
    assert browser.title == 'Climb Hard - Trainers'
    # When I try to enter on the edit exercise page
    browser.get(f'{live_server_url}/exercises/{exercise.id}')
    # Then I should be redirected to the login page
    assert (
        browser.current_url
        == f'{live_server_url}/?next=/exercises/{exercise.id}'
    )
    assert browser.title == 'Climb Hard - Trainers'


@pytest.mark.ignore_template_errors()
@pytest.mark.django_db(transaction=True)
def test_trainer_tries_to_update_exercise_name(
    live_server_url: str,
    authenticated_browser: webdriver.Remote,
    pending_review_exercise: Exercise,
) -> None:
    """
    Feature: Trainer editing an exercise
    Scenario: Trainer tries to update an exercise name
    """
    # Given I'm a logged-in user
    # And I'm at the edit exercise page
    authenticated_browser.get(
        f'{live_server_url}/exercises/{pending_review_exercise.id}'
    )
    # When I fill in the following details:
    # | Name             | Push Up |
    new_exercise_name = 'Push Up'
    fill_in_exercise_input(
        authenticated_browser=authenticated_browser, name=new_exercise_name
    )
    # And I click on the save button
    click_on_save_button(authenticated_browser=authenticated_browser)
    # Then I should be redirected to the home page
    assert authenticated_browser.current_url == f'{live_server_url}/home/'
    assert authenticated_browser.title == 'Climb Hard - Home'
    # And I should receive a successful exercise update message
    assert_that_has_displayed_a_successful_update_message(
        name=new_exercise_name,
        message='Success',
        authenticated_browser=authenticated_browser,
    )
    # And the pending review exercise must be displayed with the updated name
    assert_pending_review_exercise_must_be_updated(
        name=new_exercise_name,
        exercise=pending_review_exercise,
        authenticated_browser=authenticated_browser,
    )


@pytest.mark.ignore_template_errors()
@pytest.mark.django_db(transaction=True)
def test_trainer_tries_to_update_sub_categories(
    live_server_url: str,
    authenticated_browser: webdriver.Remote,
    pending_review_exercise: Exercise,
) -> None:
    """
    Feature: Trainer editing an exercise
    Scenario: Trainer tries to update the exercise type
    """
    new_sub_categories = str(
        baker.make(
            SubCategory,
            name='Mobility',
            category=baker.make(Category, name='Conditioning'),
        )
    )
    # Given I'm a logged-in user
    # And I'm at the edit exercise page
    authenticated_browser.get(
        f'{live_server_url}/exercises/{pending_review_exercise.id}'
    )
    # When I fill in the following details:
    # | Exercise Type             | Conditioning - Mobility |
    fill_in_exercise_input(
        sub_category=new_sub_categories,
        authenticated_browser=authenticated_browser,
    )
    # And I click on the save button
    click_on_save_button(authenticated_browser=authenticated_browser)
    # Then I should be redirected to the home page
    assert authenticated_browser.current_url == f'{live_server_url}/home/'
    assert authenticated_browser.title == 'Climb Hard - Home'
    # And I should receive a successful exercise update message
    assert_that_has_displayed_a_successful_update_message(
        sub_category=new_sub_categories,
        message='Success',
        authenticated_browser=authenticated_browser,
    )
    # And the pending review exercise must be displayed with the updated sub_category
    assert_pending_review_exercise_must_be_updated(
        sub_category=new_sub_categories,
        exercise=pending_review_exercise,
        authenticated_browser=authenticated_browser,
    )


@pytest.mark.ignore_template_errors()
@pytest.mark.django_db(transaction=True)
def test_trainer_tries_to_update_exercise_description(
    live_server_url: str,
    authenticated_browser: webdriver.Remote,
    pending_review_exercise: Exercise,
) -> None:
    """
    Feature: Trainer editing an exercise
    Scenario: Trainer tries to update the exercise description
    """
    # Given I'm a logged-in user
    # And I'm at the edit exercise page
    authenticated_browser.get(
        f'{live_server_url}/exercises/{pending_review_exercise.id}'
    )
    # When I fill in the following details:
    # | Exercise description             | Boulders at onsight level |
    new_description = 'Boulders at onsight level'
    fill_in_exercise_input(
        description=new_description,
        authenticated_browser=authenticated_browser,
    )
    # And I click on the save button
    click_on_save_button(authenticated_browser=authenticated_browser)
    # Then I should be redirected to the home page
    assert authenticated_browser.current_url == f'{live_server_url}/home/'
    assert authenticated_browser.title == 'Climb Hard - Home'
    # And I should receive a successful exercise update message
    assert_that_has_displayed_a_successful_update_message(
        description=new_description,
        message='Success',
        authenticated_browser=authenticated_browser,
    )
    # And the pending review exercise must be displayed with the updated sub_category
    assert_pending_review_exercise_must_be_updated(
        description=new_description,
        exercise=pending_review_exercise,
        authenticated_browser=authenticated_browser,
    )


@pytest.mark.ignore_template_errors()
@pytest.mark.django_db(transaction=True)
def test_trainer_tries_to_update_exercise_name_with_already_existing_name(
    live_server_url: str,
    authenticated_browser: webdriver.Remote,
    pending_review_exercise: Exercise,
    already_existing_exercise: Exercise,
) -> None:
    """
    Feature: Trainer editing an exercise
    Scenario: Trainer tries to update the exercise name with an already existing name
    """
    # Given I'm a logged-in user
    # And I'm at the edit exercise page
    old_name, old_sub_categories, old_description = (
        pending_review_exercise.name,
        str(pending_review_exercise.sub_category),
        pending_review_exercise.description,
    )
    authenticated_browser.get(
        f'{live_server_url}/exercises/{pending_review_exercise.id}'
    )
    assert authenticated_browser.title == 'Climb Hard - Edit Exercise'
    # When I fill in the following details:
    # | Exercise name             | 4 x 4 |
    new_name = already_existing_exercise.name
    fill_in_exercise_input(
        name=new_name, authenticated_browser=authenticated_browser
    )
    # And I click on the save button
    click_on_save_button(authenticated_browser=authenticated_browser)
    # Then I should see an exercise update error message related to duplicated name
    assert_that_has_error_update_message(
        error_message=(
            "There's already a registered or pending exercise with this name!"
        ),
        authenticated_browser=authenticated_browser,
    )
    # And the pending review exercise must not be updated
    assert_pending_exercise_was_not_updated(
        exercise=pending_review_exercise,
        old_name=old_name,
        old_sub_categories=old_sub_categories,
        old_description=old_description,
    )
    # And I should keep at the exercise update page
    assert (
        authenticated_browser.current_url
        == f'{live_server_url}/exercises/{pending_review_exercise.id}/'
    )
    assert authenticated_browser.title == 'Climb Hard - Edit Exercise'
