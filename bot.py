import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
from discord.ui import Button, View, Modal, TextInput
import json
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import aiohttp

intents = discord.Intents.all()
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None, description="#1 League Bot")


@bot.event
async def on_ready():
		await bot.change_presence(activity=discord.Game(name="!help - With ❤️ from krissan"))

# Function to load data from JSON file
def load_data():
	try:
		with open('league.json', 'r') as f:
			return json.load(f)
	except FileNotFoundError:
		return {}


# Function to save data to JSON file
def save_data(data):
	with open('league.json', 'w') as f:
		json.dump(data, f)

@bot.event
async def on_command_error(ctx, error):
		if isinstance(error, MissingPermissions):
				await ctx.send("You don't have permission to use this command.")

# Command to create a new league
@bot.command()
@has_permissions(administrator=True)
async def create_league(ctx, league_name):
		leagues_data = load_data()
		leagues_data[league_name] = {}
		save_data(leagues_data)
		await ctx.send(f'League "{league_name}" created!')


# Command to add a new team to a league
@bot.command()
@has_permissions(administrator=True)
async def add_team(ctx, league_name, team_name=None):
		if not league_name or not team_name:
				await ctx.send("Syntax error! Correct syntax: `!add_team <league_name> <team_name>`")
				return

		leagues_data = load_data()
		leagues_data.setdefault(league_name, {})
		leagues_data[league_name][team_name] = {
				'GP': 0,
				'OTW': 0,
				'L': 0,
				'P': 0,
				'W': 0,
				'OTL': 0,
				'+/-': 0,
				'points': 0,
				'players': []
		}
		save_data(leagues_data)
		await ctx.send(f'Team "{team_name}" added to league "{league_name}"!')




@bot.command()
@commands.has_permissions(administrator=True)
async def add_player(ctx, league_name=None, team_name=None, player_name=None):
		def check(m):
				return m.author == ctx.author and m.channel == ctx.channel

		leagues_data = load_data()

		if league_name is None:
				await ctx.send("Enter league name:")
				league_name_msg = await bot.wait_for('message', check=check)
				league_name = league_name_msg.content

		if league_name not in leagues_data:
				await ctx.send(f"League '{league_name}' does not exist.")
				return

		if team_name is None:
				await ctx.send("Enter team name:")
				team_name_msg = await bot.wait_for('message', check=check)
				team_name = team_name_msg.content

		if team_name not in leagues_data[league_name]:
				await ctx.send(f"Team '{team_name}' does not exist in league '{league_name}'.")
				return

		if player_name is None:
				await ctx.send(f"Enter player's name for team '{team_name}' in league '{league_name}':")
				player_name_msg = await bot.wait_for('message', check=check)
				player_name = player_name_msg.content

		leagues_data.setdefault(league_name, {})
		leagues_data[league_name].setdefault(
				team_name, {
						'GP': 0,
						'OTW': 0,
						'L': 0,
						'P': 0,
						'W': 0,
						'OTL': 0,
						'+/-': 0,
						'points': 0,
						'players': []
				})
		leagues_data[league_name][team_name]['players'].append(player_name)

		leagues_data[league_name][team_name].setdefault('player_stats', {})
		leagues_data[league_name][team_name]['player_stats'].setdefault(player_name, {
				'Height': '',
				'Weight': '',
				'Age': '',
				'Shooting Hand': '',
				'Nationality': '',
				'Archetype': '',
				'Position': '',
				'Number': ''
		})

		save_data(leagues_data)
		await ctx.send(f'Player "{player_name}" added to team "{team_name}" in league "{league_name}"!')



