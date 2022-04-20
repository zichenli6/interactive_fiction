import torch
from transformers import AutoModelForCausalLM, GPT2Tokenizer

device = "cuda:0" if torch.cuda.is_available() else "cpu"


def load_models():
    global device

    # initialize tokenizer
    tokenizer = GPT2Tokenizer.from_pretrained('microsoft/DialoGPT-small')

    # initialize model
    model_path = "game/static/game/dialoGPT.pth"
    model = AutoModelForCausalLM.from_pretrained(pretrained_model_name_or_path="microsoft/DialoGPT-medium").to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()

    return tokenizer, model


def get_dialogue(tokenizer, model, player, character, input_str, chat_history_ids):
    prompt = "Setting:\n* " + character["location"] + ": " + character["location_description"] + "\n\n" \
             + "Characters:\n* " + character["name"] + ":\n- persona: " + character["persona"] + "\n" \
             + "- appearance: " + character["appearance"] + "\n* Player:\n" + "- persona: " + player["persona"] + "\n" \
             + "- appearance: " + player["appearance"] + "\n\n\n===\n\nConversation:\n"
    player_str = "Player:"
    npc_str = character["name"] + ":"
    return generate_response(tokenizer, model, input_str, prompt, chat_history_ids, player_str, npc_str)
        


def inference(
    tokenizer, model,
    prompt_ids, chat_history_ids,
    start_character_ids=None, eos_token_id=None, max_length=256
):
    newline_ids = tokenizer.encode("\n", return_tensors='pt').to(device)
    chat_history_ids = torch.cat([chat_history_ids, newline_ids], dim=-1)
    if start_character_ids is not None:
        chat_history_ids = torch.cat([chat_history_ids, start_character_ids], dim=-1)
    
    bot_input_ids = torch.cat([prompt_ids, chat_history_ids], dim=-1)
    if eos_token_id is None:
        eos_token_id = tokenizer.encode("###")[0]
    
    bot_ouput_ids = model.generate(
        bot_input_ids,
        pad_token_id=tokenizer.eos_token_id,
        max_length=len(bot_input_ids[0]) + max_length,
        no_repeat_ngram_size=3,
        top_k=100, top_p=0.9, temperature = 0.9,
        eos_token_id=eos_token_id.item()
    )
    
    chat_history_ids = bot_ouput_ids[:, prompt_ids.shape[-1]:]
    response = tokenizer.decode(bot_ouput_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
    return chat_history_ids, response


def generate_response(tokenizer, model, input_str, prompt, chat_history_ids, player_str, npc_str):
    global device

    prompt_ids = tokenizer.encode(prompt, return_tensors='pt').long().to(device)
    user_ids = tokenizer.encode(player_str, return_tensors='pt').long().to(device)
    other_character_ids = tokenizer.encode(npc_str, return_tensors='pt').long().to(device)

    newline_ids = tokenizer.encode("\n", return_tensors='pt').to(device)
    eos_token_id = newline_ids[0]

    user_input_ids = tokenizer.encode(input_str, return_tensors='pt').to(device)
    chat_history_ids = torch.cat([chat_history_ids, user_ids, user_input_ids], dim=-1)

    chat_history_ids, response = inference(
        tokenizer, model,
        prompt_ids, chat_history_ids, 
        start_character_ids=other_character_ids, eos_token_id=eos_token_id
    )
    return chat_history_ids, response



def main():
    global device
    
    tokenizer, model = load_models()

    prompt = """Setting:
* Lavoratory: The lavatory contains a long trough for which the knights can use for urination. Crude toilets are also included for defecation. The design is all stone walls with candles, and no privacy walls.

Characters:
* King:
- persona: I am the king of my lands, or, I used to be. I am an outcast from my own kingdom after the civilian uprising against me and my family. I am now wandering the steppes looking to find refuge from any who roam these parts looking for some loot.
- appearance: I am wearing pants. A pair of leather breeches. Good for hiding one's shame. I am wearing shirt. The shirt is worn and tattered, but could still be used to cover up. I am wearing robe. Thick, brown, and heavy, the robe seems perfect for cold weather. I am wearing crown. The crown is made of gold and embedded with rare jewels I have dull sword. The sword could hardly pierce anything due to its severe lack of an edge.
* Player:
- persona: I am an explorer from earth. I like to travel to different places and learn about strong but interesting things. I am always excited about exploring the unknown.
- appearance: I am wearing jeans. The jeans are loose but strong. I am wearing windbreaker. The windbreaker is long, black and looks very cold. I am wearing a hat. I'm wearing a hat. The hat is brown and partly hides my face.


===

Conversation:
"""

    chat_history = ""
    player = "Player:"
    other_character = "King:"

    prompt_ids = tokenizer.encode(prompt, return_tensors='pt').long().to(device)
    chat_history_ids = tokenizer.encode(chat_history, return_tensors='pt').long().to(device)
    user_ids = tokenizer.encode(player, return_tensors='pt').long().to(device)
    other_character_ids = tokenizer.encode(other_character, return_tensors='pt').long().to(device)

    newline_ids = tokenizer.encode("\n", return_tensors='pt').to(device)
    eos_token_id = newline_ids[0]

    is_user_turn = True
    while True:
        if is_user_turn:
            input_str = input("Player:") 
            if input_str == "":
                break
            user_input_ids = tokenizer.encode(input_str, return_tensors='pt').to(device)
            chat_history_ids = torch.cat([chat_history_ids, user_ids, user_input_ids], dim=-1)
            is_user_turn = not is_user_turn
        else:
            chat_history_ids, response = gen_response(tokenizer, model, prompt_ids, chat_history_ids, start_character_ids=other_character_ids, eos_token_id=eos_token_id)
            print(f"{other_character}{response}", end="")
            is_user_turn = not is_user_turn

if __name__ == '__main__':
    main()