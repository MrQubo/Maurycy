#!/usr/bin/env python3

import asyncio
import logging
import os
import random
import string

import discord

# logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('bot')


client = discord.Client()

guild_id = 846678318928625684
patryk_id = 654412645688016898
redirect_to_general_channel_ids = [
    # ustalenia-ważne
    846678662102515733,
]
# ogólny
general_channel_id = 846678318928625687

message_count = 0

typing_lock = asyncio.Lock()


@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.id != guild_id:
            await guild.leave()

    global general_channel
    general_channel = client.get_channel(general_channel_id)

    log.info('Ready.')

@client.event
async def on_guild_join(guild):
    log.debug('Joined new guild:', guild)

    if guild.id != guild_id:
        await guild.leave()

@client.event
async def on_message(message):
    global message_count

    if message.guild is None or message.guild.id != guild_id:
        return

    if message.author == client.user:
        return

    if message.channel.id in redirect_to_general_channel_ids:
        channel = general_channel
    else:
        channel = message.channel

    message_count += 1
    if message_count >= 70:
        message_count = 0
        await send_funny_message(channel)

async def send_funny_message(channel):
    log.debug('Sending funny message...')

    typing_time = get_typing_time()
    msg = get_funny_message()

    # channel.typing() context manager is buggy
    async with typing_lock:
        await channel.trigger_typing()
        await asyncio.sleep(typing_time)
        await channel.send(msg)

    log.debug('Send funny message.')

def get_typing_time():
    return min(random.expovariate(1/0.5) + 0.9, 4.0)

funny_messages = [
    'dajcie admina',
    'mogę admina',
    'poproszę admina',

    'dodajcie boty',
    'nk boty',
    'gdzie są boty',
]
def get_funny_message():
    from random import choice, randrange

    msg = choice(funny_messages)
    if random_chance(1/2):
        msg = mutation_capitalize(msg)
    if random_chance(1/2):
        msg = mutation_add_period(msg)
    while random_chance(1/20):
        msg = mutation_swap(msg)
    if random_chance(1/20):
        msg = mutation_switch_period(msg)
    while random_chance(1/50):
        msg = mutation_switch_letter(msg)
    while random_chance(1/25):
        msg = mutation_skip_char(msg)
    if random_chance(1/3):
        msg = mutation_mention_patryk(msg)
    return msg

def random_chance(p):
    assert 0 <= p <= 1
    if p >= 1:
        return True
    if p <= 0:
        return False
    return random.uniform(0, 1) < p

def mutation_capitalize(msg):
    return msg.capitalize()

periods = '?!.'
def mutation_add_period(msg):
    if msg[-1] in periods:
        return msg
    return msg + random.choice(periods)

def mutation_switch_period(msg):
    msg = list(msg)
    if msg[-1] == '?':
        msg[-1] = '/'
    elif msg[-1] == '!':
        msg[-1] = '1'
    return ''.join(msg)

def mutation_swap(msg):
    if len(msg) < 2:
        return msg
    idx = random.randrange(len(msg) - 1)
    msg = list(msg)
    msg[idx], msg[idx+1] = msg[idx+1], msg[idx]
    return ''.join(msg)

letters = frozenset(string.ascii_letters + 'ęóąśłżźćĘÓĄŚŁŻŹĆ')
def mutation_switch_letter(msg):
    assert len(msg) >= 1
    idx = random.randrange(len(msg))
    if msg[idx] not in letters:
        return msg
    msg = list(msg)
    msg[idx] = random.choice(letters)
    return ''.join(msg)

def mutation_skip_char(msg):
    if len(msg) < 2:
        return msg
    idx = random.randrange(len(msg))
    msg = list(msg)
    msg.pop(idx)
    return ''.join(msg)

def mutation_mention_patryk(msg):
    return f'<@{patryk_id}> {msg}'


if __name__ == '__main__':
    log.info('Starting.')
    client.run(os.environ['DISCORD_TOKEN'])
