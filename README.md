# 🏆 LeagueBot - The Ultimate Discord League Manager

**LeagueBot** is a powerful and fully customizable Discord bot for managing sports leagues, teams, and player data directly from your server. Built with love by **krissan ❤️**, this bot brings stats, trades, tables, and team profiles to life — all without leaving Discord!

---

## ✨ Features

- 📊 **Live League Tables**  
  Display dynamically updated standings with games played, wins, losses, points, and more.

- 🧑‍🤝‍🧑 **Team & Player Management**  
  Add, update, and delete players and teams with ease. Supports full player profiles (age, position, archetype, etc.).

- 🖼️ **Visual Player Cards**  
  Automatically generate stylish stat cards with custom images and player info using PIL.

- 🔁 **Trades & Transfers**  
  Easily perform trades or copy players and teams between leagues.

- 🎯 **Interactive Commands**  
  Use commands with arguments or enter interactive prompt mode for guided input.

- 🔐 **Admin Control**  
  Role-protected commands for league moderation like result reporting, point adjustments, and picture uploads.

- 🔍 **Searchable League Database**  
  List all leagues, view individual teams, players, or full league tables.

---

## 🛠️ Built With

- **Python 3.11+**
- [discord.py](https://github.com/Rapptz/discord.py)
- `Pillow` for image manipulation
- `aiohttp` for async image downloading
- JSON-based persistent storage

---

## 📌 Commands Overview

Use `!help` in your server to get a categorized list of all available commands for both regular users and admins.

---

## 🚀 Getting Started

1. Clone this repo and install requirements  
   ```bash
   pip install -r requirements.txt
   ```

2. Add your Discord bot token in `bot.run('YOUR_TOKEN')`

3. Run the bot  
   ```bash
   python bot.py
   ```

---

## 🧠 Tips

- Use `!add_player`, `!add_team`, etc., in interactive mode if you’re not comfortable with command-line arguments.
- Player cards require `stats.png` and `BebasNeue-Regular.ttf` in your working directory.
- Use `!set_team_picture` to personalize visuals.

---

## 🙌 Contribute

Feel free to fork, contribute, or suggest features via pull requests or issues. LeagueBot is community-driven!

---

## 📜 License

MIT License – free to use, modify, and share!
