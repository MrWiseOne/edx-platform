from openedx.core.lib.plugins import PluginManager


class ProjectType(object):
    lms = 'lms.djangoapp'
    cms = 'cms.djangoapp'


class DjangoAppRegistry(PluginManager):

    @classmethod
    def get_installable_apps(cls, project_type):
        """
        Returns a list of all registered django apps.
        """
        return [
            u'{module_name}.{class_name}'.format(
                module_name=plugin.__module__,
                class_name=plugin.__name__,
            )
            for plugin in
            cls.get_available_plugins(project_type).itervalues()
        ]
