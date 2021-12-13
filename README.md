# MAIR Chatbot
Welcome! This is the MAIR 2021 project. We, as members of group 25, made a chatbot which can recommend restaurants based on the users preferences. The chatbot engages in a conversation to get to know the required preferences to give a good recommendation.


## Installation
Install the necessary packages using:

```python
pip install -r requirements.txt
```

The required python files:
- chatbot.py
- nlp.py
- dialog_manager.py
- evaluation.py

The following datafiles should be in the same map as the python files:

- dialog_acts.dat
- new.csv
- restaurant_info.csv
- survey.csv

## Usage
To start the program use:

```python
python chatbot.py
```
Many different options are available for the output which can be printed using:

```python
python chatbot.py --help
```
If you want to check the accuracy of the used models simply use:

```python
python evaluation.py
```

Next to that, we also made it possible for users to choose between the algorithms to determine which bot they want to speak to. This will appear in their screen as soon as the program starts running.

## Contributors
- Amy Oey
- Andrea van Roijen
- Kathleen de Boer
- Sunny Hseih
