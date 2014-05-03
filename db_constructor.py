import sys
import select
import math
import re
from pymongo import MongoClient
import datetime
from time import strptime

movie_tags = ["action", "adventure", "animation", "childrens", "comedy",
           "crime", "documentary", "drama", "fantasy", "film-noir",
            "horror", "musical", "mystery", "romance", "sci-fi",
            "thriller", "war", "western"]
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

ratings = open("ml-100k/u.item", "r")

client = MongoClient()
db = client.recommender_db
movies = db.movies
db.dropDatabase
for line_number, line in enumerate(ratings):
    movie_data = line.rstrip('\n').split('|')
    if movie_data[1] != "unknown":
        movie = {"m_id":movie_data[0],
                  "m_title":movie_data[1].decode('iso-8859-1').encode('utf8'),
                  "release-date":date_time_converter(movie_data[2]),
                  "video-release-date":date_time_converter(movie_data[3]),
                  "tags":tag_generator(movie_data[6:],movie_tags)}
        print movie_data[0]
        #print datetime.datetime.fromtimestamp(float(movie_data[2]), None)
        tag_generator(movie_data[6:],movie_tags)
        date_time_converter(movie_data[2])
        print datetime.datetime(2011, 12, 4, 16, 46, 59, 786000)
        movies.insert(movie)