from django.apps import AppConfig


class WagtailLocalizeGitTestAppConfig(AppConfig):
    label = "wagtail_localize_git_test"
    name = "testapp"
    verbose_name = "Localize Git tests"
    default_auto_field = "django.db.models.AutoField"
