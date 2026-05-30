from django.urls import path
from .views import add_bookmark
from .views import (
    add_bookmark,
    semantic_search
)
from .views import signup
from .views import dashboard 

urlpatterns = [
    path('', add_bookmark, name='add_bookmark'),
    path('search/', semantic_search, name='semantic_search'),
    path('signup/', signup, name='signup'),
    path('dashboard/', dashboard, name='dashboard'),
]


