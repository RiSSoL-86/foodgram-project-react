from django.contrib import admin
from django.shortcuts import render
from django.urls import include, path


def redoc(request):
    """Документация API."""
    return render(request, 'redoc.html')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('redoc/', redoc, name='redoc')
]
