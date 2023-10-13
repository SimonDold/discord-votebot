import random

import bot_memory
import utils
from utils import BOT_CHAR
from info import VERSION

from datetime import datetime, timedelta

winner_list = []
date1_string = ""
date2_string = ""

def prep_author_and_content(message):
    assert message.content[0] == BOT_CHAR
    author = message.author
    words = message.content.split()
    command = words[0].lower()[1::]
    content = message.content[len(command) + 2::]
    return author, content

def default(message):
    return ["unknown command. Try !help"], False


def greet(message):
    author, _ =prep_author_and_content(message)
    return [f"""beep beep boop {author.id} (this is bot language for "hello {author.nick}.")"""], False

def version(message):
    return [f"""VoteBot Version: {VERSION}."""], False


def suggestion_key_to_txt(key):
    msg = ""
    for char in key:
        msg += char
    return msg


def suggest(message):
    author, content = prep_author_and_content(message)
    msg = ""
    print(f"content: {content}")
    key = tuple(utils.remove_empty_lines(content))
    print(f"key: {key}")
    print(f"author: {author}, ID: {author.id}")
    paper = utils.untuple_str(key)
    if paper in bot_memory.get_papers():
        msg += utils.resubmit_waring

    msg = f"Suggestion:\n{suggestion_key_to_txt(key)}" + msg
    bot_memory.update_suggestions(paper, author.id, "👍")
    return [msg], True


def remove(message):
    author, content = prep_author_and_content(message)
    print("unsuggesting")
    msg = ""
    print(f"content: {content}")
    key = tuple(utils.remove_empty_lines(content))
    print(f"key: {key}")
    paper = utils.untuple_str(key)
    print(f"paper:{paper}")
    if paper in bot_memory.get_papers():
        msg += "was removed"

    msg = f"\n{suggestion_key_to_txt(key)}" + msg
    bot_memory.remove_suggestions(paper)
    return [msg], False


def remove_user(message):
    author, content = prep_author_and_content(message)
    bot_memory.remove_user(content)
    return ["removed " + content], False


def suggestions(message):
    author, content = prep_author_and_content(message)
    lst = []
    for suggestion in bot_memory.get_papers():
        lst.append("Suggestion:\n" + utils.untuple_str(suggestion) + "\n\n")
    if len(lst) == 0:
        lst = ["There are no suggestions at the moment. Add one with !suggest [string]."]
    return lst, False


def my_votes(message):
    author, content = prep_author_and_content(message)
    return bot_memory.get_user_votes_table(author.id), False


def all_votes(message):
    author, content = prep_author_and_content(message)
    msgs = ["ALL VOTES:"]
    for m in bot_memory.get_suggestions_table():
        msgs += [str(m)]
    return msgs, False


def claim_in(user_id):
    bot_memory.update_in_claims(user_id, "in")
    return

def claim_out(user_id):
    bot_memory.update_in_claims(user_id, "out")
    return

def claim_nothing(user_id):
    bot_memory.update_in_claims(user_id, "uk")
    return

def vote(message):
    global winner_list
    print("Lets vote")
    vote_winner, vote_info = utils.get_winner()
    print(f"the winner is...\n{utils.untuple_str(vote_winner)}\n\n{vote_info}")
    winner_list.append(vote_winner)
    return [f"Winner is:\n{utils.untuple_str(vote_winner)}\n\n{vote_info}"], False


def accept_by_rank(rank):
    global winner_list
    final_winner = winner_list[rank-1]
    winner_list = []
    bot_memory.remove_suggestions(utils.untuple_str(final_winner))
    bot_memory.purge_in_claims()
    upcoming_date = bot_memory.get_info(info_key=bot_memory.NEXT_DATE)
    print(f"extracted previously next_date, now upcoming_date: {upcoming_date}")
    bot_memory.set_info(info_key=bot_memory.UPCOMING_DATE, info_value=upcoming_date)
    bot_memory.set_info(info_key=bot_memory.UPCOMING_PAPER, info_value=final_winner)
    print(f"change date")
    if upcoming_date == "N/A":
        bot_memory.set_info(info_key=bot_memory.NEXT_DATE, info_value="N/A")
    else:
        next_date = datetime.strptime(upcoming_date, "%Y/%m/%d") + timedelta(days=7)
        bot_memory.set_info(info_key=bot_memory.NEXT_DATE, info_value=next_date.strftime("%Y/%m/%d"))
    return [f"{utils.untuple_str(final_winner)}\n\nwas accepted as winner for the meeting on {upcoming_date}."], False


