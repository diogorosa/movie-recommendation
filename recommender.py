from pymongo import MongoClient
import math
import time

movie_tags = ["action", "adventure", "animation", "childrens", "comedy",
           "crime", "documentary", "drama", "fantasy", "film-noir",
            "horror", "musical", "mystery", "romance", "sci-fi",
            "thriller", "war", "western"]


#order user ratings based on tag names
#most rated types will stay at the top
def tag_organizer(u_id, tags):
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
        print item.keys()
        print len(item.values()[0])
        if len(sorted_tags) > 0:
          if len(sorted_tags[0].values()[0]) < len(item.values()[0]):
              sorted_tags.insert(0, item)
          else:
            sorted_tags.append(item)
        else:
          sorted_tags.append(item)
    return sorted_tags

def avg_rate_tag(tag_movies, u_id):
    #print len(sorted_tags[0].values()[0])
    client = MongoClient()
    db = client.recommender_db
    ratings = db.ratings
    for t in tag_movies:
        for m_id in t.values()[0]:
            print ratings.find_one({"u_id":str(u_id)})



t = tag_organizer(1, movie_tags)
print t
avg_rate_tag(t, 1)
