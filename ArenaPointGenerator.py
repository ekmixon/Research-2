import requests, time, random, json, subprocess

username = input("What is your username?\n")
password = input("What is your password?\n")

try:
    token = json.loads(subprocess.Popen(f"node tokenify.js {username} {password}", shell=True, stdout=subprocess.PIPE).stdout.read().decode())
except:
    print("\x1b[31mUsername or Password are incorrect.\x1b[0m")
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
        print("Failed to add points.")
        time.sleep(61+random.random())
        continue
    try:
        print(f'{r.json()["points"]} (+100). Your are in place number {requests.get(f"https://api.prodigygame.com/leaderboard-api/season/{arenaseason}/user/{userID}/rank?userID={userID}", headers={"authorization": token}).json()["rank"]}.')
    except KeyError:
        print("You are being rate limited.")
        break
    time.sleep(61+random.random())
