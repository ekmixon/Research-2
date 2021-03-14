(async() => {
    const tokenify = require("./tokenify").tokenify
    const fetch = require("node-fetch")
	const readline = require("readline");
	var rl = readline.createInterface({
		input: process.stdin,
		output: process.stdout
	});
	var token;
	rl.question("What is your username?\n", async(username) => {
	rl.question("What is your password?\n", async(password) => {
    token = await tokenify(username, password)
    var userID = token.userID
    token = `Bearer ${token.token}`
    let arenaseason = await (await fetch(`https://api.prodigygame.com/leaderboard-api/user/${userID}/init?userID=${userID}`, {
        method: 'GET',
        credentials: 'same-origin',
        headers: {
            'Authorization': token,
        },
    })).json();
    arenaseason = arenaseason.seasonID;

	setInterval(async() => {
		const data = await (
			await fetch(
				`https://api.prodigygame.com/leaderboard-api/season/${arenaseason}/user/${userID}/pvp?userID=${userID}`,
				{
					headers: {
						authorization: token,
						"content-type":
							"application/x-www-form-urlencoded; charset=UTF-8",
					},
					body: `seasonID=${arenaseason}&action=win`,
					method: "POST",
					mode: "cors",
				}
			)
		).json();
		console.log(`${data.points} (+100).`);
	}, 60500);
})
})
})()