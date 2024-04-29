import discord
from discord.ext import commands
import asyncio
import requests
import os
import time

client = commands.Bot(command_prefix='', self_bot = True)
print("https://github.com/pinkiwinter\n")


def authmethod():
        while True:
            email = input("Enter Email: ").strip()
            password = input("Enter Password: ").strip()

            payload = {
                "login": email,
                "password": password
            }
            headers = {
                "Content-Type": "application/json"
            }
            response = requests.post("https://discord.com/api/v9/auth/login", json=payload, headers=headers)
            if response.ok:
                data = response.json()
                if 'token' in data:
                    return data['token']
                elif 'ticket' in data:
                    while True:
                        print("\nTwo-factor authentication is enabled. Please provide the code.")
                        code = input("Enter the authentication code: ").strip()
                        token_payload = {
                            "code": code,
                            "ticket": data["ticket"]
                        }
                        token_response = requests.post("https://discord.com/api/v9/auth/mfa/totp", json=token_payload, headers=headers)
                        if token_response.ok:
                            token_data = token_response.json()
                            if 'token' in token_data:
                                token = token_data['token']
                                return token
                            else:
                                print("\nFailed to retrieve token after 2FA authentication.")
                                continue
                        else:
                            print("\nFailed to authenticate using the provided code.")
                            continue
                else:
                    print("\nUnknown response format.")
                    continue

            else:
                print("\nLogin Failed. Please check your credentials.")
                continue


def run_client():
    try:
        token = authmethod()
        client.run(token)
    except Exception as e:
        print("")


async def choiced():
            choice = input("\nMethods:\n1. Enter 'here' in the channel where you want to delete messages.\n2. Provide the channel ID.\n(1/2)\n")
            while True:
                if choice == "2":
                    try:
                        channel_id = int(input("\nProvide the channel ID: "))
                        channel = client.get_channel(channel_id)
                        if channel is None:
                            print("[-] Channel not found. Please enter a valid channel ID.")
                        else:
                            await delete_messages(channel)
                            break
                    except ValueError:
                        print("[-] Invalid channel ID. Please enter a valid integer.")
                elif choice == "1": 
                    print("\nEnter 'here' in the channel where you want to delete messages.")
                    await delete_messages(None)
                    break
                else:
                    print("[-] Provide the number (1/2)")


@client.event
async def on_ready():
    print(f"\nSuccessfully logged into your account: {client.user.name}.")
    await choiced()


async def delete_messages(channel):
        c = 0
        if channel is not None:
            if isinstance(channel, discord.DMChannel):
                print(f"\nSelected DMs with {channel.recipient.name}")
            else:
                print(f"\nSelected channel '{channel.name}' in '{channel.guild.name}' server.")

            try:
                while True:
                    amount_input = input("\nProvide the number of messages you wish to delete: ")
                    try:
                        amount = int(amount_input)
                        break  
                    except ValueError:
                        print("[-] Invalid input. Please enter a number.")
            except ValueError:
                print("\n[-] Operation cancelled by user.")
                return

            async for m in channel.history(limit=None):
                if m.author == client.user:
                    try:
                        print(f"[-] {m.content}")
                        await m.delete()
                        await asyncio.sleep(2)
                        c += 1 
                        if c >= amount:
                            break
                    except discord.errors.Forbidden as e:
                        if e.code == 50021:
                            pass
            print("\nMessages have been deleted.")

            while True:
                choice = input("\nDo you want to continue? (yes/no): ")
                if choice.lower() == "yes":
                    c = 0
                    await choiced()
                    break
                elif choice.lower() == "no":
                    print("See ya next time!")
                    time.sleep(2)
                    os._exit(0)
                else:
                    print("\n[-] Answer is yes or no only.")
        else:
           pass


@client.event
async def on_message(message):
    channel = None
    if isinstance(message.channel, discord.DMChannel) and "here" in message.content or isinstance(message.channel, discord.TextChannel) and "here" in message.content:
        try:
            if message.author == client.user:
                channel = message.channel
        except (UnboundLocalError, AttributeError) as e:
            pass
            
    if channel is not None:
        await delete_messages(channel)


run_client()