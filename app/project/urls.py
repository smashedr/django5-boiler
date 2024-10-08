from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import include
from django.contrib import admin
from django.urls import path
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    path('', include('home.urls')),
    path('oauth/', include('oauth.urls')),
    path('admin/', admin.site.urls),
    path('flower/', RedirectView.as_view(url='/flower/'), name='flower'),
    path('redis/', RedirectView.as_view(url='/redis/'), name='redis'),
    path('phpmyadmin/', RedirectView.as_view(url='/phpmyadmin/'), name='phpmyadmin'),
    path('flush-cache/', views.flush_cache_view, name='flush_cache'),
    path('app-health-check/', views.health_check, name='health_check'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = 'project.views.handler400_view'
handler403 = 'project.views.handler403_view'
handler404 = 'project.views.handler404_view'
handler500 = 'project.views.handler500_view'

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path('debug/', include(debug_toolbar.urls))] + urlpatterns