@bot.command()
async def player(ctx, league_name=None, team_name=None, player_name=None):
		def check(m):
				return m.author == ctx.author and m.channel == ctx.channel



	
		try:
				# Prompt for league name if not provided
				if league_name is None:
						await ctx.send("Enter league name:")
						league_name_msg = await bot.wait_for('message', check=check, timeout=60)
						league_name = league_name_msg.content

				# Prompt for team name if not provided
				if team_name is None:
						await ctx.send("Enter team name:")
						team_name_msg = await bot.wait_for('message', check=check, timeout=60)
						team_name = team_name_msg.content

				# Prompt for player's name if not provided
				if player_name is None:
						await ctx.send(f"Enter player's name for team '{team_name}' in league '{league_name}':")
						player_name_msg = await bot.wait_for('message', check=check, timeout=60)
						player_name = player_name_msg.content

				# Load leagues data
				leagues_data = load_data()
				print("Loaded leagues data")

				if league_name in leagues_data and team_name in leagues_data[league_name]:
						team_data = leagues_data[league_name][team_name]
						player_stats = team_data.get('player_stats', {})
						print(f"Team and player stats found for {league_name} -> {team_name}")

						# Check if player exists in player_stats
						if player_name in player_stats or player_name.capitalize() in player_stats:
								player_data = player_stats.get(player_name.capitalize(), player_stats.get(player_name))
								print(f"Player data found for {player_name}")

								# Extract player data
								height = player_data.get('Height', 'Unknown')
								weight = player_data.get('Weight', 'Unknown')
								age = player_data.get('Age', 'Unknown')
								shooting_hand = player_data.get('Shooting Hand', 'Unknown')
								nationality = player_data.get('Nationality', 'Unknown')
								archetype = player_data.get('Archetype', 'Unknown')
								position = player_data.get('Position', 'Unknown')
								number = player_data.get('Number', 'Unknown')
								print(f"Extracted player data for {player_name}")

								# Load the stats.png image
								try:
										img = Image.open("stats.png")
										print("Loaded stats.png image")
								except IOError:
										await ctx.send("Unable to load image: stats.png")
										print("Failed to load stats.png image")
										return

								# Initialize drawing context
								d = ImageDraw.Draw(img)

								# Load the custom font and set its size
								try:
										font_size = 60  # Adjust as needed
										font = ImageFont.truetype("BebasNeue-Regular.ttf", font_size)
										print(f"Loaded custom font 'BebasNeue-Regular.ttf' with size {font_size}")
								except IOError:
										await ctx.send("Unable to load font: BebasNeue-Regular.ttf")
										print("Failed to load font 'BebasNeue-Regular.ttf'")
										return

								# Write player information onto the image with the custom font
								d.text((240, 660), f"{league_name}", fill=(255, 255, 255), font=font)
								d.text((85, 570), f"Player Profile: {player_name}", fill=(255, 255, 255), font=font)
								d.text((205, 725), f"{team_name}", fill=(255, 255, 255), font=font)
								d.text((225, 790), f"{height}", fill=(255, 255, 255), font=font)
								d.text((235, 855), f"{weight}", fill=(255, 255, 255), font=font)
								d.text((175, 920), f"{age}", fill=(255, 255, 255), font=font)
								d.text((375, 990), f"{shooting_hand.capitalize()}", fill=(255, 255, 255), font=font)
								d.text((325, 1055), f"{nationality.capitalize()}", fill=(255, 255, 255), font=font)
								d.text((310, 1120), f"{archetype.capitalize()}", fill=(255, 255, 255), font=font)
								d.text((260, 1185), f"{position}", fill=(255, 255, 255), font=font)
								d.text((250, 1250), f"{number}", fill=(255, 255, 255), font=font)
								print("Added text to image")

								# Load the team image
								team_img_path = f"{league_name}_{team_name}_picture.png"
								try:
										team_img = Image.open(team_img_path).convert("RGBA")
										print(f"Loaded team image: {team_img_path}")
								except IOError:
										try:
												team_img = Image.open("default_team.png").convert("RGBA")
												print("Loaded default team image")
										except IOError:
												await ctx.send("Unable to load default team image.")
												print("Failed to load default team image")
												return

								# Resize the team image to fit on the stats image
								team_img = team_img.resize((256, 256))

								# Create a circular mask
								mask = Image.new('L', (256, 256), 0)
								draw = ImageDraw.Draw(mask)
								draw.ellipse((0, 0, 256, 256), fill=255)

								# Apply the circular mask to the team image
								team_img.putalpha(mask)

								# Create a new image for the outline
								outline_img = Image.new('RGBA', (266, 266), (255, 255, 255, 0))
								draw = ImageDraw.Draw(outline_img)
								draw.ellipse((0, 0, 266, 266), fill=(255, 255, 255, 255))

								# Paste the team image with outline onto the stats image at the specified coordinates
								img.paste(outline_img, (360 - 5, 250 - 5), mask=outline_img)
								img.paste(team_img, (360, 250), mask=team_img)

								print("Pasted team image with outline onto stats image")

								# Save the image with added text and team image
								img_path = f"{player_name}_profile.png"
								try:
										img.save(img_path)
										print("Saved the generated image")
								except IOError:
										await ctx.send("Unable to save the generated image.")
										print("Failed to save the generated image")
										return

								# Send the image in Discord
								try:
										await ctx.send(file=discord.File(img_path))
										print("Sent the image to Discord")
								except Exception as e:
										await ctx.send(f"Unable to send the image: {e}")
										print(f"Failed to send the image: {e}")

						else:
								await ctx.send(f'Player "{player_name}" not found in team "{team_name}"!')
								print(f'Player "{player_name}" not found in team "{team_name}"!')
				else:
						await ctx.send(f'Team "{team_name}" not found in league "{league_name}"!')
						print(f'Team "{team_name}" not found in league "{league_name}"!')

		except asyncio.TimeoutError:
				await ctx.send("Timed out. Please try again.")
		except Exception as e:
				await ctx.send(f"An error occurred: {e}")



# Adding a new command to set team picture
@bot.command()
@has_permissions(administrator=True)
async def set_team_picture(ctx, league_name, team_name, picture_url):
		leagues_data = load_data()

		if league_name in leagues_data and team_name in leagues_data[league_name]:
				async with aiohttp.ClientSession() as session:
						async with session.get(picture_url) as response:
								if response.status == 200:
										img_data = await response.read()
										img_path = f"{league_name}_{team_name}_picture.png"
										with open(img_path, 'wb') as f:
												f.write(img_data)

										await ctx.send(f'Team picture for "{team_name}" in league "{league_name}" set successfully!')
								else:
										await ctx.send("Failed to download image. Please check the URL and try again.")
		else:
				await ctx.send(f'Team "{team_name}" not found in league "{league_name}"!')

