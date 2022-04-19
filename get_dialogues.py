import csv
import pandas as pd


corpus = "cornell-movie-dialogs-corpus"

# Importing the dataset (lines for correlation to match in conversations)
lines = open(corpus + '/movie_lines.txt', encoding='utf-8', errors='ignore').read().split('\n')
conversations = open(corpus + '/movie_conversations.txt', encoding = 'utf-8', errors = 'ignore').read().split('\n')

# Creating a dictionary that maps each line/id
id2line = {}
for line in lines:
    _line = line.split(' +++$+++ ')
    if len(_line) == 5:
        id2line[_line[0]] = _line[4]

# List of all of the conversations
conversations_ids = []
for conversation in conversations[:-1]:
    _conversation = conversation.split(' +++$+++ ')[-1][1:-1].replace("'", "").replace(" ", "")
    conversations_ids.append(_conversation.split(','))
    
print(conversations_ids[0])