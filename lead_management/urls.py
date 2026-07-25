from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),

    # Custom Login Page
    path(
        "registration/login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),

    # Logout
    path(
        "registration/logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),

  

    # CRM App URLs
    path("", include("crm.urls")),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()

handler400 = "crm.views.bad_request"
handler403 = "crm.views.permission_denied"
handler404 = "crm.views.page_not_found"
handler500 = "crm.views.server_error"