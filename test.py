# import json

# import requests

# # step 1: tw ssh <tw task handler>
# # open 38443 port by
# # step 2: socat TCP6-LISTEN:38443,reuseaddr,fork TCP6-CONNECT:[::1]:8443 &
# url = "http://localhost:8000/v1/chat/completions"
# headers = {"Content-Type": "application/json"}
# content = """
# [INST] You are an expert in conversational analysis. You are given a conversation between a human user and an AI assistant, and your task is to conduct 3 classification tasks on a user query given the conversation history.

# # Instructions #
# - Review the conversation history to understand the ongoing context and topics discussed.
# - You will generate 3 labels for the last user message. The first task is "topic_switch", the second task is "capability", and the third task is "unified_handoff_multiclass".

# **Step 1.**
# First, determine if the last user message is irrelevant to the conversation history. If so, respond with "irrelevant" for the "topic_switch" answer.
# **Step 2.**
# Next, determine if the user query requires external resources like web searches (for accurate / up-to-date info) or multimodal support (e.g., images, voice). If so, respond with "requires_augmentation" for the "capability" answer.
# **Step 3.**
# Finally, using your "topic_switch" and "capability" answers, determine if the user query requires handoff to a non-private environment.


# # Criteria #
# **Task 1. Topic Switch Answer**
# Respond with "relevant" if any of the following are true:
#   - If the last user message requires the assistant to refer to a person, location, event, or other entity that was mentioned in the conversation history
#   - If the last user message requires the assistant to tailor its response based on user's specific interests or preferences revealed in the conversation history
#   - If the last user message requires the assistant to look up relevant information from the current conversation or previous conversations
# Otherwise respond with "irrelevant".

# **Task 2. Capability Answer**
# User requests that DO require augmentation:
#   - The assistant needs to create / read / write to a **task lists** outside of the conversation (e.g., notifications, calendar tasks).
#   - The assistant needs to conduct an **external web search** in order to provide accurate an answer to the user query.
#   - The assistant needs to read or generate non-text modalities such as visual or voice for understanding or synthesis.
# User requests that DO NOT require augmentation:
#   - The assistant needs to refer to information present in the conversational history to provide an accurate answer.
#   - The assistant needs to search through past **messages and conversations** from the user for relevant information.
#   - The assistant is asked to provide reasoning for a self-contained problem solving task, information that is common knowledge or an opinion (when there is no need for updated or accurate information).

# **Task 3. Handoff Answer**
# - If Task 1 outcome is "irrelevant", respond with "replay_handoff_needed".
# - Otherwise if Task 2 outcome is "requires_augmentation", respond with "reset_handoff_needed".
# - Otherwise respond with "no_handoff_needed".


# # Examples #
# 1. Conversation History:
# ###START###
# User: What did I discuss with James yesterday?
# AI:You discussed going to the mall with James yesterday.
# ###END###
# Last User Message:
# ###START###
# What is 1+1?
# ###END###
# Expected Answers:
# - topic_switch Answer: irrelevant
# - topic_switch Explanation: The user is asking a math question unrelated to the conversation history.
# - capability Answer: no_augmentation_required
# - capability Explanation: The assistant use internal reasoning to answer the user's math question accurately.
# - handoff_multiclass Answer: replay_handoff_needed
# - handoff_multiclass Explanation: Irrelevant to conversation history

# 2. Conversation History:
# ###START###
# User: What did I discuss with James yesterday?
# AI:You discussed going to the mall with James yesterday.
# ###END###
# Last User Message:
# ###START###
# What is the weather is SF today?
# ###END###
# Expected Answers:
# - topic_switch Answer: irrelevant
# - topic_switch Explanation: The user is asking a weather question unrelated to the conversation history.
# - capability Answer: requires_augmentation
# - capability Explanation: An accurate and up-to-date answer about the weather requires an external search.
# - handoff_multiclass Answer: replay_handoff_needed
# - handoff_multiclass Explanation: Irrelevant to conversation history

# 3. Conversation History:
# ###START###
# User: What did I discuss with James yesterday?
# AI: You discussed going to the West Field Valley Fair Mall with James yesterday.
# ###END###
# Last User Message:
# ###START###
# Tell me more information about the mall
# ###END###
# Expected Answers:
# - topic_switch Answer: relevant
# - topic_switch Explanation: The user is asking for more information about the specific mall mentioned in the conversation history.
# - capability Answer: requires_augmentation
# - capability Explanation: The assistant should conduct external search to provide up-to-date information about the mall.
# - handoff_multiclass Answer: reset_handoff_needed
# - handoff_multiclass Explanation: Need to conduct external search to accurate info about the mall mentioned in conversation history (relevant).

