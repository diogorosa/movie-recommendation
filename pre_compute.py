from pymongo import MongoClient
import math

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
        return final_sum/(math.sqrt(quad_i)*math.sqrt(quad_j))
    except ZeroDivisionError:
        print "no similarity here"
    print "--------------------------------------------------"


#cf_similarity_calculator(1,2)

client = MongoClient()
db = client.recommender_db
ratings = db.ratings
movies = db.movies
similars = []
for rating in ratings.find({"u_id":"1"}):
    print int(rating["m_id"])
    if movies.find_one({"m_id":rating["m_id"]}):
        sim = cf_similarity_calculator(int(rating["m_id"]),666)
        if sim:
            similars.append(sim)
print "----------------All similar items-----------------------"
print sorted(similars, key=int, reverse=True)
