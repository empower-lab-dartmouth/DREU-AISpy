import spacy
import numpy as np
import requests
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet as wn
from string import punctuation
from nltk.tokenize import RegexpTokenizer
from rake_nltk import Rake
from string import punctuation
import random
import time
from gingerit.gingerit import GingerIt
parser = GingerIt()
nlp = spacy.load("en_core_web_sm")

relation_dict= {"MadeOf": "is made of", "CapableOf": "is capable of", "UsedFor": "is used for", "ReceivesAction": "can be", "HasProperty": "is", "IsA": "is a", "SimilarTo": "is similar to", "HasA": "has a"}

possible_nouns={}


#returns the relation that should be queried on
def is_valid_relation(sentence):
#    relations= ["MadeOf", "CapableOf", "UsedFor", "RelatedTo", "ReceivesAction", "HasProperty", "IsA", "LocatedNear", "SimilarTo", "HasA"]
    valid=True
    relation=''
    split=''
    if "made of" in sentence:
        relation='MadeOf'
        split='is made of'
    elif "capable of"in sentence:
        relation="CapableOf"
        split='is capable of'
    elif "used for"in sentence:
        relation='UsedFor'
        split='is used for'
#     i.e. a button can be pushed
    elif "can be"in sentence:
        relation='ReceivesAction'
        split='can be'
    elif "is a" in sentence:
        relation="IsA"
        split='is a'
    elif "next to" in sentence:
        relation="LocatedNear"
        split='is next to'
    elif "similar to" in sentence:
        relation="SimilarTo"
        split='is similar to'
    elif "has a" in sentence:
        relation="HasA"
        split='has a'
    elif "is" in sentence:
        relation="HasProperty"
        split='is'
    else:
        relation=input("Sorry, I couldn't understand you, can you repeat what you said?: ")
        valid=False
    return relation, split, valid

#extract the clue
def extract_phrase(sentence,relation):
    #from main.py of the Rudimentary implementation
    if relation != 'NotValid':
        text=sentence.split("I spy something that " + relation + ' ')
        return text[1]
    else:
        return "Sorry, I can't understand you. Please say your clue in the form of 'I spy something that...' "


def query_clue_end(clue, relation):
    clue = clue.replace(' ', '_')
    obj = requests.get('http://api.conceptnet.io/query?end=/c/en/' + clue + '&rel=/r/'+relation).json()
    weights=[]
    for edge in obj['edges']:
        phrase=edge['start']['label']
        lang=edge['start']['language']
        weight=edge['weight']
        if lang=='en'and weight>=2.0 and phrase not in possible_nouns:
            possible_nouns[phrase]=0
            weights.append(weight)
    lowercase = [each_string.lower() for each_string in possible_nouns]
    final, index=np.unique(lowercase, return_index=True)
    weights=np.array([weights[i] for i in index])
    sort_indices=np.argsort(weights)
    sort_indices=list(sort_indices)
    final=final[sort_indices]
    weights=weights[sort_indices]
    return list(final), list(weights)

# def relationProperties(images,relation):
#     properties={}
#     for image in images:
#         properties[image]=[]
#         obj = requests.get('http://api.conceptnet.io/query?start=/c/en/' + image + '&rel=/r/'+relation).json()
#         for edge in obj['edges']:
#             phrase=edge['end']['label']
#             lang=edge["end"]["language"]
#             weight=edge["weight"]
#             if lang=='en' and weight >=2.0:
#                 if phrase not in properties[image]:
#                     properties[image].append(phrase.lower())
#     return properties


# def relatedTo(images):
#     properties={}
#     for image in images:
#         properties[image]=[]
#         obj = requests.get('http://api.conceptnet.io/query?start=/c/en/' + image + '&rel=/r/RelatedTo').json()
#         for edge in obj['edges']:
#             phrase=edge['end']['label']
#             lang=edge["end"]["language"]
#             weight=edge["weight"]
#             if lang=='en' and weight >=2.0:
#                 phrase=phrase.split()
#                 for token in phrase:
#                     token2=nlp(token)[0]
#                     if token2.pos_=="ADJ":
#                         if token in properties[image]:
#                             continue
#                         else:
#                             properties[image].append(token)
#     return properties


