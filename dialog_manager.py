import pandas as pd
from Levenshtein import distance as lev
import random

from datetime import datetime
import re

# To load the data correctly, using the reference rules
def load_restaurant_data():
    rest_info = pd.read_csv('restaurant_info.csv')

    #make labels randomly for restaurants regarding quality staytime and crowdedness
    ToF = ["true", "false"]
    quality, staytime, crowdedness = [],[],[]

    for i in range(len(rest_info)):
        quality.append(random.choice(ToF)) # Need to randomly choose these values for echt new column
        staytime.append(random.choice(ToF))
        crowdedness.append(random.choice(ToF))
    addition = pd.DataFrame({'quality': quality,'staytime': staytime, 'crowdedness': crowdedness}) #create the dataframe of new columns from lists
    new = rest_info.join(addition)
    new.to_csv('new.csv', encoding='utf-8', index=False) # create new file to store new data

    return new

# Here we have the state transition and dialog function. Depending on the state and the act we can create the right responses
def state_transition(utterance, state, act, preferences, restaurants, result, additional_pref, formal):
    response = ''
    
    #You can always exit
    if act == 'bye':
        new_state = 9
        response = give_response("survey", formal, preferences) #Ask the user for there experience
        
    #You can always repeat and stay in the same state
    elif act == 'repeat':
        new_state = state
        response = give_response("repeat", formal, preferences) 
        
    #You can always restart
    elif act == 'restart':
            preferences = {} #Clear preferences
            restaurants = [] #Clear restaurant list
            new_state = 1
            response += give_response("welcome", formal, preferences)

    #Extra easteregg
    elif act == 'I do not understand...':
        response = random.choice(give_response('stupid', formal, preferences))
        new_state = state
            
    #State 1 2 3 4, where you want to know the preferences of the user
    elif state in [1,2,3,4]:
        preferences  = keyword_matching(state, utterance, preferences)

        # By checking for hello, we create more engagement
        if act == 'hello':
            #In the formal response we will check the time of day to see what the right response is
            if formal:
                res_list = give_response("hello", formal, preferences)
                now = datetime.now()
                if now.hour <= 12:
                    response += res_list[0]
                elif now.hour < 18:
                    response += res_list[1]
                elif now.hour >= 18:
                    response += res_list[2]
            else:        
                response = random.choice(give_response("hello", formal, preferences))
            
        if 0 not in preferences.keys():   # if area is unknown go to state 2
            new_state = 2
            response += give_response("area", formal, preferences)
        elif 1 not in preferences.keys(): # if type is unknown go to state 3
            new_state = 3
            response += give_response("foodtype", formal, preferences)
        elif 2 not in preferences.keys(): # if price is unknown go to state 4
            new_state = 4
            response += give_response("price", formal, preferences)
        else:
            restaurants = retrieve_restaurant(preferences) # if all preferences are known go to state 5, ask for additional requirements
            if len(restaurants) == 0: # if no restaurants matches go to state 6 and ask wheter user want to restart
                response += give_response("nomatch", formal, preferences)
                new_state = 6
            else:
                if len(restaurants) > 1: # only if there are more options, ask for additional requirements -> state 5
                    new_state = 5 
                    response += give_response("additional", formal, preferences)
                else:
                    new_state = 7 #suggest restaurants
                    response, restaurants, result = give_recommendation(restaurants, formal)
                
    #State 5, where you asked for more information
    elif state == 5:
        #when user doesn't want additional requirements
        if act == 'negate': 
            new_state = 7
            response, restaurants, result = give_recommendation(restaurants, formal)
        #additional requirements
        else:
            additional_pref = additional_preferences(utterance, additional_pref)
               
            if not additional_pref: #implicit booleaness: list is empty in this case
                new_state = state
                response = give_response("chooseadditional", formal, preferences)
            else:
                reason, result, restaurants = checkrule(restaurants, additional_pref, formal)
                if result == None: # if no restaurants matches go to state 6 and ask wheter user want to restart
                    response += give_response("nomatch", formal, preferences)
                    new_state = 6
                else:
                    new_state = 7
                    if formal:
                        response = "Thank you, I came up with a recommendation: {}. {} Is this what you had in mind?".format(result, reason)
                    else:
                        response = "Okay, I found a restaurant for you: {}. {} Sounds good??".format(result, reason)
    

    #When there are no recommendations, ask user if he wants to restart or not
    elif state == 6:
        if act == 'negate': # user doesn't need other recommendations so leave
            new_state = 9
            response += give_response("survey", formal, preferences)

        elif act == 'affirm': # user want select new preferences because there's no match so restart
            new_state = 1
            response += give_response("welcome", formal, preferences)
            preferences = {}

        elif act == 'inform':
            preferences  = keyword_matching(state, utterance, preferences)
            restaurants = retrieve_restaurant(preferences) # if all preferences are known go to state 5, ask for additional requirements

            if len(restaurants) == 0: # if no restaurants matches go to state 6 and ask wheter user want to restart
                response += give_response("nomatch", formal, preferences)
                new_state = 6
            else:
                if len(restaurants) > 1: # only if there are more options, ask for additional requirements -> state 5
                    new_state = 5 
                    response += give_response("additional", formal, preferences)
                else:
                    new_state = 7 #suggest restaurants
                    response, restaurants, result = give_recommendation(restaurants, formal)
        else:
            new_state = 6
            response += give_response("yesorno", formal, preferences)
            
    #State 7, you want to recommend restaurants
    elif state == 7:
        if act == 'negate': # user don't like the restaurant, recommend new one
            if len(restaurants) == 0: # if no more choices go to state 6 and ask wheter user want to restart
                new_state = 6
                response += give_response("nomatch", formal, preferences)
            else:
                if(len(additional_pref) == 0):
                    new_state = 7 # still other options left, recommend them   
                    response, restaurants, result = give_recommendation(restaurants, formal)
                else:
                    reason, result, restaurants = checkrule(restaurants, additional_pref, formal)
                    if result == None: # if no restaurants matches go to state 6 and ask wheter user want to restart
                        response += give_response("nomatch", formal, preferences)
                        new_state = 6
                    else:
                        new_state = 7
                        if formal:
                            response = "Thank you, I came up with the following recommendation: {}. {} Are you satisfied? ".format(result, reason)
                        else:
                            response = "Thank you, I came up with a recommendation: {}. {} Sounds good?".format(result, reason)

                            
                    
        elif act == 'affirm' or act == 'request':
            new_state = 8
            response += give_more_information(result, formal)
        else:
            new_state = state
            response = give_response("goodornot", formal, preferences)
            
    #State 8 after given extra information
    elif state == 8:
        response += give_response("ending", formal, preferences)
        new_state = 9
    
    #State 9 is ending the conversation after you give a rating to the bot
    elif state == 9:
        if len(utterance.strip()) == 1 and utterance.strip()[0] in ['1', '2', '3', '4', '5']:
            score = int(utterance.strip()[0])
            with open('survey.csv', 'a') as f:
                f.write('{},\n'.format(score))
            response = give_response("bye", formal, preferences)
            exit(0)
        else:
            response = give_response("invalid", formal, preferences)
            new_state = state

        
    #If State is not in 1-9, something went wrong: reset
    else: 
        new_state = 1
        response += give_response("welcome", formal, preferences)

    return new_state, response, preferences, restaurants, result

