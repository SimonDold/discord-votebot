import bot_memory
import utils
from utils import BOT_CHAR
from info import VERSION

from datetime import datetime, timedelta

winner_list = []
vote_active = False
date1_string = ""
date2_string = ""

def get_vote_active():
    return vote_active

def prep_author_and_content(message):
    assert message.content[0] == BOT_CHAR
    author = message.author
    words = message.content.split()
    command = words[0].lower()[1::]
    content = message.content[len(command) + 2::]
    return author, content

async def default(message, client):
    return ["unknown command. Try !help"], False, None


async def greet(message, client):
    author, _ =prep_author_and_content(message)
    nick = author.nick
    if nick is None:
        nick = author.name
    return [f"""beep beep boop {author.id} (this is bot language for "hello {nick}.")"""], False, None

async def version(message, client):
    return [f"""VoteBot Version: {VERSION}."""], False, None


def suggestion_key_to_txt(key):
    msg = ""
    for char in key:
        msg += char
    return msg


async def suggest(message, client):
    author, content = prep_author_and_content(message)
    print(f"content: {content}")
    key = tuple(utils.remove_empty_lines(content))
    print(f"key: {key}")
    print(f"author: {author}, ID: {author.id}")
    msg = f"Suggestion:\n{suggestion_key_to_txt(key)}"
    return [msg], False, utils.PAPER_SUGGESTIONS_CHANNEL_ID





async def vote(message, client):
    global winner_list
    global vote_active
    await message.add_reaction("🤖")
    vote_active = True
    print("Lets vote")
    (vote_winner, vote_info) = await utils.get_winner(client)
    if vote_winner is None:
        return [f"No options"], False, None
    winner_list.append(vote_winner.id)
    content = vote_winner.content.partition("Suggestion:")[-1][1::] #remove first word
    print(f"winner content: {content}")
    return [f"Winner is:\n{utils.untuple_str(content)}"], False, None


async def accept_by_rank(rank, channel):
    global winner_list
    global vote_active
    if not vote_active:
        print("outside of voting phase")
        return [""], False, None
    vote_active = False
    final_winner = winner_list[rank-1]
    final_winner_message = await channel.fetch_message(final_winner)
    final_content = final_winner_message.content
    winner_list = []
    await final_winner_message.delete()
    upcoming_date = bot_memory.get_info(info_key=bot_memory.NEXT_DATE)
    print(f"extracted previously next_date, now upcoming_date: {upcoming_date}")
    bot_memory.set_info(info_key=bot_memory.UPCOMING_DATE, info_value=upcoming_date)
    bot_memory.set_info(info_key=bot_memory.UPCOMING_PAPER, info_value=final_content)
    print(f"change date")
    if upcoming_date == "N/A":
        bot_memory.set_info(info_key=bot_memory.NEXT_DATE, info_value="N/A")
    else:
        next_date = datetime.strptime(upcoming_date, "%Y/%m/%d") + timedelta(days=7)
        bot_memory.set_info(info_key=bot_memory.NEXT_DATE, info_value=next_date.strftime("%Y/%m/%d"))
    print("done accept_by_rank")
    return [f"{utils.untuple_str(final_content)}\n\nwas accepted as winner for the meeting on {upcoming_date}."], False, None


async def deny(message, client):
    global winner_list
    global vote_active
    if not vote_active:
        print("outside of voting phase")
        return [""], False, None
    print("Lets vote again")
    (vote_winner, vote_info) = await utils.get_winner(client, winner_list)
    if vote_winner is None:
        return [f"No further options"], False, None
    content = vote_winner.content.partition("Suggestion:")[-1][1::] #remove first word
    print(f"the new winner is...\n{utils.untuple_str(content)}\n\n{vote_info}")
    winner_list.append(vote_winner.id)
    print(f"Winner list: {winner_list}")
    return [f"Winner #{len(winner_list)} is:\n{utils.untuple_str(content)}"], False, None

