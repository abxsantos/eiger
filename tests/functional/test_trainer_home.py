from typing import Optional, Tuple

import pytest
from django.contrib.auth import get_user_model
from model_bakery import baker
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

from eiger.trainers.models import Exercise


def retrieve_pending_exercise_card_texts(
    authenticated_browser: webdriver.Remote,
) -> Tuple[str | None, str, str, str, str]:
    pending_exercise_card = authenticated_browser.find_element(
        by=By.CLASS_NAME, value='pending-exercises-card'
    )
    exercise_header = pending_exercise_card.find_element(
        by=By.CLASS_NAME, value='exercise-header'
    )
    exercise_name_text = exercise_header.find_element(
        by=By.CLASS_NAME, value='exercise-name'
    ).text
    edit_exercise_icon_href = exercise_header.find_element(
        by=By.CLASS_NAME, value='edit-icon'
    ).get_attribute('href')
    exercise_badge_text = pending_exercise_card.find_element(
        by=By.CLASS_NAME, value='badge'
    ).text
    exercise_description_text = pending_exercise_card.find_element(
        by=By.CLASS_NAME, value='exercise-description'
    ).text
    exercise_created_by_text = pending_exercise_card.find_element(
        by=By.CLASS_NAME, value='exercise-created-by'
    ).text
    return (
        edit_exercise_icon_href,
        exercise_badge_text,
        exercise_created_by_text,
        exercise_description_text,
        exercise_name_text,
    )


def retrieve_exercise_variations_components(
    authenticated_browser: webdriver.Remote, has_weight_component: bool = True
) -> dict[str, Optional[str]]:
    components: dict[str, Optional[str]] = {}
    pending_variation_card = authenticated_browser.find_element(
        by=By.CLASS_NAME, value='pending-variations-card'
    )
    exercise_header = pending_variation_card.find_element(
        by=By.CLASS_NAME, value='exercise-header'
    )
    components['exercise_name_text'] = exercise_header.find_element(
        by=By.CLASS_NAME, value='exercise-name'
    ).text
    components['edit_exercise_icon_href'] = exercise_header.find_element(
        by=By.CLASS_NAME, value='edit-icon'
    ).get_attribute('href')
    components['exercise_badge_text'] = pending_variation_card.find_element(
        by=By.CLASS_NAME, value='badge'
    ).text
    components['sets_text'] = pending_variation_card.find_element(
        by=By.CLASS_NAME, value='sets'
    ).text
    components['repetitions_text'] = pending_variation_card.find_element(
        by=By.CLASS_NAME, value='repetitions'
    ).text
    components['rest_between_sets_text'] = pending_variation_card.find_element(
        by=By.CLASS_NAME, value='rest-between-sets'
    ).text
    components[
        'duration_per_repetition_text'
    ] = pending_variation_card.find_element(
        by=By.CLASS_NAME, value='duration-per-repetition'
    ).text
    if has_weight_component:
        components['weight_text'] = pending_variation_card.find_element(
            by=By.CLASS_NAME, value='weight'
        ).text
    components[
        'rest_between_repetitions_text'
    ] = pending_variation_card.find_element(
        by=By.CLASS_NAME, value='rest-between-repetitions'
    ).text
    components[
        'exercise_created_by_text'
    ] = pending_variation_card.find_element(
        by=By.CLASS_NAME, value='exercise-created-by'
    ).text

    return components


@pytest.mark.ignore_template_errors()
def test_unauthenticated_trainer_enter_home_page_without_being_logged_in(
    live_server_url: str, browser: webdriver.Remote
) -> None:
    """
    Feature: Trainer Home
    Scenario: Trainer tries to access home page without being logged in
    """
    # Given I didn't log in
    browser.get(live_server_url)
    assert browser.title == 'Climb Hard - Trainers'
    # When I try to enter on the home page
    browser.get(f'{live_server_url}/home/')
    # Then I should be redirected to the login page
    assert browser.current_url == f'{live_server_url}/?next=/home/'
    assert browser.title == 'Climb Hard - Trainers'


@pytest.mark.ignore_template_errors()
@pytest.mark.django_db(transaction=True)
def test_trainer_enter_home_page_without_pending_data(
    live_server_url: str, authenticated_browser: webdriver.Remote
) -> None:
    """
    Feature: Trainer Home
    Scenario: Trainer enters the home page without any pending Exercise or ExerciseVariation
    """
    # Given I'm a logged-in user with no pending data
    # When I access the home page
    authenticated_browser.get(f'{live_server_url}/home/')
    # Then no pending exercise or exercise variation should be displayed
    assert authenticated_browser.title == 'Climb Hard - Home'
    with pytest.raises(
        NoSuchElementException,
        match='Message: Unable to locate element: .pending-exercises-card',
    ):
        authenticated_browser.find_element(
            by=By.CLASS_NAME, value='pending-exercises-card'
        )


@pytest.mark.ignore_template_errors()
@pytest.mark.django_db(transaction=True)
def test_trainer_enter_home_page_with_pending_exercise(
    live_server_url: str, authenticated_browser: webdriver.Remote
) -> None:
    """
    Feature: Trainer Home
    Scenario: Trainer enters the home page without any pending Exercise or ExerciseVariation
    """
    created_exercise = baker.make(
        Exercise, created_by=get_user_model().objects.get(), reviewed=False
    )
    # Given I'm a logged-in user with no pending data
    # When I access the home page
    authenticated_browser.get(f'{live_server_url}/home/')
    assert authenticated_browser.title == 'Climb Hard - Home'
    # Then a pending exercise should be displayed
    (
        edit_exercise_icon_href,
        exercise_badge_text,
        exercise_created_by_text,
        exercise_description_text,
        exercise_name_text,
    ) = retrieve_pending_exercise_card_texts(authenticated_browser)

    assert exercise_name_text == created_exercise.name
    assert (
        edit_exercise_icon_href
        == f'{live_server_url}/exercises/{created_exercise.id}'
    )
    assert exercise_badge_text == str(created_exercise.sub_category)
    assert exercise_description_text == created_exercise.description
    assert (
        exercise_created_by_text
        == f'Created by: {str(created_exercise.created_by)}'
    )
