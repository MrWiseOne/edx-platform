
from django.apps import AppConfig
from openedx.core.djangolib.django_plugins import ProjectType, PluginURL


plugin_urls_config = {PluginURL.namespace: u'theming', PluginURL.prefix: u'theming/'}


class ThemingConfig(AppConfig):
    name = 'openedx.core.djangoapps.theming'
    plugin_app = {
        PluginURL.config: {
            ProjectType.cms: plugin_urls_config,
            ProjectType.lms: plugin_urls_config,
        }
    }
    verbose_name = "Theming"

    def ready(self):
        # settings validations related to theming.
        from . import checks
