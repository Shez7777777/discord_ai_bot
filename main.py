import os
import discord
from groq import Groq
from flask import Flask
from threading import Thread

# Get environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Groq client
client_ai = Groq(api_key=GROQ_API_KEY)

# Discord intents
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# Flask app for health checks (Render requirement)
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Discord Bot is running!"

@app.route('/health')
def health():
    return "OK", 200

def run_flask():
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 10000)))

@client.event
async def on_ready():
    print(f"✅ Bot is online as {client.user}")
    print(f"📊 Connected to {len(client.guilds)} servers")

@client.event
async def on_message(message):
    # Ignore bot's own messages
    if message.author == client.user:
        return

    user_text = message.content.strip()
    if not user_text:
        return

    # Show typing indicator
    async with message.channel.typing():
        try:
            ai_response = client_ai.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a friendly assistant chatting on Discord."},
                    {"role": "user", "content": user_text}
                ]
            )

            reply = ai_response.choices[0].message.content
            await message.channel.send(reply)

        except Exception as e:
            print("❌ GROQ ERROR >>>", repr(e))
            await message.channel.send("⚠️ AI error occurred. Please try again.")

# Start Flask in a separate thread
if __name__ == "__main__":
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    print("🚀 Starting Discord bot...")
    client.run(DISCORD_TOKEN)