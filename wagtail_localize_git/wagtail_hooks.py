from django.urls import path, include, reverse
from django.utils.translation import ugettext_lazy as _
from django.views.i18n import JavaScriptCatalog

from wagtail.admin.menu import MenuItem
from wagtail.core import hooks

from . import views


@hooks.register("register_admin_urls")
def register_admin_urls():
    urls = [
        path("/", views.dashboard, name="dashboard"),
        path("force-sync/", views.force_sync, name="force_sync"),
        path('jsi18n/', JavaScriptCatalog.as_view(packages=['wagtail_localize_git']), name='javascript_catalog'),
    ]

    return [
        path(
            "localize/git/",
            include(
                (urls, "wagtail_localize_git"),
                namespace="wagtail_localize_git",
            ),
        )
    ]


class PontoonMenuItem(MenuItem):
    def is_shown(self, request):
        return True


@hooks.register("register_settings_menu_item")
def register_menu_item():
    return PontoonMenuItem(
        _("Pontoon"),
        reverse("wagtail_localize_git:dashboard"),
        classnames="icon icon-site",
        order=500,
    )
