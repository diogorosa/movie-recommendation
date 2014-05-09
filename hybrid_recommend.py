import recommender as r
import prediction_compute as p
from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

#user movies and recommend proposal
def synopse_compare(u_movies, r_movie):
    client = MongoClient()
    db = client.recommender_db
    movies = db.movies
    r_movie = movies.find_one({"m_id":r_movie['m_id']})
    for item in u_movies:
        print item['sin']
    u_movies.insert(0, r_movie)
    u_movies_sin = [d['sin'][0] for d in u_movies]
    tfidf = TfidfVectorizer().fit_transform(u_movies_sin)
    #print tfidf[0:1]
    #cosine similarity of others to iten zero
    cosine_similarities = linear_kernel(tfidf[0:1], tfidf).flatten()
    print cosine_similarities
    related_docs_indices = cosine_similarities.argsort()[:-6:-1]
    print related_docs_indices
    return cosine_similarities[related_docs_indices]
    #for x in range(1, len(related_docs_indices)):
     #   print "most similar n " + str(x)
      #  print u_movies[related_docs_indices[x]]



def content_analysis(item, u_id):
    client = MongoClient()
    db = client.recommender_db
    movies = db.movies
    most_seen = r.tag_organizer(u_id)
    tag_avg = r.avg_rate_tag(most_seen, u_id)
    top_4 =  r.top_rated_4(u_id, tag_avg, most_seen)
    r.synopsis_fetcher([item])
    item = movies.find_one({"m_id":item['m_id']})
    if item.has_key('sin'):
        synopsis = r.synopsis_fetcher(top_4)
        text_result = synopse_compare(synopsis, item)
        print sum(text_result[1:])
        print r.tag_classifier(item, most_seen, tag_avg, 3)
        return sum(text_result[1:]) + r.tag_classifier(item, most_seen, tag_avg, 3)
    else:
        print "movie to compare has no synopsis"
        return  r.tag_classifier(item, most_seen, tag_avg, 5)

def hybrid_model(item, u_id):
    client = MongoClient()
    db = client.recommender_db
    suggestions = db.suggestions
    content_based = content_analysis(item, u_id)
    collaborative = p.preditction(u_id, item['m_id'])
    suggestion = {"u_id":u_id, "m_id":item["m_id"]}
    if content_based == 0 & int(collaborative) > 0:
        print "not enough user/movie rate will be only collabprative"
        print collaborative
        suggestion["score"]=collaborative
    elif collaborative > 0:
        print collaborative
        print (content_based + collaborative)/2
        suggestion["score"] = (content_based + collaborative)/2
    else:
        print "data not accurate enough to suggest good movie"
    if suggestion.has_key('score'):
        suggestions.insert(suggestion)





