#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ Admin Panel Module
لوحة تحكم الأدمن مع الإحصائيات والإدارة
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Optional, List, Dict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# ملف قاعدة البيانات
DATA_FILE = "admin_data.json"

# قائمة الأدمن
ADMIN_IDS = [7627857345, 962731079]

def load_data() -> dict:
    """تحميل البيانات من الملف"""
    default_data = {
        "admins": ADMIN_IDS,
        "banned_users": [],
        "force_channels": [],
        "stats": {
            "total_users": 0,
            "total_commands": 0,
            "commands_today": 0,
            "last_reset": str(datetime.now().date()),
            "command_stats": {},
            "users_list": []
        }
    }
    
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # تحديث الأدمن دائماً
                data["admins"] = ADMIN_IDS
                return data
    except:
        pass
    
    save_data(default_data)
    return default_data


def save_data(data: dict):
    """حفظ البيانات إلى الملف"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving data: {e}")


def is_admin(user_id: int) -> bool:
    """التحقق إذا كان المستخدم أدمن"""
    return user_id in ADMIN_IDS


def is_banned(user_id: int) -> bool:
    """التحقق إذا كان المستخدم محظور"""
    data = load_data()
    return user_id in data.get("banned_users", [])


def get_force_channels() -> List[str]:
    """الحصول على قنوات الاشتراك الإجباري"""
    data = load_data()
    return data.get("force_channels", [])


def add_user(user_id: int, username: str = None):
    """إضافة مستخدم جديد للإحصائيات"""
    data = load_data()
    users_list = data["stats"].get("users_list", [])
    
    user_info = {"id": user_id, "username": username, "joined": str(datetime.now())}
    
    # تحقق إذا المستخدم موجود
    existing_ids = [u.get("id") for u in users_list]
    if user_id not in existing_ids:
        users_list.append(user_info)
        data["stats"]["users_list"] = users_list
        data["stats"]["total_users"] = len(users_list)
        save_data(data)


def increment_command(command_name: str):
    """زيادة عداد الأوامر"""
    data = load_data()
    
    # إعادة تعيين الإحصائيات اليومية
    today = str(datetime.now().date())
    if data["stats"].get("last_reset") != today:
        data["stats"]["commands_today"] = 0
        data["stats"]["last_reset"] = today
    
    data["stats"]["total_commands"] += 1
    data["stats"]["commands_today"] += 1
    
    # إحصائيات كل أمر
    cmd_stats = data["stats"].get("command_stats", {})
    cmd_stats[command_name] = cmd_stats.get(command_name, 0) + 1
    data["stats"]["command_stats"] = cmd_stats
    
    save_data(data)


async def check_subscription(bot, user_id: int) -> tuple:
    """التحقق من اشتراك المستخدم في القنوات الإجبارية
    يرجع: (مشترك, قائمة_القنوات_غير_مشترك_فيها)
    """
    channels = get_force_channels()
    if not channels:
        return (True, [])
    
    not_subscribed = []
    
    for channel in channels:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ['left', 'kicked']:
                not_subscribed.append(channel)
        except Exception as e:
            # إذا فشل التحقق، نعتبره غير مشترك
            not_subscribed.append(channel)
    
    return (len(not_subscribed) == 0, not_subscribed)


def get_subscription_keyboard(channels: List[str]) -> InlineKeyboardMarkup:
    """إنشاء لوحة مفاتيح للاشتراك في القنوات"""
    keyboard = []
    
    for i, channel in enumerate(channels):
        channel_name = channel.replace("@", "")
        keyboard.append([
            InlineKeyboardButton(f"📢 اشترك في القناة {i+1}", url=f"https://t.me/{channel_name}")
        ])
    
    keyboard.append([
        InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_subscription")
    ])
    
    return InlineKeyboardMarkup(keyboard)


# ===== أوامر الأدمن =====

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """لوحة تحكم الأدمن الرئيسية"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ هذا الأمر للأدمن فقط!")
        return
    
    keyboard = [
        [
            InlineKeyboardButton("📊 الإحصائيات", callback_data="admin_stats"),
            InlineKeyboardButton("👥 المستخدمين", callback_data="admin_users"),
        ],
        [
            InlineKeyboardButton("📢 إذاعة", callback_data="admin_broadcast"),
            InlineKeyboardButton("🚫 الحظر", callback_data="admin_ban_menu"),
        ],
        [
            InlineKeyboardButton("📺 قنوات الاشتراك", callback_data="admin_channels"),
            InlineKeyboardButton("⚙️ الإعدادات", callback_data="admin_settings"),
        ],
    ]
    
    text = """
🛡️ *لوحة تحكم الأدمن*

مرحباً بك في لوحة التحكم!
اختر من القائمة أدناه:

👤 *الأدمن:*
"""
    for admin_id in ADMIN_IDS:
        text += f"• `{admin_id}`\n"
    
    await update.message.reply_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض الإحصائيات"""
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        await query.answer("❌ للأدمن فقط!", show_alert=True)
        return
    
    data = load_data()
    stats = data.get("stats", {})
    
    # أكثر الأوامر استخداماً
    cmd_stats = stats.get("command_stats", {})
    sorted_cmds = sorted(cmd_stats.items(), key=lambda x: x[1], reverse=True)[:10]
    
    text = f"""