# Command to add points to a team
@bot.command()
@has_permissions(administrator=True)
async def add_points(ctx, league_name, team_name, points: int):
	leagues_data = load_data()
	leagues_data.setdefault(league_name, {})
	leagues_data[league_name].setdefault(team_name, {
			'GP': 0,
			'OTW': 0,
			'L': 0,
			'P': 0,
			'W': 0,
			'OTL': 0,
			'+/-': 0,
			'players': []
	})
	leagues_data[league_name][team_name]['P'] += points
	save_data(leagues_data)
	await ctx.send(
			f'{points} points added to team "{team_name}" in league "{league_name}"!'
	)


@bot.command()
async def leagues(ctx):
	leagues_data = load_data()
	print("Loaded leagues data:",
				leagues_data)  # Verify that the data loads correctly
	# Initialize variables to track the maximum length for each column
	max_lengths = {
			'Team': 0,
			'GP': 0,
			'W': 0,
			'L': 0,
			'OTL': 0,
			'OTW': 0,
			'+/-': 0,
			'P': 0
	}  # Modify the order here
	# Calculate the maximum length for each column
	for teams in leagues_data.values():
		for team, data in teams.items():
			max_lengths['Team'] = max(max_lengths['Team'], len(team))
			for key, value in data.items():
				if key in max_lengths:  # Check if the key is one of the columns we're tracking
					max_lengths[key] = max(max_lengths[key], len(str(value)))
	# Create table header with dynamically adjusted column widths
	table_header = "```css\n"
	columns_order = ['Team', 'GP', 'W', 'OTW', 'L', 'OTL', '+/-',
									 'P']  # Update the order here
	for key in columns_order:
		if key == 'Team':  # Left-align 'Team' column
			table_header += f"{key.ljust(max_lengths[key] + 2)}"
		else:
			table_header += f"{key.center(max_lengths[key] + 2)}"  # Center-align other columns
	table_header += "\n```"
	# Create table body
	table_body = ""
	for league, teams in leagues_data.items():
		print(f"Processing league: {league}"
					)  # Print to check which league is being processed
		# Check if there are teams in the league
		if teams:
			# Sort teams based on points
			sorted_teams = sorted(teams.items(),
														key=lambda x: x[1]['P'],
														reverse=True)
			# Create table body for each league
			league_table = ""
			for team, data in sorted_teams:
				row = ""
				row += f"{team.ljust(max_lengths['Team'] + 2)}"  # Left-align the team names
				for key in columns_order:
					if key != 'Team':  # Skip the team name for the rest of the columns
						row += f"{str(data.get(key, '')).center(max_lengths[key] + 2)}"  # Center-align the data in the columns
				league_table += f"{row}\n"
			print("League table for", league, ":",
						league_table)  # Print to check the table contents for each league
			# Create embed for each league
			embed = discord.Embed(title=f'{league}',
														color=discord.Color.blue())
			embed.description = table_header + "```\n" + league_table + "```"
			await ctx.send(embed=embed)
		else:
			await ctx.send(f"No teams found in league: {league}")



@bot.command()
@has_permissions(administrator=True)
async def result(ctx, league_name, team1, score1: int, team2, score2: int):
		leagues_data = load_data()

		if league_name in leagues_data:
				if team1 in leagues_data[league_name] and team2 in leagues_data[league_name]:
						leagues_data[league_name][team1]['GP'] += 1
						leagues_data[league_name][team2]['GP'] += 1

						# Determine the winner and update statistics
						if score1 > score2:
								# Team 1 wins
								leagues_data[league_name][team1]['W'] += 1
								leagues_data[league_name][team1]['P'] += 3
								leagues_data[league_name][team1]['+/-'] += (score1 - score2)
								leagues_data[league_name][team2]['L'] += 1
								leagues_data[league_name][team2]['+/-'] += (score2 - score1)
						elif score2 > score1:
								# Team 2 wins
								leagues_data[league_name][team2]['W'] += 1
								leagues_data[league_name][team2]['P'] += 3
								leagues_data[league_name][team2]['+/-'] += (score2 - score1)
								leagues_data[league_name][team1]['L'] += 1
								leagues_data[league_name][team1]['+/-'] += (score1 - score2)
						else:
								await ctx.send("For a tie game, use the `tie` command.")
								return

						save_data(leagues_data)
						await ctx.send(f"Game added between {team1} and {team2} in league {league_name}.")
				else:
						await ctx.send("One or both teams not found in the league.")
		else:
				await ctx.send("League not found.")


@bot.command()
@has_permissions(administrator=True)
async def tie(ctx, league_name, team1, score1: int, team2, score2: int, otw_team):
		leagues_data = load_data()

		if league_name in leagues_data:
				if team1 in leagues_data[league_name] and team2 in leagues_data[league_name]:
						leagues_data[league_name][team1]['GP'] += 1
						leagues_data[league_name][team2]['GP'] += 1

						if otw_team in [team1, team2]:
								if otw_team == team1:
										leagues_data[league_name][team1]['OTW'] += 1
										leagues_data[league_name][team1]['P'] += 2
										leagues_data[league_name][team2]['OTL'] += 1
										leagues_data[league_name][team2]['P'] += 1
								elif otw_team == team2:
										leagues_data[league_name][team2]['OTW'] += 1
										leagues_data[league_name][team2]['P'] += 2
										leagues_data[league_name][team1]['OTL'] += 1
										leagues_data[league_name][team1]['P'] += 1

								save_data(leagues_data)
								await ctx.send(f"Tie game recorded between {team1} and {team2} with OTW for {otw_team} in league {league_name}.")
						else:
								await ctx.send("The specified OTW team is not valid.")
				else:
						await ctx.send("One or both teams not found in the league.")
		else:
				await ctx.send("League not found.")




