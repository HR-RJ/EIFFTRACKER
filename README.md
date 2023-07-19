# EIFFTRACKER(TFT discord tracker)
This bot tracks the TFT stats of registered users in a discord

## docker:
To create a docker container for the bot you can run the following command while in the folder:
```bash
docker build -t <nameOfBot> .
```
Then run:
```bash
docker-compose up
```
you should then see:
```bash
eifftracker-python-1  | 2023-07-19 12:31:40 INFO     discord.client logging in using static token
eifftracker-python-1  | 2023-07-19 12:31:41 INFO     discord.gateway Shard ID None has connected to Gateway (Session ID: <your id>).
```
## Commands:

- $help 
  - help commands shows all the commands, how they should be used and what they di
- $firstoreiff
  - rolls to see if you'll go first or eiff next game 
- $register <name>
  - link your discord account to your riot account
- $unregister
  - unlinks your discord account from the linked riot account
- $tftme
  - check the stats of the last 5 games of the linked riot account
- $tft <name>
  - Lookup a tft user with rank and last 5 games
- $zcompare <name>, <name>
  - Compares the average placements of two summoners
