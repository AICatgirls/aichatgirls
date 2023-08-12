import json
import discord

class Whitelist:
    def __init__(self, filename="whitelist.json"):
        self.filename = filename
        self.whitelist = self.load_whitelist()

    def load_whitelist(self):
        try:
            with open(self.filename, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_whitelist(self):
        with open(self.filename, "w") as f:
            json.dump(self.whitelist, f)

    def add_channel(self, channel_id):
        if channel_id not in self.whitelist:
            self.whitelist.append(channel_id)
            self.save_whitelist()

    def remove_channel(self, channel_id):
        if channel_id in self.whitelist:
            self.whitelist.remove(channel_id)
            self.save_whitelist()

    def is_channel_whitelisted(self, channel):
        return channel.id in self.whitelist or isinstance(channel, discord.DMChannel)
