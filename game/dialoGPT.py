import torch
from transformers import AutoModelForCausalLM, GPT2Tokenizer

device = "cuda:0" if torch.cuda.is_available() else "cpu"


def load_models(model_path="game/static/game/dialoGPT.pth"):
    global device

    # initialize tokenizer
    tokenizer = GPT2Tokenizer.from_pretrained('microsoft/DialoGPT-small')

    # initialize model
    model = AutoModelForCausalLM.from_pretrained(pretrained_model_name_or_path="microsoft/DialoGPT-medium").to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()

    return tokenizer, model


def get_dialogue(tokenizer, model, player, character, input_str, chat_history_ids):
    prompt_str = "Setting:\n* " + character["location"] + ": " + character["location_description"] + "\n\n" \
             + "Characters:\n* " + character["name"] + ":\n- persona: " + character["persona"] + "\n" \
             + "- appearance: " + character["appearance"] + "\n* Player:\n" + "- persona: " + player["persona"] + "\n" \
             + "- appearance: " + player["appearance"] + "\n\n\n===\n\nConversation:\n"
    player_str = "Player:"
    npc_str = character["name"] + ":"
    return generate_response(tokenizer, model, input_str, prompt_str, player_str, npc_str, chat_history_ids)
        

def generate_response(tokenizer, model, input_str, prompt_str, player_str, npc_str, chat_history_ids, max_length=256):
    global device

    newline_ids = tokenizer.encode("\n", return_tensors='pt').to(device)
    eos_token_id = newline_ids[0]

    prompt_ids = tokenizer.encode(prompt_str, return_tensors='pt').to(device)
    player_ids = tokenizer.encode(player_str, return_tensors='pt').to(device)
    npc_ids = tokenizer.encode(npc_str, return_tensors='pt').long().to(device)
    input_str_ids = tokenizer.encode(input_str, return_tensors='pt').to(device)
    chat_history_ids = torch.cat([chat_history_ids, player_ids, input_str_ids, newline_ids, npc_ids], dim=-1)

 
    bot_input_ids = torch.cat([prompt_ids, chat_history_ids], dim=-1)
    bot_ouput_ids = model.generate(
        bot_input_ids,
        pad_token_id=tokenizer.eos_token_id,
        max_length=len(bot_input_ids[0]) + max_length,
        no_repeat_ngram_size=3,
        top_k=50, top_p=0.9, temperature = 0.3,
        do_sample=True,
        num_beams=1,
        eos_token_id=tokenizer.encode("\n")[0]
    )
    
    chat_history_ids = bot_ouput_ids[:, prompt_ids.shape[-1]:]
    response = tokenizer.decode(bot_ouput_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
    response = response.replace("#", "")
    return chat_history_ids, response
