#!/usr/bin/env python3

import asyncio
from collections import OrderedDict
from dataclasses import dataclass
import logging
import random
import string

import discord

# logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('bot')


client = discord.Client()

allowed_guild_ids = [
    846678318928625684,  # WWI 2021
    #  777974044698869780,  # test
]
patryk_id = 654412645688016898
redirect_to_general_channel_ids = [
    # ustalenia-ważne
    846678662102515733,
]
# ogólny
general_channel_id = 846678318928625687

message_count = 0

typing_lock = asyncio.Lock()


# Who the fuck adds __slots__ without '__dict__' in public interface classes!!!1!1!1
@dataclass
class PrivateMessage:
    is_funny_message: bool = False
    was_resend_after_delete: bool = False

max_messages = 1000
private_message_cache = None


@client.event
async def on_ready():
    for guild in client.guilds:
        await ensure_guild_allowed(guild)

    global general_channel
    general_channel = client.get_channel(general_channel_id)

    global private_message_cache
    private_message_cache = OrderedDict()

    log.info('Ready.')

@client.event
async def on_guild_join(guild):
    log.debug('Joined new guild:', guild)

    await ensure_guild_allowed(guild)

@client.event
async def on_message(message):
    global message_count

    if not is_guild_allowed(message.guild):
        return

    if message.author == client.user:
        return

    if message.channel.id in redirect_to_general_channel_ids:
        channel = general_channel
    else:
        channel = message.channel

    message_count += 1
    if message_count >= 100:
        message_count = 0

        content = get_funny_message_content()

        log.debug('Sending funny message...')
        message = await send_message(channel, content)
        private_message = get_private_message(message)
        private_message.is_funny_message = True
        log.debug('Send funny message.')

@client.event
async def on_message_delete(message):
    if not is_guild_allowed(message.guild):
        return

    if message.author != client.user:
        return

    private_message = get_private_message(message)

    if not private_message.is_funny_message:
        return

    if message.channel.id in redirect_to_general_channel_ids:
        channel = general_channel
    else:
        channel = message.channel

    if private_message.was_resend_after_delete:
        content = message.content
        rere = 'Re-re'
    else:
        content = get_funny_resend_message_content(message)
        rere = 'Re'

    log.debug(f'{rere}sending funny message...')
    new_message = await send_message(channel, content)
    new_private_message = get_private_message(new_message)
    new_private_message.is_funny_message = True
    new_private_message.was_resend_after_delete = True
    log.debug(f'{rere}send funny message.')

def get_private_message(message):
    global private_message_cache
    if message.id not in private_message_cache:
        private_message_cache[message.id] = PrivateMessage()
        while len(private_message_cache) > max_messages:
            private_message_cache.popitem()
    return private_message_cache[message.id]

def is_guild_allowed(guild):
    return guild is not None and guild.id in allowed_guild_ids

async def ensure_guild_allowed(guild):
    if not is_guild_allowed(guild):
        await guild.leave()

async def send_message(channel, content):
    typing_time = get_typing_time()

    # channel.typing() context manager is buggy
    async with typing_lock:
        await channel.trigger_typing()
        await asyncio.sleep(typing_time)
        return await channel.send(content)

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
def get_funny_message_content():
    msg = random.choice(funny_messages)
    msg = mutate_sentence(msg)
    return msg

funny_resend_messages = [
    'a co to za cenzura',
    'w internecie nic nie ginie',
    'w internetach nic nie ginie',
]
def get_funny_resend_message_content(message):
    msg = random.choice(funny_resend_messages)
    msg = mutate_sentence(msg)
    msg += '\n'
    msg += cite_content(message.content)
    return msg

def random_chance(p):
    assert 0 <= p <= 1
    if p >= 1:
        return True
    if p <= 0:
        return False
    return random.uniform(0, 1) < p

def mutate_sentence(msg):
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
    return msg

def mutation_capitalize(msg):
    return msg.capitalize()

periods = '?!.'
def mutation_add_period(msg):
    if len(msg) < 1:
        return msg
    if msg[-1] in periods:
        return msg
    return msg + random.choice(periods)

def mutation_switch_period(msg):
    if len(msg) < 1:
        return msg
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
    if len(msg) < 1:
        return msg
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
    if len(msg) == 0:
        return f'<@{patryk_id}>'
    return f'<@{patryk_id}> {msg}'

def cite_content(msg):
    return '> ' + '\n> '.join(msg.split('\n'))


if __name__ == '__main__':
    import os
    log.info('Starting.')
    client.run(os.environ['DISCORD_TOKEN'])
