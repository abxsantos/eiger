from typing import Any

import structlog
from django.core.management import BaseCommand
from django.db import transaction

from eiger.moonboard.models import AccountData, Boulder, HoldSetup, Move
from eiger.moonboard.service.moonboard_api import MoonBoardAPI

logger = structlog.get_logger(__name__)


def import_data():
    for hold_setup in HoldSetup.objects.all():
        logger.info('Starting to import moonboard data...')
        account_data = AccountData.objects.first()
        json_data = MoonBoardAPI(
            username=account_data.username, password=account_data.password
        ).get_problems(
            hold_set=hold_setup.description,
            angle=hold_setup.angle,
            problem_number=0,
        )

        request_data = json_data['data']
        boulders_to_create = []
        moves_to_create = []
        logger.info(f'Preparing to create {len(request_data)} boulders')
        for request_boulder in request_data:
            if Boulder.objects.filter(
                api_id=request_boulder['apiId']
            ).exists():
                logger.info('Boulder already exists')
                continue

            boulder = Boulder(
                name=request_boulder['name'],
                grade=request_boulder['grade'],
                setter_name=request_boulder['setby'],
                setter_user_id=request_boulder['setbyId'],
                method=request_boulder['method'],
                user_rating=request_boulder['userRating'],
                repeats=request_boulder['repeats'],
                hold_setup=hold_setup,
                is_benchmark=request_boulder['isBenchmark'],
                is_master=request_boulder['isMaster'],
                upgraded=request_boulder['upgraded'],
                downgraded=request_boulder['downgraded'],
                has_beta_video=request_boulder['hasBetaVideo'],
                api_id=request_boulder['apiId'],
                date_inserted=request_boulder['dateInserted'],
                date_updated=request_boulder['dateUpdated'],
                date_deleted=request_boulder['dateDeleted'],
            )
            boulders_to_create.append(boulder)
            logger.info('Added boulder for creation')
            for request_move in request_boulder['moves']:
                move = Move(
                    is_start=request_move['isStart'],
                    is_end=request_move['isEnd'],
                    hold=request_move['description'],
                    boulder=boulder,
                )
                moves_to_create.append(move)
                logger.info('Added Move for creation')

        with transaction.atomic():
            logger.info('Starting to create boulders')
            Boulder.objects.bulk_create(objs=boulders_to_create, batch_size=500)
            logger.info('Starting to create moves')
            Move.objects.bulk_create(objs=moves_to_create, batch_size=500)
        logger.info('Created Boulder entries and Move entries.')


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> None:
        import_data()
