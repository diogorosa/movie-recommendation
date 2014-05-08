import sys
import select
import math
import re
import time
from pymongo import MongoClient
import datetime
from time import strptime

movie_tags = ["action", "adventure", "animation", "childrens", "comedy",
           "crime", "documentary", "drama", "fantasy", "film-noir",
            "horror", "musical", "mystery", "romance", "sci-fi",
            "thriller", "war", "western"]
user_tags = ["administrator","artist","doctor","educator","engineer",
            "entertainment","executive","healthcare","homemaker","lawyer","librarian",
            "marketing","none","other","programmer","retired","salesman","scientist",
            "student","technician","writer"]
def db_drop():
    client = MongoClient()
    client.drop_database("recommender_db")
    print "database droped"

def tag_generator(tag_array, m_tags):
    tags = []
    for v_number,value in enumerate(tag_array):
        if int(value):
            tags.append(movie_tags[v_number])
    return tags

def date_time_converter(normal_date):
    if not normal_date:
        return
    date_array = normal_date.split("-")
    month = strptime(date_array[1],'%b').tm_mon
    return datetime.datetime(int(date_array[2]), int(month), int(date_array[0]),0, 0, 0, 786000)

def build_movies_db():
    movies_txt = open("ml-100k/u.item", "r")
    client = MongoClient()
    db = client.recommender_db
    movies = db.movies
    for line_number, line in enumerate(movies_txt):
        movie_data = line.rstrip('\n').split('|')
        if movie_data[1] != "unknown":
            movie = {"m_id":movie_data[0],
                    "m_title":movie_data[1].decode('iso-8859-1').encode('utf8'),
                    "release-date":date_time_converter(movie_data[2]),
                    "video-release-date":date_time_converter(movie_data[3]),
                    "imdb-url":movie_data[4],
                    "tags":tag_generator(movie_data[6:],movie_tags),
                    "ratings":[]}
            print movie_data[0]
            #print datetime.datetime.fromtimestamp(float(movie_data[2]), None)
            tag_generator(movie_data[6:],movie_tags)
            date_time_converter(movie_data[2])
            print datetime.datetime(2011, 12, 4, 16, 46, 59, 786000)
            movies.insert(movie)
    movies.ensure_index([("m_id", 1), ("movie.ratings",1)])

def build_users_db():
    users_txt = open("ml-100k/u.user", "r")
    client = MongoClient()
    db = client.recommender_db
    users = db.users
    for line_number, line in enumerate(users_txt):
        user_data = line.rstrip('\n').split('|')
        user = { "u_id":user_data[0],
                "age":user_data[1],
                "gender":user_data[2],
                "occupation":user_data[3],
                "zipcode":user_data[4],
                "g_rate":0,
                "t_rate":0}
        users.insert(user)
        print user
    users.ensure_index([("u_id", 1), ("t_rate", 1)])

def build_ratings_db():
    ratings_txt = open("ml-100k/u.data", "r")
    client = MongoClient()
    db = client.recommender_db
    movies = db.movies
    ratings = db.ratings
    users = db.users
    for line_number, line in enumerate(ratings_txt):
        rating_data = line.rstrip('\n').split('\t')
        print rating_data
        movies.update({"m_id":rating_data[1]},
                        {'$push':{'ratings': {"u_id":rating_data[0],
                                                "score":int(rating_data[2]),
                                                "timestamp":datetime.datetime.utcfromtimestamp(float(rating_data[3]))}}})
        rating = {"u_id":rating_data[0],
                  "m_id":rating_data[1],
                  "score":int(rating_data[2]),
                  "timestamp":datetime.datetime.utcfromtimestamp(float(rating_data[3]))}
        users.update({"u_id":rating_data[0]}, {"$inc": {"t_rate":int(rating_data[2]), "g_rate":1}})
        ratings.insert(rating)
    ratings.ensure_index([("u_id", 1), ("m_id", 1)])
start = time.time()
print "db constructor start"
db_drop()
build_movies_db()
build_users_db()
build_ratings_db()
end = time.time()
print "time"
print end - start
