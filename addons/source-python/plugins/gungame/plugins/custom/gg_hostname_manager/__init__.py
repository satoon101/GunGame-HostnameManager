# ../gungame/plugins/custom/gg_hostname_manager/__init__.py

"""Plugin to dynamically set the hostname."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Site-package
from configobj import ConfigObj

# GunGame
from gungame.core.paths import GUNGAME_DATA_PATH

# Plugin
from .info import info

# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
database = ConfigObj(GUNGAME_DATA_PATH / info.name + ".ini", unrepr=True)


# =============================================================================
# >> FUNCTIONS
# =============================================================================
def _create_database_file():
    database["Settings"] = {}
    database["Settings"]["base_name"] = "So and so's GunGame Server"
    database["Settings"]["base_break"] = " - "
    database["Settings"]["feature_break"] = " | "
    for name, verbose_name, priority in (
        ("gg_teamplay", "TeamPlay", 1),
        ("gg_teamwork", "TeamWork", 1),
        ("gg_ffa", "Free For All", 1),
        ("gg_deathmatch", "DeathMatch", 2),
        ("gg_elimination", "Elimination", 2),
        ("gg_bombing_objective", "Bombing", 3),
        ("gg_hostage_objective", "Hostage", 3),
    ):
        database[name] = {}
        database[name]["name"] = verbose_name
        database[name]["priority"] = priority
        database.comments[name] = [""]
    database.write()


if not database:
    _create_database_file()
