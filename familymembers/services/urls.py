from django.contrib.auth import views as auth_views
from django.urls import path,include
from .import views
urlpatterns = [  

    path('agency/signup/', views.agency_signup, name='agency_signup'),
    path('agency/dashboard/', views.agency_dashboard, name='agency_dashboard'),

    path('staff/list', views.staff_list, name='staff_list'),
    
    path('staff/add/', views.add_staff, name='add_staff'),
    path('staff/<int:staff_id>/view/', views.view_staff, name='view_staff'),

    path('staff/<int:staff_id>/edit/', views.edit_staff, name='edit_staff'),   
    path('staff/<int:pk>/delete/', views.delete_staff, name='delete_staff'),
    path('staff/<int:pk>/activate/', views.activate_staff, name='activate_staff'),
    path('staff/<int:pk>/deactivate/', views.deactivate_staff, name='deactivate_staff'),


]