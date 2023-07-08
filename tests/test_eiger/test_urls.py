from http import HTTPStatus

import pytest
from django.test import Client


def test_admin_unauthorized(client: Client) -> None:
    """This test ensures that admin panel requires auth."""
    response = client.get('/admin/')

    assert response.status_code == HTTPStatus.FOUND


def test_admin_authorized(admin_client: Client) -> None:
    """This test ensures that admin panel is accessible."""
    response = admin_client.get('/admin/')

    assert response.status_code == HTTPStatus.OK


def test_admin_docs_unauthorized(client: Client) -> None:
    """This test ensures that admin panel docs requires auth."""
    response = client.get('/admin/doc/')

    assert response.status_code == HTTPStatus.FOUND


def test_admin_docs_authorized(admin_client: Client) -> None:
    """This test ensures that admin panel docs are accessible."""
    response = admin_client.get('/admin/doc/')

    assert response.status_code == HTTPStatus.OK
    assert b'docutils' not in response.content


@pytest.mark.django_db()
def test_health_check(client: Client) -> None:
    """This test ensures that health check is accessible."""
    response = client.get('/healthcheck/')

    assert response.status_code == HTTPStatus.OK
    assert (
        '<td>DatabaseBackend</td><td><p>working</p></td>'
        in response.content.decode('utf-8').replace('\n', '').replace(' ', '')
    )