@bot.command()
async def table(ctx, league_name=None):
	if not league_name:
		await ctx.send('Syntax error! Correct syntax: `!table <league_name>`')
		return

	leagues_data = load_data()
	if league_name in leagues_data:
		teams = leagues_data[league_name]
		# Initialize variables to track the maximum length for each column
		max_lengths = {
				'Team': 0,
				'GP': 0,
				'W': 0,
				'OTW': 0,
				'L': 0,
				'OTL': 0,
				'+/-': 0,
				'P': 0
		}
		# Calculate the maximum length for each column
		for team, data in teams.items():
			max_lengths['Team'] = max(max_lengths['Team'], len(team))
			for key, value in data.items():
				if key in max_lengths:  # Check if the key is one of the columns we're tracking
					max_lengths[key] = max(max_lengths[key], len(str(value)))
		# Create table header with dynamically adjusted column widths
		table_header = "```css\n"
		columns_order = ['Team', 'GP', 'W', 'OTW', 'L', 'OTL', '+/-', 'P']
		for key in columns_order:
			if key == 'Team':  # Left-align 'Team' column
				table_header += f"{key.ljust(max_lengths[key] + 2)}"
			else:
				table_header += f"{key.center(max_lengths[key] + 2)}"  # Center-align other columns
		table_header += "\n```"
		# Sort teams based on points
		sorted_teams = sorted(teams.items(), key=lambda x: x[1]['P'], reverse=True)
		# Create table body for the league
		league_table = ""
		for team, data in sorted_teams:
			row = ""
			row += f"{team.ljust(max_lengths['Team'] + 2)}"  # Left-align the team names
			for key in columns_order:
				if key != 'Team':  # Skip the team name for the rest of the columns
					row += f"{str(data.get(key, '')).center(max_lengths[key] + 2)}"  # Center-align the data in the columns
			league_table += f"{row}\n"
		print("League table for", league_name, ":",
					league_table)  # Print to check the table contents for the league
		# Create embed for the league
		embed = discord.Embed(title=f'{league_name}',
													color=discord.Color.blue())
		embed.description = table_header + "```\n" + league_table + "```"
		await ctx.send(embed=embed)
	else:
		await ctx.send(f'League "{league_name}" not found!')

@bot.command()
async def team(ctx, league_name=None, team_name=None):
		def check(m):
				return m.author == ctx.author and m.channel == ctx.channel

		try:
				# If league_name or team_name are not provided, ask for them interactively using embeds
				if league_name is None:
						league_embed = discord.Embed(title="Enter League Name", description="Please enter the name of the league:")
						await ctx.send(embed=league_embed)

						league_name_msg = await bot.wait_for('message', check=check, timeout=60)
						league_name = league_name_msg.content

				if team_name is None:
						team_embed = discord.Embed(title="Enter Team Name", description=f"Please enter the team name for '{league_name}':")
						await ctx.send(embed=team_embed)

						team_name_msg = await bot.wait_for('message', check=check, timeout=60)
						team_name = team_name_msg.content

				leagues_data = load_data()

				if league_name in leagues_data and team_name in leagues_data[league_name]:
						team_data = leagues_data[league_name][team_name]

						embed = discord.Embed(title=f'Team Profile: {team_name}', color=discord.Color.blue())
						embed.add_field(name='League', value=league_name, inline=False)
						embed.add_field(name='Statistics', value=(
								f"GP: {team_data.get('GP', 'N/A')}\n"
								f"W: {team_data.get('W', 'N/A')}\n"
								f"L: {team_data.get('L', 'N/A')}\n"
								f"OTW: {team_data.get('OTW', 'N/A')}\n"
								f"OTL: {team_data.get('OTL', 'N/A')}\n"
								f"+/-: {team_data.get('+/-', 'N/A')}\n"
								f"P: {team_data.get('P', 'N/A')}\n"
						), inline=False)

						players_info = '\n'.join(team_data.get('players', [])) if team_data.get('players') else 'No players found'
						embed.add_field(name='Players', value=players_info, inline=False)

						await ctx.send(embed=embed)
				else:
						await ctx.send(f'Team "{team_name}" not found in league "{league_name}"!')

		except asyncio.TimeoutError:
				await ctx.send("Timed out. Please try again.")
		except Exception as e:
				await ctx.send(f"An error occurred: {e}")

@bot.command()
@has_permissions(administrator=True)
async def delete_team(ctx, league_name, team_name):
		leagues_data = load_data()
		if league_name in leagues_data:
				if team_name in leagues_data[league_name]:
						del leagues_data[league_name][team_name]
						save_data(leagues_data)
						await ctx.send(f"Team {team_name} has been deleted from league {league_name}.")
				else:
						await ctx.send("Team not found in the league.")
		else:
				await ctx.send("League not found.")

@bot.command()
@has_permissions(administrator=True)
async def delete_league(ctx, league_name):
		leagues_data = load_data()
		if league_name in leagues_data:
				del leagues_data[league_name]
				save_data(leagues_data)
				await ctx.send(f"League {league_name} has been deleted.")
		else:
				await ctx.send("League not found.")

