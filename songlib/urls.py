from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app import views

router = DefaultRouter()
router.register(r"setlistsongs", views.SetListSongViewSet)


urlpatterns = [
    # Auth
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(redirect_authenticated_user=True),
        name="login",
    ),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("accounts/register/", views.register_view, name="register"),
    # Songs
    path("songs/", views.song_list, name="song_list"),
    path("songs/create/", views.song_create, name="song_create"),
    path("songs/<int:pk>/edit/", views.song_edit, name="song_edit"),
    path("songs/<int:pk>/delete/", views.song_delete, name="song_delete"),
    path("songs/search/", views.song_search_api, name="song_search_api"),
    # Categories
    path("categories/", views.category_list, name="category_list"),
    path("categories/<int:pk>/edit/", views.category_edit, name="category_edit"),
    path(
        "categories/<int:pk>/delete/",
        views.category_delete,
        name="category_delete",
    ),
    # Tags
    path("tags/", views.tag_list, name="tag_list"),
    path("tags/<int:pk>/edit/", views.tag_edit, name="tag_edit"),
    path("tags/<int:pk>/delete/", views.tag_delete, name="tag_delete"),
    path("tags/search/", views.tag_search_api, name="tag_search_api"),
    # Set Lists
    path("setlists/", views.setlist_list, name="setlist_list"),
    path("setlists/create/", views.setlist_create, name="setlist_create"),
    path("setlists/<int:pk>/edit/", views.setlist_edit, name="setlist_edit"),
    path("setlists/<int:pk>/delete/", views.setlist_delete, name="setlist_delete"),
    path(
        "setlists/<int:pk>/add-song/",
        views.setlist_add_song,
        name="setlist_add_song",
    ),
    path(
        "setlists/<int:pk>/remove-song/<int:song_pk>/",
        views.setlist_remove_song,
        name="setlist_remove_song",
    ),
    path(
        "setlists/<int:pk>/reorder/",
        views.setlist_reorder,
        name="setlist_reorder",
    ),
    # Existing public views
    path("setlist/<int:setlist_id>/", views.setlist_detail, name="setlist_detail"),
    path(
        "setlist/<int:setlist_id>/export.txt",
        views.setlist_export_txt,
        name="setlist_export_txt",
    ),
    path(
        "setlist/<int:setlist_id>/reader/",
        views.setlist_reader,
        name="setlist_reader",
    ),
    # API & Admin
    path("api/", include(router.urls)),
    path("admin/", admin.site.urls),
    # Root redirect
    path("", views.song_list),
]
