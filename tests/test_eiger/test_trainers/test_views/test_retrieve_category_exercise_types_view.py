from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse
from model_bakery import baker

from eiger.trainers.models import Category, SubCategory


@pytest.fixture()
def url(category: Category) -> str:
    return reverse('retrieve_category_sub_categoriess', args=[category.id])


@pytest.fixture()
def sub_categories(category: Category) -> list[SubCategory]:
    return baker.make(SubCategory, category=category, _quantity=3)


@pytest.mark.django_db
def test_successful_response(
    authenticated_client: Client,
    category: Category,
    sub_categories: list[SubCategory],
    url: str,
) -> None:

    response = authenticated_client.get(url)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == [
        {'id': sub_category.id, 'name': sub_category.name}
        for sub_category in sub_categories
    ]


@pytest.mark.django_db
def test_successful_empty_response(
    authenticated_client: Client, category: Category, url: str
) -> None:

    response = authenticated_client.get(url)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == []


@pytest.mark.django_db
def test_must_redirect_to_index_given_non_authenticated_user(
    client: Client, category: Category, url: str
) -> None:

    response = client.get(url)

    assert response.status_code == HTTPStatus.FOUND
    assert response.content == b''
    assert response.url == f'/?next={url}'  # type: ignore[attr-defined]


@pytest.mark.django_db
def test_view_caching(
    authenticated_client: Client,
    category: Category,
    sub_categories: list[SubCategory],
    url: str,
) -> None:

    response = authenticated_client.get(url)

    assert response.get('Cache-Control') == f'max-age={60 * 60 * 24}'
    assert response.has_header('Expires')
    assert response.json() == [
        {'id': sub_category.id, 'name': sub_category.name}
        for sub_category in sub_categories
    ]
