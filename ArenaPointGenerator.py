from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import json, requests, time

username = input("What is your username?\n")
password = input("What is your password?\n")

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
    print(f'{r.json()["points"]} (+100)')
    time.sleep(61)