def query_entity(image, relation):
    obj = requests.get('http://api.conceptnet.io/query?start=/c/en/' + image + '&rel=/r/' + relation).json()
    if len(obj['edges'])!=0:
        for edge in obj['edges']:
            phrase=edge['end']['label']
            lang=edge["end"]["language"]
            weight=edge["weight"]
            if lang=='en' and weight >=2.0:
                # phrase=phrase.split()
                # for token in phrase:
                #     token2=nlp(token)[0]
                #     if token2.pos_=="ADJ":
                #         if token in attributes:
                #             continue
                #         else:
                # attributes.append(phrase)
                return phrase
    return ''

def relatedTo_dict(clue, image_list):
    nouns=[]
    weights=[]
    obj = requests.get('http://api.conceptnet.io/query?end=/c/en/' + clue + '&rel=/r/RelatedTo').json()
    for edge in obj['edges']:
        phrase=edge['start']['label']
        lang=edge["start"]["language"]
        weight=edge["weight"]
        if lang=='en' and weight >=2.0:
            phrase=phrase.split()
            for token in phrase:
                token2=nlp(token)[0]
                if token2.pos_=="NOUN" or token2.pos_=="PROPN":
                    if token in nouns:
                        continue
                    elif token in image_list:
                        nouns.append(token)
                        weights.append(weight)
    return nouns, weights

# def match_relation(images, clue, dictionary):
#     guess=''
#     clue_similar=find_similar(clue)
#     i=0
#     for key in dictionary.keys():
#         for value in dictionary[key]:
#             compare=wn.synsets(value)[0]
#             if compare in clue_similar:
#                 return key
#     return guess
#
# def match_picture(image_list,queries):
#     match=''
#     for image in image_list:
#         if image in queries[0]:
#             match=image
#     return match
#
# def find_similar(clue):
#     syn=wn.synsets(clue,'a')[0]
#     similar=set(syn.similar_tos())
#     return set(similar)

# def is_similar(clue):
#     syn=wn.synsets(clue,'a')[0]
#     similar=set(syn.similar_tos())
#     return set(similar)

#first check to see if the given relation returns the proper query
def check_query(response):
    if response=='y':
        return input("Yay one point for me! Do you want to play again? type y/n: ")
    else:
        return input("Can you provide another clue?: ")


#ideas on how to incorporate QA into this section
#if there is not enough info, child can provide commonsense info to use in the future
#use this as an opportunity to "learn together". i.e. "hey, look what I found! Guess if [fact about entity] is true"
#the idea would be to make them feel more knowledgeable than the agent encouraging them to provide more information
def agent_spy(image_list, times=3):
    #first pick a random entity
    choose_entity=random.choice(image_list)

    #choose a random relation
    relations= ["MadeOf", "CapableOf", "UsedFor", "ReceivesAction", "HasProperty", "IsA", "LocatedNear", "SimilarTo", "HasA"]

    #query this entity
    choose_relation=random.choice(relations)
    attribute=query_entity(choose_entity,choose_relation)

    hint='y'

    already_used=[]
    i=0
    #in theory we would randomly choose a relation, but for now we are only using on relation
    while i < times:
        #if the relation is empty, have the child teach more about that relation. i.e.
        #squirrel, HasProperty empty. Have child teach agent about the properties of squirrels
        print(choose_relation, attribute)
        if hint=='y':
            if attribute=='':
                choose_relation=random.choice(relations)
                attribute=query_entity(choose_entity,choose_relation)
                continue
            #answer=input("Aw man, I don't have many hints. Actually, would you like to teach me more about " + choose_entity)

        if attribute not in already_used:
            guess_statement=parser.parse("I spy something that " + relation_dict[choose_relation] + ' ' + attribute + ": ")["result"]
            spy=input(guess_statement)
        else:
            attribute=random.choice(attributes)
            continue

        guess=guess_statement.split()[0]

        if guess==choose_entity:
            return input("Aw man, I thought I could trick you! One point for you! ")

        else:
            want_hint=input("Good guess, but I was thinking of something else. Do you want another hint? type y/n ")
            if want_hint=='y':
                already_used.append(attribute)
                choose_relation=random.choice(relations)
                attributes=query_entity(choose_entity,choose_relation)
                hint='y'
                i+=1
                continue
            else:
                print("Alright, take another guess")
                hint='n'
                i+=1
                time.sleep(2)
                continue


    return input("Gotcha! I was spying a " + choose_entity + ". One point for me!")