async def show_admins(message, client):
    return ["admins DB:\n" + str(bot_memory.get_admins_table())], False, None


async def show_db(message, client):

    bi = await bot_info(message, client)
    sa = await show_admins(message, client)

    return [bi[0][0]] + \
           [
            sa[0][0],
            ], False, None

async def bot_info(message, client):
    upcoming_date = bot_memory.get_info(info_key=bot_memory.UPCOMING_DATE)
    paper = bot_memory.get_info(info_key=bot_memory.UPCOMING_PAPER)
    next_date = bot_memory.get_info(info_key=bot_memory.NEXT_DATE)
    return [f"The date of the upcoming meeting: {upcoming_date}.\n" \
           f"We will discuss the paper:\n{paper}\n" \
           f"\n" \
           f"The date of the next meeting: {next_date}.\n"], False, None

def meeting_announcment():
    upcoming_date = bot_memory.get_info(info_key=bot_memory.UPCOMING_DATE)
    paper = bot_memory.get_info(info_key=bot_memory.UPCOMING_PAPER)
    return f"For the upcoming meeting on {upcoming_date} we read:\n" \
           f"\n{paper}\n"


def vote_announcement():
    next_date = bot_memory.get_info(info_key=bot_memory.NEXT_DATE)
    return f"-----------------------------------------\n" + \
           f"The date of the next meeting: {next_date}.\n" + \
        f"Tell me with 🇯/🇸 reactions whether you will 🇯oin or 🇸kip the next meeting "\
        "so I can consider your votes accordingly."


def new_meeting_announcment():
    global date1_string
    global date2_string
    return f"For the next meeting on {date1_string} we have the vote on {date2_string}."


async def admin_set_upcoming_date(message, client):
    author, content = prep_author_and_content(message)
    bot_memory.set_info(info_key=bot_memory.UPCOMING_DATE, info_value=content)
    await message.add_reaction("✅")
    return [], False, None


async def admin_set_upcoming_paper(message, client):
    author, content = prep_author_and_content(message)
    bot_memory.set_info(info_key=bot_memory.UPCOMING_PAPER, info_value=content)
    await message.add_reaction("✅")
    return [], False, None


async def set_next(message, client):
    author, content = prep_author_and_content(message)
    try:
        date = datetime.strptime(content, "%Y/%m/%d")
        bot_memory.set_info(info_key=bot_memory.NEXT_DATE, info_value=content)
        await message.add_reaction("✅")
        return [], False, None
    except Exception as e:
        await message.add_reaction("❌")
    return [], False, None


async def set_next_na(message, client):
    author, content = prep_author_and_content(message)
    bot_memory.set_info(info_key=bot_memory.NEXT_DATE, info_value="N/A")
    await message.add_reaction("✅")
    return [], False, None


async def announce_new_meeting(message, client):
    author, content = prep_author_and_content(message)
    global date1_string
    global date2_string
    try:
        date1_string = content.split()[0]
        date1 = datetime.strptime(date1_string, "%Y/%m/%d")
        date2_string = content.split()[1]
        date2 = datetime.strptime(date2_string, "%Y/%m/%d")
        bot_memory.set_info(info_key=bot_memory.NEXT_DATE, info_value=date1_string)
        bot_memory.set_info(info_key=bot_memory.UPCOMING_DATE, info_value="N/A")
        return [new_meeting_announcment(), vote_announcement()], False, utils.MEETING_CHANNEL_ID
    except Exception as e:
        await message.add_reaction("❌")
    return [], False, None


async def add_admin(message, client):
    author, content = prep_author_and_content(message)
    bot_memory.update_admins(content, add=True)
    await message.add_reaction("✅")
    return [], False, None


async def remove_admin(message, client):
    author, content = prep_author_and_content(message)
    bot_memory.update_admins(content, add=False)
    await message.add_reaction("✅")
    return [], False, None

async def admin_announce_meeting(message, client):
    return [meeting_announcment(), vote_announcement()], False, utils.MEETING_CHANNEL_ID


