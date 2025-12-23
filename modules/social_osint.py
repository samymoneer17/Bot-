#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📱 Social Media OSINT Module
أدوات البحث في السوشيال ميديا
"""

import os
import aiohttp
import asyncio
import re

try:
    from instascrape import Profile, Hashtag
    INSTASCRAPE_AVAILABLE = True
except ImportError:
    INSTASCRAPE_AVAILABLE = False


async def facebook_osint(username: str) -> str:
    """جلب معلومات صفحة فيسبوك باستخدام Web Scraping"""
    
    try:
        fb_url = f"https://www.facebook.com/{username}"
        
        # محاولة جلب البيانات باستخدام requests
        async with aiohttp.ClientSession() as session:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            try:
                async with session.get(fb_url, headers=headers, timeout=10) as response:
                    if response.status == 200:
                        html = await response.text()
                        
                        # استخراج البيانات من HTML
                        text = f"📘 معلومات فيسبوك: {username}\n"
                        text += "=" * 35 + "\n\n"
                        
                        # محاولة استخراج معلومات من meta tags
                        if 'profile_owner_id' in html or 'id=' in html:
                            text += "✅ الحساب موجود\n"
                            text += f"🌐 الرابط: {fb_url}\n"
                        else:
                            text += "❌ الحساب غير موجود أو خاص\n"
                        
                        return text
                    else:
                        return f"❌ خطأ في الوصول: {response.status}"
            except asyncio.TimeoutError:
                return "❌ انتهت مهلة الاتصال"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"


async def instagram_osint(username: str) -> str:
    """استخراج معلومات حساب انستجرام باستخدام RapidAPI أو Web Scraping كخيار احتياطي"""
    
    rapidapi_key = os.getenv('RAPIDAPI_KEY')
    
    # محاولة استخدام RapidAPI إذا كان المفتاح متوفراً
    if rapidapi_key:
        url = "https://instagram-data1.p.rapidapi.com/user/info"
        querystring = {"username": username}
        headers = {
            "X-RapidAPI-Key": rapidapi_key,
            "X-RapidAPI-Host": "instagram-data1.p.rapidapi.com"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=querystring, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        user_data = data.get('data', {})
                        
                        text = f"📸 معلومات انستجرام (RapidAPI): {username}\n"
                        text += "=" * 35 + "\n\n"
                        text += f"👤 الاسم: {user_data.get('full_name', 'غير معروف')}\n"
                        text += f"👥 المتابعون: {user_data.get('follower_count', 0):,}\n"
                        text += f"👉 يتابع: {user_data.get('following_count', 0):,}\n"
                        text += f"📷 المنشورات: {user_data.get('media_count', 0):,}\n"
                        if user_data.get('biography'):
                            text += f"📝 السيرة: {user_data.get('biography')}\n"
                        text += f"🌐 الرابط: https://www.instagram.com/{username}/\n"
                        return text
        except Exception:
            pass # الانتقال للخيار الاحتياطي في حال فشل API

    # الخيار الاحتياطي: Web Scraping
    try:
        ig_url = f"https://www.instagram.com/{username}/"
        async with aiohttp.ClientSession() as session:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            }
            async with session.get(ig_url, headers=headers, timeout=15) as response:
                if response.status == 200:
                    html = await response.text()
                    text = f"📸 معلومات انستجرام: {username}\n"
                    text += "=" * 35 + "\n\n"
                    
                    description_match = re.search(r'<meta name="description" content="([^"]*)"', html)
                    if description_match:
                        text += f"📝 ملخص: {description_match.group(1)}\n"
                    
                    title_match = re.search(r'<meta property="og:title" content="([^"]*)"', html)
                    if title_match:
                        title = title_match.group(1).split(' • ')[0]
                        text += f"👤 الاسم: {title}\n"

                    text += f"🌐 الرابط: {ig_url}\n"
                    return text
                elif response.status == 429:
                    return "❌ خطأ (429): تم حظر الطلب مؤقتاً من إنستجرام. يرجى إضافة مفتاح RAPIDAPI_KEY في الإعدادات لتجنب هذه المشكلة."
                else:
                    return f"❌ خطأ في الوصول ({response.status}): قد يكون الحساب خاصاً أو تم حظر الطلب"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"


async def twitter_history(username: str) -> str:
    """عرض تاريخ أسماء المستخدم على X/Twitter"""
    
    url = f"https://api.memory.lol/v1/tw/{username}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    text = f"🐦 *تاريخ أسماء X/Twitter:* `{username}`\n\n"
                    
                    accounts = data.get("accounts", [])
                    
                    if accounts:
                        for account in accounts:
                            text += f"🆔 *ID:* {account.get('id_str', 'غير معروف')}\n\n"
                            text += "*أسماء المستخدم:*\n"
                            
                            screen_names = account.get("screen_names", {})
                            for name, dates in screen_names.items():
                                dates_str = ", ".join(dates)
                                text += f"  • `{name}`: {dates_str}\n"
                    else:
                        text += "❌ لم يتم العثور على تاريخ"
                    
                    return text
                else:
                    return f"❌ خطأ في الاتصال: {response.status}"
    except asyncio.TimeoutError:
        return "❌ انتهت مهلة الاتصال"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"