def agent_guess(image_list, times=3):
    sentence=input("Please provide a clue: ")
    i=0
    while i < times:
        relations=is_valid_relation(sentence)
        #if the relation provided is valid
        if relations[2]==True:
            guess_1=query_clue(image_list, sentence, relations)
            guess_list=[guess_1[0], random.choice(image_list)]
            if guess_1[1]:
                response_grammar=parser.parse("Is it a "+ random.choice(guess_list))
                response=input(response_grammar) + " type y/n: ")
                answer=check_query(response)
                if (answer=='y' or answer=='n'):
                    return answer
                sentence=answer
                i+=1
                continue
            if i != times-1:
                response=input("I'm still learning new words. I don't understand the word "+ guess_list[0] +". Can you provide a synonym?: ")
                sentence=response
                i+=1
        else:
            new_clue=input(relations[0])
            sentence=new_clue
            i-=1


    store_data=input("I don't know. One point for you! What was the answer: ")

    return input("I'll remember for next time! Would you like to play again? type y/n: ")


def query_clue(image_list, sentence, relations):
    clue=extract_phrase(sentence,relations[1])
    queries=query_clue_end(clue,relations[0])
    for i in range(2):
        guess=match_picture(image_list,queries)
        if guess != '':
            return guess, True

        queries=relatedTo_dict(clue, image_list)

    return clue, False

# def game_start(pick_images, name='Emma'):
#     #we can try to incorporate Q and A generation in this function
#     print("Hi "+ name + ", let's play I Spy!")
#     time.sleep(2)
#     again=game_play(pick_images)
#     i=0
#     while i<5:
#         if again=='y':
#             again=game_play(pick_images)
#             i+=1
#         else:
#             return "That was fun! See you next time!"
#
#     qa_game=input("Wow, we spied many things already! Would you like to learn more about them? type y/n: ")
#     if qa_game=='y':
#         #qa generation function
#         print("Let's play trivia!")

# def game_play(pick_images):
#     game=''
#     turn=input("Who do you want to be the spy? type you/me: ")
#     if turn=="me":
#         print("Great, I'll do the guessing")
#         time.sleep(2)
#         game=agent_guess(pick_images)
#     elif turn=="you":
#         print("Great, I'll do the spying")
#         time.sleep(2)
#         game=agent_spy(pick_images)
#
#     return game



def game_play(pick_images, name='Emma'):
    #we can try to incorporate Q and A generation in this function
    print("Hi "+ name + ", let's play I Spy!")
    time.sleep(2)
    turn=input("Who do you want to be the spy? type you/me: ")
    i=0
    k="yes"
    while k=="yes":
        while i < 3:
            if turn=='you':
                print("Okay, I'll do the spying")
                agent_spy(pick_images)
                print("Now, it's your turn to spy")
                agent_guess(pick_images)
                i+=1
            elif turn=="me":
                print("Okay, I'll do the guessing")
                turn1=agent_guess(pick_images)
                print("Now, it's your turn to guess")
                turn2=agent_spy(pick_images)
                i+=1
            else:
                turn=input("Can you repeat what you said?: ")
                continue

        print("Wow, we spied many things already! Let's learn more about them! ")