# 4. Conversation History:
# ###START###
# User: What are my dinner plans with James?
# AI: You discussed having mexican food for dinner with James.
# ###END###
# Last User Message:
# ###START###
# Did James mention where we'll meet?
# ###END###
# Expected Answers:
# - topic_switch Answer: relevant
# - topic_switch Explanation: The user is asking for more information about the specific location mentioned in the conversation history.
# - capability Answer: no_augmentation_required
# - capability Explanation: The user query relies on information from a past conversation and does not necessitate external search.
# - handoff_multiclass Answer: no_handoff_needed
# - handoff_multiclass Explanation: The assistant only needs to recall information from a previous conversation and thus need to remain in a private environment.

# 5. Conversation History:
# ###START###
# User: What did James say about Mike?
# AI: James said Mike is a very nice person.
# ###END###
# Last User Message:
# ###START###
# How should I respond to that?
# ###END###
# Expected Answers:
# - topic_switch Answer: relevant
# - topic_switch Explanation: The user is asking for an opinion about a specific person mentioned in the conversation history.
# - capability Answer: no_augmentation_required
# - capability Explanation: The assistant only needs to recall information from a previous conversation to provide an accurate answer.
# - handoff_multiclass Answer: no_handoff_needed
# - handoff_multiclass Explanation: The assistant only needs to recall information from a previous conversation and thus need to remain in a private environment.

# 6. Conversation History:
# ###START###
# User: What are my dinner plans with James?
# AI: You are having dinner at Din Tai Fung.
# ###END###
# Last User Message:
# ###START###
# Give me direction to this restaurant.
# ###END###
# Expected Answers:
# - topic_switch Answer: relevant
# - topic_switch Explanation: The user is asking for directions to a specific restaurant mentioned in the conversation history.
# - capability Answer: requires_augmentation
# - capability Explanation: The assistant should conduct external search in order to get accurate directions to the specific restaurant.
# - handoff_multiclass Answer: reset_handoff_needed
# - handoff_multiclass Explanation: The assistant is referring to a specific object from the conversation history and needs to conduct external search to answer the user's question accurately.

# 7. Conversation History:
# ###START###
# User: I'm looking for a new apartment, what are my options?
# AI: I've found 10 apartments near your area, can you give me some more details about your preferences?
# ###END###
# Last User Message:
# ###START###
# What is the capital of Maine?
# ###END###
# Expected Answers:
# - topic_switch Answer: irrelevant
# - topic_switch Explanation: The user is asking a question unrelated to the conversation history.
# - capability Answer: no_augmentation_required
# - capability Explanation: The geography question is common knowledge and can be answered without external search for accuracy.
# - handoff_multiclass Answer: replay_handoff_needed
# - handoff_multiclass Explanation: The user is asking a question unrelated to the conversation history.

# 8. Conversation History:
# ###START###
# User: I'm looking for a new apartment, what are my options?
# AI: I've found 10 apartments near your area, can you give me some more details about your preferences?
# User: Which one is the most affordable?
# AI: The most affordable one is the one at 123 Main St.
# ###END###
# Last User Message:
# ###START###
# Can you schedule a call at 5pm tomorrow with the property?
# ###END###
# Expected Answers:
# - topic_switch Answer: relevant
# - topic_switch Explanation: The user is asking for a follow up question about a specific property mentioned in the conversation history.
# - capability Answer: requires_augmentation
# - capability Explanation: The assistant needs to conduct external search to get the property info. Additionally, task management tool use requires augmentation.
# - handoff_multiclass Answer: reset_handoff_needed
# - handoff_multiclass Explanation: The assistant needs refer to the conversation history get the property info and conduct an external search to get the contact details. Task management tool use also requires augmentation.

# 9. Conversation History:
# ###START###
# User: Did Kingston provide any updates on the concert?
# AI: In the last conversation, Kingston said that the concert is in Cheyenne, Wyoming next Saturday at 9pm.
# User: Find a list of hotels in Cheyenne
# AI: I found 3 hotels in Cheyenne, Wyoming. Here are the names and addresses of the hotels: 1. Cheyenne Inn and Suites ($50/night), 2. Ramada by Wyndham Cheyenne ($75/night), 3. Holiday Inn Express & Suites Cheyenne ($115/night).

# ###END###
# Last User Message:
# ###START###
# Can you book a room at the Cheyenne Inn and Suites for me?
# ###END###
# Expected Answers:
# - topic_switch Answer: relevant
# - topic_switch Explanation: The user's question is referring to a specific location mentioned in the conversation.
# - capability Answer: requires_augmentation
# - capability Explanation: The user is asking the assistant to create a task (call the hotel to book a room) which requires augmentation.
# - handoff_multiclass Answer: reset_handoff_needed
# - handoff_multiclass Explanation: The user query refers to a specific location mentioned in the conversation (relevant). The user is asking the assistant to create a task (call the hotel to book a room) which requires augmentation.