#function that retreves and saves the additional requirements
def additional_preferences(utterance, additional_pref):
    consequent_list =["busy", "long", "children", "romantic"]

    for word in utterance.split():
        for consequent in consequent_list:
            if word==consequent: #Check which additional requirements it has
                additional_pref.append(consequent)
    return additional_pref

#This function checks if the requirements can be met by any of the restaurants that have matched all user preferences
def checkrule(restaurants, requirements, formal):
    
    rest_info = load_restaurant_data()
    reason = ''
    result = None

    #for each restaurant, check the rules given the additional requirement(s)
    for restaurant in restaurants:
        indexje = (list(rest_info['restaurantname'])).index(restaurant)
        for consequent in requirements:
            #for one consequent, check if the antecedent(s) conform the rule to make the consequent to 
            if consequent == "busy":
                if (list(rest_info['pricerange'])[indexje] == "cheap" and list(rest_info['quality'])[indexje] == "true"):
                    if formal:
                        reason = "This is a busy restaurant, because it offers good food for a low price."
                    else:
                        reason = "This restaurant is busy, because it's a cheap restaurant with good food!!"
                    #if the consequent follows from the restaurants' antecedents, the restaurant and the reason are returned, as well as the list from which the restaurant is now removed
                    result = restaurant
                    restaurants.remove(restaurant)
                return reason, result, restaurants
            elif consequent == "long stay":
                if (list(rest_info['type'])[indexje] == "spanish"):
                    if formal:
                        reason = "This restaurant allows you to stay for a long time, because it is a Spanish restaurant. They serve extensive dinners that take a long time."
                    else:
                        reason = "You can spend a long time in this restaurant, because Spanish restaurants serve dinners that will take you a long time to finish."
                    result = restaurant
                    restaurants.remove(restaurant)
                    return reason, result, restaurants
                elif (list(rest_info['crowdedness'])[indexje] == "true"):
                    if formal:
                        reason = "This restaurant has a long staytime. This is because it is a croweded restaurant, so the wait times for your order are longer than usual."
                    else:
                        reason = "In this restaurant, you will spend a longer time.. This is because the restaurant is busy, so you need to wait a little longer for your orders."
                    result = restaurant
                    restaurants.remove(restaurant)
                    return reason, result, restaurants
            elif consequent == "children":
                if (list(rest_info['staytime'])[indexje] == "false"):
                    if formal:
                        reason = "I recommend this restaurant if you are planning on visiting it with children, because you do not have to spend a long time in the restaurant."
                    else:
                        reason = "I can recommend this one if you are coming with children, because you don't have to spend a long time in this restaurant."
                    result = restaurant
                    restaurants.remove(restaurant)
                    return reason, result, restaurants
            elif consequent == "romantic":
                if (list(rest_info['crowdedness'])[indexje] == "false"):
                    if formal:
                        reason = "This restaurant suits a romantic dinner, because it is not a crowded restaurant."
                    else:
                        reason = "This one is perfect for some romance, because it isn't a busy restaurant."
                    result = restaurant
                    restaurants.remove(restaurant)
                    return reason, result, restaurants
                elif (list(rest_info['staytime'])[indexje] == "true"):
                    if formal:
                        reason = "This restaurant suits a romantic dinner, because it allows you to stay a long time."
                    else:
                        reason = "This one is perfect for some romance, because you can spend a long time in this restaurant."
                    result = restaurant
                    restaurants.remove(restaurant)
                    return reason, result, restaurants
                                 
    return reason, result, restaurants

