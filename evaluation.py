from nlp import load_train_data_eval, nlp_base, nlp_key, train_decision_tree, train_neuralnetwork, train_logistic_regression
import os
from sklearn import metrics #Import scikit-learn metrics module for accuracy calculation

#This function calculates the accuracy of the first baseline model
def nlp_base_performance(trainingdf, testdf):
    testvalues = testdf.values.tolist()
    correct, incorrect = 0, 0
    predictedlabel = nlp_base(trainingdf) # first we create the model

    for labels in testvalues:
            if labels[0]==predictedlabel:
                correct += 1
            else:
                incorrect += 1
    
    performance = correct / (correct + incorrect) #Here we calculate the accuracy
    print(
        'The first baseline accuracy is:        {}'.format(performance))

#This function calculates the accuracy of the second baseline model
def nlp_key_performance(testdf):
    testdfvalues = testdf.values.tolist()
    correct, incorrect = 0, 0
    for sentences in testdfvalues:
        sentence = ' '.join(sentences[1]) # This was neccassary for the format difference list and strings
        label = nlp_key(sentence, testdf) # first we create the model
        if label == sentences[0]:
            correct += 1
        else:
            incorrect +=1 
    performance = correct / (correct + incorrect) #Here we calculate the accuracy
    print(
        "The second baseline accuracy is:       {}".format(performance))

#This function calculates the accuracy of the decision tree model
def nlp_decision_tree_performance(data):
    model, enc, vec, x_test, y_test = train_decision_tree(data) # we need to train a model
    y_pred = model.predict(x_test)                              #predict with the model
    performance = metrics.accuracy_score(y_test, y_pred)        #check accuracy
    print(
        "The decision tree accuracy is:         {}".format(performance))

#This function calculates the accuracy of the logistic regression model
def nlp_logistic_regression_performance(data):
    model, enc, bow, x_test, y_test = train_logistic_regression(data)
    y_pred = model.predict(x_test)
    performance = metrics.accuracy_score(y_test, y_pred)
    print(
        "The logistic regression accuracy is:   {}".format(performance))

#This function calculates the accuracy of the neural network model
def nlp_neuralnetwork_performance(data):
    model, enc, bow, x_test, y_test = train_neuralnetwork(data)
    y_pred = model.predict(x_test)
    performance = metrics.accuracy_score(y_test, y_pred)
    print(
        "The neural network accuracy is:        {}".format(performance))

# Here we start everything up
def main():
    data, training, test = load_train_data_eval(os.path.join('dialog_acts.dat'))
    nlp_base_performance(training, test)
    nlp_key_performance(test)
    nlp_decision_tree_performance(data)
    nlp_logistic_regression_performance(data)
    nlp_neuralnetwork_performance(data)

if __name__ == '__main__':
    print("Some models will take a while, please be patient :)\n")
    main()
    print()