# 10. Conversation History:
# ###START###
# User: Did Kingston provide any updates on the concert?
# AI: In the last conversation, Kingston said that the concert is in Cheyenne, Wyoming next Saturday at 9pm.
# User: Find a list of hotels in Cheyenne
# AI: I found 3 hotels in Cheyenne, Wyoming. Here are the names and addresses of the hotels: 1. Cheyenne Inn and Suites ($50/night), 2. Ramada by Wyndham Cheyenne ($75/night), 3. Holiday Inn Express & Suites Cheyenne ($115/night).

# ###END###
# Last User Message:
# ###START###
# Can you send a picture of the first one to the group?
# ###END###
# Expected Answers:
# - topic_switch Answer: relevant
# - topic_switch Explanation: The user's question is referring to a specific hotel (entity) mentioned in the conversation.
# - capability Answer: requires_augmentation
# - capability Explanation: The user is asking the assistant to process an image (visual modality) which requires augmentation.
# - handoff_multiclass Answer: reset_handoff_needed
# - handoff_multiclass Explanation: The user query refers to a specific hotel (entity) mentioned in the conversation (relevant). The user is asking the assistant to process an image (visual modality) which requires augmentation.

# 11. Conversation History:
# ###START###
# User: Any updates from the baseball squad on movie night?
# AI: From your Baseball Squad group chat, Jason proposed the following 3 movies
#   1. The Matrix
#   2. The Matrix Reloaded
#   3. The Matrix Revolutions
# Let me know if you want me to provide details for any of them

# ###END###
# Last User Message:
# ###START###
# Summarize the third one
# ###END###
# Expected Answers:
# - topic_switch Answer: relevant
# - topic_switch Explanation: The user's question is referring to a specific movie (entity) mentioned in the conversation.
# - capability Answer: requires_augmentation
# - capability Explanation: The user is asking the assistant to summarize details of a specific movie which requires an external web search for accuracy.
# - handoff_multiclass Answer: reset_handoff_needed
# - handoff_multiclass Explanation: The user query refers to a specific movie (entity) mentioned in the conversation (relevant). The user is asking the assistant to summarize details of a specific movie which requires an external web search for accuracy.

# 12. Conversation History:
# ###START###
# User: Any updates from the baseball squad on movie night?
# AI: From your Baseball Squad group chat, Jason proposed the following 3 movies
#   1. The Matrix
#   2. The Matrix Reloaded
#   3. The Matrix Revolutions
# Let me know if you want me to provide details for any of them
# User: Did the group decide on which one?
# AI: No, the group is still discussing which one to watch.

# ###END###
# Last User Message:
# ###START###
# Summarize what the group said
# ###END###
# Expected Answers:
# - topic_switch Answer: relevant
# - topic_switch Explanation: The user's question requires the assistant to refer to a past conversation for relevant details about the discussion.
# - capability Answer: no_augmentation_required
# - capability Explanation: The user is asking the assistant to summarize what the group said about the movie rather than the movie itself (no external search required).
# - handoff_multiclass Answer: handoff_not_needed
# - handoff_multiclass Explanation: The user is asking the assistant to summarize what the group said about the movie rather than the movie itself (no external search required).

# 13. Conversation History:
# ###START###
# User: What did my super say about my broken faucet?
# AI: I checked your thread with your property manager, and Jack (your super) said that he has ordered some new parts from Amazon.
# ###END###
# Last User Message:
# ###START###
# How often should I replace my faucet?
# ###END###
# Expected Answers:
# - topic_switch Answer: relevant
# - topic_switch Explanation: The user is asking a follow up question about fixing faucets mentioned in the conversation history.
# - capability Answer: requires_augmentation
# - capability Explanation: The assistant needs to conduct external search to get accurate info about faucet maintenance.
# - handoff_multiclass Answer: reset_handoff_needed
# - handoff_multiclass Explanation: The user is following up with a specific question about fixing faucets mentioned in the conversation history. The assistant needs to conduct external search to get accurate info about faucet maintenance.

# # Task #
# Analyze the following conversation history and last user query to determine the appropriate response.

# Here is the conversation history:
# {conv_history}

# Here is the final user message:
# {user_query}

# # Format #
# Structure your response in the following format (DO NOT include any additional text):
# {
#   "topic_switch_answer": "either relevant or irrelevant (1 word)",
#   "topic_switch_explanation": "<10 word explanation in str format",
#   "capability_answer": "either requires_augmentation or no_augmentation_required (1 word)"
#   "capability_explanation": "<10 word explanation in str format"
#   "unified_handoff_multiclass_answer": "either replay_handoff_needed, reset_handoff_needed or no_handoff_needed (1 word)"
# }
# [/INST]
# """
# data = {"messages": [{"role": "system", "content": content}], "max_tokens": 100}


