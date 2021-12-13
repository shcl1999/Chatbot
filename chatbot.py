import os
import argparse

from nlp import load_train_data, nlp_stupid, nlp_base, nlp_key, train_decision_tree, train_neuralnetwork, train_logistic_regression, number_to_word
from dialog_manager import state_transition

#to run this code, please CD to the correct file and run 
#python chatbot.py 
#or 
#python3 chatbot.py

#you can also switch on some configurations with: 
#-c (system answers all utterances in capslog will be swtiched on)
#-f (formal response will be switched on)
#-a (the dialog acts will be shown as well will be swtiched on)
#example of running it:
#python chatbot.py -c -f -a 
#or 
#python3 chatbot.py -c -f -a

# This is the first message you see when running the code
WELCOME_MESSAGE = """
Welcome! This is a beautiful chatbot.

However.. it is as smart as you want it to be. So choose wisely!

If you have had enough of the chatbot, simply type abort or exit,
and it will shut up.

"""

# This code makes it possible to add arguments to your runcode
parser = argparse.ArgumentParser(
    description='MAIR chatbot project.'
)

# This part makes it possible to choose between capital letters or lower letters
parser.add_argument(
    '-c', '--caps',                                         
    action = 'store_true',                                  
    help='By using -c the bot will only respond in caps'    
)

# This determines whether the response is formal or not
parser.add_argument(
    '-f', '--formal',
    action = 'store_true',
    help='By using -f the bot will give formal responds'
)

# This determines whether we see the dialog acts in the conversation or not
parser.add_argument(
    '-a', '--acts',
    action = 'store_true',
    help='By using -a the bot will also show you the acts'
)

args = parser.parse_args()

# This displays the conversation that is extracted in chat_client
def display_convo(convo, show_acts, max_sentences=10):
    # max_sentences is a hyperparameter
    os.system('clear')
    
    print(0*'\n')
    print(40*'#' + ' BEAUTIFUL CHATBOT ' + 40*'#')
    
    # To create a conversation within the borders of the terminal
    if len(convo) < max_sentences:
        print(3 * (max_sentences - len(convo)) * '\n')
   
    # To create a conversation within the borders of the terminal
    if len(convo) > 0: 
        for i in range(0, min(len(convo), max_sentences)):
            i += max(0, len(convo) - max_sentences)
            print('> {}'.format(convo[i]['user']))
            print('--> {}'.format(convo[i]['bot']))
            if show_acts:
                print('speech act:({})'.format(convo[i]['act']))
            print()

# This creates the dialog
def chat_client(method, caps, formal, show_acts, name):
    
    keep_chatting = True
    state = 1 # to set the start state
    preferences = {} # Initiate preference
    restaurants = []
    additional_pref = list()
    result = ''
    
    if formal:
        beginconvo = 'Hello, welcome to the Group 25 restaurant system! \n    You can ask for restaurants by area, price range or food type. How may I help you?'
    else:
        beginconvo = 'Hey there!!! Welcome to the Group 25 restaurant system! \n    You can ask for restaurants by area, price range, or food type. Let\'s go, enter your request! :)'
 
    if caps:
        beginconvo = beginconvo.upper()
    
    convo = []

    
    #The first interation so that we know to which bot we are talking and what is asked from the user
    if show_acts:
        convo.append({
                'user': 'You are talking to the {} bot'.format(name),
                'bot': beginconvo,
                'act': ''
            })
    else:
        convo.append({
                'user': 'You are talking to the {} bot'.format(name),
                'bot': beginconvo
            })
    
    # During the conversation
    while keep_chatting:
        
        display_convo(convo, show_acts)
        
        user_input = input('> ')
        
        #Extra to always be able to leave the bot
        if user_input.lower() == 'abort' or user_input.lower() == 'exit':
            message = '--> bye bye, hope to see you again soon!'
            if caps:
                print(message.upper())
            else:
                print(message) 
            exit(0)
            
        act = method(user_input)
        # By talking to the dialog manager we get the neccessary information and response back for the conversation
        state, client_output, preferences, restaurants, result = state_transition(user_input, state, act, preferences, restaurants, result, additional_pref, formal) 
        
        # Make output caps if its true
        if caps:
            client_output = client_output.upper()

        # Creating the right conversation logs for show_acts = true or not
        if show_acts:
            convo.append({
                'user': user_input,
                'bot': client_output,
                'act': act
            })
        else:
            convo.append({
                'user': user_input,
                'bot': client_output
            })
        
    return

def main(caps, formal, show_acts):
    os.system('clear')

    # Will happen more often when bot text is shown and caps=True
    if caps:
        print(WELCOME_MESSAGE.upper())
    else:
        print(WELCOME_MESSAGE)
    
    data, training = load_train_data(os.path.join('dialog_acts.dat')) # Create the neccessary datasets
    
    #In this loop we will train the models based on the input.
    while True:
        method = input('Choose a method for your bot. The options are: \n(s)tupid, (b)ase, (k)ey, (t)ree, (n)eural, (l)ogistic \n> ')

        if method.lower() == 's' or method.lower() == 'stupid':         # This is the extremely stupid bot that does nothing correct
            algo = lambda x: nlp_stupid(x)
            break
        if method.lower() == 'b' or method.lower() == 'base':           # This is the base which only predicts the majority class
            algo = lambda x: nlp_base(data)
            break
        if method.lower() == 'k' or method.lower() == 'key':            # This other base is completely based on keyword detection
            algo = lambda x: nlp_key(x, training)
            break 
        if method.lower() == 't' or method.lower() == 'tree':           # This is our Decision Tree model
            model, enc, bow, x_test, y_test = train_decision_tree(data)
            algo = lambda x: number_to_word(x, model, enc, bow)
            break
        if method.lower() == 'n' or method.lower() == 'neural':         # This is our Neural Network model
            message = '\nThanks for choosing my brain! Let me get those gears oiled up and ready to grind, give me a few seconds.'
            if caps:                                                    # We need to use CAPS for everything that seems like a text from the bot when caps = true
                print(message.upper())
            else:
                print(message)
            model, enc, bow, x_test, y_test = train_neuralnetwork(data)
            algo = lambda x: number_to_word(x, model, enc, bow)         # For vector translation to words
            break
        if method.lower() == 'l' or method.lower() == 'logistic':       # This is our Logistic regression model
            message = '\nGive me a few seconds to become a very logical being, capable of helping you out with all your restaurant related questions! You\'re welcome! :)'
            if caps:                                                    # We need to use CAPS for everything that seems like a text from the bot when caps = true
                print(message.upper())
            else:
                print(message) 
            model, enc, bow, x_test, y_test = train_logistic_regression(data)
            algo = lambda x: number_to_word(x, model, enc, bow)         # For vector translation to words
            break
            
        os.system('clear')
    
        # If nothing of the above happens, we stay in the loop, but display a new message to indicate that the input did not suffice
        print(WELCOME_MESSAGE)
        print('WHOOPS... that method is NOT recognized.')
        print()
    
    os.system('clear')
    
    #Here we will make the UI
    chat_client(algo, caps, formal, show_acts, method) # We only need to train our model once and give it to the chat_client
    
if __name__ == '__main__':
    main(args.caps, args.formal, args.acts)     # To give these booleans to the main function
    
    