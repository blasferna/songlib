from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app import views

router = DefaultRouter()
router.register(r"setlistsongs", views.SetListSongViewSet)


urlpatterns = [
    path("setlist/<int:setlist_id>/", views.setlist_detail, name="setlist_detail"),
    path(
        "setlist/<int:setlist_id>/export.txt",
        views.setlist_export_txt,
        name="setlist_export_txt",
    ),
    path("api/", include(router.urls)),
    path("", admin.site.urls),
]
