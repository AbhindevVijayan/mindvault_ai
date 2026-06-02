from django.urls import path
from .views import (
    index,
    add_bookmark,
    summarize,
    semantic_search,
    signup,
    dashboard,
    login_user,
    chat,
    admin_panel,
    admin_user_detail,
    admin_edit_bookmark
    ,admin_users_list, admin_bookmarks_list
)

urlpatterns = [
    path('', index, name='index'),
    path('summarize/', summarize, name='summarize'),
    path('search/', semantic_search, name='semantic_search'),
    path('signup/', signup, name='signup'),
    path('login/', login_user, name='login_user'),
    path('chat/', chat, name='chat'),
    path('dashboard/', dashboard, name='dashboard'),
    path('admin-panel/', admin_panel, name='admin_panel'),
    # Backwards-compatible alias (underscore) in case external links use it
    path('admin_panel/', admin_panel, name='admin_panel_underscore'),
    path('admin-panel/users/', admin_users_list, name='admin_users_list'),
    path('admin-panel/bookmarks/', admin_bookmarks_list, name='admin_bookmarks_list'),
    path('admin-panel/users/<int:user_id>/', admin_user_detail, name='admin_user_detail'),
    path('admin-panel/bookmark/<int:bookmark_id>/edit/', admin_edit_bookmark, name='admin_edit_bookmark'),
]


