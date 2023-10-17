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

2. Create the text channels "meetings", "paper-suggestions" and "votebot-channel". Remove the permission to send messages for everyone except the bot.

1. Copy 'Dockerfile' and 'docker-compose.yml' to your machine (No need to clone the repository. The container will do this for you.)
Change the relative path 'context' in 'docker-compose.yml' if you put the two files into different locations. 

1. Create a file '.env' in the same folder where you put 'docker-compose.yml' to define the environment variables.
It should be of the pattern:
    
        BOT_TOKEN=<your personal bot token>
        ADMIN_ID=<discord user id of you>
        MEETING_CHANNEL_ID=<id of the textchannel called 'meetings'>
        PAPER_SUGGESTIONS_CHANNEL_ID=<id of the textchannel called 'paper-suggestions'>

1. Navigate into the folder with 'docker-compose.yml'.

1. Start the bot with:

         sudo docker-compose up --build -d

1. Interact with the bot by sending it the message "!help" or "!admin_help" in the discord channel 
"paper-suggestions", "votebot-channel" or as a private message.

1. Stop the bot with:
    
         sudo docker-compose down

