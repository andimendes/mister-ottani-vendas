# misterottani_crm/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
     path('admin/', admin.site.urls),
     # Todas as nossas URLs de API começarão com 'api/'
     path('api/', include('gestao.urls')),
 ]