📊 *إحصائيات البوت*

👥 *المستخدمين:* {stats.get('total_users', 0)}
📝 *إجمالي الأوامر:* {stats.get('total_commands', 0)}
📅 *أوامر اليوم:* {stats.get('commands_today', 0)}
🚫 *المحظورين:* {len(data.get('banned_users', []))}
📺 *قنوات الاشتراك:* {len(data.get('force_channels', []))}

📈 *أكثر الأوامر استخداماً:*
"""
    
    for cmd, count in sorted_cmds:
        text += f"• `/{cmd}`: {count}\n"
    
    if not sorted_cmds:
        text += "لا توجد إحصائيات بعد\n"
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="admin_back")]]
    
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def admin_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض قائمة المستخدمين"""
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        return
    
    data = load_data()
    users = data["stats"].get("users_list", [])[-20:]  # آخر 20 مستخدم
    
    text = f"👥 *آخر المستخدمين* ({len(data['stats'].get('users_list', []))} إجمالي)\n\n"
    
    for user in reversed(users):
        username = user.get("username") or "بدون اسم"
        text += f"• `{user.get('id')}` - @{username}\n"
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="admin_back")]]
    
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def admin_channels_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """قائمة إدارة قنوات الاشتراك"""
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        return
    
    data = load_data()
    channels = data.get("force_channels", [])
    
    text = "📺 *قنوات الاشتراك الإجباري*\n\n"
    
    if channels:
        for i, ch in enumerate(channels, 1):
            text += f"{i}. {ch}\n"
    else:
        text += "لا توجد قنوات مضافة\n"
    
    text += "\n*الأوامر:*\n"
    text += "`/addchannel @username` - إضافة قناة\n"
    text += "`/removechannel @username` - إزالة قناة\n"
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="admin_back")]]
    
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def admin_ban_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """قائمة إدارة الحظر"""
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        return
    
    data = load_data()
    banned = data.get("banned_users", [])
    
    text = f"🚫 *إدارة الحظر* ({len(banned)} محظور)\n\n"
    
    if banned:
        for user_id in banned[:20]:
            text += f"• `{user_id}`\n"
        if len(banned) > 20:
            text += f"... و {len(banned) - 20} آخرين\n"
    else:
        text += "لا يوجد مستخدمين محظورين\n"
    
    text += "\n*الأوامر:*\n"
    text += "`/ban user_id` - حظر مستخدم\n"
    text += "`/unban user_id` - فك حظر مستخدم\n"
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="admin_back")]]
    
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def admin_broadcast_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """قائمة الإذاعة"""
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        return
    
    data = load_data()
    total_users = len(data["stats"].get("users_list", []))
    
    text = f"""
📢 *الإذاعة*

👥 سيتم إرسال الرسالة إلى: {total_users} مستخدم

*طريقة الاستخدام:*
`/broadcast رسالتك هنا`

*مثال:*
`/broadcast مرحباً! هذا تحديث جديد للبوت 🎉`

⚠️ *تنبيه:* الإذاعة قد تستغرق بعض الوقت
"""
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="admin_back")]]
    
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def admin_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """العودة للوحة التحكم"""
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        return
    
    keyboard = [
        [
            InlineKeyboardButton("📊 الإحصائيات", callback_data="admin_stats"),
            InlineKeyboardButton("👥 المستخدمين", callback_data="admin_users"),
        ],
        [
            InlineKeyboardButton("📢 إذاعة", callback_data="admin_broadcast"),
            InlineKeyboardButton("🚫 الحظر", callback_data="admin_ban_menu"),
        ],
        [
            InlineKeyboardButton("📺 قنوات الاشتراك", callback_data="admin_channels"),
            InlineKeyboardButton("⚙️ الإعدادات", callback_data="admin_settings"),
        ],
    ]
    
    text = """
🛡️ *لوحة تحكم الأدمن*

مرحباً بك في لوحة التحكم!
اختر من القائمة أدناه:
"""
    
    await query.edit_message_text(
        text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ===== أوامر الأدمن النصية =====

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """حظر مستخدم"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ هذا الأمر للأدمن فقط!")
        return
    
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال ID المستخدم\nمثال: `/ban 123456789`", parse_mode='Markdown')
        return
    
    try:
        user_id = int(context.args[0])
    except:
        await update.message.reply_text("❌ ID غير صالح!")
        return
    
    if user_id in ADMIN_IDS:
        await update.message.reply_text("❌ لا يمكن حظر الأدمن!")
        return
    
    data = load_data()
    if user_id not in data["banned_users"]:
        data["banned_users"].append(user_id)
        save_data(data)
        await update.message.reply_text(f"✅ تم حظر المستخدم: `{user_id}`", parse_mode='Markdown')
    else:
        await update.message.reply_text("⚠️ المستخدم محظور بالفعل!")


async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """فك حظر مستخدم"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ هذا الأمر للأدمن فقط!")
        return
    
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال ID المستخدم\nمثال: `/unban 123456789`", parse_mode='Markdown')
        return
    
    try:
        user_id = int(context.args[0])
    except:
        await update.message.reply_text("❌ ID غير صالح!")
        return
    
    data = load_data()
    if user_id in data["banned_users"]:
        data["banned_users"].remove(user_id)
        save_data(data)
        await update.message.reply_text(f"✅ تم فك حظر المستخدم: `{user_id}`", parse_mode='Markdown')
    else:
        await update.message.reply_text("⚠️ المستخدم غير محظور!")


