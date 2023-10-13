import bot_memory

import math
import os

BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = os.environ["ADMIN_ID"]
MEETING_CHANNEL_ID = os.environ["MEETING_CHANNEL_ID"]
PAPER_SUGGESTIONS_CHANNEL_ID = os.environ["PAPER_SUGGESTIONS_CHANNEL_ID"]


BOT_CHAR = "!"

W_IN_UP = 1
W_UK_UP = 0
W_OUT_UP = -0.001
W_IN_DOWN = -1
W_UK_DOWN = 0
W_OUT_DOWN = 0

resubmit_waring = "\n\n(already suggested btw)"


def untuple_str(tup):
    msg = ""
    for t in tup:
        msg += t
    return msg


def get_vote_value(key):
    print("check the votes for " + untuple_str(key))
    paper = untuple_str(key)
    in_up = bot_memory.db_count(paper, reaction="👍", claim="in")
    uk_up = bot_memory.db_count(paper, reaction="👍", claim="uk")
    out_up = bot_memory.db_count(paper, reaction="👍", claim="out")
    in_down = bot_memory.db_count(paper, reaction="👎", claim="in")
    uk_down = bot_memory.db_count(paper, reaction="👎", claim="uk")
    out_down = bot_memory.db_count(paper, reaction="👎", claim="out")

    out_marked = bot_memory.count_mark_conflicts(paper)
    w_out_marked = -2 * len(bot_memory.get_in_claims_table())

    value = in_up * W_IN_UP + \
            out_up * W_OUT_UP + \
            uk_up * W_UK_UP + \
            in_down * W_IN_DOWN + \
            out_down * W_OUT_DOWN + \
            uk_down * W_UK_DOWN + \
            out_marked * w_out_marked

    vote_info = f"👍:+{in_up},-{out_up},?{uk_up}"
    print(f"in get_vote_value:\n{vote_info}")

    return value, vote_info
    # \n👎:+{in_down},-{out_down},?{uk_down}"


def get_winner(winner_list=[]):
    print("who is the winner?")
    best = ["NONE", -math.inf, ""]
    papers = bot_memory.get_papers()
    print(f"candidate papers:\n{papers}")
    for packed_paper in papers:
        (paper,) = packed_paper
        print(f"checking suggestion: {paper}")
        value, vote_info = get_vote_value(paper)
        print(f"done checking suggestion: {paper}")
        print(f"value:{value}\nbest:{best}")
        if value > best[1] and (not paper in winner_list):
            best = [paper, value, vote_info]

            print(f"new best: {best}")
        else:
            print("no new best")
    print("i know the winner now")
    winner, _, vote_info = best
    return winner, vote_info


def remove_empty_lines(s):  # from chatGPT 3
    lines = s.split("\n")  # Split the string into lines

    cleaned_lines = []
    for line in lines:
        line = line.rstrip()  # Remove trailing whitespaces
        line = " ".join(line.split())  # Combine multiple whitespaces into one
        if line:  # Skip empty lines
            cleaned_lines.append(line)

    cleaned_string = "\n".join(cleaned_lines)  # Join the cleaned lines back into a string
    return cleaned_string


def remove_first_word(input_string):  # chatGPT 3
    # Find the index of the first whitespace or newline character
    space_index = input_string.find(' ')
    newline_index = input_string.find('\n')

    # Use the first valid index
    if space_index == -1:
        index = newline_index
    elif newline_index == -1:
        index = space_index
    else:
        index = min(space_index, newline_index)

    # If a whitespace or newline character is found, remove the first word and the leading whitespace
    if index != -1:
        return input_string[index + 1:].lstrip()

    # If no whitespace or newline character is found, return an empty string
    return ''