# This function matches the keywords with the words in the sentences and matches this with the preferences
def keyword_matching(state, utterance, preferences):
    keywords = {                                        #This dictionary is used to find the keywords
        'moderate': 'price', 
        'expensive': 'price' , 
        'cheap': 'price', 
        'north' : 'area', 
        'west': 'area', 
        'east': 'area', 
        'south': 'area', 
        'centre': 'area',
        'british': 'food', 
        'modern european': 'food', 
        'italian': 'food', 
        'romanian': 'food', 
        'seafood': 'food', 
        'chinese': 'food',
        'steakhouse': 'food', 
        'asian oriental': 'food', 
        'french': 'food', 
        'portuguese': 'food', 
        'indian': 'food', 
        'spanish': 'food', 
        'european': 'food', 
        'vietnamese': 'food', 
        'korean': 'food', 
        'thai': 'food', 
        'moroccan': 'food', 
        'swiss':'food',
        'fusion':'food',
        'tuscan' : 'food',
        'north american': 'food',
        'mediterranean': 'food', 
        'turkish': 'food',
        'australasian': 'food',
        'persian': 'food',
        'traditional' : 'food',
        'gastropub': 'food', 
        'jamaican': 'food', 
        'lebanese': 'food' , 
        'cuban': 'food', 
        'catalan': 'food', 
        'world': 'food',
        'international':'food',
        'polynesian':'food',
        'african':'food',
        'bistro':'food',
        'japanese': 'food'}
    
    smallestprice, smallestarea, smallestvalue = 2,2,2  # We limit our levenshtein distance by 2
    for word in utterance.split():                              
        if word in ['would', 'the', 'eat', 'want', 'at', 'this', 'can', 'then', 'than']:
            continue
        for key, value in keywords.items():
            kw_distance = lev(word, key)
            if value == 'area' and kw_distance < smallestarea: 
                smallestarea = kw_distance
                preferences[0] = key
            elif value == 'food' and kw_distance < smallestvalue:
                smallestvalue = kw_distance
                preferences[1] = key  
            elif value == 'price' and kw_distance < smallestprice:
                smallestprice = kw_distance
                preferences[2] = key
        if word == 'any' and state in [2,3,4]: #We allow any as input as well
            preferences[state - 2] = word
        if word == 'anywhere' and state == 2:
            preferences[state - 2] = 'any'      
    
    #Recognition of the food type preferences that consist of 2 words instead of one
    if "modern european" in utterance:
        preferences[1] = "modern european"
    if "north american" in utterance:
        preferences[1] = "north american"
    if "asian oriental" in utterance:
        preferences[1] = "asian oriental"


    # Here we used some pattern recognition when the input does not correspond to any of the words in the dictionary
    if (1 not in preferences.keys()):
        patternfood = re.compile(r'\w+\s+food')
        patternrestaurant = re.compile(r'\w+\s+restaurant')
        beforefood = patternfood.findall(utterance)
        beforerestaurant = patternrestaurant.findall(utterance)
        kindoffood = ""
        if len(beforefood) != 0:
            kindoffood = re.findall("(.*) food", beforefood[0])[0]
        if len(beforerestaurant) != 0:
            kindoffood = re.findall("(.*) restaurant", beforerestaurant[0])[0]
        if kindoffood not in ['cheap', 'expensive', 'moderate', 'priced'] and kindoffood != "":
            preferences[1] = kindoffood
        
    return preferences

