from typing import Any

import structlog
from django.core.management import BaseCommand
from django.utils.text import slugify
from django_q.tasks import async_task

from eiger.moonboard.models import AccountData, Boulder, LogbookEntry
from eiger.moonboard.service.moonboard_api import MoonBoardAPI

logger = structlog.get_logger(__name__)


def convert_number_of_tries(number_of_tries: str, attempts: int) -> int:
    if number_of_tries == 'Flashed':
        return 1
    elif number_of_tries == '2nd try':
        return 2
    elif number_of_tries == '3rd try':
        return 3
    else:
        return attempts


def process_logbook_import(*args, **kwargs) -> None:
    climber_id, username, password = args
    logger.info('Importing logbook entries for climber_id %s', climber_id)
    moonboard_logbook_entries = MoonBoardAPI(
        username=username, password=password
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
            'Preparing the LogbookEntry %s for Boulder %s', api_id, boulder
        )
        logbook_entry = LogbookEntry(
            id=api_id,
            boulder=boulder,
            climber_id=climber_id,
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
        'Created %s LogbookEntry in database', len(logbook_entries_to_create)
    )


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> None:
        for account_data in AccountData.objects.all().iterator():
            async_task(
                f'{process_logbook_import.__module__}.{process_logbook_import.__name__}',
                account_data.climber_id,
                account_data.username,
                account_data.password,
            )
