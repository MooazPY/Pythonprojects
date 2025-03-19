import discord
import random
# import datetime




dis_token = "----------YOUR DISCORD TOKEN----------"

def get_random_page():#GET RANDOM PAFE FROM ONLINE WEBSITE ((YOU CAN SCRAPE IT ALSO))
    
    random_num = random.randint(1,604)
    
    if random_num < 10:
        url = f"https://www.searchtruth.com/quran/images/images1/00{random_num}.jpg"
    elif random_num < 100:
        url = f"https://www.searchtruth.com/quran/images/images1/0{random_num}.jpg"
    else:
        url = f"https://www.searchtruth.com/quran/images/images1/{random_num}.jpg"
    return url



class MyClient(discord.Client):
  async def on_ready(self):# CHECK IF IT'S LOGGEN IN SUCCESSFULLY
    print('Logged on as {0}!'.format(self.user))

  async def on_message(self, message):
    if message.author == self.user:
      return
    if message.content.startswith('$quran'): # IF USERS TYPED $quran SO THE BOT STARTS DYNAMICALLY SENT A RANDOM PAGE OF THE QURAN
        await message.channel.send("الورد اليومي ")
        await message.channel.send(get_random_page())


intents = discord.Intents.default() # SET THE DEFAULT SETTING OF TJE BOT ((SENDING MESSAGES))
intents.message_content = True

client = MyClient(intents=intents)
client.run(dis_token) 
        
