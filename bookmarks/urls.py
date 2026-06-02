from django.urls import path
from .views import (
    index,
    add_bookmark,
    summarize,
    semantic_search,
    signup,
    dashboard,
    login_user,
    chat
)

urlpatterns = [
    path('', index, name='index'),
    path('summarize/', summarize, name='summarize'),
    path('search/', semantic_search, name='semantic_search'),
    path('signup/', signup, name='signup'),
    path('login/', login_user, name='login_user'),
    path('chat/', chat, name='chat'),
    path('dashboard/', dashboard, name='dashboard'),
]


