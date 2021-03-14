from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from discord.ext import commands
import time, discord, threading, requests, random

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
    await client.process_commands(message)

def _generate(username, password):
    chrome_options = Options()
    chrome_options.add_extension('./extension.crx')

    driver = webdriver.Chrome(options=chrome_options)

    driver.get('https://sso.prodigygame.com/game/login')
    driver.find_element_by_id("unauthenticated_game_login_form_username").send_keys(username)
    driver.find_element_by_id("unauthenticated_game_login_form_password").send_keys(password)
    driver.find_element_by_id("unauthenticated_game_login_form_password").send_keys(Keys.ENTER)
    time.sleep(30)

    token = driver.execute_script("return localStorage.JWT_TOKEN")
    userID = driver.execute_script("return _.player.userID")
    arenaseason = requests.get(f"https://api.prodigygame.com/leaderboard-api/user/{userID}/init?userID={userID}", headers={'Authorization': token})
    arenaseason = arenaseason.json()["seasonID"]
    driver.close()

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
        try:
            print(f'{r.json()["points"]} (+100)')
        except:
            break
        time.sleep(61+random.random())

@client.command()
async def generate(ctx, username, password):
    thread = threading.Thread(target=_generate, args=(username, password))
    thread.daemon = True
    thread.start()
    await ctx.send("Arena points have started generating. Expect for 5,000 to 6,000 arena points to be generated.")

client.run("token")
