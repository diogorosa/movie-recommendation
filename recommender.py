from pymongo import MongoClient
import math
import time
import operator
from rottentomatoes import RT
import imdb
from bs4 import BeautifulSoup as BS
import requests

tags = ["action", "adventure", "animation", "childrens", "comedy",
           "crime", "documentary", "drama", "fantasy", "film-noir",
            "horror", "musical", "mystery", "romance", "sci-fi",
            "thriller", "war", "western"]

#order user ratings based on tag names
#most rated types will stay at the top
def tag_organizer(u_id):
    client = MongoClient()
    db = client.recommender_db
    movies = db.movies
    ratings = db.ratings
    test = []
    for tag in tags:
        matches = []
        count = 0
        search = movies.find({ "tags": tag }, {"ratings":1, "m_id":1})
        for m in search:
            for r in m["ratings"]:
                if r['u_id']==str(u_id):
                  matches.append(m['m_id'])
        test.append({tag:matches})
    return sort_by_tags(test)

def sort_by_tags(data):
    sorted_tags = []
    for item in data:
        #print item.keys()
        #print len(item.values()[0])
        if len(sorted_tags) > 0:
          if len(sorted_tags[0].values()[0]) < len(item.values()[0]):
              sorted_tags.insert(0, item)
          else:
            sorted_tags.append(item)
        else:
          sorted_tags.append(item)
    return sorted_tags

#returns average rate for each movie type
def avg_rate_tag(tag_movies, u_id):
    #print len(sorted_tags[0].values()[0])
    client = MongoClient()
    db = client.recommender_db
    ratings = db.ratings
    rate_list = []
    for t in tag_movies:
        m_tag = t.keys()[0]
        score_sum = 0
        for m_id in t.values()[0]:
            score = ratings.find_one({"u_id":str(u_id), "m_id":m_id})
            score_sum += score["score"]
        if len(t.values()[0]) == 0:
            avg_rating = 0
        else:
            avg_rating = score_sum/float(len(t.values()[0]))
        rate_list.append({"tag":m_tag, "avg":avg_rating})
    return sorted(rate_list, key=lambda k: k['avg'], reverse=True)

#returns 5 movies based on most rated and best rated tags of user
#return based on first tag and second if avg rating on first - avg_rating
#on second is < 0.8
def my_rated_5(most_seen, u_id):
    client = MongoClient()
    db = client.recommender_db
    movies = db.movies
    avg_r_var = 0.8
    m_r_5 = []
    tags_list = []
    top_movie = most_seen[0]
    top_movie_2 = most_seen[1]
    if (top_movie["avg"] - top_movie_2["avg"]) < avg_r_var:
        tags_list.append(top_movie["tag"])
        tags_list.append(top_movie_2["tag"])
    else:
        tags_list.append(top_movie)

    rated_movies = movies.find({"ratings":{"$elemMatch":{"u_id":u_id}}} )
    for movie in rated_movies:
        for tag in movie['tags']:
            for r_tag in tags_list:
                if tag == r_tag:
                    rate = movies.find_one({"m_id":movie['m_id']}, {"ratings":{"$elemMatch":{"u_id":u_id}}})['ratings'][0]
                    m_r_5.append({"m_id":movie['m_id'], "rate": rate["score"], "m_title":movie['m_title']})
    sorted_rate = sorted(m_r_5[0:5], key=lambda k: k['rate'], reverse=True)
    movies.update({"m_id":movie['m_id']},
                {'$set':{'top_5': sorted_rate}})
    return sorted_rate


def get_imdb_plot(id):
    i = imdb.IMDb()
    i = imdb.IMDb(accessSystem='http')
    m = i.get_movie(id)
    m_plot = m.get('plot')
    return m_plot

def get_m_desc(imdb_link):
    html = requests.get(imdb_link).text
    soup = BS(html)
    desc = soup.find(itemprop="description")
    print desc
    return desc

def synopsis_fetcher(movies):
    print movies
    client = MongoClient()
    db = client.recommender_db
    movies_db = db.movies
    synopsis = []
    for movie in movies:
        #print movie
        synopse = {}
        s_rotten = RT().feeling_lucky(movie['m_title'])
        r_synopse = s_rotten['synopsis']
        if r_synopse:
            #print r_synopse
            synopse = {'m_id': movie['m_id'], 'sin':r_synopse}
        else:
            i_id = s_rotten['alternate_ids']['imdb']
            imdb_request_plot = get_imdb_plot(i_id)
            if imdb_request_plot:
                #print imdb_request_plot
                synopse = {'m_id': movie['m_id'], 'sin':imdb_request_plot}
            else:
                print "no movie plot or synopse "
        if synopse:
            synopsis.append(synopse)
            print "----------------fetched synopse--------------"
            print synopse
            print "---------------------------------------------"
            movies_db.update({"m_id":synopse['m_id']}, {'$set':{"synopsis":synopse['sin'] }})
    return synopsis




