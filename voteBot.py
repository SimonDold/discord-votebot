import discord
import voteBot_responses as responses
import utils
import bot_memory

from utils import BOT_CHAR, BOT_TOKEN, ADMIN_ID, MEETING_CHANNEL_ID

CLIENT = None

p = print


def print(self, *args, sep=' ', end='\n', file=None):
    p("VB:", self)


print("HELLO")
bot_memory.init(ADMIN_ID)
intents = discord.Intents.default()  # Create a default Intents object
intents.reactions = True  # Enable the reactions intent


async def react_message(message, user_message, is_private):
    try:
        response_list = responses.handle_responses(user_message, message.author, is_private)
        for response in response_list:
            offset = 0
            while offset < len(response):
                chunk = response[offset:offset + 2000]
                offset += 2000
                await message.author.send(response) if is_private else await message.channel.send(chunk)
    except Exception as e:
        print(e)


async def self_reactions(message, user_message):
    if "Suggestion:" == user_message.split()[0]:
        await message.add_reaction("👍")
        await message.add_reaction("🤷")
        await message.add_reaction("👎")
    if user_message.split()[0] == "Winner":
        await message.add_reaction("✅")
        await message.add_reaction("⏩")
    if user_message.split()[0:7] == "----------------------------------------- The date of the next meeting:".split():
        await message.add_reaction("🇯")
        await message.add_reaction("🇸")
    if user_message.split()[0] == "Announcement":
        await announce_new_meeting()


async def send_message_in_channel(message, channel):
    try:
        offset = 0
        while offset < len(message):
            chunk = message[offset:offset + 2000]
            offset += 2000
            await channel.send(chunk)
    except Exception as e:
        print(e)


async def announce_meeting():
    global CLIENT
    channel = CLIENT.get_channel(int(MEETING_CHANNEL_ID))
    text = responses.meeting_announcment()
    await send_message_in_channel(text, channel)
    text_2 = responses.vote_announcement()
    await send_message_in_channel(text_2, channel)


async def announce_new_meeting():
    global CLIENT
    channel = CLIENT.get_channel(int(MEETING_CHANNEL_ID))
    text = responses.new_meeting_announcment()
    await send_message_in_channel(text, channel)


async def reaction_reaction(message, channel, emoji, user, user_id):
    if "Suggestion:" == message.content.split()[0]:
        if isinstance(channel, discord.TextChannel):
            # Remove the reaction
            await message.remove_reaction(emoji, user)
        else:
            print("Cannot remove reaction in a DM channel.")

            # normalize
        message_content = message.content
        while message_content[len(message_content) - len(utils.resubmit_waring):] == utils.resubmit_waring:
            message_content = message_content[0:len(message_content) - len(utils.resubmit_waring)]

        key = tuple(utils.remove_first_word(message_content))
        print(f"key: {key}")

        bot_memory.update_suggestions(utils.untuple_str(key), user_id, emoji)
    if message.content.split()[0] == "Winner":
        print(f"reaction to Winner message with {emoji}")
        if str(emoji) == "✅":
            print(f"accepted {message.content} by reaction")
            winner_rank = 1
            if not message.content.split()[1] == "is:":  # if not the very first winner
                winner_rank = int(message.content.split()[1][1:])
            responses.accept_by_rank(winner_rank)
            print("accepted :)")
            await announce_meeting()
        elif str(emoji) == "⏩":
            print("denied by reaction")
            new_winner_message = responses.deny(None, None)
            await send_message_in_channel(new_winner_message, channel)
        else:
            print(f"unexpected emoji: {emoji}")
    if message.content.split()[0:5] == "For the upcoming meeting on".split():
        if str(emoji) == "🇯":
            try:
                await message.remove_reaction("🇸", user)
            except Exception as e:
                print(e)
            responses.claim_in(user_id)
        elif str(emoji) == "🇸":
            try:
                await message.remove_reaction("🇯", user)
            except Exception as e:
                print(e)
            responses.claim_out(user_id)


async def unreaction_reaction(message, channel, emoji, user, user_id):
    if message.content.split()[0:5] == "For the upcoming meeting on".split():
        if str(emoji) == "🇯" and bot_memory.get_user_in_claim(user_id) == "in":
            responses.claim_nothing(user_id)
        elif str(emoji) == "🇸" and bot_memory.get_user_in_claim(user_id) == "out":
            responses.claim_nothing(user_id)


def run_vote_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    global CLIENT
    CLIENT = discord.Client(intents=intents)

    @CLIENT.event
    async def on_ready():
        print(f"{CLIENT.user} is now running.")

    @CLIENT.event
    async def on_message(message):
        username = str(message.author)
        user_message = str(message.content)
        channel = message.channel
        if message.author == CLIENT.user:
            await self_reactions(message, user_message)
            return
        elif user_message[0] == BOT_CHAR:
            if isinstance(channel, discord.DMChannel):
                await react_message(message, user_message, is_private=True)
            elif channel.name in ["paper-suggestions", "votebot-channel"]:
                print(f"{username} said: '{user_message}' (in {channel.name})")
                await react_message(message, user_message, is_private=False)

    @CLIENT.event
    async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
        if payload.user_id == CLIENT.user.id:
            return

        user_id = payload.user_id
        user = await CLIENT.fetch_user(user_id)
        channel_id = payload.channel_id
        channel = await CLIENT.fetch_channel(channel_id)
        message_id = payload.message_id
        message = await channel.fetch_message(message_id)
        message_content = message.content
        emoji = payload.emoji

        print(f"{user} reacted with {emoji} to message: '{message_content}' (in {channel})")

        if message.author == CLIENT.user:
            await reaction_reaction(message, channel, emoji, user, user_id)

    @CLIENT.event
    async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
        if payload.user_id == CLIENT.user.id:
            return
        user_id = payload.user_id
        user = await CLIENT.fetch_user(user_id)
        channel_id = payload.channel_id
        channel = await CLIENT.fetch_channel(channel_id)
        message_id = payload.message_id
        message = await channel.fetch_message(message_id)
        message_content = message.content
        emoji = payload.emoji

        print(f"{user} unreacted {emoji} from message: '{message_content}' (in {channel})")

        if message.author == CLIENT.user:
            await unreaction_reaction(message, channel, emoji, user, user_id)

    CLIENT.run(BOT_TOKEN)
