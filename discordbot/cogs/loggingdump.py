import logging
import discord

class LoggingDump():
    
    def __init__(self, bot, channel_id):
        self.bot = bot
        self.channel_id = channel_id