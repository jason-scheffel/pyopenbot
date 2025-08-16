import discord
from discord.ext import commands
from pyopenbot.platforms.base_platform import BasePlatform
from pyopenbot.llm_service import LLMService
from pyopenbot.memory import Memory
from typing import Dict, List, Optional
from rich.console import Console
import asyncio


class DiscordPlatform(BasePlatform):
    """Discord platform implementation for PyOpenBot"""
    
    DISCORD_CONTEXT_PROMPT = """
[Discord Context]
You're in a Discord chat. Messages marked [username - PENDING] arrived while you were typing your response.
Respond naturally - don't mention "pending" or "I can see" - just respond as a human would who noticed new messages while typing.

Examples:
- If someone asks "what's 2+2?" and then says "never mind, it's 4" → Reply: "Yep, you got it!" (not "I can see you said 4")
- If someone asks "what number am I thinking?" and then says "7" → Reply: "7, apparently!" (not "I can see in pending you said 7")

IMPORTANT: You don't need to respond to every message. Your decision to respond should be based on:
1. Your character/personality (as defined in your character card)
2. Whether the message is relevant to you
3. Whether a response would be helpful or natural

If you choose not to respond, simply reply with: [NO_RESPONSE]

When to use [NO_RESPONSE]:
- When your character wouldn't naturally respond (e.g., a shy character might not jump into every conversation)
- When the message is casual chat between others that doesn't involve you
- When silence would be more appropriate than speaking
- When you've been talking too much and should let others converse

Remember: Stay in character. An enthusiastic assistant might respond often, while a reserved character might be selective.
Be natural. Be human. Don't explain your message reading process."""
    
    def __init__(self, character, llm_service: LLMService, memory: Memory):
        self.character = character
        self.llm_service = llm_service
        self.memory = memory
        self.console = Console()
        self.message_queue = asyncio.Queue()
        self.processing_task = None
        
        intents = discord.Intents.default()
        intents.message_content = True
        self.bot = commands.Bot(command_prefix='/', intents=intents)
        self._setup_events()
        self._setup_commands()
    
    def _setup_events(self):
        
        @self.bot.event
        async def on_ready():
            self.console.print(f'[green]✓ {self.bot.user} connected to Discord![/green]')
            self.console.print(f'[cyan]Bot is in {len(self.bot.guilds)} servers[/cyan]')
            # Start the message processing task
            if not self.processing_task:
                self.processing_task = asyncio.create_task(self.process_message_queue())
        
        @self.bot.event
        async def on_message(message: discord.Message):
            # Ignore bot's own messages
            if message.author == self.bot.user:
                return
            
            # Process commands
            if message.content.startswith('/'):
                await self.bot.process_commands(message)
                return
            
            # Check if we should respond to this message
            if self._should_respond(message):
                await self.message_queue.put(message)
    
    def _setup_commands(self):
        
        @self.bot.command(name='clear', help='Clear conversation memory')
        async def clear_memory(ctx):
            await self._cmd_clear_memory(ctx)
        
        @self.bot.command(name='stats', help='Show session statistics')
        async def show_stats(ctx):
            await self._cmd_show_stats(ctx)
        
        @self.bot.command(name='system', help='Show system prompt')
        async def show_system(ctx):
            await self._cmd_show_system(ctx)
        
        @self.bot.command(name='history', help='Show conversation history sent to model')
        async def show_history(ctx):
            await self._cmd_show_history(ctx)
        
        @self.bot.command(name='config', help='Show current configuration')
        async def show_config(ctx):
            await self._cmd_show_config(ctx)
        
        @self.bot.command(name='resume', help='Resume previous conversation by loading N messages')
        async def resume_conversation(ctx, count: int):
            await self._cmd_resume(ctx, count)
    
    def _should_respond(self, message: discord.Message) -> bool:
        if self.character.discord_channel_id:
            return str(message.channel.id) == str(self.character.discord_channel_id)
        return False
    
    def _clean_message_content(self, message: discord.Message) -> str:
        """Clean message content by removing bot mentions"""
        content = message.content.replace(f'<@{self.bot.user.id}>', '').strip()
        return content if content else "Hello"
    
    def _format_pending_message(self, message: discord.Message) -> Dict[str, str]:
        """Format a message as a pending message for LLM context"""
        content = self._clean_message_content(message)
        username = message.author.name
        return {
            "role": "user",
            "content": f"[{username} - PENDING]: {content}"
        }
    
    async def _get_pending_messages(self) -> tuple[List[Dict], List[discord.Message]]:
        """Get pending messages from queue without removing them"""
        pending_messages = []
        temp_queue = []
        
        while not self.message_queue.empty():
            try:
                pending_msg = self.message_queue.get_nowait()
                temp_queue.append(pending_msg)
                pending_messages.append(self._format_pending_message(pending_msg))
            except asyncio.QueueEmpty:
                break
        
        # Put messages back in queue
        for msg in temp_queue:
            await self.message_queue.put(msg)
        
        return pending_messages, temp_queue
    
    def _build_enhanced_system_prompt(self) -> str:
        return f"{self.character.character_card}\n{self.DISCORD_CONTEXT_PROMPT}"
    
    def _build_llm_context(self, content: str, username: str, pending_messages: List[Dict]) -> List[Dict]:
        """Build the complete message context for the LLM"""
        response_indicator = f"[System]: Now responding to {username}'s message: \"{content}\""
        
        return [
            {"role": "system", "content": self._build_enhanced_system_prompt()},
            *self.memory.get_messages(),
            *pending_messages,
            {"role": "system", "content": response_indicator}
        ]
    
    async def process_single_message(self, message: discord.Message):
        """Process a single Discord message"""
        content = self._clean_message_content(message)
        username = message.author.name
        
        self.memory.add_message("user", f"[{username}]: {content}")
        
        pending_messages, _ = await self._get_pending_messages()
        
        llm_messages = self._build_llm_context(content, username, pending_messages)
        
        async with message.channel.typing():
            response, usage = self.llm_service.get_response(
                f"[System]: Now responding to {username}'s message: \"{content}\"",
                llm_messages
            )
        
        bot_name = self.bot.user.name if self.bot.user else "assistant"
        
        # Check if bot chose not to respond
        if response.strip() == "[NO_RESPONSE]":
            self.memory.add_message("assistant", f"[{bot_name}]: [NO_RESPONSE]")
            if usage:
                self.memory.add_usage(usage)
            self.console.print(f"[dim]{bot_name} chose not to respond to {username}[/dim]")
            return
        
        # Normal response
        self.memory.add_message("assistant", f"[{bot_name}]: {response}")
        if usage:
            self.memory.add_usage(usage)
        
        await message.reply(response)
        
        if usage and usage.get('cost') is not None:
            self.console.print(
                f"[dim]Discord response to {username} - "
                f"Cost: ${usage['cost']:.6f} | "
                f"Tokens: {usage.get('total_tokens', 0)}[/dim]"
            )
    
    async def process_message_queue(self):
        """Process messages from the queue sequentially"""
        while True:
            try:
                message = await self.message_queue.get()
                await self.process_single_message(message)
            except Exception as e:
                self.console.print(f"[red]Error processing message: {e}[/red]")
    
    # Command implementations
    async def _cmd_clear_memory(self, ctx):
        self.memory.clear()
        await ctx.send("✅ Memory cleared!")
    
    async def _cmd_show_stats(self, ctx):
        stats = self.memory.get_stats()
        embed = discord.Embed(title="Session Statistics", color=0x00ff00)
        embed.add_field(name="Messages", value=str(stats["message_count"]), inline=True)
        embed.add_field(name="Total Cost", value=f"${stats['total_cost']:.6f}", inline=True)
        embed.add_field(name="Total Tokens", value=str(stats["total_tokens"]), inline=True)
        embed.add_field(name="Prompt Tokens", value=str(stats["prompt_tokens"]), inline=True)
        embed.add_field(name="Completion Tokens", value=str(stats["completion_tokens"]), inline=True)
        embed.add_field(name="Context Usage", value=stats["context_usage"], inline=True)
        await ctx.send(embed=embed)
    
    async def _cmd_show_system(self, ctx):
        """Show system prompt"""
        system_prompt = self.character.character_card
        # Discord has a 4096 char limit for embed descriptions
        if len(system_prompt) > 4096:
            system_prompt = system_prompt[:4093] + "..."
        
        embed = discord.Embed(
            title="System Prompt",
            description=system_prompt,
            color=0x0099ff
        )
        await ctx.send(embed=embed)
    
    async def _cmd_show_history(self, ctx):
        enhanced_prompt = self._build_enhanced_system_prompt()
        messages = self.memory.get_messages()
        
        full_messages = [
            {"role": "system", "content": enhanced_prompt},
            *messages
        ]
        
        history_text = ""
        for msg in full_messages:
            role = msg['role'].upper()
            content = msg['content']
            if len(content) > 400:
                content = content[:397] + "..."
            history_text += f"**{role}**: {content}\n\n"
        
        if len(history_text) > 1900:
            history_text = history_text[:1897] + "..."
        
        embed = discord.Embed(
            title="Conversation History (sent to model)",
            description=history_text if history_text else "No messages yet",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    async def _cmd_show_config(self, ctx):
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
    
    async def _cmd_resume(self, ctx, count: int):
        self.memory.clear()
        
        messages_added = 0
        messages_skipped = 0
        conversation_messages = []
        
        async for message in ctx.channel.history(limit=count):
            if message.content.startswith('/'):
                messages_skipped += 1
                continue
            if message.embeds and message.author == self.bot.user:
                messages_skipped += 1
                continue
            
            conversation_messages.append(message)
        
        conversation_messages.reverse()
        
        for message in conversation_messages:
            if message.author == self.bot.user:
                bot_name = message.author.name
                self.memory.add_message("assistant", f"[{bot_name}]: {message.content}")
            else:
                username = message.author.name
                content = self._clean_message_content(message)
                self.memory.add_message("user", f"[{username}]: {content}")
            messages_added += 1
        
        total_processed = messages_added + messages_skipped
        await ctx.send(f"✅ Restored {messages_added} messages to memory (skipped {messages_skipped} commands/embeds, processed {total_processed}/{count} total)")
    
    def run(self, token: str):
        self.bot.run(token)
    
    def send_message(self, message: str):
        """Send message stub - not used in Discord platform"""
        pass