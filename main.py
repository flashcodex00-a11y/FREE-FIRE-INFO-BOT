import requests
import asyncio
import time
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# ================= CONFIG =================
BOT_TOKEN = "8466154917:AAEanaHGULeHAwsV9pvkxLcGyyV1F2lSWvk"
ALLOWED_GROUP_ID = -1003512881577
OWNER_ID = 6474022249
SERVERS = ["BD", "IND", "PK"]
SPAM_DELAY = 0.8
MAX_LENGTH = 800
user_last_message = {}
# =========================================

# -------- Anti-spam ---------
async def anti_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    text = update.message.text or ""
    now = time.time()

    if chat_id != ALLOWED_GROUP_ID or user_id == OWNER_ID:
        return

    if len(text) > MAX_LENGTH or now - user_last_message.get(user_id,0) < SPAM_DELAY:
        try: await update.message.delete()
        except: pass
        return

    user_last_message[user_id] = now

# -------- Helper ---------
def ts_to_date(ts):
    try:
        return datetime.utcfromtimestamp(int(ts)).strftime("%d-%m-%Y %H:%M:%S")
    except:
        return "N/A"

# -------- /inf command ---------
async def inf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if chat_id != ALLOWED_GROUP_ID and user_id != OWNER_ID:
        await update.message.reply_text("❌ This bot works only in the official group.")
        return

    if len(context.args) not in [1,2]:
        await update.message.reply_text("❗ Wrong command format!\nUse:\n/inf <uid>\n/inf <server> <uid>")
        return

    msg = await update.message.reply_text("⚡ Processing 30%...")
    await asyncio.sleep(0.5)
    await msg.edit_text("⚡ Processing 60%...")
    await asyncio.sleep(0.5)
    await msg.edit_text("⚡ Processing 80%...")
    await asyncio.sleep(0.5)

    server = None
    data = None

    try:
        if len(context.args) == 2:
            server = context.args[0].upper()
            uid = context.args[1]
            api = f"https://free-fire-info-api-1.vercel.app/info?uid={uid}&region={server}"
            r = requests.get(api, timeout=10).json()
            if r.get("basicInfo") is None:
                await msg.edit_text("❌ Invalid UID or Server")
                return
            data = r
        else:
            uid = context.args[0]
            for s in SERVERS:
                api = f"https://free-fire-info-api-1.vercel.app/info?uid={uid}&region={s}"
                r = requests.get(api, timeout=10).json()
                if r.get("basicInfo") is not None:
                    server = s
                    data = r
                    break
            if not server:
                await msg.edit_text("❌ UID not found in any server")
                return

        # -------- Parse Data ---------
        basic = data.get("basicInfo",{})
        clan = data.get("clanBasicInfo",{})
        pet = data.get("petInfo",{})
        profile = data.get("profileInfo",{})
        social = data.get("socialInfo",{})

        # -------- Format Text ---------
        text = f"""
🔥 FREE FIRE FULL PROFILE 🔥

👤 Name: {basic.get('nickname','N/A')}
🆔 UID: {basic.get('accountId',uid)}
🌍 Server: {basic.get('region',server or 'N/A')}
⭐ Level: {basic.get('level','N/A')}
📈 EXP: {basic.get('exp','N/A')}
👍 Likes: {basic.get('liked','N/A')}
📅 Account Created: {ts_to_date(basic.get('createAt','0'))}
🕒 Last Login: {ts_to_date(basic.get('lastLoginAt','0'))}

🏆 RANK INFO
🥇 CS Rank: {basic.get('csRank','N/A')}
⭐ CS Max Rank: {basic.get('csMaxRank','N/A')}
⭐ Ranking Points: {basic.get('rankingPoints','N/A')}

📊 GUILD INFO
🏰 Guild Name: {clan.get('clanName','No Guild')}
👑 Captain ID: {clan.get('captainId','N/A')}
👥 Members: {clan.get('currentMembers','N/A')}/{clan.get('maxMembers','N/A')}
📈 Guild Level: {clan.get('clanLevel','N/A')}

🐾 PET INFO
🐶 Pet: {pet.get('petName','None')}
⭐ Pet Level: {pet.get('level','N/A')}
✅ Selected: {"Yes" if pet.get('isSelected') else "No"}

💻 PROFILE INFO
Avatar ID: {profile.get('avatarId','N/A')}
Cosmetic Items: {profile.get('cosmeticItems','N/A')}

🌐 SOCIAL INFO
Gender: {social.get('gender','N/A')}
Language: {social.get('language','N/A')}
Social Highlight: {social.get('socialHighlight','No Highlight')}
"""

        await msg.edit_text(text)

    except Exception as e:
        print("Error:", e)
        await msg.edit_text("⚠️ System error, try again later.")

# -------- /start ---------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 FF INFO BOT READY 🔥\n\nUse:\n/inf uid\n/inf server uid"
    )

# -------- App Setup ---------
app = ApplicationBuilder().token(BOT_TOKEN).build()

# Command handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("inf", inf))

# Anti-spam
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, anti_spam))

# Run
app.run_polling()