@bot.command()
@has_permissions(administrator=True)
async def delete_player(ctx, league_name, team_name, player_name):
		leagues_data = load_data()
		if league_name in leagues_data and team_name in leagues_data[league_name]:
				if player_name in leagues_data[league_name][team_name]['players']:
						leagues_data[league_name][team_name]['players'].remove(player_name)
						save_data(leagues_data)
						await ctx.send(f'Player "{player_name}" deleted from team "{team_name}" in league "{league_name}"!')
				else:
						await ctx.send(f'Player "{player_name}" not found in team "{team_name}"!')
		else:
				await ctx.send(f'Team "{team_name}" not found in league "{league_name}"!')

@bot.command()
@has_permissions(administrator=True)
async def player_info(ctx, *args):
		leagues_data = load_data()

		def check(m):
				return m.author == ctx.author and m.channel == ctx.channel

		if len(args) == 0:
				await ctx.send("Enter league name:")
				league_name_msg = await bot.wait_for('message', check=check)
				league_name = league_name_msg.content

				await ctx.send("Enter team name:")
				team_name_msg = await bot.wait_for('message', check=check)
				team_name = team_name_msg.content

				await ctx.send(f"Enter player's name for team '{team_name}' in league '{league_name}':")
				player_name_msg = await bot.wait_for('message', check=check)
				player_name = player_name_msg.content

				await ctx.send("Enter player's height:")
				height_msg = await bot.wait_for('message', check=check)
				height = height_msg.content

				await ctx.send("Enter player's weight:")
				weight_msg = await bot.wait_for('message', check=check)
				weight = weight_msg.content

				await ctx.send("Enter player's age:")
				age_msg = await bot.wait_for('message', check=check)
				age = age_msg.content

				await ctx.send("Enter player's shooting hand:")
				shooting_hand_msg = await bot.wait_for('message', check=check)
				shooting_hand = shooting_hand_msg.content

				await ctx.send("Enter player's nationality:")
				nationality_msg = await bot.wait_for('message', check=check)
				nationality = nationality_msg.content

				await ctx.send("Enter player's archetype:")
				archetype_msg = await bot.wait_for('message', check=check)
				archetype = archetype_msg.content

				await ctx.send("Enter player's position:")
				position_msg = await bot.wait_for('message', check=check)
				position = position_msg.content

				await ctx.send("Enter player's number:")
				number_msg = await bot.wait_for('message', check=check)
				number = number_msg.content

				leagues_data.setdefault(league_name, {})
				leagues_data[league_name].setdefault(team_name, {})
				leagues_data[league_name][team_name].setdefault('player_stats', {})
				leagues_data[league_name][team_name]['player_stats'].setdefault(player_name, {})

				leagues_data[league_name][team_name]['player_stats'][player_name]['Height'] = height
				leagues_data[league_name][team_name]['player_stats'][player_name]['Weight'] = weight
				leagues_data[league_name][team_name]['player_stats'][player_name]['Age'] = age
				leagues_data[league_name][team_name]['player_stats'][player_name]['Shooting Hand'] = shooting_hand
				leagues_data[league_name][team_name]['player_stats'][player_name]['Nationality'] = nationality
				leagues_data[league_name][team_name]['player_stats'][player_name]['Archetype'] = archetype
				leagues_data[league_name][team_name]['player_stats'][player_name]['Position'] = position
				leagues_data[league_name][team_name]['player_stats'][player_name]['Number'] = number

		elif len(args) == 1:
				parameter = args[0].lower()

				if parameter not in ['age', 'height', 'weight', 'shooting_hand', 'nationality', 'archetype', 'position', 'number']:
						await ctx.send("Invalid parameter. Specify one of: `age`, `height`, `weight`, `shooting_hand`, `nationality`, `archetype`, `position`, `number`.")
						return

				await ctx.send("Enter league name:")
				league_name_msg = await bot.wait_for('message', check=check)
				league_name = league_name_msg.content

				if league_name not in leagues_data:
						await ctx.send(f"League '{league_name}' does not exist.")
						return

				await ctx.send("Enter team name:")
				team_name_msg = await bot.wait_for('message', check=check)
				team_name = team_name_msg.content

				if team_name not in leagues_data[league_name]:
						await ctx.send(f"Team '{team_name}' does not exist in league '{league_name}'.")
						return

				await ctx.send(f"Enter player's name for team '{team_name}' in league '{league_name}':")
				player_name_msg = await bot.wait_for('message', check=check)
				player_name = player_name_msg.content

				await ctx.send(f"Enter player's {parameter}:")
				value_msg = await bot.wait_for('message', check=check)
				value = value_msg.content

				leagues_data[league_name][team_name]['player_stats'].setdefault(player_name, {})
				leagues_data[league_name][team_name]['player_stats'][player_name][parameter.capitalize()] = value

		elif len(args) == 11:
				league_name, team_name, player_name, height, weight, age, shooting_hand, nationality, archetype, position, number = args

				leagues_data.setdefault(league_name, {})
				leagues_data[league_name].setdefault(team_name, {})
				leagues_data[league_name][team_name].setdefault('player_stats', {})
				leagues_data[league_name][team_name]['player_stats'].setdefault(player_name, {})

				leagues_data[league_name][team_name]['player_stats'][player_name]['Height'] = height
				leagues_data[league_name][team_name]['player_stats'][player_name]['Weight'] = weight
				leagues_data[league_name][team_name]['player_stats'][player_name]['Age'] = age
				leagues_data[league_name][team_name]['player_stats'][player_name]['Shooting Hand'] = shooting_hand
				leagues_data[league_name][team_name]['player_stats'][player_name]['Nationality'] = nationality
				leagues_data[league_name][team_name]['player_stats'][player_name]['Archetype'] = archetype
				leagues_data[league_name][team_name]['player_stats'][player_name]['Position'] = position
				leagues_data[league_name][team_name]['player_stats'][player_name]['Number'] = number

		else:
				await ctx.send("Invalid command format. Use either:\n"
											 "`!player_info <parameter>` (to update a specific parameter)\n"
											 "OR\n"
											 "`!player_info <league_name> <team_name> <player_name> <height> <weight> <age> <shooting_hand> <nationality> <archetype> <position> <number>` (to update all parameters at once)")
				return

		save_data(leagues_data)
		await ctx.send(f'Successfully updated player "{player_name}"\'s stats in team "{team_name}" of league "{league_name}"!')




