# ../gungame/plugins/custom/gg_hostname_manager/gg_hostname_manager.py

"""Dynamically set the hostname based on loaded plugins."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
from cvars import ConVar
from events import Event
from filters.entities import BaseEntityIter
from listeners import OnLevelInit
from listeners.tick import Delay

# GunGame
from gungame.core.plugins.manager import gg_plugin_manager

# Plugin
from . import database


# =============================================================================
# >> CLASSES
# =============================================================================
class _HostnameManager:
    """Class used to set the hostname."""

    def __init__(self):
        """Store the base delay."""
        self._convar = ConVar("hostname")
        self._original_hostname = str(self._convar)
        self.delay = Delay(0.1, self._set_hostname)

    def reset_hostname(self):
        """Set the hostname back to the original value on unload."""
        self._convar.set_string(self._original_hostname)

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

        # Set the hostname to the new value
        self._convar.set_string(self.get_hostname_value())

    @staticmethod
    def get_hostname_value():
        """Return the full value of the new hostname."""
        # Get the basename
        value = database["Settings"]["base_name"]

        # Create an empty dictionary
        plugin_values = {}

        # Loop through all plugins in the database
        for plugin_name, values in database.items():

            # Is the plugin loaded?
            if plugin_name in gg_plugin_manager:

                if (
                    plugin_name == "gg_bombing_objective" and
                    not list(BaseEntityIter("func_bomb_target"))
                ):
                    continue

                if (
                    plugin_name == "gg_hostage_objective" and
                    not list(BaseEntityIter("func_hostage_rescue"))
                ):
                    continue

                # Store the plugin's name and priority
                plugin_values[values["name"]] = int(values["priority"])

        # Are there any plugins that are loaded?
        if plugin_values:

            # Add the base_break to the string
            value += database["Settings"]["base_break"]

            # Sort the loaded plugins by their priority
            plugins = sorted(
                plugin_values,
                key=lambda plugin: plugin_values[plugin],
            )

            # Add all loaded plugins to the string
            # Separate each with the feature_break
            value += database["Settings"]["feature_break"].join(plugins)

        return value


hostname_manager = _HostnameManager()


# =============================================================================
# >> LOAD & UNLOAD
# =============================================================================
def unload():
    """Reset the hostname when unloading."""
    hostname_manager.reset_hostname()


# =============================================================================
# >> GUNGAME EVENTS
# =============================================================================
@Event("gg_plugin_loaded", "gg_plugin_unloaded")
@OnLevelInit
def update_hostname(*args):
    """Check to see if the hostname needs updated."""
    hostname_manager.set_hostname()
