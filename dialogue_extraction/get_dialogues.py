import os 
import jsonlines
from pprint import pprint
from collections import defaultdict

import openai
openai.api_key = os.getenv("OPENAI_API_KEY")


def read_dataset():
    """
    Importing the dataset (lines for correlation to match in conversations)
    """
    corpus = "cornell-movie-dialogs-corpus"
    lines = open(corpus + '/movie_lines.txt', encoding='utf-8', errors='ignore').read().split('\n')
    conversations= open(corpus + '/movie_conversations.txt', encoding = 'utf-8', errors = 'ignore').read().split('\n')
    characters = open(corpus + '/movie_characters_metadata.txt', encoding = 'utf-8', errors = 'ignore').read().split('\n')
    return lines, conversations, characters


def extract_characters_and_persona(characters_data, movie):
    """
    Extract character names and use GPT3 to extract personas.
    """
    id2character = {}
    for line_raw in characters_data:
        line = line_raw.split(' +++$+++ ')
        if len(line) != 6:
            continue
        character_id, character_name, movie_id, movie_name = line[:4]
        if movie_name != movie:
            continue
        prompt = "Who is {} in the movie '{}' and what is their persona?".format(character_name.lower().capitalize(), movie_name.title())
        response = openai.Completion.create(
            engine="text-curie-001",
            prompt=prompt,
            temperature=0.7,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        persona = response['choices'][0]['text'].replace("\n", "")
        id2character[character_id] = {
            "name": character_name.lower().capitalize(),
            "persona": persona
        }
        print(character_name + ": " + persona)
    return id2character


def create_id2movie(characters_data):
    id2movie = {}
    for line in characters_data:
        _line = line.split(' +++$+++ ')
        if len(_line) != 6:
            continue
        character_id, character_name, movie_id, movie_name = _line[:4]
        id2movie[movie_id] = movie_name        
    return id2movie


def create_id2line(lines_data):
    """
    Creating a dictionary that maps each line id to the actual text 
    and the ID of the character that it belongs to.
    """
    id2line = {}
    for line in lines_data:
        _line = line.split(' +++$+++ ')
        if len(_line) == 5:
            id2line[_line[0]] = {"line": _line[4], "character_id": _line[1]}
    return id2line


def count_conversations(conversations_data, id2movie):
    counter = defaultdict(int)
    for conversation_raw in conversations_data:
        conversation = conversation_raw.split(' +++$+++ ')
        if len(conversation) != 4:
            continue
        characterA_id, characterB_id, movie_id, lines_id = conversation
        movie_name = id2movie[movie_id]
        counter[movie_name] += 1
    pprint(sorted(counter.items(), key=lambda kv: kv[1], reverse=True))


def extract_dialogue_data(id2line, id2movie, conversations_data, characters_data, movie):
    id2character = extract_characters_and_persona(characters_data, movie)

    data = []
    for conversation_raw in conversations_data:
        conversation = conversation_raw.split(' +++$+++ ')
        if len(conversation) != 4:
            continue
        characterA_id, characterB_id, movie_id, lines_id = conversation
        if id2movie[movie_id] != movie:
            continue
        lines_id = lines_id[1:-1].replace("'", "").replace(" ", "").split(",")
        dialogue = []
        for line_id in lines_id:
            character_id = id2line[line_id]["character_id"]
            character_name = id2character[character_id]["name"]
            line_text = id2line[line_id]["line"]
            dialogue.append({"name": character_name, "line": line_text})

        conversation = {
            "characters": [id2character[characterA_id], id2character[characterB_id]],
            "dialogue": dialogue
        }
        data.append(conversation)

    filename = "dialogues/" + movie + ".jsonl"
    with jsonlines.open(filename, 'w') as writer:
        writer.write_all(data)
    

def main():
    # import dataset    
    lines_data, conversations_data, characters_data = read_dataset()

    # create data mapping
    id2line = create_id2line(lines_data)
    id2movie = create_id2movie(characters_data)

    # create a dialogue file for each movie
    movies = ["aliens", "alien", "alien vs. predator"]
    for movie in movies:
        extract_dialogue_data(id2line, id2movie, conversations_data, characters_data, movie)


if __name__ == '__main__':
    main()