# Trade command
@bot.command()
@has_permissions(administrator=True)
async def trade(ctx):
		def check_author(m):
				return m.author == ctx.author and m.channel == ctx.channel

		try:
				# Embed for collecting league name
				embed = discord.Embed(title="Trade Initiation 🔄", description="Which league are you trading within?", color=discord.Color.blue())
				league_name_msg = await ctx.send(embed=embed)

				league_name_response = await bot.wait_for('message', check=check_author, timeout=30)
				league_name = league_name_response.content.strip()

				# Embed for collecting team 1 name
				embed = discord.Embed(title="Trade Initiation 🔄", description=f"From which team in {league_name} are you trading a player?", color=discord.Color.blue())
				team1_name_msg = await ctx.send(embed=embed)

				team1_name_response = await bot.wait_for('message', check=check_author, timeout=30)
				team1_name = team1_name_response.content.strip()

				# Embed for collecting player 1 name
				embed = discord.Embed(title="Trade Initiation 🔄", description=f"Which player from {team1_name} is being traded?", color=discord.Color.blue())
				player1_name_msg = await ctx.send(embed=embed)

				player1_name_response = await bot.wait_for('message', check=check_author, timeout=30)
				player1_name = player1_name_response.content.strip()

				# Embed for collecting team 2 name
				embed = discord.Embed(title="Trade Initiation 🔄", description=f"Which team in {league_name} is receiving {player1_name}?", color=discord.Color.blue())
				team2_name_msg = await ctx.send(embed=embed)

				team2_name_response = await bot.wait_for('message', check=check_author, timeout=30)
				team2_name = team2_name_response.content.strip()

				# Embed for collecting player 2 name
				embed = discord.Embed(title="Trade Initiation 🔄", description=f"Which player from {team2_name} is being traded in exchange?", color=discord.Color.blue())
				player2_name_msg = await ctx.send(embed=embed)

				player2_name_response = await bot.wait_for('message', check=check_author, timeout=30)
				player2_name = player2_name_response.content.strip()

				# Process the trade based on collected data
				data = load_data()

				# Check if league, teams, and players exist
				league = data.get(league_name)
				if not league:
						await ctx.send(f"League '{league_name}' doesn't exist.")
						return

				team1 = league.get(team1_name)
				team2 = league.get(team2_name)

				if not team1:
						await ctx.send(f"Team '{team1_name}' isn't found in '{league_name}'.")
						return
				if not team2:
						await ctx.send(f"Team '{team2_name}' isn't found in '{league_name}'.")
						return

				players1 = team1.get("players", [])
				players2 = team2.get("players", [])

				if player1_name not in players1:
						await ctx.send(f"Player '{player1_name}' isn't on the roster for '{team1_name}'.")
						return
				if player2_name not in players2:
						await ctx.send(f"Player '{player2_name}' isn't on the roster for '{team2_name}'.")
						return

				# Perform the trade
				players1.remove(player1_name)
				players1.append(player2_name)
				players2.remove(player2_name)
				players2.append(player1_name)

				# Save data
				save_data(data)

				# Success embed with emojis
				success_embed = discord.Embed(title="Trade Successful! ✅", color=discord.Color.green())
				success_embed.add_field(name="Trade Details", value=f"{player1_name} is now on {team2_name}'s roster.\n{player2_name} is now on {team1_name}'s roster.")
				await ctx.send(embed=success_embed)

		except asyncio.TimeoutError:
				await ctx.send("Trade timed out. Please try again.")
		except Exception as e:
				await ctx.send(f"Error during trade: {e}")
				print(f"Error during trade: {e}")