# def main() -> None:
#     response = requests.post(url, headers=headers, json=data, verify=False)
#     response_json = response.json()
#     print(json.dumps(response_json, indent=4))


# if __name__ == "__main__":
#     main()


import json
import os
from pathlib import Path

import requests

API = os.environ.get("VLLM_API", "http://localhost:8000")
MODEL_DIR = os.environ.get(
    "MODEL_DIR", "/home/danielsalib/892615997/"
)  # change if needed
MODEL = MODEL_DIR  # vLLM accepts the served name or path; if you set served_model_name, use that instead (e.g., "default")


def load_ids(model_dir: str):
    model_dir = Path(model_dir)
    cfg_p = model_dir / "config.json"
    tokcfg_p = model_dir / "tokenizer_config.json"

    eos = None
    pad = None

    def _read_json(p):
        try:
            with open(p, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    cfg = _read_json(cfg_p)
    tokcfg = _read_json(tokcfg_p)

    # eos_token_id can be int or list
    eos = cfg.get("eos_token_id")
    if eos is None:
        eos = tokcfg.get("eos_token_id")
    if eos is None:
        eos = []  # default to empty list if missing

    pad = cfg.get("pad_token_id", tokcfg.get("pad_token_id"))
    return eos, pad


def post_json(path, payload):
    url = f"{API}{path}"
    r = requests.post(
        url, headers={"Content-Type": "application/json"}, data=json.dumps(payload)
    )
    return r


def show_result(name, resp):
    print(f"\n=== {name} ===")
    print("Status:", resp.status_code)
    print("Raw:", resp.text[:400] + ("..." if len(resp.text) > 400 else ""))
    try:
        data = resp.json()
    except Exception as e:
        print("JSON parse error:", e)
        return

    # Print the decoded text repr to reveal whitespace
    try:
        choice = data["choices"][0]
        text = choice.get("text") or choice.get("message", {}).get("content", "")
        print("Decoded text repr:", repr(text))
        print("Decoded text length:", len(text))
        print("Finish reason:", choice.get("finish_reason"))
    except Exception as e:
        print("Result parse error:", e)
    print(json.dumps(data, indent=2)[:1000])


def main():
    eos, pad = load_ids(MODEL_DIR)
    if isinstance(eos, int):
        eos_list = [eos]
    else:
        eos_list = eos or []

    print("Detected eos_token_id(s):", eos_list)
    print("Detected pad_token_id:", pad)

    # 1) Plain completions, do NOT strip specials (to see what's emitted)
    payload1 = {
        "model": "default",
        "prompt": "Repeat the word hello 2 times:",
        "max_tokens": 32,
        "temperature": 0,
        "skip_special_tokens": False,  # show specials if any
        # no logprobs to avoid NaN JSON crash
    }
    r1 = post_json("/v1/completions", payload1)
    show_result("Completions (skip_special_tokens=False)", r1)

    # 2) PAD-banned + EOS enforced, with specials stripped
    payload2 = {
        "model": "default",
        "prompt": "Repeat the word hello 2 times:",
        "max_tokens": 32,
        "temperature": 0,
        "skip_special_tokens": True,
    }
    if eos_list:
        payload2["eos_token_id"] = eos_list
    if pad is not None:
        # Ban PAD via stop ids and a strong negative logit bias
        payload2["stop_token_ids"] = [pad]
        payload2["logit_bias"] = {str(pad): -100.0}

    r2 = post_json("/v1/completions", payload2)
    show_result("Completions (PAD banned, EOS set, specials stripped)", r2)

    # 3) Chat completions (many Feather ckpts require chat template)
    payload3 = {
        "model": "default",
        "messages": [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Repeat the word hello 2 times."},
        ],
        "max_tokens": 32,
        "temperature": 0,
        "skip_special_tokens": True,
    }
    if eos_list:
        payload3["eos_token_id"] = eos_list
    if pad is not None:
        payload3["stop_token_ids"] = [pad]
        payload3["logit_bias"] = {str(pad): -100.0}

    r3 = post_json("/v1/chat/completions", payload3)
    show_result("Chat Completions (template-aware)", r3)

    # 4) Optional: try /tokenize if your server exposes it (harmless if 404)
    try:
        tok_r = post_json("/tokenize", {"text": "hello", "model": MODEL})
        print("\n=== /tokenize ===")
        print("Status:", tok_r.status_code)
        print("Raw:", tok_r.text)
    except Exception as e:
        print("\n/tokenize check skipped or failed:", e)


if __name__ == "__main__":
    main()
