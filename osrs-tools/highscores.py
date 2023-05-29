"""highscores.py - Chris Fisher "cdfisher", 2023
Highscores submodule of osrs-tools. Fetches and formats data from the Old
School RuneScape highscores via the index_lite JSON API endpoint.
"""
import json
import requests
from warnings import warn
from pprint import pformat
from resources.entries import *
from resources.url_builder import build_url


def get_target_type(target: str) -> str:
    """Returns whether a given contest target is a skill, activity, or boss.

    :param target: String representation of target to query
    :return: String representing type.
    """
    if target in skill_attributes:
        return 'skill'
    elif target in activity_attributes:
        return 'activity'
    elif target in boss_attributes:
        return 'boss'
    else:
        raise ValueError(f'Target {target} not recognized.')


class SkillEntry:
    """SkillEntry

    Class used to wrap up data for skills in order for it to be easily accessed via object attributes.
    @:arg data      dict: Highscores entries for a given skill.
    """
    def __init__(self, data: dict):
        self.rank = data["rank"]
        self.level = data["level"]
        self.xp = data["xp"]

    def __str__(self) -> str:
        return f'{{"rank": {self.rank},\n"level": {self.level},\n"xp": {self.xp}}}'

    def __repr__(self) -> str:
        self._rep_dict = {"rank": self.rank, "level": self.level, "xp": self.xp}
        return str(self._rep_dict)


class ActivityEntry:
    """ActivityEntry

    Class used to wrap up data for activities so it can be easily accessed via object attributes.
    @:arg data      dict: Highscores entries for a given activity.
    """
    def __init__(self, data: dict):
        self.rank = data["rank"]
        self.score = data["score"]

    def __str__(self) -> str:
        return f'{{"rank": {self.rank},\n"score": {self.score}}}'

    def __repr__(self) -> str:
        self._rep_dict = {"rank": self.rank, "score": self.score}
        return str(self._rep_dict)


class BossEntry:
    """BossEntry

    Class used to wrap up data for bosses so it can be easily accessed via object attributes.
    @:arg data      dict: Highscores entries for a given boss.
    """
    def __init__(self, data: dict):
        self.rank = data["rank"]
        self.kc = data["score"]

    def __str__(self) -> str:
        return f'{{"rank": {self.rank},\n"KC": {self.kc}}}'

    def __repr__(self) -> str:
        self._rep_dict = {"rank": self.rank, "kc": self.kc}
        return str(self._rep_dict)


class Highscores:
    """Highscores

    Class to fetch and represent a player's entries on the OSRS highscores.
    @:arg rsn       str: The player's current Old School RuneScape username.
    @:arg target    str: Category of the Highscores being queried. Defaults to
                        'default'
                        Valid values: {'default', 'ironman', 'ultimate',
                        'hardcore_ironman', 'seasonal', 'deadman',
                        'tournament', 'fresh_start', 'skiller',
                        'skiller_defence'}
    """

    def __init__(self, rsn: str, target='default'):
        self.rsn = rsn
        self.target = target
        self._parse_data(self._fetch_data())

    def _fetch_data(self) -> dict:
        max_retries = 5
        n_retries = 0
        while n_retries <= max_retries:
            self._response = requests.get(build_url(self.target, self.rsn))
            if self._response.status_code == 404:
                n_retries += 1
                if n_retries > max_retries:
                    raise ValueError(f'Data for user {self.rsn} not found!')
                else:
                    continue
            else:
                self.data = json.loads(self._response.content.decode('utf-8'))
                return self.data

    def _parse_data(self, data: dict):
        for i in range(len(data["skills"])):
            try:
                self.__setattr__(entries_dict[data["skills"][i]["name"]], SkillEntry(data["skills"][i]))
            except KeyError:
                warn(f'Skill {data["skills"][i]["name"]} at id: {i} not recognized.'
                     f' Potential update to highscores found.')

        for i in range(len(activity_attributes)):
            try:
                self.__setattr__(entries_dict[data["activities"][i]["name"]], ActivityEntry(data["activities"][i]))
            except KeyError:
                warn(f'Activity {data["activities"][i]["name"]} at id: {i} not recognized.'
                     f' Potential update to highscores found.')

        for i in range(len(boss_attributes)):
            idx = len(activity_attributes) + i
            try:
                self.__setattr__(entries_dict[data["activities"][idx]["name"]], BossEntry(data["activities"][idx]))
            except KeyError:
                warn(f'Boss {data["activities"][idx]["name"]} at id: {idx} not recognized.'
                     f' Potential update to highscores found.')

    def update(self):
        self._parse_data(self._fetch_data())

    def get_all_scores(self):
        """Returns a list of XP for all skills, score for all activities, and KC for all bosses.

        :return: list of ints with length n_entries.
        """
        score_list = []
        for i in range(len(skill_attributes)):
            _entry = self.__getattribute__(skill_attributes[i]).xp
            if _entry <= 0:
                _entry = 0
            score_list.append(_entry)
        for i in range(len(activity_attributes)):
            _entry = self.__getattribute__(activity_attributes[i]).score
            if _entry <= 0:
                _entry = 0
            score_list.append(_entry)
        for i in range(len(boss_attributes)):
            _entry = self.__getattribute__(boss_attributes[i]).kc
            if _entry <= 0:
                _entry = 0
            score_list.append(_entry)

        return score_list

    def get_all_levels(self):
        """Returns a list of all levels listed on the highscores for a given player. Any level not listed
        is assumed to be 1.
        """
        levels = []
        for i in range(n_skills):
            _entry = self.__getattribute__(skill_attributes[i]).level
            if _entry <= 1:
                _entry = 1
            levels.append(_entry)
        return levels

    def get_all_xp(self):
        """Returns a list of experience for all skills listed on the highscores for a given player. Any skill not
        listed is assumed to have 0 XP.
        """
        xp = []
        for i in range(n_skills):
            _entry = self.__getattribute__(skill_attributes[i]).xp
            if _entry <= 0:
                _entry = 0
            xp.append(_entry)
        return xp

    def get_all_activity_scores(self):
        """Returns a list of scores for all activities listed on the highscores for a given player. Any activity not
            listed is assumed to have a score of 0.
            """
        scores = []
        for i in range(n_activities):
            _entry = self.__getattribute__(activity_attributes[i]).score
            if _entry <= 0:
                _entry = 0
            scores.append(_entry)
        return scores

    def get_all_kc(self):
        """Returns a list of KC for all bosses listed on the highscores for a given player. Any boss not
            listed is assumed to have 0 KC.
            """
        kc = []
        for i in range(n_bosses):
            _entry = self.__getattribute__(boss_attributes[i]).kc
            if _entry <= 0:
                _entry = 0
            kc.append(_entry)
        return kc

    # TODO handle ordering of attributes in __str__ and __repr__
    def __repr__(self) -> dict:
        self._rep_dict = dict()
        for k in entries_dict:
            self._rep_dict[entries_dict[k]] = self.__getattribute__(entries_dict[k])
        _rep = dict()
        _rep[self.rsn] = self._rep_dict
        return _rep

    def __str__(self):
        return pformat(self.__repr__())
