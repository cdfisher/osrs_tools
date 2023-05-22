"""calculators.py - Chris Fisher "cdfisher", 2023
Calculators submodule of osrs-tools. Provides functions to calculate various
useful pieces of information for Old School RuneScape players.
"""

from math import floor
from resources.entries import *
from resources.utils import EHB_RATES


def calc_combat_level(attack: int, defence: int, strength: int, hitpoints: int, ranged: int,
                      prayer: int, magic: int) -> int:
    """Calculates a player's combat level.

    @:param attack:      Player's level in the Attack skill.
    @:param defence:     Player's level in the Defence skill.
    @:param strength:    Player's level in the Strength skill.
    @:param hitpoints:   Player's level in the Hitpoints skill.
    @:param ranged:      Player's level in the Ranged skill.
    @:param prayer:      Player's level in the Prayer skill.
    @:param magic:       Player's level in the Magic skill.

    @:returns int : the player's combat level.
    """
    base_lvl = round((0.25 * (float(defence) + float(hitpoints) + floor((float(prayer) * 0.5)))), 4)
    melee_lvl = round((13 / 40) * (float(attack) + float(strength)), 4)
    range_lvl = round((13 / 40) * floor((float(ranged) * (3 / 2))), 4)
    mage_lvl = round((13 / 40) * floor((float(magic) * (3 / 2))), 4)

    return floor(base_lvl + max(melee_lvl, range_lvl, mage_lvl))


def ehb_entry(kc: int, boss: str, is_iron: bool) -> float:
    if is_iron:
        return kc / EHB_RATES[boss][1]
    else:
        return kc / EHB_RATES[boss][0]


def ehb_from_list(kc_list: list, is_iron=False) -> float:
    """Calculates a player's efficient hours bossed and returns it
        as a float.
        @:param kc_list: list representing a player's KC for each boss

        @:return float correspoding to the player's efficient hours bossed.
        """
    # TODO having is_iron default to False may cause issues which might need to be addressed later
    total_ehb = 0.0
    for i in range(len(boss_attributes)):
        kc = kc_list[i]
        boss = boss_attributes[i]
        ehb = ehb_entry(kc, boss, is_iron)
        if (kc > 0) & (ehb > 0):
            total_ehb += ehb

    total_ehb = round(total_ehb, 2)
    return total_ehb
