from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('blog/', views.blog, name='blog'),
    path('blog-details/', views.blog_details, name='blog_details'),
    path('portfolio-details/', views.portfolio_details, name='portfolio_details'),
    path('service-details/', views.service_details, name='service_details'),
    path('starter/', views.starter, name='starter'),
]