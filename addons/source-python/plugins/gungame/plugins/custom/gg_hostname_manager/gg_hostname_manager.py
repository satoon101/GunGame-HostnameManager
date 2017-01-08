# ../gungame/plugins/custom/gg_hostname_manager/gg_hostname_manager.py

"""Dynamically set the hostname based on loaded plugins."""

# =============================================================================
# >> IMPORTS
# =============================================================================
from configobj import ConfigObj

from cvars import ConVar
from events import Event
from filters.entities import EntityIter
from listeners import OnLevelInit
from listeners.tick import Delay

from gungame.core.paths import GUNGAME_DATA_PATH
from gungame.core.plugins.manager import gg_plugin_manager

from .info import info


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
database = ConfigObj(GUNGAME_DATA_PATH / info.name + '.ini')


# =============================================================================
# >> CLASSES
# =============================================================================
class _HostnameManager(object):
    """Class used to set the hostname."""

    def __init__(self):
        """Store the base delay."""
        self.delay = Delay(0.1, self._set_hostname)

    def set_hostname(self):
        """Delay changing the hostname."""
        # Is there currently a delay?
        if self.delay is not None:

            # Cancel the delay
            self.delay.cancel()

        # Delay before setting the hostname
        self.delay = Delay(0.2, self._set_hostname)

    def _set_hostname(self):
        """Set the hostname to show GunGame and Included/Custom Plugins."""
        # Set the delay back to None
        self.delay = None

        # Get the basename
        value = database['Settings']['base_name']

        # Create an empty dictionary
        plugin_values = dict()

        # Loop through all plugins in the database
        for plugin_name, values in database.items():

            # Is the plugin loaded?
            if plugin_name in gg_plugin_manager:

                if (
                    plugin_name == 'gg_bombing_objective' and
                    not len(EntityIter('func_bomb_target'))
                ):
                    continue

                if (
                    plugin_name == 'gg_hostage_objective' and
                    not len(EntityIter('func_hostage_rescue'))
                ):
                    continue

                # Store the plugin's name and priority
                plugin_values[values['name']] = int(values['priority'])

        # Are there any plugins that are loaded?
        if plugin_values:

            # Add the base_break to the string
            value += database['Settings']['base_break']

            # Sort the loaded plugins by their priority
            plugins = sorted(
                plugin_values,
                key=lambda plugin: plugin_values[plugin],
            )

            # Add all loaded plugins to the string
            # Separate each with the feature_break
            value += database['Settings']['feature_break'].join(plugins)

        # Set the hostname to the new value
        ConVar('hostname').set_string(value)

hostname_manager = _HostnameManager()


# =============================================================================
# >> GUNGAME EVENTS
# =============================================================================
@Event('gg_plugin_loaded', 'gg_plugin_unloaded')
@OnLevelInit
def update_hostname(arg):
    """Check to see if the hostname needs updated."""
    hostname_manager.set_hostname()
