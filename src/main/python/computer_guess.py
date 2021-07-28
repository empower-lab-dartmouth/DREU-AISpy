import requests


def create_Rank(clue, relation, objectPool):
    print(clue,relation)
    rank={}
    obj = requests.get('http://api.conceptnet.io/query?end=/c/en/' + clue + '&rel=/r/'+relation).json()
    possible_nouns=[]
    weights=[]
    for edge in obj['edges']:
        phrase=edge['start']['label']
        lang=edge['start']['language']
        weight=edge['weight']
        for entity in objectPool:
            sing_phrase=SnowballStemmer("english").stem(phrase)
            sing_entity=SnowballStemmer("english").stem(entity)
            if sing_phrase in sing_entity:
                if rank.has_key(entity):
                    rank[entity]+=weight
                else:
                    rank[entity]=weight

    rank=sorted(rank.items(), key=lambda x: x[1], reverse=True)
    return rank


# def create_Rank(clue, relation, object):
#     print(objectPool)
#     rank={}
#     obj = requests.get('http://api.conceptnet.io/query?end=/c/en/' + object + '&rel=/r/'+relation).json()
#     weights=[]
#     for edge in obj['edges']:
#         phrase=edge['end']['label']
#         lang=edge['end']['language']
#         weight=edge['weight']
#         sing_phrase=SnowballStemmer("english").stem(phrase)
#         sing_entity=SnowballStemmer("english").stem(entity)
#             if phrase in entity:
#                 if rank.has_key(entity):
#                     rank[entity]+=weight
#                 else:
#                     rank[entity]=weight
#
#     rank=sorted(rank.items(), key=lambda x: x[1], reverse=True)
#     return rank
