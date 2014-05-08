import recommender as r
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

#user movies and recommend proposal
def synopse_compare(u_movies, r_movie):
    u_movies_sin = [d['sin'][0] for d in synopsis]
    tfidf = TfidfVectorizer().fit_transform(u_movies_sin)
    #print tfidf[0:1]
    #cosine similarity of others to iten zero
    cosine_similarities = linear_kernel(tfidf[0:1], tfidf).flatten()
    #print cosine_similarities
    related_docs_indices = cosine_similarities.argsort()[:-5:-1]
    print related_docs_indices
    print cosine_similarities[related_docs_indices]
    for x in range(1, len(related_docs_indices)):
        print "most similar n " + str(x)
        print u_movies[related_docs_indices[x]]


i_id = "1"
t = r.tag_organizer(i_id)
tag_avg = r.avg_rate_tag(t, i_id)
most_rated_5 =  r.my_rated_5(tag_avg, i_id)
synopsis = r.synopsis_fetcher(most_rated_5)

synopse_compare(synopsis, [])