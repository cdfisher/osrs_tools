"""url_builder.py - Chris Fisher "cdfisher", 2023
Functions for building URLs to query the OSRS Highscores API for use in the
highscores submodule.
"""


def _parse_target(target: str) -> str:
    if target == 'default':
        return 'hiscore_oldschool'
    elif target == 'ironman':
        return 'hiscore_oldschool_ironman'
    elif target == 'ultimate':
        return 'hiscore_oldschool_ultimate'
    elif target == 'hardcore_ironman':
        return 'hiscore_oldschool_hardcore_ironman'
    elif target == 'seasonal':
        return 'hiscore_oldschool_seasonal'
    elif target == 'deadman':
        return 'hiscore_oldschool_deadman'
    elif target == 'tournament':
        return 'hiscore_oldschool_tournament'
    elif target == 'fresh_start':
        return 'hiscore_oldschool_fresh_start'
    elif target == 'skiller':
        return 'hiscore_oldschool_skiller'
    elif target == 'skiller_defence':
        return 'hiscore_oldschool_skiller_defence'
    else:
        raise ValueError(f'Invalid highscores target :{target}')


def build_url(target: str, rsn: str) -> str:
    return f'https://secure.runescape.com/m={_parse_target(target)}/index_lite.json?player={rsn}'
