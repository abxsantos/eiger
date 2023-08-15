import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)


class MoonBoardAPI:
    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password

        self.base_url = 'https://restapimoonboard.ems-x.com'
        self.token_url = f'{self.base_url}/token'

        self.headers = {
            'accept-encoding': 'gzip, gzip',
            'content-type': 'application/x-www-form-urlencoded',
            'host': 'restapimoonboard.ems-x.com',
            'user-agent': 'MoonBoard/1.0',
        }
        self.refresh_token = None
        self.access_token = None

    def get_refresh_token(self) -> str:
        data = {
            'username': self.username,
            'password': self.password,
            'grant_type': 'password',
            'client_id': 'com.moonclimbing.mb',
        }
        response = requests.get(
            self.token_url, headers=self.headers, data=data
        )
        logger.info('Retrieved refresh token from moonboard api.')
        self.refresh_token = response.json()['refresh_token']
        return self.refresh_token

    def get_access_token(self) -> str:
        data = {
            'refresh_token': self.refresh_token
            if self.refresh_token
            else self.get_refresh_token(),
            'grant_type': 'refresh_token',
            'client_id': 'com.moonclimbing.mb',
        }
        response = requests.get(
            self.token_url, headers=self.headers, data=data
        )
        logger.info('Retrieved access token from moonboard api.')
        self.access_token = response.json()['access_token']
        return self.access_token

    def get_access_headers(self):
        token = (
            self.access_token if self.access_token else self.get_access_token()
        )
        return {
            'accept-encoding': 'gzip, gzip',
            'authorization': f'BEARER {token}',
            'host': 'restapimoonboard.ems-x.com',
            'user-agent': 'MoonBoard/1.0',
        }

    @staticmethod
    def hold_set_angle_mapping(hold_set: str, angle: str):
        if hold_set == 'MoonBoard 2016' and angle == '40':
            return '1', '0'
        elif hold_set == 'MoonBoard Masters 2017' and angle == '40':
            return '15', '1'
        elif hold_set == 'MoonBoard Masters 2017' and angle == '25':
            return '15', '2'
        elif hold_set == 'MoonBoard Masters 2019' and angle == '40':
            return '17', '1'
        elif hold_set == 'MoonBoard Masters 2019' and angle == '25':
            return '17', '2'
        elif hold_set == 'Mini MoonBoard 2020' and angle == '40':
            return '19', '1'
        else:
            raise ValueError(hold_set, angle)

    def get_problems(
        self,
        hold_set: str,
        angle: str,
        problem_number: int = 0,
        result_data: Optional[dict] = None,
    ):
        if not result_data:
            result_data = {}

        mapped_hold_set, mapped_angle = self.hold_set_angle_mapping(
            hold_set, angle
        )
        problems_url = (
            f'{self.base_url}/v1/_moonapi/problems/v3/'
            f'{mapped_hold_set}/{mapped_angle}/{problem_number}'
            '?v=8.3.4'
        )
        headers = self.get_access_headers()
        response = requests.get(problems_url, headers=headers).json()
        logger.info('Retrieved moonboard data from moonboard api.')
        if problem_number == 0:
            result_data = requests.get(problems_url, headers=headers).json()
        else:
            for data in response['data']:
                result_data['data'].append(data)

        if len(response['data']) == 5000:
            return self.get_problems(
                hold_set=hold_set,
                angle=angle,
                problem_number=result_data['data'][-1]['apiId'],
                result_data=result_data,
            )
        else:
            logger.info('Returning final moonboard data from moonboard api.')
            return result_data

    def get_logbook(self):
        response = requests.get(
            url=f'{self.base_url}/v1/_moonapi/Logbook/0?v=8.3.4',
            headers=self.get_access_headers(),
        )
        logger.info('Retrieved the logbook data from moonboard api')
        return response.json()
