# To host this server you need a webhook id and webhook token for discord.
# Then go to http://localhost:5000/gen/ with a post requests and a body being '[username, password]'
# Python example:
# import requests
# requests.post('http://localhost:5000/gen/', data='["username", "password"]')
# JavaScript example:
# const fetch = require("node-fetch")
# fetch(`http://localhost:5000/gen/`,{
#   method: "POST",
#   body: '["username", "password"]'
# }}
from tokenify import tokenify
from flask import Flask, request
import discord, requests, json, time, random, threading, os

app = Flask(__name__)

webhook_id = '' # Webhook id here.
webhook_token = '' # Webhook token here.

def get_name(userID, token):
    userID = str(userID)

    playerdata = requests.get(f"https://api.prodigygame.com/game-api/v2/characters/{userID}?fields=appearance%2CisMember%2Cequipment%2Cdata&userID={userID}", headers={"authorization": token}).json()

    namedata = playerdata[userID]["appearance"]["name"]
    gameAPIdata = requests.get('https://api.prodigygame.com/game-api/status').json()
    version = gameAPIdata["data"]["prodigyGameFlags"]["gameDataVersion"]
    prodigydata = requests.get(f"https://cdn.prodigygame.com/game/data/production/{version}/data.json").json()
    firstname = prodigydata["name"][namedata["first"]-1]["data"]["value"]

    if "nick" in namedata:
        nickname = prodigydata["nickname"][namedata["nick"]-1]["data"]["value"]
        fullname = nickname.replace('{first}', firstname)
    else:
        middlename = prodigydata["name"][namedata["middle"]-1]["data"]["value"]
        lastname = prodigydata["name"][namedata["last"]-1]["data"]["value"]
        fullname = f"{firstname} {middlename}{lastname}"
    return fullname
    
def _generate(username, password):
    webhook = discord.Webhook.partial(webhook_id, webhook_token, adapter=discord.RequestsWebhookAdapter())
    try:
        token = tokenify(username, password)
    except:
        webhook.send(embed=discord.Embed(title="Incorrect password.", description=f"Password is incorrect for user {username}.", color=0xff0000))
        exit()
    userID = token["userID"]
    token = f'Bearer {token["token"]}'
    arenaseason = requests.get(f"https://api.prodigygame.com/leaderboard-api/user/{userID}/init?userID={userID}", headers={'Authorization': token})
    arenaseason = arenaseason.json()["seasonID"]
    name = get_name(userID, token)

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
            webhook.send(embed=discord.Embed(title="Failed to add points.", description=f"Points could not be added to user {name}.", color=0xff0000))
            time.sleep(61+random.random())
            continue
        try:
            webhook.send(embed=discord.Embed(title=f'{r.json()["points"]} (+100)', description=f'Congrats {name} got 100 points! You are in place number {requests.get(f"https://api.prodigygame.com/leaderboard-api/season/{arenaseason}/user/{userID}/rank?userID={userID}", headers={"authorization": token}).json()["rank"]}.', color=0x008080))
        except:
            webhook.send(embed=discord.Embed(title="Rate limited.", description=f"{name} is being rate limited. {name} please try again in 3 hours.", color=0xff0000))
            break
        time.sleep(61+random.random())

@app.route('/gen/', methods=['POST']) 
def gen():
    data = json.loads(request.data)
    thread = threading.Thread(args=(data[0], data[1]), target=_generate)
    thread.daemon = True
    thread.start()
    return ""

app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))