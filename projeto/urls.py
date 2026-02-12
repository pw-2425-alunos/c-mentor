from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('geral/', include('app.urls')),
    path('', include('mentoria.urls')),
    path('deisihub/', include('deisihub.urls')),
    path('accounts/', include('allauth.urls')),
#    path('impersonate/', include('impersonate.urls')),
]


urlpatterns += static(
      settings.MEDIA_URL,
      document_root=settings.MEDIA_ROOT)