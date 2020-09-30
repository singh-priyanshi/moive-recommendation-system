import pandas as pd
import numpy as np
import imdb

from sklearn.neighbors import NearestNeighbors
from scipy.spatial.distance import correlation, cosine,euclidean, minkowski
from sklearn.metrics import mean_absolute_error, mean_squared_error
from math import sqrt
import time

class Functions:

    def __init__(self):
        print('preprocessing start')
        self.user = pd.read_csv('D:\\moviesReviews\\Dataset\\user.csv', sep=",")
        self.rating = pd.read_csv('D:\\moviesReviews\\Dataset\\rating.csv', sep=",")
        self.movie = pd.read_csv('D:\\moviesReviews\\Dataset\\movie.csv', sep=",")
        self.user_genre_df = pd.read_csv('D:\\moviesReviews\\Dataset\\user_genre.csv', sep=",")

        # ------------------------- prediction start ------------------------
        self.user_genre_matrix = self.user_genre_df.pivot(index='user_id', columns='genre', values='proportion')
        self.user_item_matrix = self.rating.pivot(index='user_id', columns='movie_id', values='rating')
        self.user_mean = self.user_item_matrix.mean(axis=1)  # type float64
        self.user_item_matrix = self.user_item_matrix.fillna(0)

        self.model_knn_UI = NearestNeighbors(metric='cosine', algorithm='brute')  # insted of cosine try corelation also
        self.model_knn_UI.fit(self.user_genre_matrix)


        self.model_knn_USRD = NearestNeighbors(metric='cosine', algorithm='brute')  # insted of cosine try corelation also
        self.model_knn_USRD.fit(self.user_item_matrix)

        self.model_knn_trad = NearestNeighbors(metric='cosine', algorithm='brute')  # insted of cosine try corelation also
        self.model_knn_trad.fit(self.user_item_matrix)

        # --------------------------prediction end ---------------------------


        # -------------------------Genre-start----------------------------

        # merge the 'rating' table with the 'movie' table
        self.rating_movie = pd.merge(self.rating[['user_id', 'movie_id', 'rating']], self.movie, on='movie_id')
        self.rating_movie.drop(columns=['user_id', 'IMDb URL'], inplace=True)

        # -------------------------Genre-start----------------------------

        # -------------------------profession-start----------------------------

        # merge the 'rating' table with 'user' table
        self.rating_user = pd.merge(self.rating[['user_id', 'movie_id', 'rating']], self.user[['user_id', 'occupation']], on='user_id')
        self.rating_user.drop(columns=['user_id'], inplace=True)

        # merge the 'rating_User' dataframe with 'movie' dataframe to get each rating, occupation of user and title
        self.rating_user_movie = pd.merge(self.rating_user[['movie_id', 'rating', 'occupation']],
                                     self.movie[['movie_id', 'title', 'imdb_id', 'poster']], on='movie_id')

        # group the rating by occupation and title and sort with decreasing average ratings
        self.rating_user_movie_sorted = self.rating_user_movie.groupby(['occupation', 'title', 'movie_id', 'imdb_id', 'poster'], as_index=False)['rating'].mean().sort_values('rating', ascending=False)

        # -------------------------profession-end----------------------------

        # -------------------------age-start----------------------------

        # create a column of age_group in the users dataframe
        bin = [0, 6, 12, 18, 30, 50, 200]

        label = ['<=6', '<=12', '<=18', '<=30', '<=50', '50+']

        self.user['age_group'] = pd.cut(self.user['age'], bins=bin, labels=label, right=True)

        # merge the 'rating' table with the 'user' table
        self.rating_user_age = pd.merge(self.rating[['user_id', 'movie_id', 'rating']], self.user[['user_id', 'age_group']],
                                   on='user_id')
        self.rating_user_age.drop(columns=['user_id'], inplace=True)

        # merge the 'data_user_age' table with the 'item' table to get each rating, age_group of user and title
        self.data_user_item_age = pd.merge(self.rating_user_age[['movie_id', 'rating', 'age_group']],
                                      self.movie[['movie_id', 'title', 'imdb_id']], on='movie_id')
        # data_user_item_age.drop(columns = ['movie_id'], inplace=True)
        self.data_user_item_age['age_group'] = self.data_user_item_age['age_group'].astype('category')

        # group the data by age_group and title and sort with decreasing average ratings
        self.data_user_item_age_sorted = self.data_user_item_age.groupby(['age_group', 'title'], as_index=False)[
            'rating'].mean().sort_values('rating', ascending=False)

        # -------------------------------age-end----------------------------

        # ------------------------------ Prediction--------------------------
        self.movie_data_rating_data = self.movie.merge(self.rating, on='movie_id', how='inner')

        # ------------------------------ movieRatingCount start--------------------------
        # collection of count of ratings
        # 1* -> x   2* -> y
        self.movieRatingCount = self.movie_data_rating_data.groupby(['movie_id', 'title', 'rating'], as_index=False).size()
        self.movieRatingCount = pd.DataFrame(self.movieRatingCount)
        self.movieRatingCount.rename(columns={0: 'rating_count'}, inplace=True)

        # ------------------------------ movieRatingCount end--------------------------

        # ------------------------------ userCountRating start--------------------------

        self.userCountRating = self.movie_data_rating_data.groupby('user_id')['rating'].count().sort_values(ascending=False)
        # userCountRating[:350]

        # ------------------------------ userCountRating end--------------------------
        print('preprocessing end')

    def Profession(self,N,profession):
        temp = self.rating_user_movie_sorted[self.rating_user_movie_sorted['occupation'].str.contains(profession)][:N]
        # temp.loc[:,'title':'rating']
        return temp

    def Top_N_Movies_in_Genre(self,TopN,gen):
        # For each genre get the top N movies by average rating
        top_N_genre = pd.DataFrame()
        g_r = self.rating_movie[self.rating_movie[gen] == 1]
        # new_gen = pd.DataFrame(g_r.groupby(['title', 'movie_id', 'imdb_id', 'poster'], as_index=False)['rating'].mean().sort_values(['rating', 'title'], ascending=[False, True]).head(TopN))
        new_gen = pd.DataFrame(g_r.groupby(['title', 'movie_id', 'imdb_id', 'poster'], as_index=False)['rating'].mean().sort_values(['rating', 'title'], ascending=[False, True]))
        new_gen.insert(0, 'genre', gen)
        top_N_genre = top_N_genre.append(new_gen, ignore_index=True)
        return top_N_genre

    def Top_N_byAge(self,TopN, age):
        ageGrp='-1'
        if age <= 6:
            ageGrp = '<=6'
        elif age <= 12:
            ageGrp = '<=12'
        elif age <= 18:
            ageGrp = '<=18'
        elif age <= 30:
            ageGrp = '<=30'
        elif age <= 50:
            ageGrp = '<=50'
        elif age <= 200:
            ageGrp = '50+'

        print(ageGrp)

        # group data by occupation, title and select top 3 movies for each occupation
        top_N_age_all = self.data_user_item_age_sorted.groupby(['age_group']).head(TopN).sort_values(['age_group', 'title'],ascending=[True,True]).reset_index()
        top_N_age_all.drop(['index'], axis=1, inplace=True)

        top_N_age_new = top_N_age_all.merge(self.movie[['movie_id', 'title', 'imdb_id', 'poster']], on='title')
        top_N_age = top_N_age_new[top_N_age_new['age_group'] == ageGrp]

        return top_N_age

    def Users_who_rated_movieID_X(self,movie_id):

        demo= self.movie_data_rating_data[self.movie_data_rating_data['movie_id']==movie_id]
        return demo[['movie_id','title', 'user_id','rating']]

    def top_rated_movies(self,N):
        most_rated = self.movie_data_rating_data.groupby(['title', 'movie_id', 'imdb_id', 'poster'], as_index=False)['rating'].count().sort_values(by=['rating'], ascending=False)
        # most_rated= pd.DataFrame(most_rated)
        most_rated.reset_index(drop=True, inplace=True)
        most_rated.rename(columns={'rating': 'count'}, inplace=True)
        return most_rated[:N]

    # movies realsed in year ABCD
    def movie_yearWise(self,year_str):
        demo = self.movie_data_rating_data[self.movie_data_rating_data['title'].str.contains(year_str)]
        yearwise_list = pd.DataFrame(demo['title'].unique())
        yearwise_list.columns = ['title']
        yearwise_result = pd.merge(yearwise_list, self.movie[['movie_id', 'title', 'imdb_id', 'poster']], on='title')
        return yearwise_result

    def search_movie(self,search_str):
        demo = self.movie_data_rating_data[self.movie_data_rating_data['title'].str.contains(search_str, case=False)]
        search_list = pd.DataFrame(demo['title'].unique())
        search_list.columns = ['title']
        search_result = pd.merge(search_list, self.movie[['movie_id', 'title', 'imdb_id', 'poster']], on='title')
        return search_result

    def movie_rating_count(self,movie_id):
         movie_rating_info = self.movieRatingCount.loc[movie_id]
         x=movie_rating_info.iloc[0][0]
         # print('{0}'.format(x))
         x=movie_rating_info.iloc[1][0]
         # print('{0}'.format(x))
         x=movie_rating_info.iloc[2][0]
         # print('{0}'.format(x))
         x=movie_rating_info.iloc[3][0]
         # print('{0}'.format(x))
         x=movie_rating_info.iloc[4][0]
         # print('{0}'.format(x))

    def user_rating_count(self,user_id):
        return self.userCountRating.loc[user_id]

    def which_movies_user_rated(self,user_id):
        demo= self.movie_data_rating_data[self.movie_data_rating_data['user_id']==user_id]
        demo=demo.reset_index(drop=True)
        return demo[['user_id','movie_id','rating']]

    def common_movies_u1_u2(self,u1,u2):
        u1=self.which_movies_user_rated(u1)
        u2=self.which_movies_user_rated(u2)
        common_u1_u2 = pd.merge(u1, u2, how='inner', on=['movie_id'])
        return common_u1_u2

    def get_poster(self,movie_id):
        x = self.movie[self.movie['movie_id'] == movie_id]['poster']
        return x.iloc[0]

    def all_movies(self):
        return self.movie[['movie_id', 'title', 'imdb_id', 'poster']]

    def get_myMovieInfo(self, df):
        my_movie_info = pd.DataFrame(columns = ['movie_id','title', 'imdb_id', 'poster'])
        for row in df.itertuples():
            x = self.movie[self.movie['movie_id'] == row[3]][['movie_id','title', 'imdb_id', 'poster']]
            my_movie_info = my_movie_info.append(x , ignore_index = True )
        #print(my_movie_info)
        result = pd.merge(df , my_movie_info , on='movie_id' )
        #print(result)
        return result.reindex(index=result.index[::-1]) # to reverse dataframe so that latest rated movies will be searched

    def calculate_similarity(self, T_df, T_RD, T_UI, N):
        lamda = 0.5
        omega = 0.1

        u1 = T_df[['user_id', 'movie_id', 'rating']]

        distances, indices = self.model_knn_UI.kneighbors(T_UI.values.reshape(1, -1), n_neighbors=943)
        sim_UI = 1 - distances.flatten()
        index_UI = indices.flatten() + 1
        sim_index_list_UI = pd.DataFrame(list(zip(sim_UI, index_UI)), columns=['sim_UI', 'user_id'])
        sim_index_list_UI = sim_index_list_UI.sort_values(by='user_id')

        distances, indices = self.model_knn_USRD.kneighbors(T_RD.values.reshape(1, -1), n_neighbors=943)
        sim_USRD = 1 - distances.flatten()
        index_USRD = indices.flatten() + 1
        sim_index_list_USRD = pd.DataFrame(list(zip(sim_USRD, index_USRD)), columns=['sim_USRD', 'user_id'])
        sim_index_list_USRD = sim_index_list_USRD.sort_values(by='user_id')
        sim_index_list_USRD = sim_index_list_USRD.reset_index(drop=True)

        for i in range(len(sim_index_list_USRD)):
            u2 = self.which_movies_user_rated(int(sim_index_list_USRD.loc[i][
                                                 1]))
            common_u1_u2 = pd.merge(u1, u2, how='inner', on=['movie_id'])
            common_u1_u2['Ru1_Minus_Ru2_square'] = (common_u1_u2.rating_x - common_u1_u2.rating_y) ** 2
            # Nr=common_u1_u2['Ru1_Minus_Ru2_square'].sum()
            Nr = common_u1_u2['Ru1_Minus_Ru2_square'].mean()
            # Dr=common_u1_u2['Ru1_Minus_Ru2_square'].count()
            # Dr=common_u1_u2.shape[0]
            f = sqrt(Nr)
            sim_index_list_USRD.loc[i][0] = sim_index_list_USRD.loc[i][0] * (lamda ** f)

        final_sim = pd.merge(sim_index_list_UI, sim_index_list_USRD, how='inner', on=['user_id'])
        final_sim['final'] = (omega * final_sim.sim_USRD) + ((1 - omega) * final_sim.sim_UI)
        # final_sim.drop(final_sim[final_sim.user_id == Target_Uid ].index, inplace=True)
        final_sim.sort_values(by='final', ascending=False, inplace=True)
        final_sim = final_sim.reset_index(drop=True)
        return final_sim[:N]

    def cos_similarity(self,T_array, N):
        distances, indices = self.model_knn_trad.kneighbors(T_array.values.reshape(1, -1), n_neighbors=943)
        sim_USRD = 1 - distances.flatten()
        index_USRD = indices.flatten() + 1
        sim_index_list_USRD = pd.DataFrame(list(zip(sim_USRD, index_USRD)), columns=['final', 'user_id'])
        # sim_index_list_USRD.drop(sim_index_list_USRD[sim_index_list_USRD.user_id == Target_Uid ].index, inplace=True)
        sim_index_list_USRD.sort_values(by='final', ascending=False, inplace=True)
        sim_index_list_USRD = sim_index_list_USRD.reset_index(drop=True)
        return sim_index_list_USRD[:N]

    def predict_userbased(self, T_df, T_RD, T_UI, T_mean, choice, process):
        TopNMovies = self.top_rated_movies(300)
        prediction = []
        product = 1
        wtd_sum = 0

        if choice == 'modified':
            KNN_list = self.calculate_similarity(T_df, T_RD, T_UI, 60)  # similar users based on cosine similarity
        else:                           #elif choice == 'traditional':
            KNN_list = self.cos_similarity(T_RD, 60)

        # resnick
        sum_wt = abs(np.sum(KNN_list['final']))
        # j=
        if process == 'test':
            movieset = T_df
        else:                           #elif process == 'recommend':
            movieset = TopNMovies

        for item_id in movieset.itertuples():
            # print(j)
            # j=j+1#use here most rated movies
            wtd_sum = 0
            for i in range(0, len(KNN_list)):
                uID = KNN_list.loc[i][1]
                simID = KNN_list.loc[i][0]
                ratings_diff_of_uId = self.user_item_matrix.loc[uID, item_id[2]] - self.user_mean[uID]
                # ratings_diff = abs(ratings.loc[uID,item_id]-user_mean[uID])
                product = ratings_diff_of_uId * (simID)
                wtd_sum = wtd_sum + product

            if process == 'test':
                predicted_Rating = T_mean + (wtd_sum/sum_wt)
            else:  # elif process == 'recommend':
                predicted_Rating = round(T_mean + (wtd_sum / sum_wt))

            # predicted_Rating = T_mean + (wtd_sum/sum_wt)
            # if predicted_Rating > 0  :
            prediction.append([predicted_Rating, item_id[2]])
        return sorted(prediction, reverse=True)

    def get_recommendations(self,T_df):
        rd_list = []
        ui_list = []
        genre_list = ['unknown', 'Action', 'Adventure', 'Animation', "Children's", 'Comedy', 'Crime', 'Documentary',
                      'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller',
                      'War', 'Western']
        my_movie_info = pd.DataFrame(
            columns=['movie_id', 'unknown', 'Action', 'Adventure', 'Animation', "Children's", 'Comedy', 'Crime',
                     'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance',
                     'Sci-Fi', 'Thriller', 'War', 'Western'])

        for row in T_df.itertuples():
            y = self.movie[self.movie['movie_id'] == row[2]][
                ['movie_id', 'unknown', 'Action', 'Adventure', 'Animation', "Children's", 'Comedy', 'Crime',
                 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi',
                 'Thriller', 'War', 'Western']]
            my_movie_info = my_movie_info.append(y, ignore_index=True)

        T_df = pd.merge(T_df, my_movie_info, how='inner', on=['movie_id'])

        mymovielist = T_df['movie_id'].tolist()
        total_ratings = len(T_df)
        T_mean = T_df['rating'].mean()

        for i in range(1, 1683):
            if i in mymovielist:
                temp = T_df[T_df['movie_id'] == i]['rating'].tolist()
                rd_list.append(temp[0])
            else:
                rd_list.append(0)
        T_RD = pd.Series(rd_list)

        for j in genre_list:
            q = T_df[T_df[j] == 1]
            temp = len(q) / total_ratings
            ui_list.append(temp)
            # print(j,temp)
        T_UI = pd.Series(ui_list)

        start = time.time()
        modi_t = self.predict_userbased(T_df, T_RD, T_UI, T_mean, 'modified', 'test')
        modi_t = pd.DataFrame(modi_t, columns=['prediction', 'movie_id'])
        print('time for modi_t {0}'.format(time.time() - start))

        start = time.time()
        trad_t = self.predict_userbased(T_df, T_RD, T_UI, T_mean, 'traditional', 'test')
        trad_t = pd.DataFrame(trad_t, columns=['prediction', 'movie_id'])
        print('time for trad_t {0}'.format(time.time() - start))

        start = time.time()
        modi_r = self.predict_userbased(T_df, T_RD, T_UI, T_mean, 'modified', 'recommend')
        modi_r = pd.DataFrame(modi_r, columns=['prediction', 'movie_id'])
        print('time for modi_r {0}'.format(time.time() - start))

        # start = time.time()
        # trad_r = self.predict_userbased(T_df, T_RD, T_UI, T_mean, 'traditional', 'recommend')
        # trad_r = pd.DataFrame(trad_r, columns=['prediction', 'movie_id'])
        # print('time for trad_r {0}'.format(time.time() - start))

        my_movie_info = pd.DataFrame(columns=['movie_id', 'title', 'imdb_id', 'poster'])
        for row in modi_r.itertuples():
            y = self.movie[self.movie['movie_id'] == row[2]][['movie_id', 'title', 'imdb_id', 'poster']]
            my_movie_info = my_movie_info.append(y, ignore_index=True)
        modi_r = pd.merge(modi_r, my_movie_info, how='inner', on=['movie_id'])

        # my_movie_info = pd.DataFrame(columns=['movie_id', 'title', 'imdb_id', 'poster'])
        # for row in trad_r.itertuples():
        #     y = self.movie[self.movie['movie_id'] == row[2]][['movie_id', 'title', 'imdb_id', 'poster']]
        #     my_movie_info = my_movie_info.append(y, ignore_index=True)
        # trad_r = pd.merge(trad_r, my_movie_info, how='inner', on=['movie_id'])

        pred_m = modi_t['prediction'].tolist()
        pred_t = trad_t['prediction'].tolist()
        actual = T_df['rating'].tolist()

        trad_MAE = mean_absolute_error(actual, pred_t)
        modifid_MAE = mean_absolute_error(actual, pred_m)

        trad_RMSE = sqrt(mean_squared_error(actual, pred_t))
        modifid_RMSE = sqrt(mean_squared_error(actual, pred_m))
        trad_r = 0
        return modi_r, trad_r, trad_MAE, modifid_MAE, trad_RMSE, modifid_RMSE





    # def unrated_movies(self,argetID):
    #     unrated_movies=[]
    #     temp=which_movies_user_rated(TargetID)['movie_id']
    #     KNN_list=calculate_similarity(TargetID)
    #     for i in KNN_list.itertuples():
    #         temp1=which_movies_user_rated(i[2])['movie_id']
    #         for j in range(len(temp1)):
    #             if temp1[j] not in temp.values and temp1[j] not in unrated_movies:
    #                 unrated_movies.append(temp1[j])
    #
    #     return unrated_movies