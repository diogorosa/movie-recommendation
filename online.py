import hybrid_recommend as r
from pymongo import MongoClient
import sys
import datetime
from time import strptime

general_user = '0'
client = MongoClient()
db = client.recommender_db
def show_movie_collection():
    movies = db.movies
    for movie in movies.find({"ratings":{'$elemMatch':{"u_id":general_user}}}, {"m_id":1, "m_title":1, "ratings":{"$elemMatch":{"u_id":general_user}}}).limit(10):
      print "--------------movie-------------"
      print "title --> " + movie['m_title']
      print "id --> " + movie['m_id']
      print "rating --> " + str(movie['ratings'][0]["score"])


def get_user_id():
    global general_user
    user_id = 0
    while user_id == 0:
      print "\n-------------- insert user id ---------------"
      user_id = int(raw_input('u_id: '))
      print user_id
    general_user = str(user_id)


def get_m_id():
    movies = db.movies
    m_id = 0
    while m_id == 0:
      print "\n-------------- movie id to rate ---------------"
      m_id = int(raw_input('m_id: '))
      print "option --->" + str(m_id)
    if movies.find_one({"m_id": str(m_id)}):
        return m_id
    else:
        return

def rate_movies():
    m_id = get_m_id()
    rate = 0
    while rate == 0:
      print "\n-------------- Insert Rating min:0 max:5 ---------------"
      rate = int(raw_input('value: '))
      print "rated --->" + str(rate)
    movies = db.movies
    ratings = db.ratings
    movies.update({"m_id":str(m_id)},
                        {'$push':{'ratings': {"u_id":general_user,
                                                "score":rate,
                                                "timestamp":datetime.datetime.utcnow()}}})
    rating = {"u_id":general_user, "m_id":str(m_id), "score":rate, "timestamp":datetime.datetime.utcnow()}
    ratings.insert(rating)

def unseen_movies():
    movies = db.movies
    unseen = movies.find({"ratings.u_id":{"$ne":general_user}})
    for movie in unseen.limit(20):
      print "--------------movie-------------"
      print "title --> " + movie['m_title']
      print "id --> " + movie['m_id']
    print "unseen movies until now -----> " + str(unseen.count())

def see_movie():
    m_id = get_m_id()
    movies = db.movies
    movie = movies.find_one({"ratings.u_id":general_user, "m_id":str(m_id)}, {"m_id":1, "m_title":1, "ratings":{"$elemMatch":{"u_id":general_user}}})
    if movie:
        print "--------------movie-------------"
        print "title --> " + movie['m_title']
        print "id --> " + movie['m_id']
        print "rating --> " + str(movie['ratings'][0]["score"])
    else:
        movie = movies.find_one({"m_id":str(m_id)})
        print "--------------movie-------------"
        print "title --> " + movie['m_title']
        print "id --> " + movie['m_id']
        print "Rate this movie !!!!"
    select = 0
    s_options = ['','y','n']
    while select == 0:
      print "\n-------------- rate? ---------------"
      for i, option in enumerate(s_options):
          print('%s. %s' % (i, option))
      select = int(raw_input('? '))
    if select == 1:
        return
    else:
        rate_movies()

def view_suggestions():
    movies = db.movies
    suggestions = db.suggestions
    unseen = movies.find({"ratings.u_id":{"$ne":general_user}}).limit(2)
    for movie in unseen:
        r.hybrid_model(movie, general_user)
    to_suggest = db.suggestions.aggregate([{"$match":{"u_id":general_user}}, {"$sort":{"score":-1}}])
    print to_suggest
    for s in to_suggest['result']:
        print "-------------Suggestion---------------"
        m = {}
        m = movies.find_one({"m_id":s['m_id']})
        print m
        print m['m_title']
        print m['tags']
        if m.has_key('sin'):
            print m['sin']
def exit():
    sys.exit(0)

options = ['insert u_id', 'seen movies', 'unseen movies', 'rate movies', 'see movie','view suggestions','Quit']
callbacks = [get_user_id, show_movie_collection, unseen_movies, rate_movies, see_movie, view_suggestions, exit]


while True:
    print "\n-------------- Movie Recommender ---------------"
    for i, option in enumerate(options):
        print('%s. %s' % (i, option))
    choice = int(raw_input('your choice? '))
    print choice
    callbacks[choice]()

