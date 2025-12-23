#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
👤 Username OSINT Module
البحث المحسن عن أسماء المستخدمين في 50+ منصة
"""

import aiohttp
import asyncio
import json


SOCIAL_PLATFORMS = {
    "GitHub": {
        "url": "https://api.github.com/users/{username}",
        "error_type": "status_code",
        "emoji": "💻"
    },
    "Instagram": {
        "url": "https://www.instagram.com/{username}/",
        "error_type": "status_code",
        "emoji": "📸"
    },
    "X/Twitter": {
        "url": "https://x.com/{username}",
        "error_type": "status_code",
        "emoji": "🐦"
    },
    "TikTok": {
        "url": "https://www.tiktok.com/@{username}",
        "error_type": "status_code",
        "emoji": "🎵"
    },
    "YouTube": {
        "url": "https://www.youtube.com/@{username}",
        "error_type": "status_code",
        "emoji": "📺"
    },
    "LinkedIn": {
        "url": "https://www.linkedin.com/in/{username}/",
        "error_type": "status_code",
        "emoji": "💼"
    },
    "Facebook": {
        "url": "https://www.facebook.com/{username}",
        "error_type": "status_code",
        "emoji": "📘"
    },
    "Reddit": {
        "url": "https://www.reddit.com/user/{username}",
        "error_type": "status_code",
        "emoji": "🤖"
    },
    "Pinterest": {
        "url": "https://www.pinterest.com/{username}/",
        "error_type": "status_code",
        "emoji": "📌"
    },
    "Telegram": {
        "url": "https://t.me/{username}",
        "error_type": "status_code",
        "emoji": "✈️"
    },
    "Twitch": {
        "url": "https://www.twitch.tv/{username}",
        "error_type": "status_code",
        "emoji": "🎮"
    },
    "Steam": {
        "url": "https://steamcommunity.com/id/{username}",
        "error_type": "status_code",
        "emoji": "🎮"
    },
    "Spotify": {
        "url": "https://open.spotify.com/user/{username}",
        "error_type": "status_code",
        "emoji": "🎧"
    },
    "SoundCloud": {
        "url": "https://soundcloud.com/{username}",
        "error_type": "status_code",
        "emoji": "🔊"
    },
    "Medium": {
        "url": "https://medium.com/@{username}",
        "error_type": "status_code",
        "emoji": "📝"
    },
    "DeviantArt": {
        "url": "https://www.deviantart.com/{username}",
        "error_type": "status_code",
        "emoji": "🎨"
    },
    "Behance": {
        "url": "https://www.behance.net/{username}",
        "error_type": "status_code",
        "emoji": "🎨"
    },
    "Dribbble": {
        "url": "https://dribbble.com/{username}",
        "error_type": "status_code",
        "emoji": "🏀"
    },
    "Flickr": {
        "url": "https://www.flickr.com/people/{username}",
        "error_type": "status_code",
        "emoji": "📷"
    },
    "Vimeo": {
        "url": "https://vimeo.com/{username}",
        "error_type": "status_code",
        "emoji": "🎬"
    },
    "Tumblr": {
        "url": "https://{username}.tumblr.com",
        "error_type": "status_code",
        "emoji": "📓"
    },
    "Snapchat": {
        "url": "https://www.snapchat.com/add/{username}",
        "error_type": "status_code",
        "emoji": "👻"
    },
    "Discord": {
        "url": "https://discord.com/users/{username}",
        "error_type": "status_code",
        "emoji": "💬"
    },
    "Patreon": {
        "url": "https://www.patreon.com/{username}",
        "error_type": "status_code",
        "emoji": "💰"
    },
    "Ko-fi": {
        "url": "https://ko-fi.com/{username}",
        "error_type": "status_code",
        "emoji": "☕"
    },
    "Linktree": {
        "url": "https://linktr.ee/{username}",
        "error_type": "status_code",
        "emoji": "🌳"
    },
    "GitLab": {
        "url": "https://gitlab.com/{username}",
        "error_type": "status_code",
        "emoji": "🦊"
    },
    "Bitbucket": {
        "url": "https://bitbucket.org/{username}/",
        "error_type": "status_code",
        "emoji": "🪣"
    },
    "StackOverflow": {
        "url": "https://stackoverflow.com/users/{username}",
        "error_type": "status_code",
        "emoji": "📚"
    },
    "HackerNews": {
        "url": "https://news.ycombinator.com/user?id={username}",
        "error_type": "status_code",
        "emoji": "📰"
    },
    "ProductHunt": {
        "url": "https://www.producthunt.com/@{username}",
        "error_type": "status_code",
        "emoji": "🚀"
    },
    "Keybase": {
        "url": "https://keybase.io/{username}",
        "error_type": "status_code",
        "emoji": "🔐"
    },
    "Mastodon": {
        "url": "https://mastodon.social/@{username}",
        "error_type": "status_code",
        "emoji": "🐘"
    },
    "Threads": {
        "url": "https://www.threads.net/@{username}",
        "error_type": "status_code",
        "emoji": "🧵"
    },
    "Quora": {
        "url": "https://www.quora.com/profile/{username}",
        "error_type": "status_code",
        "emoji": "❓"
    },
    "Gravatar": {
        "url": "https://gravatar.com/{username}",
        "error_type": "status_code",
        "emoji": "👤"
    },
    "About.me": {
        "url": "https://about.me/{username}",
        "error_type": "status_code",
        "emoji": "👋"
    },
    "Wattpad": {
        "url": "https://www.wattpad.com/user/{username}",
        "error_type": "status_code",
        "emoji": "📖"
    },
    "Goodreads": {
        "url": "https://www.goodreads.com/{username}",
        "error_type": "status_code",
        "emoji": "📚"
    },
    "Last.fm": {
        "url": "https://www.last.fm/user/{username}",
        "error_type": "status_code",
        "emoji": "🎵"
    },
    "Myspace": {
        "url": "https://myspace.com/{username}",
        "error_type": "status_code",
        "emoji": "🎤"
    },
    "VK": {
        "url": "https://vk.com/{username}",
        "error_type": "status_code",
        "emoji": "🔵"
    },
    "OK.ru": {
        "url": "https://ok.ru/{username}",
        "error_type": "status_code",
        "emoji": "🟠"
    },
    "Weibo": {
        "url": "https://weibo.com/{username}",
        "error_type": "status_code",
        "emoji": "🔴"
    },
    "Zhihu": {
        "url": "https://www.zhihu.com/people/{username}",
        "error_type": "status_code",
        "emoji": "📘"
    },
    "Clubhouse": {
        "url": "https://www.clubhouse.com/@{username}",
        "error_type": "status_code",
        "emoji": "🔊"
    },
    "Roblox": {
        "url": "https://www.roblox.com/users/profile?username={username}",
        "error_type": "status_code",
        "emoji": "🎮"
    },
    "Minecraft": {
        "url": "https://namemc.com/profile/{username}",
        "error_type": "status_code",
        "emoji": "⛏️"
    },
    "Xbox": {
        "url": "https://www.xboxgamertag.com/search/{username}",
        "error_type": "status_code",
        "emoji": "🎮"
    },
    "PSN": {
        "url": "https://psnprofiles.com/{username}",
        "error_type": "status_code",
        "emoji": "🎮"
    },
}


async def check_platform(session: aiohttp.ClientSession, platform: str, config: dict, username: str) -> dict:
    """فحص منصة واحدة"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    url = config['url'].format(username=username)
    emoji = config.get('emoji', '🔗')
    
    try:
        async with session.get(url, headers=headers, timeout=8, allow_redirects=True) as response:
            if response.status == 200:
                if platform == "GitHub":
                    try:
                        data = await response.json()
                        return {
                            "platform": platform,
                            "exists": True,
                            "url": url,
                            "emoji": emoji,
                            "extra": {
                                "name": data.get("name"),
                                "bio": data.get("bio"),
                                "followers": data.get("followers"),
                                "repos": data.get("public_repos"),
                                "avatar": data.get("avatar_url")
                            }
                        }
                    except:
                        pass
                
                text = await response.text()
                if 'not found' in text.lower() or 'doesn\'t exist' in text.lower():
                    return {"platform": platform, "exists": False, "emoji": emoji}
                
                return {
                    "platform": platform,
                    "exists": True,
                    "url": url,
                    "emoji": emoji
                }
            else:
                return {"platform": platform, "exists": False, "emoji": emoji}
    except asyncio.TimeoutError:
        return {"platform": platform, "exists": False, "error": "timeout", "emoji": emoji}
    except:
        return {"platform": platform, "exists": False, "error": True, "emoji": emoji}


