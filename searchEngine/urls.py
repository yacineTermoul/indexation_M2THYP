
from django.urls import path
from .views import my_view, home,search_view,loginView,logoutView,deleteDoc,crawler


urlpatterns = [
    #path('', home),
    path('upload/', my_view, name='my-view'),
    path('post/', crawler),
    # path('upload/', crawler, name='crawler'),
    path('', search_view, name='search-view'),
    path('login/', loginView, name='login-view'),
    path('logout/', logoutView, name='logout-view'),
    path('delete/<id>', deleteDoc, name='deleteDoc'),

]
