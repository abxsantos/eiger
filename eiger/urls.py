"""
URL configuration for eiger project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import URLPattern, URLResolver, include, path
from health_check import urls as health_urls

from eiger.trainers import urls as trainers_urls

urlpatterns: list[URLPattern | URLResolver] = [
    path('', include(trainers_urls)),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    # Health checks:
    path('healthcheck/', include(health_urls)),
]

if settings.DEBUG:  # pragma: no cover
    from django.conf.urls.static import static  # noqa: WPS433

    urlpatterns += [
        # URLs specific only to django-debug-toolbar:
        path('__debug__/', include('debug_toolbar.urls')),
        # Serving static files in development only:
        *static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
    ]
