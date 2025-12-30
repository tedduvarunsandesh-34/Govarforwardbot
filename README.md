<div align="center">
  <img src="https://graph.org/file/7f7dcc89135e7d6c64bbb.jpg" alt="Ultra Forward Bot Logo" width="220" height="220" style="border-radius: 20px; box-shadow: 0px 0px 20px rgba(0,0,0,0.5);">

  # 🚀 Ultra Forward Bot
  
  **The Advanced, High-Speed Telegram Forwarding Solution**

  <p>
    <a href="https://github.com/LastPerson07/Ultra-Forward-Bot/stargazers"><img src="https://img.shields.io/github/stars/LastPerson07/Ultra-Forward-Bot?color=yellow&logo=github&style=for-the-badge" alt="Stars"/></a>
    <a href="https://github.com/LastPerson07/Ultra-Forward-Bot/network/members"><img src="https://img.shields.io/github/forks/LastPerson07/Ultra-Forward-Bot?color=orange&logo=github&style=for-the-badge" alt="Forks"/></a>
    <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python"/></a>
    <a href="https://docs.pyrogram.org/"><img src="https://img.shields.io/badge/Pyrogram-v2.0-red?style=for-the-badge&logo=telegram&logoColor=white" alt="Pyrogram"/></a>
  </p>

  <h4>
    <a href="#-features">Features</a> •
    <a href="#-deployment">Deploy</a> •
    <a href="#-configuration">Config</a> •
    <a href="#-commands">Commands</a>
  </h4>
</div>

---

### ⚡ Overview
**Ultra Forward Bot** is a powerful Python-based bot designed to automate message forwarding on Telegram. Whether you need to clone public channels, migrate content from private restricted channels, or remove duplicate media, this bot does it all with **10x speed** using concurrent batch processing.

---

### 🚀 Deployment

<div align="center">
  <b>Deploy your own instance in one click:</b>
  <br><br>
  
  <a href="https://app.koyeb.com/deploy?type=git&repository=github.com/LastPerson07/Ultra-Forward-Bot&branch=main&name=ultra-forward-bot">
    <img src="https://www.koyeb.com/static/images/deploy/button.svg" alt="Deploy to Koyeb" width="220">
  </a>
  
  <a href="https://heroku.com/deploy?template=https://github.com/LastPerson07/Ultra-Forward-Bot">
    <img src="https://www.herokucdn.com/deploy/button.svg" alt="Deploy to Heroku" width="220">
  </a>
</div>

---

### 💎 Features

| 🌟 Feature | 📝 Description |
| :--- | :--- |
| **🚀 Ultra Speed** | Forwards messages in parallel batches (10x faster than standard bots). |
| **🔐 Private Access** | Forward content from **Private/Restricted** channels using a Userbot session. |
| **🧹 Smart Cleaner** | Automatically detects and removes duplicate media/files. |
| **📝 Customization** | Add your own **Captions** and **Buttons** to forwarded messages. |
| **🛡️ Filters** | Whitelist/Blacklist content by **File Type**, **Keywords**, **Size**, or **Extension**. |
| **🤖 Multi-Platform** | Optimized for Heroku, Koyeb, Railway, and VPS. |

---

### ⚙️ Configuration

<details>
<summary><b>🔻 Click to view all Environment Variables</b></summary>
<br>

| Variable | Description | Required |
| :--- | :--- | :---: |
| `API_ID` | Get this from [my.telegram.org](https://my.telegram.org) | ✅ |
| `API_HASH` | Get this from [my.telegram.org](https://my.telegram.org) | ✅ |
| `BOT_TOKEN` | Get this from [@BotFather](https://t.me/BotFather) | ✅ |
| `OWNER_ID` | Your Telegram User ID (Space separated for multiple admins). | ✅ |
| `DB_URL` | MongoDB Connection String from [MongoDB Atlas](https://cloud.mongodb.com). | ✅ |
| `DB_NAME` | Name of your Database (Default: `madflixbotz`). | ❌ |
| `BOT_SESSION` | Session name for the bot (Default: `forward-bot`). | ❌ |

</details>

---

### 🤖 Commands

<details>
<summary><b>🔻 Click to view Bot Commands</b></summary>
<br>

| Command | Description |
| :--- | :--- |
| `/start` | Check if the bot is alive and get the menu. |
| `/forward` | Start a forwarding task (Public or Private). |
| `/unequify` | Remove duplicate messages in a channel. |
| `/settings` | Configure Userbot, Target Channels, and Filters. |
| `/cancel` | Stop the current active forwarding task. |
| `/reset` | Reset your personal settings to default. |
| `/stats` | Check bot statistics (Admin Only). |
| `/broadcast` | Broadcast a message to all bot users (Admin Only). |
| `/restart` | Restart the bot server (Admin Only). |

</details>

---

<div align="center">
  <b>Maintained by <a href="https://github.com/LastPerson07">LastPerson07</a></b>
  <br>
  Made with ❤️ using Python & Pyrogram
</div>