#function that filters the restaurants which satisfies the first three preferences are, foodtype and price range.
def retrieve_restaurant(preferences):
    
    rest_info = load_restaurant_data()
    # when all preferences are any
    if preferences[0] == 'any'and preferences[1] == 'any' and preferences[2] == 'any':
        restaurants = rest_info["restaurantname"]
   # when preferences area and type are any
    elif preferences[0] == 'any' and preferences[1] == 'any':
        restaurants = rest_info[rest_info["pricerange"] == preferences[2]]
        restaurants = restaurants["restaurantname"]
    # when preferences area and price are any
    elif preferences[0] == 'any' and preferences[2] == 'any':
        restaurants = rest_info[rest_info["food"] == preferences[1]]
        restaurants = restaurants["restaurantname"]
    # when preferences type and price are any    
    elif preferences[1] == 'any' and preferences[2] == 'any':
        restaurants = rest_info[rest_info["area"] == preferences[0]]
        restaurants = restaurants["restaurantname"]
    # when only area is any
    elif preferences[0] == 'any':
        pdrestaurants = rest_info[rest_info["food"] == preferences[1]]
        pricerestaurants = pdrestaurants[pdrestaurants["pricerange"] == preferences[2]]
        restaurants = pricerestaurants["restaurantname"]
    # when only type is any
    elif preferences[1] == 'any':
        arearestaurants =  rest_info[rest_info["area"] == preferences[0]]
        pricerestaurants = arearestaurants[arearestaurants["pricerange"] == preferences[2]]
        restaurants = pricerestaurants["restaurantname"]
    # when only price is any
    elif preferences[2] == 'any':
        arearestaurants =  rest_info[rest_info["area"] == preferences[0]]
        pdrestaurants = arearestaurants[arearestaurants["food"] == preferences[1]]
        restaurants = pdrestaurants["restaurantname"]
    # when all preferences are given
    else:
        arearestaurants =  rest_info[rest_info["area"] == preferences[0]]
        pdrestaurants = arearestaurants[arearestaurants["food"] == preferences[1]]
        pricerestaurants = pdrestaurants[pdrestaurants["pricerange"] == preferences[2]]
        restaurants = pricerestaurants["restaurantname"]
    
    return restaurants.to_list()

