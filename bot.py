#!/usr/bin/env python3

import os
import random
import string

import discord


client = discord.Client()

message_count = 0


@client.event
async def on_ready():
    global guild

    guild = client.get_guild(846678318928625684)

@client.event
async def on_message(message):
    global message_count

    if message.author == client.user:
        return

    message_count += 1
    if message_count == 30:
        message_count = 0
        await message.channel.send(get_funny_message())

funny_messages = [
    'mogę admina?',
    'poproszę admina',
    'nk doda boty',
]
def get_funny_message():
    from random import choice, randrange

    msg = choice(funny_messages)
    if randrange(2) == 0:
        msg = mutation_capitalize(msg)
    if randrange(2) == 0:
        msg = mutation_add_period(msg)
    while randrange(20) == 0:
        msg = mutation_swap(msg)
    if randrange(20) == 0:
        msg = mutation_switch_period(msg)
    while randrange(30) == 0:
        msg = mutation_switch_letter()
    while randrange(25) == 0:
            msg = mutation_skip_char()
    return msg

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

letters = frozenset(string.ascii_letters)
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


if __name__ == '__main__':
    client.run(os.environ['DISCORD_TOKEN'])
