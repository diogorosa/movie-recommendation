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


#top 2 from two most rated tags
def top_rated_4(u_id, top_rated, most_seen):
    client = MongoClient()
    db = client.recommender_db
    movies = db.movies
    sum_rating = 0
    avg_vote_qty = 0
    filtered_top = []
    top_tag_movies = []
    filtered_top = filtered_top_tags(most_seen, top_rated)
    for x in filtered_top[0:2]:
        movie_query = movies.find({"tags":x['tag'],"ratings":{'$elemMatch':{"u_id":"1", "score":{'$gte':x['avg']}}}}, {"m_id":"1","m_title":1, "ratings":{'$elemMatch':{"u_id":"1"}}})
        top_tag_movies.extend(list(movie_query)[0:2])
    return top_tag_movies
    #synopsis_fetcher(top_tag_movies)

def filtered_top_tags(most_seen, top_rated):
    top_seen_rated = []
    avg_vote_qty = genre_vote_qty(most_seen)
    for genre in top_rated:
        for item in most_seen:
            if item.keys()[0] == genre['tag']:
                if len(item.values()[0]) > avg_vote_qty:
                    top_seen_rated.append(genre)
    return top_seen_rated

def genre_vote_qty(most_seen):
    sum_rating = 0
    for ratings in most_seen:
        sum_rating += len(ratings.values()[0])
    return sum_rating/float(len(most_seen))


def get_imdb_plot(id):
    i = imdb.IMDb()
    i = imdb.IMDb(accessSystem='http')
    m = i.get_movie(id)
    m_plot = m.get('plot')
    return m_plot
#gets movie description scraping imdb movie site
def get_m_desc(imdb_link):
    html = requests.get(imdb_link).text
    soup = BS(html)
    desc = soup.find(itemprop="description")
    print desc
    return desc

def search_title_imdb(title):
    i = imdb.IMDb()
    movie_list = i.search_movie(title)
    if movie_list:
        i = imdb.IMDb(accessSystem='http')
        m_id = i.get_imdbID(movie_list[0])
        return get_imdb_plot(m_id)

#fetch synopsis from rottentomatoes, imdb api and imdb site
def synopsis_fetcher(movies):
    print movies
    client = MongoClient()
    db = client.recommender_db
    movies_db = db.movies
    synopsis = []
    for movie in movies:
        print movie['m_title']
        synopse = {}
        movie_in_db = movies_db.find_one({'m_id':movie['m_id']})
        if not movie_in_db.has_key('sin'):
            print movie['m_title']
            s_rotten = RT().search(movie['m_title'])
            sy_from_rotten = check_in_rotten(movie)
            if sy_from_rotten:
                synopse = sy_from_rotten
            else:
                search_imdb = search_title_imdb(movie['m_title'])
                if search_imdb:
                    synopse = {'m_id': movie['m_id'], 'sin':search_imdb}
        else:
            synopsis.append(movie_in_db)
            print "synopse append----------------------------"
        if synopse:
            synopsis.append(synopse)
            print "----------------fetched synopse--------------"
            print synopse
            print "---------------------------------------------"
            movies_db.update({"m_id":synopse['m_id']}, {'$set':{"sin":synopse['sin'] }})
    return synopsis

def check_in_rotten(movie):
    s_rotten = RT().search(movie['m_title'])
    synopse = {}
    if s_rotten:
        m_rotten = s_rotten[0]
        r_synopse = m_rotten['synopsis']
        if r_synopse:
            synopse = {'m_id': movie['m_id'], 'sin':r_synopse}
        elif m_rotten.has_key('alternate_ids'):
            i_id = m_rotten['alternate_ids']['imdb']
            imdb_request_plot = get_imdb_plot(i_id)
            if imdb_request_plot:
                print imdb_request_plot
                synopse = {'m_id': movie['m_id'], 'sin':imdb_request_plot}
            else:
                print "no movie plot or synopse "
    return synopse

#tags weighted sum the mix between most rated and most_seen
#each tag in that mix has a weight of
#(tag_organized/(weight of tag classifier) * index)
def tag_classifier(item, most_seen, tag_avg, weight):
    organized_tags =  filtered_top_tags(most_seen,tag_avg)
    tag_weight = float(weight)/len(organized_tags)
    tag_classifier_rate = 0
    for i,tag in enumerate(organized_tags):
        if tag['tag'] in item['tags']:
            tag_classifier_rate = ((i+1) * tag_weight)
    return tag_classifier_rate