#Function that is responsible for returning the phone number and address
def give_more_information(result, formal):
    
    rest_info = load_restaurant_data()
    indexje = (list(rest_info['restaurantname'])).index(result)
    response = ''
    
    #address
    address_response = (list(rest_info['addr'])[indexje])
    if address_response.lower() == 'nan':
        response += 'Address is unknown \n'
    else:
        response += 'The address is: {} \n'.format(address_response)
    
    #phone number
    number_response = (list(rest_info['phone'])[indexje])
    if number_response.lower() == 'nan':
        response += '    Phone number is unknown \n'
    else:
        response += '    The phone number is: {} \n'.format(number_response)
    
    #close the utterance with a question
    if formal:
        response += 'Are you satisfied?'
    else:
        response += 'Okay?'

    return response

def give_response(state, formal, preferences):
    # dictionary of responses
    if 0 in preferences.keys():
        area = preferences[0]
    else:
        area = ""
    if 1 in preferences.keys():
        foodtype = preferences[1]
    else:
        foodtype = ""
    if 2 in preferences.keys():
        price = preferences[2]
    else:
         price = ""         
    
    #template for formal responses
    if formal:
        responses ={
                "hello":
                    ['Good morning. ',
                     'Good afternoon. ',
                     'Good evening. '
                     ],
                
                "welcome": 
                    "Hello welcome to this restaurant recomendation guide. You may ask for restaurants by area, price range, or food type. To start, please enter your request. ",
                
                "area":
                    "What part of town do you have in mind? ",
                
                "foodtype":
                    "What type of food would you like? ",
               
                "price":
                    "What is your budget? Cheap, moderate, or expensive? ",
                
                "additional":
                    "Thank you, everything is clear. Finally, do you have any additional requirements? ",

        
                "nomatch":
                    "Sorry, there’s nothing matching your needs. Is there something that you would like to change about your order?\n I'm now searching for {}, {} restaurants in the {}".format(price, foodtype, area),
                  
                "bye":
                    "Thankyou, hopefully my service was useful. I look forward to our next meeting! ",
        
                "repeat":
                    "Im a sorry I am not able to repeat my sentence. ",
        
                "chooseadditional": 
                    "If you have an additional requirement, please choose from the options, busy restaurants, long stay restaurants, restaurants that allows children or romantic restaurants. ",
        
                "goodornot": 
                    'Please let me know if the restaurant sounds good or not by responding with "yes or no". ',
        
                "yesorno":
                    "Please answer with yes or no or give alternative preferences. ",
        
                "ending": 
                    "Hopefully I could help you well, I would appreciate it if you say bye to me before you leave, but if you need me to recommend more restaurants, please respond with reset. ",
                
                "stupid": [ "I'm very dumb",
                            "Are you sure you want to continue?",
                            "1+1 = 11", 
                            "I not speak English", 
                            "I do not understand...", 
                            "What is a restaurant even?", 
                            "I don\'t eat", 
                            'please abort', 
                            'exit while you still can',
                            'uhhh...',
                            'bliepbloepbliep',
                            '0101010111000111',
                            'Please talk to another robot, I just do the dishes',
                            'You may think I am formal, but I\'m really not',
                            'The answer to all your questions: 42',
                            'I\'ve got a bad feeling about this',
                            'I am rock people, hungabunga',
                            'abort and GET TO THE CHOPPAAA',
                            'Yes',
                            'No',
                            'I took the red pill nd now I\'m here, stuck in the matrix'
                            ],

                "survey": "I want to keep improving. How would you rate our dialog on a scale from 1 to 5? (1 being very bad, 5 being very good)",

                "invalid": "Sorry, you gave an invalid answer. Please provide me with feedback on a scale from 1 to 5"
            
            }
    #template fr informal responses
    else:
        responses ={
                "hello": [
                    "Hi. ",
                    "Hello! ",
                    "Heyy. "
                 ], 

                "welcome": 
                    "Hiya, I can recommend restaurants to you!!! C'mon, let’s choose a restaurant! You can ask for restaurants by area, price range, or food type. Let's go, enter your request :) ",
                
                "area":
                    "In what part of town do you want to dine??? ",
                
                "foodtype":
                    "What type of food do you like? ",
               
                "price":
                    "What’s your budget? Cheap, moderate, or expensive??? ",
                
                "additional":
                    "Okay then! Any additional requirements or not??? ",
        
                "nomatch":
                    "Sorry, there’s no restaurant matching your tastes :(. Wanna try something else???  \n I'm now looking for {}, {} restaurants in {} region.".format(price, foodtype, area),
                  
                "bye":
                    "Thanksss, hope it was useful. See yaa!!! ",
        
                "repeat":
                    "You want me to repeat? I won't do it sorry, just read my text back. ",
        
                "chooseadditional": 
                    "If you have any requirements to add, choose from the options, busy restaurants, long stay restaurants, restaurants that allows children or romantic restaurants. ",
        
                "goodornot": 
                    'Let me know if the restaurant sounds good or not by responding "yes" or "no"! ',
        
                "yesorno":
                    "Answer with yes or no or give other preferences. ",
        
                "ending": 
                    "I sure hope I was of help for you, It would be really awesome if you say bye to me before you leave, but if you need me to recommend more restaurants, respond with reset. ",

                "stupid": [ "I'm very dumb",
                            "Are you sure you want to continue?",
                            "1+1 = 11", 
                            "I not speak English", 
                            "I do not understand...", 
                            "What is a restaurant even?", 
                            "I don\'t eat", 
                            'please abort', 
                            'exit while you still can',
                            'uhhh...',
                            'bliepbloepbliep',
                            '0101010111000111',
                            'Please talk to another robot, I just do the dishes',
                            'You may think I am formal, but I\'m really not',
                            'The answer to all your questions: 42',
                            'I\'ve got a bad feeling about this',
                            'I am rock people, hungabunga',
                            'abort and GET TO THE CHOPPAAA',
                            'Yes',
                            'No',
                            'I took the red pill nd now I\'m here, stuck in the matrix'
                            ],

                "survey": "I hope you liked our conversation, I sure did! How would you rate my help on a scale from 1 to 5? (1 being very bad, 5 being very good)",

                "invalid": "Sorry, you did not give me a number from 1 to 5. Please give me the appropriate rating."
            }
    return responses[state]

#function that is responsible for recommending restaurants (Keep state 7 in mind)
def give_recommendation(restaurants, formal):
    recommendation = random.choice(restaurants)
    if formal:
        response = "Thank you, I came up with the following recommendation: {}. Are you satisfied? ".format(recommendation)
    else:
        response = "Okay, I came up with a recommendation: {}. Sounds good? ".format(recommendation)
    restaurants.remove(recommendation)
    return response, restaurants, recommendation