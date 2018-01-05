from importlib import import_module
from django.conf.urls import include, url
from logging import getLogger
from openedx.core.lib.plugins import PluginManager


log = getLogger(__name__)


PLUGIN_APP_CLASS_ATTRIBUTE_NAME = u'plugin_app'
PLUGIN_APP_SETTINGS_FUNC_NAME = u'plugin_settings'


class ProjectType(object):
    lms = u'lms.djangoapp'
    cms = u'cms.djangoapp'


class SettingsType(object):
    aws = u'aws'
    common = u'common'
    devstack = u'devstack'
    test = u'test'


class PluginSettings(object):
    config = u'settings_config'
    relative_path = u'relative_path'
    DEFAULT_RELATIVE_PATH = u'settings'


class PluginURL(object):
    config = u'url_config'
    app_name = u'app_name'
    namespace = u'namespace'
    prefix = u'prefix'
    relative_path = u'relative_path'
    DEFAULT_RELATIVE_PATH = u'urls'


class DjangoAppRegistry(PluginManager):

    @classmethod
    def get_plugin_apps(cls, project_type):
        """
        Returns a list of all registered django apps.
        """
        plugin_apps = [
            u'{module_name}.{class_name}'.format(
                module_name=app_config.__module__,
                class_name=app_config.__name__,
            )
            for app_config in cls._get_app_configs(project_type)
            if getattr(app_config, PLUGIN_APP_CLASS_ATTRIBUTE_NAME, True)
        ]
        log.info(u'Plugin Apps: Found %s', plugin_apps)
        return plugin_apps

    @classmethod
    def import_plugin_settings(cls, base_module_path, project_type, settings_type):
        base_module = import_module(base_module_path)
        for settings_module in cls.iter_plugin_settings(project_type, settings_type):
            settings_func = getattr(settings_module, PLUGIN_APP_SETTINGS_FUNC_NAME)
            settings_func(base_module)

    @classmethod
    def iter_plugin_settings(cls, project_type, settings_type):
        for app_config in cls._get_app_configs(project_type):
            settings_config = _get_settings_config(app_config, project_type, settings_type)
            if settings_config is None:
                log.info(
                    u'Plugin Apps [Settings]: Did NOT find %s for %s and %s',
                    app_config.name,
                    project_type,
                    settings_type,
                )
                continue

            settings_module_path = _get_module_path(app_config, settings_config, PluginSettings)
            log.info(u'Plugin Apps [Settings]: Found %s for %s and %s', app_config.name, project_type, settings_type)
            yield import_module(settings_module_path)

    @classmethod
    def get_plugin_url_patterns(cls, project_type):
        return [
            url(
                _get_url_prefix(url_config),
                include(
                    url_module_path,
                    app_name=url_config.get(PluginURL.app_name),
                    namespace=url_config[PluginURL.namespace],
                ),
            )
            for url_module_path, url_config in cls.iter_installable_urls(project_type)
        ]

    @classmethod
    def iter_installable_urls(cls, project_type):
        for app_config in cls._get_app_configs(project_type):
            url_config = _get_url_config(app_config, project_type)
            if url_config is None:
                log.info(u'Plugin Apps [URLs]: Did NOT find %s for %s', app_config.name, project_type)
                continue

            urls_module_path = _get_module_path(app_config, url_config, PluginURL)
            url_config[PluginURL.namespace] = url_config.get(PluginURL.namespace, app_config.name)
            log.info(
                u'Plugin Apps [URLs]: Found %s with namespace %s for %s',
                app_config.name,
                url_config[PluginURL.namespace],
                project_type,
            )
            yield urls_module_path, url_config

    @classmethod
    def _get_app_configs(cls, project_type):
        return cls.get_available_plugins(project_type).itervalues()


def _get_module_path(app_config, plugin_config, plugin_cls):
    return u'{package_path}.{module_path}'.format(
        package_path=app_config.name,
        module_path=plugin_config.get(plugin_cls.relative_path, plugin_cls.DEFAULT_RELATIVE_PATH),
    )


def _get_settings_config(app_config, project_type, settings_type):
    plugin_config = getattr(app_config, PLUGIN_APP_CLASS_ATTRIBUTE_NAME, {})
    settings_config = plugin_config.get(PluginSettings.config, {})
    project_type_settings = settings_config.get(project_type, {})
    return project_type_settings.get(settings_type)


def _get_url_config(app_config, project_type):
    plugin_config = getattr(app_config, PLUGIN_APP_CLASS_ATTRIBUTE_NAME, {})
    url_config = plugin_config.get(PluginURL.config, {})
    return url_config.get(project_type)


def _iter_uppercase_attributes(obj):
    def _is_uppercase(val):
        return val == val.upper() and not val.startswith('_')

    for name in filter(_is_uppercase, dir(obj)):
        yield name, getattr(obj, name)


def _get_url_prefix(url_config):
    prefix = url_config.get(PluginURL.prefix)
    return r'^{}'.format(prefix) if prefix else r''