"""
def accept(message):
    global winner_list
    return accept_by_rank(len(winner_list)), False


def deny(message):
    global winner_list
    vote_winner, vote_info = utils.get_winner(winner_list)
    print(f"the new winner is...\n{utils.untuple_str(vote_winner)}\n\n{vote_info}")
    winner_list.append(vote_winner)
    print(f"Winner list: {winner_list}")
    return f"Winner #{len(winner_list)} is:\n{utils.untuple_str(vote_winner)}\n\n{vote_info}", False
"""

def show_participation(message):
    return ["in_claims DB:\n" + str(bot_memory.get_in_claims_table())], False


def show_marks(message):
    return ["marks DB:\n" + str(bot_memory.get_marks_table())], False


def show_admins(message):
    return ["admins DB:\n" + str(bot_memory.get_admins_table())], False


def show_db(message):
    return [bot_info(message)] + \
            all_votes(message) + \
           [show_participation(message),
            show_marks(message),
            show_admins(message),
            ], False

def bot_info(message):
    upcoming_date = bot_memory.get_info(info_key=bot_memory.UPCOMING_DATE)
    paper = bot_memory.get_info(info_key=bot_memory.UPCOMING_PAPER)
    next_date = bot_memory.get_info(info_key=bot_memory.NEXT_DATE)
    return [f"The date of the upcoming meeting: {upcoming_date}.\n" \
           f"We will discuss the paper:\n{paper}\n" \
           f"\n" \
           f"The date of the next meeting: {next_date}.\n"], False

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
    return f"For the upcoming meeting on {date1_string} we have the vote on {date2_string}.\n"\
           "Tell me with 🇯/🇸 reactions whether you will 🇯oin or 🇸kip this upcoming meeting "\
           "so I can consider your votes accordingly."


def admin_set_upcoming_date(message):
    author, content = prep_author_and_content(message)
    bot_memory.set_info(info_key=bot_memory.UPCOMING_DATE, info_value=content)
    return [f"set {content} as upcoming date"], False


def admin_set_upcoming_paper(message):
    author, content = prep_author_and_content(message)
    bot_memory.set_info(info_key=bot_memory.UPCOMING_PAPER, info_value=content)
    return [f"set {content} as upcoming paper"], False


def set_next(message):
    author, content = prep_author_and_content(message)
    date = datetime.strptime(content, "%Y/%m/%d")
    bot_memory.set_info(info_key=bot_memory.NEXT_DATE, info_value=content)
    return [f"set {content} as next date"], False


def set_next_na(message):
    author, content = prep_author_and_content(message)
    bot_memory.set_info(info_key=bot_memory.NEXT_DATE, info_value="N/A")
    return [f"set {content} as next date"], False


def mark_paper(message):
    author, content = prep_author_and_content(message)
    bot_memory.update_marks(content, author.id, True)
    return [f"The paper:\n{content}\nwill not be elected if {author.nick} is not able to attend."], False


def unmark_paper(message):
    author, content = prep_author_and_content(message)
    bot_memory.update_marks(content, author.id, False)
    return [f"Removed the marking."], False

def announce_new_meeting(message):
    author, content = prep_author_and_content(message)
    global date1_string
    global date2_string
    date1_string = content.split()[0]
    date1 = datetime.strptime(date1_string, "%Y/%m/%d")
    date2_string = content.split()[1]
    date2 = datetime.strptime(date2_string, "%Y/%m/%d")
    bot_memory.set_info(info_key=bot_memory.NEXT_DATE, info_value=date1_string)
    bot_memory.set_info(info_key=bot_memory.UPCOMING_DATE, info_value="N/A")
    return [f"Announcement in channel: meetings.\n"], False


def add_admin(message):
    author, content = prep_author_and_content(message)
    bot_memory.update_admins(content, add=True)
    return [f"Admin {content} added."], False


