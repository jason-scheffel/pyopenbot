import discord
from discord.ext import commands
from pyopenbot.platforms.base_platform import BasePlatform
from pyopenbot.llm_service import LLMService
from pyopenbot.memory import Memory
from typing import Dict
from rich.console import Console


class DiscordPlatform(BasePlatform):
    def __init__(self, character, llm_service: LLMService, memory: Memory):
        self.character = character
        self.llm_service = llm_service
        self.memory = memory
        self.console = Console()
        
        intents = discord.Intents.default()
        intents.message_content = True
        self.bot = commands.Bot(command_prefix='/', intents=intents)
        self.setup_events()
    
    def setup_events(self):
        @self.bot.event
        async def on_ready():
            self.console.print(f'[green]✓ {self.bot.user} connected to Discord![/green]')
            self.console.print(f'[cyan]Bot is in {len(self.bot.guilds)} servers[/cyan]')
        
        @self.bot.event
        async def on_message(message):
            # ignore bot's own messages
            if message.author == self.bot.user:
                return
            
            # don't add commands to memory
            if message.content.startswith('/'):
                await self.bot.process_commands(message)
                return
            
            should_respond = False
            
            if self.bot.user.mentioned_in(message):
                should_respond = True
            elif self.character.discord_channel_id and str(message.channel.id) == str(self.character.discord_channel_id):
                should_respond = True
            
            if should_respond:
                
                if content:
                    # Clean mention from message if present
                    content = message.content.replace(f'<@{self.bot.user.id}>', '').strip()
                
                user_identifier = f"{message.author.name}"
                self.memory.add_message("user", f"[{user_identifier}]: {content}")
                
                async with message.channel.typing():
                    response, usage = self.llm_service.get_response(
                        f"[{user_identifier}]: {content}", 
                        self.memory.get_messages()
                    )
                
                self.memory.add_message("assistant", response)
                
                if usage:
                    self.memory.add_usage(usage)
                
                await message.reply(response)
                

        # Slash commands (not added to memory)
        @self.bot.command(name='clear', help='Clear conversation memory')
        async def clear_memory(ctx):
            self.memory.clear()
            await ctx.send("✅ Memory cleared!")
        
        @self.bot.command(name='stats', help='Show session statistics')
        async def show_stats(ctx):
            stats = self.memory.get_stats()
            embed = discord.Embed(title="Session Statistics", color=0x00ff00)
            embed.add_field(name="Messages", value=str(stats["message_count"]), inline=True)
            embed.add_field(name="Total Cost", value=f"${stats['total_cost']:.6f}", inline=True)
            embed.add_field(name="Total Tokens", value=str(stats["total_tokens"]), inline=True)
            embed.add_field(name="Prompt Tokens", value=str(stats["prompt_tokens"]), inline=True)
            embed.add_field(name="Completion Tokens", value=str(stats["completion_tokens"]), inline=True)
            embed.add_field(name="Context Usage", value=stats["context_usage"], inline=True)
            await ctx.send(embed=embed)
        
        @self.bot.command(name='system', help='Show system prompt')
        async def show_system(ctx):
            # Discord has a 4096 char limit for embed descriptions
            system_prompt = self.character.character_card
            if len(system_prompt) > 4096:
                system_prompt = system_prompt[:1021] + "..."
            
            embed = discord.Embed(
                title="System Prompt", 
                description=system_prompt,
                color=0x0099ff
            )
            await ctx.send(embed=embed)
        
        @self.bot.command(name='history', help='Show conversation history sent to model')
        async def show_history(ctx):
            messages = self.memory.get_messages()
            
            full_messages = [
                {"role": "system", "content": self.character.character_card},
                *messages
            ]
            
            history_text = ""
            for msg in full_messages:
                role = msg['role'].upper()
                content = msg['content']
                if len(content) > 400:
                    content = content[:197] + "..."
                history_text += f"**{role}**: {content}\n\n"
            
            # Discord has a 2000 char limit for messages
            if len(history_text) > 1900:
                history_text = history_text[:1897] + "..."
            
            embed = discord.Embed(
                title="Conversation History (sent to model)", 
                description=history_text if history_text else "No messages yet",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
        
        @self.bot.command(name='config', help='Show current configuration')
        async def show_config(ctx):
            embed = discord.Embed(title="Bot Configuration", color=0x0099ff)
            embed.add_field(name="Character Name", value=self.character.character_name, inline=True)
            embed.add_field(name="Provider", value=self.character.llm_provider, inline=True)
            embed.add_field(name="Model", value=self.character.llm_model, inline=True)
            embed.add_field(name="Memory Type", value=self.character.memory_type, inline=True)
            embed.add_field(name="Temperature", value=str(self.character.settings.get('temperature', 'N/A')), inline=True)
            embed.add_field(name="Top-p", value=str(self.character.settings.get('top_p', 'N/A')), inline=True)
            embed.add_field(name="Max Tokens", value=str(self.character.settings.get('max_tokens', 'N/A')), inline=True)
            embed.add_field(name="Context Window", value=str(self.character.settings.get('context_window', 'N/A')), inline=True)
            embed.add_field(name="Platform", value=self.character.platform, inline=True)
            if self.character.discord_channel_id:
                embed.add_field(name="Channel ID", value=self.character.discord_channel_id, inline=True)
            await ctx.send(embed=embed)
    
    def run(self, token: str):
        self.bot.run(token)
    
    def send_message(self, message: str):
        pass