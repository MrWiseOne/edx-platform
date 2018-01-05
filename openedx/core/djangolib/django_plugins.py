from django.conf.urls import include, url
from openedx.core.lib.plugins import PluginManager


class ProjectType(object):
    lms = u'lms.djangoapp'
    cms = u'cms.djangoapp'


class PluginURL(object):
    config = u'url_config'
    namespace = u'namespace'
    prefix = u'prefix'
    relative_path = u'relative_path'


PLUGIN_APP_CLASS_ATTRIBUTE_NAME = u'plugin_app'


class DjangoAppRegistry(PluginManager):

    @classmethod
    def get_installable_apps(cls, project_type):
        """
        Returns a list of all registered django apps.
        """
        return [
            u'{module_name}.{class_name}'.format(
                module_name=app_config.__module__,
                class_name=app_config.__name__,
            )
            for app_config in cls._get_app_configs(project_type)
            if getattr(app_config, PLUGIN_APP_CLASS_ATTRIBUTE_NAME, True)
        ]

    @classmethod
    def get_plugin_url_patterns(cls, project_type):
        return [
            url(
                cls._get_url_prefix(url_config),
                include(url_module_path, namespace=url_config[PluginURL.namespace]),
            )
            for url_module_path, url_config in cls.iter_installable_urls(project_type)
        ]

    @classmethod
    def iter_installable_urls(cls, project_type):
        for app_config in cls._get_app_configs(project_type):
            url_config = cls._get_url_config(app_config, project_type)
            if not url_config:
                continue

            urls_module_path = u'{package_path}.{module_path}'.format(
                package_path=app_config.name,
                module_path=url_config.get(PluginURL.relative_path, u'urls'),
            )
            url_config[PluginURL.namespace] = url_config.get(PluginURL.namespace, app_config.name)
            yield urls_module_path, url_config

    @classmethod
    def _get_app_configs(cls, project_type):
        return cls.get_available_plugins(project_type).itervalues()

    @classmethod
    def _get_url_config(cls, app_config, project_type):
        plugin_config = getattr(app_config, PLUGIN_APP_CLASS_ATTRIBUTE_NAME, {})
        url_config = plugin_config.get(PluginURL.config, {})
        return url_config.get(project_type, {})

    @classmethod
    def _get_url_prefix(cls, url_config):
        prefix = url_config.get(PluginURL.prefix)
        if prefix:
            return r'^{}'.format(prefix)
        else:
            return r''
