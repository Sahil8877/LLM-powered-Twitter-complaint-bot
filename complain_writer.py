from llama_cpp import Llama
import random

def response(complains, reason):
    response_list = []
    tones = [
        "angry",
        "sarcastic",
        "dramatic",
        "passive aggressive",
        "existential",
        "british humour",
        "chronically online",
        "overreacting"
    ]
    llm = Llama(
            model_path="model/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf",
            n_ctx=2048,
            verbose=False)
    
    for complaint in complains:
        tone = random.choice(tones)
        
        messages = [
            {
                "role": "system",
                "content": (
                    f"You are a {tone} Twitter user who writes short funny complaint tweets "
                    f"about {reason} conditions. "
                    "Output ONLY the tweet text. "
                    "Mention officials for that region, use hashtags. "
                    "Do not explain anything. "
                    "Do not add headers, notes, or multiple tweets. "
                    "Maximum 1 sentence."
                )
            },
            {
                "role": "user",
                "content": complaint
            }
        ]

        response = llm.create_chat_completion(
            messages=messages,
            max_tokens=60,
            temperature=1.1,
            top_p=0.9,
            repeat_penalty=1.25,
            stop=["\n", "<|eot_id|>"]
        )

        response_list.append(response['choices'][0]['message']['content'])
        
    return response_list
        