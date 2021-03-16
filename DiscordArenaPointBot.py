from discord.ext import commands
import time, discord, threading, requests, random, json, subprocess

webhook_id = ''
webhook_token = ''

client = commands.Bot(command_prefix='!')

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    await client.change_presence(activity=discord.Game(
        name=f"{str(client.user).split('#')[0]} | !help"))

@client.event
async def on_message(message):
    if str(message.channel.type) != "private" and str(message.content).startswith("!generate"):
        await message.channel.send("Please DM the bot.")
        return
    await client.process_commands(message)

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.author.send("Username/password was not given.")

def _generate(username, password):
    webhook = discord.Webhook.partial(webhook_id, webhook_token, adapter=discord.RequestsWebhookAdapter())
    try:
        token = json.loads(subprocess.Popen(f"node tokenify.js {username} {password}", shell=True, stdout=subprocess.PIPE).stdout.read().decode())
    except:
        webhook.send(embed=discord.Embed(title="Incorrect password.", description=f"Password is incorrect for user {username}.", color=0xff0000))
        exit()
    userID = token["userID"]
    token = f'Bearer {token["token"]}'
    arenaseason = requests.get(f"https://api.prodigygame.com/leaderboard-api/user/{userID}/init?userID={userID}", headers={'Authorization': token})
    arenaseason = arenaseason.json()["seasonID"]

    while True:
        r = requests.post(f"https://api.prodigygame.com/leaderboard-api/season/{arenaseason}/user/{userID}/pvp?userID={userID}",
            headers={
                "authorization": token,
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "sec-fetch-mode": "cors",
                "body": (f"seasonID={arenaseason}&action=win"),
                "referrer": "https://play.prodigygame.com/",
                "mode": "cors"
            },
            data=(f"seasonID={arenaseason}&action=win"),
        )
        if r.text == "":
            webhook.send(embed=discord.Embed(title="Failed to add points.", description=f"Points could not be added to user {username}.", color=0xff0000))
            time.sleep(61+random.random())
            continue
        try:
            webhook.send(embed=discord.Embed(title=f'{r.json()["points"]} (+100)', description=f'Congrats {username} got 100 points! You are in place number {requests.get(f"https://api.prodigygame.com/leaderboard-api/season/{arenaseason}/user/{userID}/rank?userID={userID}", headers={"authorization": token}).json()["rank"]}.', color=0x008080))
        except:
            webhook.send(embed=discord.Embed(title="Rate limited.", description=f"{username} is being rate limited. {username} please try again in 3 hours.", color=0xff0000))
            break
        time.sleep(61+random.random())

@client.command()
async def generate(ctx, username, password):
    thread = threading.Thread(target=_generate, args=(username, password))
    thread.daemon = True
    thread.start()
    await ctx.send("Arena points have started generating.")

client.run("token")