@bot.command()
async def copyplayer(ctx, source_league=None, source_team=None, player_name=None, target_league=None, target_team=None):
					def check(m):
							return m.author == ctx.author and m.channel == ctx.channel

					try:
							# Prompt for source league if not provided
							if source_league is None:
									source_league_embed = discord.Embed(title="Enter Source League Name", description="Please enter the source league name:")
									await ctx.send(embed=source_league_embed)
									source_league_msg = await bot.wait_for('message', check=check, timeout=60)
									source_league = source_league_msg.content

							# Prompt for source team if not provided
							if source_team is None:
									source_team_embed = discord.Embed(title="Enter Source Team Name", description=f"Please enter the source team name in league '{source_league}':")
									await ctx.send(embed=source_team_embed)
									source_team_msg = await bot.wait_for('message', check=check, timeout=60)
									source_team = source_team_msg.content

							# Prompt for player name if not provided
							if player_name is None:
									player_name_embed = discord.Embed(title="Enter Player Name", description=f"Please enter the player name in team '{source_team}' in league '{source_league}':")
									await ctx.send(embed=player_name_embed)
									player_name_msg = await bot.wait_for('message', check=check, timeout=60)
									player_name = player_name_msg.content

							# Prompt for target league if not provided
							if target_league is None:
									target_league_embed = discord.Embed(title="Enter Target League Name", description="Please enter the target league name:")
									await ctx.send(embed=target_league_embed)
									target_league_msg = await bot.wait_for('message', check=check, timeout=60)
									target_league = target_league_msg.content

							# Prompt for target team if not provided
							if target_team is None:
									target_team_embed = discord.Embed(title="Enter Target Team Name", description=f"Please enter the target team name in league '{target_league}':")
									await ctx.send(embed=target_team_embed)
									target_team_msg = await bot.wait_for('message', check=check, timeout=60)
									target_team = target_team_msg.content

							# Load leagues data
							leagues_data = load_data()
							print("Loaded leagues data")

							# Validate existence of source and target
							if source_league in leagues_data and source_team in leagues_data[source_league]:
									if target_league in leagues_data and target_team in leagues_data[target_league]:
											player_stats = leagues_data[source_league][source_team].get('player_stats', {})

											if player_name in player_stats or player_name.capitalize() in player_stats:
													player_data = player_stats.get(player_name.capitalize(), player_stats.get(player_name))
													print(f"Player data found for {player_name}")

													# Copy player data to target team
													target_team_data = leagues_data[target_league][target_team]
													if 'player_stats' not in target_team_data:
															target_team_data['player_stats'] = {}
													if 'players' not in target_team_data:
															target_team_data['players'] = []

													target_team_data['player_stats'][player_name.capitalize()] = player_data
													target_team_data['players'].append(player_name.capitalize())

													# Save the updated data
													save_data(leagues_data)
													print(f"Player {player_name} copied from {source_team} in {source_league} to {target_team} in {target_league}")

													await ctx.send(f"Player {player_name} has been successfully copied from {source_team} in {source_league} to {target_team} in {target_league}.")
											else:
													await ctx.send(f'Player "{player_name}" not found in team "{source_team}"!')
													print(f'Player "{player_name}" not found in team "{source_team}"!')
									else:
											await ctx.send(f'Target team "{target_team}" not found in league "{target_league}"!')
											print(f'Target team "{target_team}" not found in league "{target_league}"!')
							else:
									await ctx.send(f'Source team "{source_team}" not found in league "{source_league}"!')
									print(f'Source team "{source_team}" not found in league "{source_league}"!')

					except asyncio.TimeoutError:
							await ctx.send("Timed out. Please try again.")
					except Exception as e:
							await ctx.send(f"An error occurred: {e}")

@bot.command()
async def copyteam(ctx, source_league=None, source_team=None, target_league=None, copy_players=None):
		def check(m):
				return m.author == ctx.author and m.channel == ctx.channel

		try:
				# Prompt for source league if not provided
				if source_league is None:
						source_league_embed = discord.Embed(title="Enter Source League Name", description="Please enter the source league name:")
						await ctx.send(embed=source_league_embed)
						source_league_msg = await bot.wait_for('message', check=check, timeout=60)
						source_league = source_league_msg.content

				# Prompt for source team if not provided
				if source_team is None:
						source_team_embed = discord.Embed(title="Enter Source Team Name", description=f"Please enter the source team name in league '{source_league}':")
						await ctx.send(embed=source_team_embed)
						source_team_msg = await bot.wait_for('message', check=check, timeout=60)
						source_team = source_team_msg.content

				# Prompt for target league if not provided
				if target_league is None:
						target_league_embed = discord.Embed(title="Enter Target League Name", description="Please enter the target league name:")
						await ctx.send(embed=target_league_embed)
						target_league_msg = await bot.wait_for('message', check=check, timeout=60)
						target_league = target_league_msg.content

				# Prompt whether to copy players or not if not provided
				if copy_players is None:
						copy_players_embed = discord.Embed(title="Copy Players?", description="Do you want to copy the players as well? (yes/no):")
						await ctx.send(embed=copy_players_embed)
						copy_players_msg = await bot.wait_for('message', check=check, timeout=60)
						copy_players = copy_players_msg.content.lower() in ['yes', 'y']

				# Load leagues data
				leagues_data = load_data()
				print("Loaded leagues data")

				# Validate existence of source and target
				if source_league in leagues_data and source_team in leagues_data[source_league]:
						if target_league in leagues_data:
								source_team_data = leagues_data[source_league][source_team]
								target_league_data = leagues_data[target_league]

								# Copy team data to target league
								target_league_data[source_team] = source_team_data.copy()

								if not copy_players:
										target_league_data[source_team]['player_stats'] = {}
										target_league_data[source_team]['players'] = []

								# Save the updated data
								save_data(leagues_data)
								print(f"Team {source_team} copied from {source_league} to {target_league}")

								await ctx.send(f"Team {source_team} has been successfully copied from {source_league} to {target_league}.")
						else:
								await ctx.send(f'Target league "{target_league}" not found!')
								print(f'Target league "{target_league}" not found!')
				else:
						await ctx.send(f'Source team "{source_team}" not found in league "{source_league}"!')
						print(f'Source team "{source_team}" not found in league "{source_league}"!')

		except asyncio.TimeoutError:
				await ctx.send("Timed out. Please try again.")
		except Exception as e:
				await ctx.send(f"An error occurred: {e}")

