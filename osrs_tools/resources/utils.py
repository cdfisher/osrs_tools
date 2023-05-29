"""utils.py - Chris Fisher "cdfisher", 2023
File containing various utility functions and reference tables for use in other
submodules.
"""

import requests
from .url_builder import build_url

# Reference information:

"""EHB_RATES:
    Dict of bosses and their respective kills per efficient bossing hour.
    EHB_RATES(boss) returns a tuple of length 2 as a key.
    key[0] is the EHB rate for main accounts, and key[1] is the rate for ironman accounts.
    A rate value of -1.0 indicates boss kills do not count toward EHB for that account type.
    Rates have been sourced from https://wiseoldman.net/rates/ehb
    """
EHB_RATES = {'abyssal_sire': (45.0, 32.0),
             'alchemical_hydra': (33.0, 29.0),
             'artio': (-1.0, -1.0),
             'barrows_chests': (-1.0, 22.0),
             'bryophyta': (-1.0, 9.0),
             'callisto': (50.0, 30.0),
             'calvar_ion': (-1.0, -1.0),
             'cerberus': (61.0, 54.0),
             'chambers_of_xeric': (3.0, 2.9),
             'chambers_of_xeric_challenge_mode': (2.4, 2.0),
             'chaos_elemental': (60.0, 48.0),
             'chaos_fanatic': (100.0, 80.0),
             'commander_zilyana': (55.0, 28.0),
             'corporeal_beast': (60.0, 8.5),
             'crazy_archaeologist': (-1.0, 75.0),
             'dagannoth_prime': (100.0, 100.0),
             'dagannoth_rex': (100.0, 100.0),
             'dagannoth_supreme': (100.0, 100.0),
             'deranged_archaeologist': (-1.0, 80.0),
             'general_graardor': (55.0, 25.0),
             'giant_mole': (100.0, 90.0),
             'grotesque_guardians': (36.0, 33.0),
             'hespori': (-1.0, 60.0),
             'kalphite_queen': (50.0, 33.0),
             'king_black_dragon': (120.0, 75.0),
             'kraken': (100.0, 82.0),
             'kree_arra': (40.0, 27.0),
             'kril_tsutsaroth': (65.0, 26.0),
             'mimic': (-1.0, 60.0),
             'nex': (13.0, 12.0),
             'nightmare': (14.0, 11.0),
             'phosanis_nightmare': (7.0, 6.5),
             'obor': (-1.0, 12.0),
             'phantom_muspah': (25.0, 25.0),
             'sarachnis': (80.0, 56.0),
             'scorpia': (130.0, 60.0),
             'skotizo': (45.0, 38.0),
             'spindel': (-1.0, -1.0),
             'tempoross': (-1.0, -1.0),
             'the_gauntlet': (10.0, 10.0),
             'the_corrupted_gauntlet': (7.0, 7.2),
             'theatre_of_blood': (3.0, 2.9),
             'theatre_of_blood_hard_mode': (3.0, 2.4),
             'thermonuclear_smoke_devil': (125.0, 100.0),
             'tombs_of_amascut': (3.5, 2.5),
             'tombs_of_amascut_expert_mode': (3.0, 2.0),
             'tzkal_zuk': (0.8, 0.9),
             'tztok_jad': (2.0, 2.0),
             'venenatis': (50.0, 35.0),
             'vet_ion': (30.0, 23.0),
             'vorkath': (34.0, 33.0),
             'wintertodt': (-1.0, -1.0),
             'zalcano': (-1.0, -1.0),
             'zulrah': (40.0, 39.0)}

# Utility methods


def is_ironman(rsn: str) -> bool:
    """Checks if a given player is an ironman by looking them up on the
    ironman highscores. This is a less-than-optimal solution and can provide
    false positives in the case that the player has de-ironed, but there isn't really
    any other way to check account status at this time.
    """
    def _query_hs(_rsn: str, endpoint='default'):
        max_retries = 5
        n_retries = 0
        while n_retries <= max_retries:
            _response = requests.get(build_url(endpoint, _rsn))
            if _response.status_code > 399:
                n_retries += 1
                if n_retries > max_retries:
                    raise ValueError(f'Data for user {_rsn} not found!')
                else:
                    continue
            else:
                return

    try:
        _query_hs(rsn, 'ironman')
        return True
    except ValueError:
        try:
            _query_hs(rsn)
            return False
        except ValueError:
            raise ValueError(f'Player {rsn} not found on highscores!')
