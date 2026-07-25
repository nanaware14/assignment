from django.urls import path

from . import api_views, views


urlpatterns = [
    path("", views.lead_capture, name="lead_capture"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("leads/", views.lead_list, name="lead_list"),
    path("leads/create/", views.lead_create, name="lead_create"),
    path("leads/<int:pk>/", views.lead_detail, name="lead_detail"),
    path("leads/<int:pk>/edit/", views.lead_update, name="lead_update"),
    path("leads/<int:pk>/delete/", views.lead_delete, name="lead_delete"),
    path("leads/<int:pk>/assign/", views.lead_assign, name="lead_assign"),
    path("leads/<int:pk>/status/", views.lead_status_update, name="lead_status_update"),
    path("leads/<int:pk>/notes/", views.lead_note_create, name="lead_note_create"),
    path("users/", views.user_list, name="user_list"),
    path("users/create/", views.user_create, name="user_create"),
    path("users/<int:pk>/edit/", views.user_update, name="user_update"),
    path("activity/", views.activity_log, name="activity_log"),
    path("api/leads/", api_views.LeadListCreateAPIView.as_view(), name="api_lead_list"),
    path("api/leads/<int:pk>/", api_views.LeadRetrieveUpdateDestroyAPIView.as_view(), name="api_lead_detail"),
]