async def username_search(username: str) -> str:
    """البحث عن اسم المستخدم في 50+ منصة"""
    
    username = username.strip().lstrip('@')
    
    text = f"👤 *البحث عن:* `{username}`\n\n"
    text += f"🔍 *جاري الفحص في {len(SOCIAL_PLATFORMS)} منصة...*\n\n"
    
    connector = aiohttp.TCPConnector(limit=20)
    timeout = aiohttp.ClientTimeout(total=30)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        tasks = [
            check_platform(session, platform, config, username)
            for platform, config in SOCIAL_PLATFORMS.items()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
    
    found = [r for r in results if isinstance(r, dict) and r.get("exists")]
    not_found = [r for r in results if isinstance(r, dict) and not r.get("exists") and not r.get("error")]
    errors = [r for r in results if isinstance(r, dict) and r.get("error")]
    
    if found:
        text = f"👤 *نتائج البحث عن:* `{username}`\n\n"
        text += f"✅ *تم العثور في {len(found)} منصة:*\n\n"
        
        for result in found:
            platform = result["platform"]
            url = result.get("url", "")
            emoji = result.get("emoji", "🔗")
            
            if platform == "GitHub" and result.get("extra"):
                extra = result["extra"]
                text += f"{emoji} *{platform}:*\n"
                text += f"   🔗 {url}\n"
                if extra.get("name"):
                    text += f"   👤 {extra['name']}\n"
                if extra.get("bio"):
                    bio = extra['bio'][:50] + "..." if len(extra['bio']) > 50 else extra['bio']
                    text += f"   📝 {bio}\n"
                if extra.get("followers"):
                    text += f"   👥 {extra['followers']:,} متابع\n"
                if extra.get("repos"):
                    text += f"   📁 {extra['repos']} مستودع\n"
                text += "\n"
            else:
                text += f"{emoji} *{platform}:*\n   🔗 {url}\n\n"
        
        text += f"\n━━━━━━━━━━━━━━━━━━━━━━\n"
        text += f"❌ *لم يتم العثور في:* {len(not_found)} منصة\n"
        if errors:
            text += f"⚠️ *أخطاء اتصال:* {len(errors)} منصة"
    else:
        text = f"👤 *نتائج البحث عن:* `{username}`\n\n"
        text += f"❌ لم يتم العثور على هذا المستخدم في أي من {len(SOCIAL_PLATFORMS)} منصة\n\n"
        text += "💡 *نصائح:*\n"
        text += "• تأكد من صحة اسم المستخدم\n"
        text += "• جرب أسماء مستخدمين مشابهة\n"
        text += "• بعض المنصات قد تحجب الوصول"
    
    return text


async def username_similar(username: str) -> str:
    """اقتراح أسماء مستخدمين مشابهة"""
    
    variations = [
        username,
        username + "_",
        "_" + username,
        username + "official",
        "official" + username,
        username + "real",
        "real" + username,
        username.replace("_", ""),
        username.replace("_", "."),
        username + "1",
        username + "123",
    ]
    
    text = f"💡 *اقتراحات لـ:* `{username}`\n\n"
    text += "*أسماء مستخدمين مشابهة:*\n"
    
    for var in variations[:8]:
        text += f"• `{var}`\n"
    
    text += f"\n🔍 *للبحث:* `/username [الاسم]`"
    
    return text
