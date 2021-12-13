import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier # Import Decision Tree Classifier
from sklearn.neural_network import MLPClassifier


#Preparing the data
def load_train_data(path, train_split=0.85):
    
    acts = list()
    sentences = list()
    
    with open(path) as dt:
        for line in dt:
            l = line.lower()
            words = l.split()
            a, b = words[0], words[1:]
            acts.append(a)
            sentences.append(b)
    
    data = pd.DataFrame({'Acts': acts,'Sentence': sentences})
    
    length = int(train_split * len(data))
    
    training = data[:length]
    
    return data, training

def load_train_data_eval(path, train_split=0.85):
    
    acts = list()
    sentences = list()
    
    with open(path) as dt:
        for line in dt:
            l = line.lower()
            words = l.split()
            a, b = words[0], words[1:]
            acts.append(a)
            sentences.append(b)
    
    data = pd.DataFrame({'Acts': acts,'Sentence': sentences})
    
    length = int(train_split * len(data))
    
    training = data[:length]
    test = data[length:]
    
    return data, training, test

#Stupid return
def nlp_stupid(x):
    
    return 'I do not understand...'

#Baseline 1
def nlp_base(data):
    counts = data['Acts'].value_counts()
    total = len(data.index)
    prob = counts.divide(total)
    highprob = prob.idxmax()
    return highprob                     #Returns act with highest probability

#Baseline 2
def nlp_key(sentence, data):
    
    acts = list(data['Acts'].unique())
    actsdict = {
        'null' : ['unintelligible', 'sil', 'cough'], 
        'inform' : ['this', 'town', 'food','restaurant', 'expensive', 'cheap'],
        'confirm' : ['does', 'serve'],
        'affirm' : ['ye', 'yeah', 'yea','yes','agreed', 'correct', 'sure'],
        'request' : ['what', 'type', 'post', 'address', 'number', 'where', 'price'] ,
        'reqalts' : ['how', 'about', 'other','anything', 'else'],
        'negate' : ['no', 'stop'],
        'hello' : ['hello', 'hi', 'hiya', 'hey', 'hola', 'moshi moshi'],
        'repeat' : ['repeat'],
        'ack' : [],
        'bye' : ['bye', 'see you later', 'ciao', 'byebye', 'goodbye'],
        'thankyou': ['thank', 'thanks', 'thankyou', 'wonderful'],
        'restart' : ['reset', 'start'],
        'deny' : ['wrong'],
        'reqmore' : ['more'],
    }
    for word in sentence.split():
        for i in acts:
            if word in actsdict[i]:     #Checks words to words in dictionary to determine which act to choose
                return i
    return 'inform'                     # Here is inform so that we have a big chance of getting it right
        


#Decision Tree
def train_decision_tree(data):
    enc = LabelEncoder()
    vectorizer = CountVectorizer()       #encoding the X, make each sentence to a vector
    
    y_raw = data['Acts']
    x_raw = data['Sentence']
    
    y = enc.fit_transform(y_raw)          #encoding the y, matching each label to a number
    corpus = [' '.join(i) for i in x_raw] #get each sentence
    x = vectorizer.fit_transform(corpus)  #fit_transform or transform?
    
    vec_dict = {'Act':y,'Sentence':x} ##dictionary
    vec_data = pd.DataFrame(vec_dict)
    
    #splitting data
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.15)
    
    classifier_dt = DecisionTreeClassifier()
    model_dt = classifier_dt.fit(x_train,y_train)
    
    return model_dt, enc, vectorizer, x_test, y_test

#Logistic Regression
def train_logistic_regression(data):
    enc = LabelEncoder()
    vectorizer = CountVectorizer()       #encoding the X, make each sentence to a vector
    
    y_raw = data['Acts']
    x_raw = data['Sentence']
    
    y = enc.fit_transform(y_raw)          #encoding the y, matching each label to a number
    corpus = [' '.join(i) for i in x_raw] #get each sentence
    x = vectorizer.fit_transform(corpus)  #fit_transform or transform?
    
    vec_dict = {'Act':y,'Sentence':x} ##dictionary
    vec_data = pd.DataFrame(vec_dict)
    
    #splitting data
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.15)
    
    classifier_lr = LogisticRegression(solver='lbfgs', max_iter=100)
    model_lr = classifier_lr.fit(x_train, y_train)
    
    return model_lr, enc, vectorizer, x_test, y_test

#Neural Network
def train_neuralnetwork(data):
    encoder = LabelEncoder()
    vectorizer = CountVectorizer()
    
    y = encoder.fit_transform(data['Acts'])
    
    X = [' '.join(i) for i in data['Sentence']]
    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)
    
    x_train = vectorizer.fit_transform(x_train)
    x_test = vectorizer.transform(x_test)
    
    clf = MLPClassifier(hidden_layer_sizes=(50,), random_state=1)
    model = clf.fit(x_train, y_train)
    
    return model, encoder, vectorizer, x_test, y_test

#inverse encoder, class (number) to word
def number_to_word(sentence, model, encoder, vectorizer):
    vec = vectorizer
    enc = encoder
    
    sent_vec = vec.transform([sentence])
    prediction = model.predict(sent_vec)
    answer = encoder.inverse_transform(prediction)[0]
    
    return answer