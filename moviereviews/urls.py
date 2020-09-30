from django.urls import path
from django.conf.urls import include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from.import views

urlpatterns = [

    # path('', views.home, name='home'),
    path('login',views.login,name="login"),
    path('signup',views.signup,name="signup"),
    path('', views.home1, name='home1'),
    path('about', views.about, name='about'),
    path("logout",views.logout,name="logout"),
    path("recommend",views.recommend,name="recommend"),
    path('<int:movie_id>/<int:imdb_id>/', views.detail, name='detail'),
    path('myratings/', views.myratings, name='myratings'),
    path('myratings/delete/<int:id>/', views.delete_rating, name='delete_rating'),
    path('myratings/update/', views.update_rating, name='update_rating'),

]

urlpatterns+=staticfiles_urlpatterns()