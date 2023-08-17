import logging
from typing import Any

from django.core.management import BaseCommand
from django.utils.text import slugify
from django_q.tasks import async_task

from eiger.moonboard.models import AccountData, Boulder, LogbookEntry
from eiger.moonboard.service.moonboard_api import MoonBoardAPI

logger = logging.getLogger(__name__)


def convert_number_of_tries(number_of_tries: str, attempts: int) -> int:
    if number_of_tries == 'Flashed':
        return 1
    elif number_of_tries == '2nd try':
        return 2
    elif number_of_tries == '3rd try':
        return 3
    else:
        return attempts


def import_logbook(payload: dict) -> None:
    logger.info('Importing logbook entries for user: %s', payload['user_id'])
    moonboard_logbook_entries = MoonBoardAPI(
        username=payload['username'], password=payload['password']
    ).get_logbook()

    logbook_entries_to_create = []
    for moonboard_logbook_entry in moonboard_logbook_entries:
        api_id = moonboard_logbook_entry['apiId']
        boulder = Boulder.objects.filter(
            api_id=moonboard_logbook_entry['problem']['apiId']
        ).first()

        if not boulder or LogbookEntry.objects.filter(id=api_id).exists():
            logger.info(f'Skipping the addition of entry {api_id}')
            continue
        comment = moonboard_logbook_entry['comment']
        logger.info(
            f'Preparing the LogbookEntry {api_id} for Boulder {boulder}'
        )
        logbook_entry = LogbookEntry(
            id=api_id,
            boulder=boulder,
            user_id=payload['user_id'],
            date_climbed=moonboard_logbook_entry['dateClimbed'],
            comment=slugify(comment) if comment else '',
            attempts=convert_number_of_tries(
                attempts=moonboard_logbook_entry['attempts'],
                number_of_tries=moonboard_logbook_entry['numberOfTries'],
            ),
            user_grade=moonboard_logbook_entry['problem']['userGrade'],
        )
        logbook_entries_to_create.append(logbook_entry)

    LogbookEntry.objects.bulk_create(logbook_entries_to_create)

    logger.info(
        f'Created {len(logbook_entries_to_create)} LogbookEntry in database'
    )


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> None:
        for account_data in AccountData.objects.all().iterator():
            async_task(
                func=import_logbook,
                payload={
                    'user_id': account_data.user_id,
                    'username': account_data.username,
                    'password': account_data.password,
                },
            )
