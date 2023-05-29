"""realtimeprices.py - Chris Fisher "cdfisher", 2023
Real time Grand Exchange prices submodule of osrs-tools. Fetches and formats pricing data from Runelite's
real time Grand Exchange info (Served by the Old School RuneScape Wiki/Weird Gloop).
"""
import json
import requests
import datetime

URL_BASE = 'http://prices.runescape.wiki/api/v1/osrs/'

# Base classes


class BaseRTPriceInfo:
    """Base class representing price data for a single item.
    Parent class of LatestRTPriceInfo, AverageRTPriceInfo
    """
    def __init__(self, item_id, high, low):
        self.item_id = item_id
        self.high = high
        self.low = low

    def __str__(self):
        return f'id: {self.item_id} high: {self.high} low: {self.low}'


class BaseRTPriceChecker:
    """Base class for fetching and parsing data from the RuneLite/Old School RuneScape Wiki's
    real time prices API.
    Parent class of LatestRTPriceChecker, AverageRTPriceChecker
    """
    def __init__(self, user_agent: str, endpoint: str, keep_updated=False):
        ua_message = "At the request of the OSRS Wiki, please set a descriptive user_agent value that includes a way" \
                     "to contact you in the case of issues with your project."
        assert (user_agent is not None) and (user_agent != ''), ua_message
        self.user_agent = user_agent + " via osrs-tools by https://github.com/cdfisher"
        self.headers = {'User-Agent': self.user_agent}
        self.endpoint = endpoint
        self.itemdata = dict()
        self.last_updated = None
        self.keep_updated = keep_updated

        self._build_item_maps()

    def get_price_info(self, query: str):
        try:
            query = int(query)
            return self._get_price_info_from_id(str(query))
        except ValueError:
            return self._get_price_info_from_string(query)

    def get_item_name(self, item_id) -> str:
        return self.item_id_map[str(item_id)]

    def _get_price_info_from_id(self, item_id: str):
        # TODO test
        return self.itemdata[item_id]

    def _get_price_info_from_string(self, query_string: str):
        # Uses the same (or similar, at least) matching method as Runelite's !price command
        # in order to give some sort of parity between the two
        item_id = self._get_item_id(query_string)
        if item_id == -1:
            raise KeyError(f'No id found matching string: {query_string}')
        return self.itemdata[item_id]

    def _build_item_maps(self):
        """Fetches item <-> id mapping from the OSRS Wiki API and builds a pair of
         lookup dicts for easy conversion between name and id.
        """
        self.item_name_map = dict()
        self.item_id_map = dict()
        max_retries = 5
        n_retries = 0
        while n_retries <= max_retries:
            self._response = requests.get(f'{URL_BASE}mapping', headers=self.headers)
            if self._response.status_code > 399:
                # Some sort of error
                n_retries += 1
                if n_retries > max_retries:
                    raise ValueError(f'Unable to fetch mapping data, received response {self._response.status_code}.')
                else:
                    continue
            else:
                self.mapping_json = json.loads(self._response.content.decode('utf-8'))
                break
        for i in range(len(self.mapping_json)):
            self.item_name_map[self.mapping_json[i]["name"].lower()] = str(self.mapping_json[i]["id"])
            self.item_id_map[str(self.mapping_json[i]["id"])] = self.mapping_json[i]["name"]

    def _get_item_id(self, query: str):
        query = query.lower()
        for key in self.item_name_map:
            if key.startswith(query):
                return self.item_name_map[key]
        return -1

    def _fetch_data(self):
        max_retries = 5
        n_retries = 0
        url = f'{URL_BASE}{self.endpoint}'
        print(f'URL: {url}')
        while n_retries <= max_retries:
            self._response = requests.get(url, headers=self.headers)
            if self._response.status_code > 399:
                # Some sort of error has been encountered, retry
                n_retries += 1
                if n_retries > max_retries:
                    raise ValueError(f'Unable to fetch data, received response {self._response.status_code}.')
                else:
                    continue
            else:
                self.json = json.loads(self._response.content.decode('utf-8'))["data"]
                return self.json

# Latest endpoint classes


class LatestRTPriceInfo(BaseRTPriceInfo):
    """Class representing price data for a single item from the /latest API endpoint
    Extends BaseRTPriceInfo
    """
    def __init__(self, item_id, high, low, high_time, low_time):
        super().__init__(item_id, high, low)
        self.high_time = high_time
        self.low_time = low_time

    def __str__(self):
        return f'id: {self.item_id} high: {self.high} low: {self.low}' \
               f' high_time: {self.high_time} low_time: {self.low_time}'


class AverageRTPriceInfo(BaseRTPriceInfo):
    """Class representing price data for a single item from the /5m and /1h API endpoints
    Extends BaseRTPriceInfo
    """
    def __init__(self, item_id, high, low, time_period, high_price_volume, low_price_volume):
        super().__init__(item_id, high, low)
        self.time_period = time_period
        self.high_price_volume = high_price_volume
        self.low_price_volume = low_price_volume

    def __str__(self):
        return f'id: {self.item_id} high: {self.high} low: {self.low} ' \
               f'time_period: {self.time_period} high_price_volume: {self.high_price_volume}' \
               f' low_price_volume: {self.low_price_volume}'


class LatestRTPriceChecker(BaseRTPriceChecker):
    def __init__(self, user_agent: str, keep_updated=False):
        super().__init__(user_agent, 'latest', keep_updated)

        self.update()

    def _process_data(self, data: dict):
        # TODO Add check for self.keep_updated here
        # For each key in data
        for key in data:
            _entry = data[key]
            self.itemdata[key] = LatestRTPriceInfo(key, _entry["high"], _entry["low"], _entry["highTime"],
                                                   _entry["lowTime"])
        self.last_updated = datetime.datetime.now()

    def update(self):
        self._process_data(self._fetch_data())


class AverageRTPriceChecker(BaseRTPriceChecker):

    def __init__(self, user_agent: str, time_period: str, keep_updated=False):
        valid_time_periods = {'5m', '1h'}
        if time_period not in valid_time_periods:
            raise ValueError(f'Invalid time period value: {time_period}. Supported values: {valid_time_periods}')
        super().__init__(user_agent, time_period, keep_updated)

        self.update()

    def _process_data(self, data: dict):
        # TODO Add check for self.keep_updated here
        # For each key in data
        for key in data:
            _entry = data[key]
            self.itemdata[key] = AverageRTPriceInfo(key, _entry["avgHighPrice"], _entry["avgLowPrice"], self.endpoint,
                                                    _entry["highPriceVolume"], _entry["lowPriceVolume"])
        self.last_updated = datetime.datetime.now()

    def update(self):
        self._process_data(self._fetch_data())