async def add_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إضافة قناة اشتراك إجباري"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ هذا الأمر للأدمن فقط!")
        return
    
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال اسم القناة\nمثال: `/addchannel @channel_name`", parse_mode='Markdown')
        return
    
    channel = context.args[0]
    if not channel.startswith("@"):
        channel = "@" + channel
    
    data = load_data()
    if channel not in data["force_channels"]:
        data["force_channels"].append(channel)
        save_data(data)
        await update.message.reply_text(f"✅ تم إضافة القناة: {channel}", parse_mode='Markdown')
    else:
        await update.message.reply_text("⚠️ القناة مضافة بالفعل!")


async def remove_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إزالة قناة اشتراك إجباري"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ هذا الأمر للأدمن فقط!")
        return
    
    if not context.args:
        await update.message.reply_text("❌ يرجى إدخال اسم القناة\nمثال: `/removechannel @channel_name`", parse_mode='Markdown')
        return
    
    channel = context.args[0]
    if not channel.startswith("@"):
        channel = "@" + channel
    
    data = load_data()
    if channel in data["force_channels"]:
        data["force_channels"].remove(channel)
        save_data(data)
        await update.message.reply_text(f"✅ تم إزالة القناة: {channel}", parse_mode='Markdown')
    else:
        await update.message.reply_text("⚠️ القناة غير موجودة!")


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إذاعة رسالة لجميع المستخدمين"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ هذا الأمر للأدمن فقط!")
        return
    
    if not context.args:
        await update.message.reply_text("❌ يرجى كتابة الرسالة\nمثال: `/broadcast مرحباً بالجميع!`", parse_mode='Markdown')
        return
    
    message = " ".join(context.args)
    data = load_data()
    users = data["stats"].get("users_list", [])
    
    if not users:
        await update.message.reply_text("❌ لا يوجد مستخدمين!")
        return
    
    status_msg = await update.message.reply_text(f"📤 جاري الإرسال إلى {len(users)} مستخدم...")
    
    success = 0
    failed = 0
    
    for user in users:
        try:
            user_id = user.get("id")
            if user_id:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"📢 *رسالة من الإدارة:*\n\n{message}",
                    parse_mode='Markdown'
                )
                success += 1
                await asyncio.sleep(0.05)  # تأخير لتجنب حدود Telegram
        except Exception as e:
            failed += 1
    
    await status_msg.edit_text(
        f"✅ *تم الإرسال!*\n\n"
        f"📨 نجح: {success}\n"
        f"❌ فشل: {failed}",
        parse_mode='Markdown'
    )


async def get_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض الإحصائيات كأمر"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ هذا الأمر للأدمن فقط!")
        return
    
    data = load_data()
    stats = data.get("stats", {})
    
    text = f"""
📊 *إحصائيات البوت*

👥 المستخدمين: {stats.get('total_users', 0)}
📝 إجمالي الأوامر: {stats.get('total_commands', 0)}
📅 أوامر اليوم: {stats.get('commands_today', 0)}
🚫 المحظورين: {len(data.get('banned_users', []))}
📺 قنوات الاشتراك: {len(data.get('force_channels', []))}
"""
    
    await update.message.reply_text(text, parse_mode='Markdown')
