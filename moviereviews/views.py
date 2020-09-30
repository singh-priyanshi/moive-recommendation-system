
from django.http import HttpResponseRedirect
from django.urls import reverse , reverse_lazy
from .models import LoginSignup  , Myrating
from django.shortcuts import render, redirect , get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User, auth
from . import Functions
from django.db.models import Q
from django.http import Http404
import pandas as pd
from imdb import IMDb
import time


# create an instance of the IMDb class
ia = IMDb()
current_ratings =[]
mymovies =[]
obj=Functions.Functions()



def detail(request,movie_id , imdb_id):
    if not request.user.is_authenticated:
        return redirect("login")
    if not request.user.is_active:
        raise Http404
    print(movie_id)
    print(imdb_id)
    print(type(imdb_id))
    movie_info = ia.get_movie(str(imdb_id))
    plot = movie_info['plot outline']
    cover= obj.get_poster(movie_id)
    print(cover)
    # for rating
    #     # if request.method == "POST":
    #     #     rate = request.POST['rating']
    #     #     ratingObject = Myrating()
    #     #     ratingObject.user   = request.user
    #     #     # ratingObject.movie_id  = movie_id
    #     #     # ratingObject.rating = rating
    #     #     ratingObject.save()
    #     #     messages.success(request,"Your Rating is submited ")
    #     #     return redirect("index")
    #     # context = {
    #     #     'title': movie_info['title']
    #     # }

    return render(request,'detail.html', {'movie_info':movie_info, 'cover' : cover , 'plot' : plot })

def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password1 = request.POST.get("password")
        password2 = request.POST.get("confirm_password")
        age = request.POST.get("age")
        email = request.POST.get("email")
        sex = request.POST.get("gender")
        profession = request.POST.get("profession")

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('signup')
            elif User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, password=password1, email=email)
                user.save()
                print(user)
                print('user created')
                Login_Signup = LoginSignup(UserName=username,
                                           email=email,
                                           Password=password1,
                                           Age=age,
                                           Sex=sex,
                                           Profession=profession)
                Login_Signup.save()
                # return redirect('login')
                user = auth.authenticate(username=username, password=password1)

                if user is not None:
                    auth.login(request, user)
                    print('user logged in ')
                    return redirect('home1')
                else:
                    messages.error(request, 'Wrong Username or Password...')


                #home1 is for taking additional input from user fav. genres and ratings
                return render(request, 'home1.html')

        else:
            messages.error(request, 'password not matching..')
            return redirect('signup')
            # return redirect('/')

    else:
        return render(request, 'signup.html')


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect("/")
        else:
            messages.error(request, 'Wrong Username or Password...')
            return redirect('login')

    else:
        return render(request, 'login.html')


def home1(request):

    #messages.info(request, 'For best recommendations please rate atleast 20+ movies.... ')
    topRated = obj.top_rated_movies(500)
    q = request.GET.get('genre')
    s = request.GET.get('query')

    if request.method == "POST":
        my_rating = request.POST.get('myrating')
        mymovie_id = request.POST.get('sub-btn')
        my_user_id = request.user
        current_rating =[my_user_id, mymovie_id , my_rating]
        current_ratings.append(current_rating)
        # mymovies.append(mymovie_id)
        # print(my_rating)
        if my_rating != None:
            myrating= Myrating( user = my_user_id ,
                                  movie_id = mymovie_id ,
                                  rating = my_rating )
            myrating.save()
        else:
            messages.info(request, 'Invalid input...')
        # print( '{0} {1} {2}'.format(my_rating , mymovie_id , my_user_id ) )

    df = pd.DataFrame(list(Myrating.objects.all().values()))
    # print(df)
    # print(request.user.id)
    mymovies = df[df['user_id'] == request.user.id]['movie_id'].tolist()
    # my_rating
    # mymovies =

    if (q != None):
        # print(q)
        topNGenre = obj.Top_N_Movies_in_Genre(25, q)
        # print(topNGenre)
        # obj.retrivePoster(topNGenre)
        return render(request, 'home1.html', {'movies': topNGenre, 'genre': q , 'mymovies':mymovies})
    elif (s != None):
        # print(s)
        searchResult = obj.search_movie(s)
        # print(searchResult)
        return render(request, 'home1.html', {'movies': searchResult, 'query': s , 'mymovies':mymovies})
    else:
        return render(request, 'home1.html', {'movies': topRated , 'mymovies':mymovies})


def myratings(request):

    df = pd.DataFrame(list(Myrating.objects.all().values()))
    # print(df)
    # print(request.user.id)
   # df = df[df['user_id']==request.user.id]
    mymovies = obj.get_myMovieInfo(df)
    print(mymovies)
    return render(request, 'myratings.html', {'mymovies':mymovies})


def recommend(request):
    start = time.time()
    T_df = pd.DataFrame(list(Myrating.objects.all().values()))
    T_df.drop(['id'], axis=1 , inplace=True)
    T_df = T_df[T_df['user_id'] == request.user.id]
    print(T_df)
    mymovies = T_df['movie_id'].tolist()
    modi_r, trad_r, trad_MAE, modifid_MAE, trad_RMSE, modifid_RMSE = obj.get_recommendations(T_df)


    # print(trad_MAE, modifid_MAE)
    # print(trad_RMSE, modifid_RMSE)

    total_time = time.time() - start
    return render(request, 'recommend.html' , {'modi_r':modi_r ,
                                               'trad_MAE':trad_MAE ,
                                               'modifid_MAE':modifid_MAE ,
                                               'trad_RMSE':trad_RMSE ,
                                               'modifid_RMSE':modifid_RMSE,
                                               'mymovies': mymovies,
                                               'total_time' : total_time
                                               })


def delete_rating(request ,id =None):
    myratingObj = get_object_or_404(Myrating,id=id)
    if  request.method=='GET':
        myratingObj.delete()
    return HttpResponseRedirect(reverse('myratings'))

def update_rating(request):
    if request.method == 'POST':
        my_new_rating  = request.POST.get('myrating')
        id = request.POST.get('upd-rating')
        myratingObj = get_object_or_404(Myrating, id=id)
        myratingObj.rating = my_new_rating
        myratingObj.save()
    return HttpResponseRedirect(reverse('myratings'))

def about(request):
    return render(request, 'about.html')

def logout(request):
    auth.logout(request)
    return redirect('/')

'''

def home(request):
    q=None
    s=None
    q = request.POST.get('genre')
    s = request.POST.get('query')
    if (q!=None):
        print(q)
        topNGenre = obj.Top_N_Movies_in_Genre(25,q)
        print(topNGenre)
        # obj.retrivePoster(topNGenre)
        return render(request, 'home.html',{'movies':topNGenre,'genre':q})
    elif (s!=None):
        print(s)
        searchResult = obj.search_movie(s)
        print(searchResult)
        return render(request, 'home.html', {'movies': searchResult ,'query':s})
    else:
        return render(request, 'home.html')
        
'''