responses_dict = {
    "info": [bot_info, f"I tell you this weeks paper, meeting date "
                   f"and the date for the meeting corresponding to the upcoming vote."],
    "suggest": [suggest, f"'{BOT_CHAR}suggest [string]' to add a suggestion.\n"
                         "Type for example "
                         f"```{BOT_CHAR}suggest Patrik Haslum and Hector Geffner.\n Heuristic Planning with Time and "
                         "Resources.\n In Proc. ECP 2001, pp. 121-132. "
                         "https://www.ida.liu.se/divisions/aiics/publications/ECP-2001-Heuristic-Planning-Time.pdf``` "
                         "to suggest this paper for a future meeting.\n"
                         "no need to follow a specific format."],
    "next": [set_next, f"set a date for the next meeting with the format %Y/%m/%d"],
    "next_na": [set_next_na, f"set the date of the next meeting to N/A"],
    "vote": [vote, "Returns a paper based on the user reactions to the suggestions and their claims to join/skip."],
    "v": [vote, f"shorthand for {BOT_CHAR}vote"],
    "announce_new_meeting": [announce_new_meeting, f"'{BOT_CHAR}announce_new_meeting [date1] [date2]' to announce"
                                                   " that a new meeting will happen at date1 and the paper will be"
                                                   " decided on date2. Date format %Y/%m/%d"],
    # admin commands
    "admin_add_admin": [add_admin, f"add an admin with '{BOT_CHAR}admin_add_admin [user_ID]'"],
    "admin_remove_admin": [remove_admin, f"remove an admin with '{BOT_CHAR}admin_remove_admin [user_ID]'"],
    "admin_show_admins": [show_admins, f"list all admins"],
    "admin_hi": [greet, f"greeting each other"],
    "admin_version": [version, f"check the version"],
    "admin_set_upcoming_date": [admin_set_upcoming_date, f"set the upcoming date for the meeting"],
    "admin_set_upcoming_paper": [admin_set_upcoming_paper, f"set the upcoming paper for the meeting"],
    "admin_announce_meeting": [admin_announce_meeting, f"announce a meeting with the current next/upcoming date and paper"],
    "admin_show_db": [show_db, f"show all tables from the DB"]

}

help_msg = "I am the VoteBot you can suggest papers to me. Everyone can react with emojis to the suggestions " \
           "(I remove them but I remember them). " \
           "You can tell me if you plan to join or skip the next meeting. " \
           "I can choose a paper based on the user reactions to the suggestions and their claims to join/skip.\n" \
           "Reactions:\n" \
           "👍: I am looking forward to discuss this paper.\n" \
           "👎: I want you to discuss this paper without me.\n" \
           "How can I help you? I know these commands:\n"


def get_help_msg(admin):
    msg = ""
    for key in responses_dict:
        if (key[0:5] == "admin") == admin:
            msg += "\n```" + BOT_CHAR + str(key) + "```" + "\t" + responses_dict[key][1] + "\n"
    post_msg = "\nYou can interact with me in a private chat, too."
    return [help_msg, msg, post_msg]

async def bot_help(message, client):
    print("preparing help")
    msg = get_help_msg(False)
    return msg, False, None


async def admin_help2(message, client):
    msg = get_help_msg(True)
    return msg, False, None


responses_dict.update({"help": [bot_help, "get a help message."]})
responses_dict.update({"admin_help": [admin_help2, "get a help message for admins."]})


async def handle_responses(message_content, message, is_private, client):
    author = message.author
    if not message_content[0] == BOT_CHAR:
        return []
    words = message_content.split()
    command = words[0].lower()[1::]
    if command[0:5] == "admin" and (author.id,) not in bot_memory.get_admins_table():
        return ["This command is only for admins."], False, None
    response_function = responses_dict.get(command, [default, "default response function"])[0]
    if is_private and response_function in [suggest, set_next, set_next_na, vote]:
        return ["This command is only usable in the public channels."]
    return await response_function(message, client) # expect list of strings and one bool and maybe channel_id
