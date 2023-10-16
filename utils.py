import discord

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
W_OUT_MARKED = -1000

resubmit_waring = "\n\n(already suggested btw)"


async def get_winner(client, winner_list=[]):
    paper_suggestion_channel = client.get_channel(int(PAPER_SUGGESTIONS_CHANNEL_ID))
    meeting_channel = client.get_channel(int(MEETING_CHANNEL_ID))
    #msg = await discord.utils.get(channel.history(), author__name='Dave')
    join_claim_message = await discord.utils.get(meeting_channel.history(limit=10), author__id=client.user.id)
    #join_claim_message = await meeting_channel.history(limit=None).get(lambda m: m.author == client.user)
    best = ["NONE", -math.inf]
    print("collect joiners/skippers")
    joiners = await get_reaction_user_list(join_claim_message, "🇯")
    skippers = await get_reaction_user_list(join_claim_message, "🇸")
    print("iterate history")
    async for message in paper_suggestion_channel.history(limit=10):
        print("collect votes")
        up_voters = await get_reaction_user_list(message, "👍")
        down_voters = await get_reaction_user_list(message, "👎")
        vote_value = 0
        print("iterate voters")
        for up_voter in up_voters:
            if up_voter in joiners:
                vote_value += W_IN_UP
            if up_voter in skippers:
                vote_value += W_OUT_UP
            if up_voter not in joiners and up_voters not in skippers:
                vote_value += W_UK_UP
        for down_voter in down_voters:
            if down_voter in joiners:
                vote_value += W_IN_DOWN
            if down_voter in skippers:
                vote_value += W_OUT_DOWN
            if down_voter not in joiners and up_voters not in skippers:
                vote_value += W_UK_DOWN
        print("done iterating voters")
        out_marked = bot_memory.count_mark_conflicts(message.content)
        vote_value += out_marked * W_OUT_MARKED
        print("check new best")
        if vote_value > best[1] and (not message.id in winner_list):
            print("new best found")
            best = [message, vote_value]
            print("assign new best")
    print("winner found")
    print(f"winner found {best[0]} {best[1]}")
    return (best[0], best[1])


def untuple_str(tup):
    msg = ""
    for t in tup:
        msg += t
    return msg

async def get_reaction_user_list(message, emoji):
    users_with_reaction = []
    for reaction in message.reactions:
        if str(reaction) == emoji:
            async for user in reaction.users():
                users_with_reaction.append(user)
    return users_with_reaction



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
