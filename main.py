import os
import urllib.parse
import aiohttp
from bs4 import BeautifulSoup
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

TARGET_GUILD_NAME = "나비"  # 검증할 문파 이름
ROLE_NAME = "나비"          # 지급할 디스코드 역할 이름

@bot.event
async def on_ready():
    print(f'로그인 완료: {bot.user.name}')

@bot.command(name="인증")
async def verify(ctx, character_info: str = None):
    if not character_info or "@" not in character_info:
        await ctx.send("❌ 올바른 형식으로 입력해주세요. 예시: `!인증 냠심@연` ")
        return

    encoded_info = urllib.parse.quote(character_info)
    url = f"https://baram.nexon.com/Profile/GuildInfo?character={encoded_info}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                await ctx.send("❌ 바람의나라 공식 홈페이지 정보를 불러올 수 없습니다.")
                return

            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

            guild_element = soup.select_one('.guild_name') or soup.select_one('.txt_guild')
            
            if not guild_element:
                await ctx.send("❌ 캐릭터 정보를 찾을 수 없거나 문파에 가입되어 있지 않습니다.")
                return

            guild_name = guild_element.get_text(strip=True)

            if TARGET_GUILD_NAME in guild_name:
                role = discord.utils.get(ctx.guild.roles, name=ROLE_NAME)
                if role:
                    await ctx.author.add_roles(role)
                    await ctx.send(f"✅ **{character_info}** 님 확인되었습니다! **[{ROLE_NAME}]** 역할이 부여되었습니다.")
                else:
                    await ctx.send(f"⚠️ 서버에 **[{ROLE_NAME}]** 역할이 존재하지 않습니다. 관리자에게 문의하세요.")
            else:
                await ctx.send(f"❌ **{character_info}** 님은 **{TARGET_GUILD_NAME}** 문파 소속이 아닙니다. (현재 문파: {guild_name})")

TOKEN = os.environ.get('DISCORD_TOKEN')
if TOKEN:
    bot.run(TOKEN)