def remove_admin(message):
    author, content = prep_author_and_content(message)
    bot_memory.update_admins(content, add=False)
    return [f"Admin {content} removed."], False


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
    "show_suggestions": [suggestions, "lists all the collected suggestions"],
    "my_votes": [my_votes, "list my votes for all the suggestions"],
    "next": [set_next, f"set a date for the next meeting with the format %Y/%m/%d"],
    "next_NA": [set_next_na, f"set the date of the next meeting to N/A"],
    "vote": [vote, "Returns a paper based on the user reactions to the suggestions and their claims to join/skip."],
    "v": [vote, f"shorthand for {BOT_CHAR}vote"],
    "mark_paper": [mark_paper, f"mark a paper with '{BOT_CHAR}mark_paper [string]' "
                               f"to ensure it won't be considered for winning if you cannot join the next meeting. "
                               f"(This is meant for authors for example. Please do not overuse it)"],
    "unmark_paper": [unmark_paper, f"undo your '{BOT_CHAR}mark_paper [string]' with '{BOT_CHAR}unmark_paper [string]'"],
    "announce_new_meeting": [announce_new_meeting, f"'{BOT_CHAR}announce_new_meeting [date1] [date2]' to announce"
                                                   " that a new meeting will happen at date1 and the paper will be"
                                                   " decided on date2. Date format %Y/%m/%d"],
    # admin commands
    "admin_add_admin": [add_admin, f"add an admin with '{BOT_CHAR}admin_add_admin [user_ID]'"],
    "admin_remove_admin": [remove_admin, f"remove an admin with '{BOT_CHAR}admin_remove_admin [user_ID]'"],
    "admin_show_admins": [show_admins, f"list all admins"],
    "admin_all_votes": [all_votes, "List all votes from all suggestions and all users"],
    "admin_show_participation": [show_participation, "show all join/skip claims"],
    "admin_sp": [show_participation, f"shorthand for {BOT_CHAR}show_participation"],
    "admin_hi": [greet, f"greeting each other"],
    "admin_version": [version, f"check the version"],
    "admin_remove_suggestion": [remove, f"'{BOT_CHAR}remove [string]' to remove a suggestion"],
    "admin_remove_user": [remove_user, f"remove user from suggestions and in_claims"],
    "admin_set_upcoming_date": [admin_set_upcoming_date, f"set the upcoming date for the meeting"],
    "admin_set_upcoming_paper": [admin_set_upcoming_paper, f"set the upcoming paper for the meeting"],
    "admin_show_marks": [show_marks, f"show all marks"],
    "admin_show_db": [show_db, f"show all tables from the DB"]

}

help_msg = "I am the VoteBot you can suggest papers to me. Everyone can react with emojis to the suggestions " \
           "(I remove them but I remember them). " \
           "You can tell me if you plan to join or skip the next meeting. " \
           "I can choose a paper based on the user reactions to the suggestions and their claims to join/skip.\n" \
           "Reactions:\n" \
           "👍: I am looking forward to discuss this paper.\n" \
           "👎: I want you to discuss this paper without me.\n" \
           "🤷: undoing your vote.\n" \
           "How can I help you? I know these commands:\n"


def bot_help(message):
    return admin_help(message, admin=False)


def admin_help(message, admin=True):
    msg = ""
    for key in responses_dict:
        if (key[0:5] == "admin") == admin:
            msg += "\n```" + BOT_CHAR + str(key) + "```" + "\t" + responses_dict[key][1] + "\n"
    post_msg = "\nYou can interact with me in a private chat, too."
    return [help_msg, msg, post_msg], False


responses_dict.update({"help": [bot_help, "get a help message."]})
responses_dict.update({"admin_help": [admin_help, "get a help message for admins."]})


def handle_responses(message_content, message, is_private):
    author = message.author
    if not message_content[0] == BOT_CHAR:
        return []
    words = message_content.split()
    command = words[0].lower()[1::]
    if command[0:5] == "admin" and (author.id,) not in bot_memory.get_admins_table():
        return ["This command is only for admins."]
    response_function = responses_dict.get(command, [default, "default response function"])[0]
    if is_private and response_function in [suggest, set_next, set_next_na, vote, mark_paper]:
        return ["This command is only usable in the paper-suggestions channel."]
    return response_function(message) # expect list of strings and one bool
