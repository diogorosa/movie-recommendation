from pymongo import MongoClient
import math
import time

def cf_similarity_calculator(m_1, m_2):
    client = MongoClient()
    db = client.recommender_db
    movies = db.movies
    users = db.users
    ratings = db.ratings
    #para cada elemento calcular a similaridade com todos os seguintes
    movie_i = movies.find_one({"m_id":str(m_1)})
    movie_j = movies.find_one({"m_id":str(m_2)},)
    users_i = ratings.find({"m_id":str(m_1)})
    final_sum = 0
    quad_i = 0
    quad_j = 0
    print movie_i["m_title"]
    print movie_j["m_title"]
    for rate_i in movie_i["ratings"]:
        for rate_j in movie_j["ratings"]:
            if rate_j["u_id"] == rate_i["u_id"]:
                user = users.find_one({"u_id":rate_i["u_id"]})
                #print ratings.aggregate([{"$match": {"u_id":"1"}},{"$group":{"_id":"$u_id", "total": {"$sum": "$score"}}}])
                #print ratings.find({"u_id":rate_i["u_id"]}).count()
                product = ((rate_i["score"] - (user["t_rate"] / float(user["g_rate"]))) * (rate_j["score"] - (user["t_rate"] / float(user["g_rate"]))))
                print (rate_i["score"] - (user["t_rate"] / float(user["g_rate"]))) * (rate_j["score"] - (user["t_rate"] / float(user["g_rate"])))
                print "rate in movie_ i"
                print rate_i["score"]
                print "rate in movie_ j"
                print rate_j["score"]
                print "user total rate"
                print user["t_rate"]
                print "user global rate"
                print user["g_rate"]
                #print (rate_i["score"] - (user["t_rate"] / float(user["g_rate"])))
                print product
                final_sum += product
                quad_i += (rate_i["score"] - (user["t_rate"] /float(user["g_rate"])))**2
                quad_j += (rate_j["score"] - (user["t_rate"] / float(user["g_rate"])))**2
    print "--------------------------------------------------"
    print "item similarity"
    try:
        return {"movie_id":m_2,"sim":(final_sum/(math.sqrt(quad_i)*math.sqrt(quad_j)))}
    except ZeroDivisionError:
        print "no similarity here"
    print "--------------------------------------------------"

def preditction(u_id, m_prediction):
    client = MongoClient()
    db = client.recommender_db
    ratings = db.ratings
    movies = db.movies
    similars = []
    for rating in ratings.find({"u_id":str(u_id)}):
        print int(rating["m_id"])
        if movies.find_one({"m_id":rating["m_id"]}):
            sim = cf_similarity_calculator(int(rating["m_id"]), m_prediction)
            if sim:
                similars.append(sim)
    print "----------------All similar items-----------------------"
    sorted_list =  sorted(similars, key=lambda k: k['sim'], reverse=True)
    half_list = sorted_list[:len(sorted_list)/2]
    print half_list



#cf_similarity_calculator(1,2)
start = time.time()
print "Pre compute began"
preditction(1,666)
end = time.time()
print end - start