@bot.command(name='help')
async def help_command(ctx):
		# Embed for regular commands
		regular_embed = discord.Embed(
				title="Regular Commands",
				description="""
**!leagues**
- Description: List all leagues.
- Example: `!leagues`

**!table <league_name>**
- Description: Show the table for a league.
- Example: `!table MyLeague`

**!team <league_name> <team_name>**
- Description: Display information about a specific team.
- Example: `!team MyLeague MyTeam`

**!player [league_name] [team_name] [player_name]**
- Description: Display information about a specific player.
- Example: `!player MyLeague MyTeam MyPlayer`
- Interactive Mode: Run `!player` without any parameters to enter interactive mode and follow the prompts to find the player.
""",
				color=discord.Color.blue()
		)

		# Embed for admin commands
		admin_embed = discord.Embed(
				title="Admin Commands",
				description="""
**!create_league <league_name>**
- Description: Create a new league.
- Example: `!create_league MyLeague`

**!add_team [league_name] [team_name]**
- Description: Add a new team to a league.
- Example: `!add_team MyLeague MyTeam`
- Interactive Mode: Run `!add_team` without any parameters to enter interactive mode and follow the prompts to add the team.

**!add_player [<league_name> <team_name> <player_name>]**
- Description: Add a player to a team in a league. If parameters are not provided, the bot will prompt for each.
- Examples:
		- `!add_player MyLeague MyTeam MyPlayer` (Direct command mode)
		- `!add_player` (Interactive mode)

**!delete_player <league_name> <team_name> <player_name>**
- Description: Remove a player from a team in a league.
- Example: `!delete_player MyLeague MyTeam MyPlayer`

**!add_points <league_name> <team_name> <points>**
- Description: Add points to a team.
- Example: `!add_points MyLeague MyTeam 3`

**!delete_team <league_name> <team_name>**
- Description: Delete a team from a league.
- Example: `!delete_team MyLeague MyTeam`

**!delete_league <league_name>**
- Description: Delete a league.
- Example: `!delete_league MyLeague`

**!player_info**
- Description: Sets info for a player in a team interactively. Prompts for league name, team name, player name, height, weight, age, shooting hand, nationality, archetype, position, and number.
- Example: `!player_info`

**!player_info <parameter>**
- Description: Updates a specific parameter for a player interactively.
- Supported parameters: `height`, `weight`, `age`, `shooting_hand`, `nationality`, `archetype`, `position`, `number`.
- Example: `!player_info age`

**!player_info <league_name> <team_name> <player_name> <height> <weight> <age> <shooting_hand> <nationality> <archetype> <position> <number>**
- Description: Sets all info for a player in a team at once.
- Example: `!player_info MyLeague MyTeam MyPlayer 180cm 110kg 25 left Canadian Butterfly Goalie 1`

**!result <league_name> <team1> <score1> <team2> <score2>**
- Description: Record the result of a game between two teams.
- Example: `!result MyLeague TeamA 3 TeamB 2`

**!tie <league_name> <team1> <score1> <team2> <score2> <otw_team>**
- Description: Record a tie game with an overtime winner.
- Example: `!tie MyLeague TeamA 3 TeamB 3 TeamA`

**!set_team_picture <league_name> <team_name> <picture_url>**
- Description: Set the team picture for a team.
- Example: `!set_team_picture MyLeague MyTeam https://example.com/team_picture.png`

**!trade [source_league] [source_team] [source_player] [target_league] [target_team]**
- Description: Trade a player between two teams.
- Example: `!trade MyLeague MyTeam MyPlayer OtherLeague OtherTeam`
- Interactive Mode: Run `!trade` without any parameters to enter interactive mode and follow the prompts to complete the trade.

**!copyplayer [source_league] [source_team] [player_name] [target_league] [target_team]**
- Description: Copy a player from one team to another across leagues.
- Example: `!copyplayer MyLeague TeamA Player1 OtherLeague TeamB`
- Interactive Mode: Run `!copyplayer` without any parameters to enter interactive mode and follow the prompts to complete the player copy.

**!copyteam [source_league] [source_team] [target_league] [copy_players (Yes/No)]**
- Description: Copy a team from one league to another. Optionally copy the players as well.
- Example: `!copyteam MyLeague TeamA OtherLeague Yes`
- Interactive Mode: Run `!copyteam` without any parameters to enter interactive mode and follow the prompts to complete the team copy.
""",
				color=discord.Color.red()
		)

		# Send the appropriate embed based on user permissions
		if ctx.author.guild_permissions.administrator:
				await ctx.send(embed=admin_embed)
		else:
				await ctx.send(embed=regular_embed)

bot.run(
		'TOKEN')