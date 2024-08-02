import discord
import math
import os

BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = os.environ["ADMIN_ID"]
MEETING_CHANNEL_ID = os.environ["MEETING_CHANNEL_ID"]
PAPER_SUGGESTING_CHANNEL_ID = os.environ["PAPER_SUGGESTING_CHANNEL_ID"]
PAPER_VOTING_CHANNEL_ID = os.environ["PAPER_VOTING_CHANNEL_ID"]


BOT_CHAR = "!"

W_IN_UP = 1
W_UK_UP = 0.5
W_OUT_UP = -0.001
W_IN_DOWN = -1
W_UK_DOWN = 0
W_OUT_DOWN = 0
W_OUT_MARKED = -1000

W_OFFSET = W_IN_UP + W_OUT_UP + W_IN_DOWN + W_OUT_DOWN + W_OUT_MARKED

resubmit_waring = "\n\n(already suggested btw)"


async def get_winner(client, winner_list=[]):
    paper_voting_channel = client.get_channel(int(PAPER_VOTING_CHANNEL_ID))
    meeting_channel = client.get_channel(int(MEETING_CHANNEL_ID))
    join_claim_message = await discord.utils.get(meeting_channel.history(), author__id=client.user.id)
    best = [None, -math.inf]
    print("collect joiners/skippers")
    joiners = await get_reaction_user_list(join_claim_message, "🇯")
    skippers = await get_reaction_user_list(join_claim_message, "🇸")
    print("joiners: ", joiners)
    print("skippers: ", skippers)
    print("iterate history")
    async for message in paper_voting_channel.history():
        print(" collect votes for: ", message.content)
        up_voters = await get_reaction_user_list(message, "👍")
        print("  up_voters:", up_voters)
        down_voters = await get_reaction_user_list(message, "👎")
        print("  down_voters:", down_voters)
        markers = await get_reaction_user_list(message, "⭐")
        print("  markers:", markers)
        vote_value = -W_OFFSET
        print("  iterate voters")
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
        for marker in markers:
            print(f"    marker: {marker}, skippers: {skippers}")
            if marker in skippers:
                vote_value += W_OUT_MARKED
        print(f" final vote value {vote_value}")
        print(" check if new best")
        if vote_value >= best[1] and (not message.id in winner_list):
            print("new best found")
            best = [message, vote_value]
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
                users_with_reaction.append(user.id)
    return users_with_reaction


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
