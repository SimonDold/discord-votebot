Setup:

1. Create a new discord application on https://discord.com/developers/applications
   with the permissions: 

 - Send Messages
 - Send Messages in Threads
 - Manage Messages
 - Read Message History
 - Add Reactions

   and invite the bot to your discord server.
   Under Settings/Bot you can Reset the Token to get the 'BOT_TOKEN'.

2. Create the text channels "meetings", "paper-suggestions" and "votebot-channel".

3. Create a file 'votebot/.env' to define the environment variables.
It should be of the pattern:
    
        BOT_TOKEN=<your personal bot token>
        ADMIN_ID=<discord user id of you>
        MEETING_CHANNEL_ID=<id of the textchannel called 'meetings'>

4. Start the bot with:

         sudo docker-compose up --build -d

5. Interact with the bot by sending it the message "!help" or "!admin_help" in the channel 
"paper-suggestions", "votebot-channel" or as a private message.
6. Stop the bot with:
    
         sudo docker-compose down

