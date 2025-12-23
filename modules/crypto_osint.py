#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
💰 Crypto OSINT Module
أدوات البحث في العملات الرقمية - Bitcoin, TON, Ethereum, USDT
"""

import aiohttp
import asyncio
from datetime import datetime


def satoshi_to_btc(satoshi: int) -> float:
    """تحويل ساتوشي إلى بيتكوين"""
    return satoshi / 100000000


def wei_to_eth(wei: int) -> float:
    """تحويل Wei إلى Ethereum"""
    return wei / 1e18


def nanoton_to_ton(nanoton: int) -> float:
    """تحويل nanoTON إلى TON"""
    return nanoton / 1e9


async def bitcoin_wallet(address: str) -> str:
    """جلب معلومات محفظة Bitcoin"""
    
    url = f"https://blockchain.info/rawaddr/{address}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    text = f"💰 *معلومات محفظة Bitcoin*\n\n"
                    text += f"📍 *العنوان:* `{data.get('address', address)}`\n\n"
                    
                    balance_btc = satoshi_to_btc(data.get('final_balance', 0))
                    total_received = satoshi_to_btc(data.get('total_received', 0))
                    total_sent = satoshi_to_btc(data.get('total_sent', 0))
                    
                    text += f"💵 *الرصيد الحالي:* {balance_btc:.8f} BTC\n"
                    text += f"📊 *إجمالي المعاملات:* {data.get('n_tx', 0)}\n"
                    text += f"📥 *إجمالي المستلم:* {total_received:.8f} BTC\n"
                    text += f"📤 *إجمالي المرسل:* {total_sent:.8f} BTC\n"
                    
                    txs = data.get('txs', [])
                    if txs:
                        first_tx = txs[-1]
                        timestamp = first_tx.get('time', 0)
                        if timestamp:
                            date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                            text += f"\n📅 *أول معاملة:* {date}\n"
                        
                        last_tx = txs[0]
                        timestamp = last_tx.get('time', 0)
                        if timestamp:
                            date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                            text += f"📅 *آخر معاملة:* {date}\n"
                    
                    text += f"\n🔗 *رابط المتصفح:*\nhttps://www.blockchain.com/btc/address/{address}"
                    
                    return text
                elif response.status == 500:
                    return f"❌ عنوان المحفظة غير صالح أو غير موجود"
                else:
                    return f"❌ خطأ في الاتصال: {response.status}"
    except asyncio.TimeoutError:
        return "❌ انتهت مهلة الاتصال"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"


async def ton_wallet(address: str) -> str:
    """جلب معلومات محفظة TON"""
    
    url = f"https://toncenter.com/api/v2/getAddressInformation?address={address}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('ok'):
                        result = data.get('result', {})
                        
                        text = f"💎 *معلومات محفظة TON*\n\n"
                        text += f"📍 *العنوان:* `{address}`\n\n"
                        
                        balance_nano = int(result.get('balance', 0))
                        balance_ton = nanoton_to_ton(balance_nano)
                        
                        text += f"💵 *الرصيد:* {balance_ton:.4f} TON\n"
                        text += f"📊 *الحالة:* {result.get('state', 'غير معروف')}\n"
                        
                        if result.get('last_transaction_id'):
                            lt = result['last_transaction_id'].get('lt', '')
                            tx_hash = result['last_transaction_id'].get('hash', '')
                            text += f"🔗 *آخر معاملة:* `{tx_hash[:16]}...`\n"
                        
                        if result.get('code'):
                            text += f"📝 *نوع المحفظة:* عقد ذكي\n"
                        else:
                            text += f"📝 *نوع المحفظة:* محفظة عادية\n"
                        
                        text += f"\n🔗 *رابط المتصفح:*\nhttps://tonscan.org/address/{address}"
                        
                        return text
                    else:
                        return f"❌ عنوان TON غير صالح"
                else:
                    return f"❌ خطأ في الاتصال: {response.status}"
    except asyncio.TimeoutError:
        return "❌ انتهت مهلة الاتصال"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"


async def ton_transactions(address: str, limit: int = 10) -> str:
    """جلب معاملات محفظة TON"""
    
    url = f"https://toncenter.com/api/v2/getTransactions?address={address}&limit={limit}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('ok'):
                        transactions = data.get('result', [])
                        
                        text = f"💎 *معاملات TON:* `{address[:16]}...`\n\n"
                        
                        if transactions:
                            text += f"📊 *آخر {len(transactions)} معاملة:*\n\n"
                            
                            for i, tx in enumerate(transactions[:5], 1):
                                utime = tx.get('utime', 0)
                                date = datetime.fromtimestamp(utime).strftime('%Y-%m-%d %H:%M')
                                
                                in_msg = tx.get('in_msg', {})
                                out_msgs = tx.get('out_msgs', [])
                                
                                if in_msg.get('value'):
                                    value = nanoton_to_ton(int(in_msg.get('value', 0)))
                                    text += f"*{i}.* 📥 استلام: {value:.4f} TON\n"
                                    text += f"   📅 {date}\n"
                                    if in_msg.get('source'):
                                        text += f"   من: `{in_msg['source'][:20]}...`\n"
                                elif out_msgs:
                                    total_out = sum(int(m.get('value', 0)) for m in out_msgs)
                                    value = nanoton_to_ton(total_out)
                                    text += f"*{i}.* 📤 إرسال: {value:.4f} TON\n"
                                    text += f"   📅 {date}\n"
                                
                                text += "\n"
                        else:
                            text += "❌ لا توجد معاملات"
                        
                        return text
                    else:
                        return f"❌ عنوان TON غير صالح"
                else:
                    return f"❌ خطأ في الاتصال: {response.status}"
    except asyncio.TimeoutError:
        return "❌ انتهت مهلة الاتصال"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"


async def ethereum_wallet(address: str) -> str:
    """جلب معلومات محفظة Ethereum"""
    
    url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('status') == '1':
                        balance_wei = int(data.get('result', 0))
                        balance_eth = wei_to_eth(balance_wei)
                        
                        text = f"💠 *معلومات محفظة Ethereum*\n\n"
                        text += f"📍 *العنوان:* `{address}`\n\n"
                        text += f"💵 *الرصيد:* {balance_eth:.6f} ETH\n"
                        
                        tx_url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&page=1&offset=5&sort=desc"
                        
                        async with session.get(tx_url, timeout=30) as tx_response:
                            if tx_response.status == 200:
                                tx_data = await tx_response.json()
                                
                                if tx_data.get('status') == '1':
                                    txs = tx_data.get('result', [])
                                    text += f"📊 *عدد المعاملات:* {len(txs)}+\n"
                                    
                                    if txs:
                                        first_tx = txs[-1]
                                        last_tx = txs[0]
                                        
                                        if last_tx.get('timeStamp'):
                                            date = datetime.fromtimestamp(int(last_tx['timeStamp'])).strftime('%Y-%m-%d %H:%M')
                                            text += f"📅 *آخر معاملة:* {date}\n"
                        
                        text += f"\n🔗 *رابط المتصفح:*\nhttps://etherscan.io/address/{address}"
                        
                        return text
                    else:
                        return f"❌ عنوان Ethereum غير صالح: {data.get('message', '')}"
                else:
                    return f"❌ خطأ في الاتصال: {response.status}"
    except asyncio.TimeoutError:
        return "❌ انتهت مهلة الاتصال"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"


async def usdt_balance(address: str, network: str = "tron") -> str:
    """جلب رصيد USDT على شبكات مختلفة"""
    
    text = f"💵 *رصيد USDT*\n\n"
    text += f"📍 *العنوان:* `{address}`\n\n"
    
    if network.lower() == "tron" or address.startswith("T"):
        url = f"https://apilist.tronscanapi.com/api/account?address={address}"
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"TRON-PRO-API-KEY": ""}
                async with session.get(url, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        text += f"🔗 *الشبكة:* TRON (TRC20)\n"
                        
                        trx_balance = data.get('balance', 0) / 1e6
                        text += f"💎 *رصيد TRX:* {trx_balance:.4f}\n"
                        
                        tokens = data.get('trc20token_balances', [])
                        usdt_found = False
                        
                        for token in tokens:
                            if 'USDT' in token.get('tokenName', '').upper() or token.get('tokenAbbr', '').upper() == 'USDT':
                                decimals = int(token.get('tokenDecimal', 6))
                                balance = int(token.get('balance', 0)) / (10 ** decimals)
                                text += f"💵 *رصيد USDT:* {balance:.2f}\n"
                                usdt_found = True
                                break
                        
                        if not usdt_found:
                            text += f"💵 *رصيد USDT:* 0.00\n"
                        
                        text += f"\n🔗 *رابط المتصفح:*\nhttps://tronscan.org/#/address/{address}"
                        
                        return text
                    else:
                        return f"❌ خطأ في الاتصال: {response.status}"
        except asyncio.TimeoutError:
            return "❌ انتهت مهلة الاتصال"
        except Exception as e:
            return f"❌ خطأ: {str(e)}"
    
    elif network.lower() == "eth" or address.startswith("0x"):
        usdt_contract = "0xdac17f958d2ee523a2206206994597c13d831ec7"
        url = f"https://api.etherscan.io/api?module=account&action=tokenbalance&contractaddress={usdt_contract}&address={address}&tag=latest"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('status') == '1':
                            balance = int(data.get('result', 0)) / 1e6
                            
                            text += f"🔗 *الشبكة:* Ethereum (ERC20)\n"
                            text += f"💵 *رصيد USDT:* {balance:.2f}\n"
                            text += f"\n🔗 *رابط المتصفح:*\nhttps://etherscan.io/address/{address}"
                            
                            return text
                        else:
                            return f"❌ خطأ: {data.get('message', 'غير معروف')}"
                    else:
                        return f"❌ خطأ في الاتصال: {response.status}"
        except asyncio.TimeoutError:
            return "❌ انتهت مهلة الاتصال"
        except Exception as e:
            return f"❌ خطأ: {str(e)}"
    
    else:
        return "❌ الشبكة غير مدعومة. استخدم: tron أو eth"


async def crypto_price() -> str:
    """جلب أسعار العملات الرقمية الرئيسية"""
    
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,toncoin,tether,binancecoin,solana,ripple&vs_currencies=usd&include_24hr_change=true"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    text = "📊 *أسعار العملات الرقمية*\n\n"
                    
                    coins = {
                        'bitcoin': ('Bitcoin', 'BTC', '₿'),
                        'ethereum': ('Ethereum', 'ETH', '💠'),
                        'toncoin': ('TON', 'TON', '💎'),
                        'tether': ('Tether', 'USDT', '💵'),
                        'binancecoin': ('BNB', 'BNB', '🔶'),
                        'solana': ('Solana', 'SOL', '🟣'),
                        'ripple': ('XRP', 'XRP', '⚪')
                    }
                    
                    for coin_id, (name, symbol, emoji) in coins.items():
                        if coin_id in data:
                            price = data[coin_id].get('usd', 0)
                            change = data[coin_id].get('usd_24h_change', 0)
                            
                            change_emoji = "🟢" if change >= 0 else "🔴"
                            text += f"{emoji} *{name}* ({symbol})\n"
                            text += f"   💰 ${price:,.2f}\n"
                            text += f"   {change_emoji} {change:+.2f}% (24h)\n\n"
                    
                    return text
                else:
                    return f"❌ خطأ في الاتصال: {response.status}"
    except asyncio.TimeoutError:
        return "❌ انتهت مهلة الاتصال"
    except Exception as e:
        return f"❌ خطأ: {str(e)}"


async def multi_wallet_check(address: str) -> str:
    """فحص العنوان في عدة شبكات"""
    
    text = f"🔍 *فحص العنوان في عدة شبكات*\n\n"
    text += f"📍 *العنوان:* `{address}`\n\n"
    
    results = []
    
    if address.startswith("0x") and len(address) == 42:
        text += "🔗 *الشبكات المتوافقة:* Ethereum, BSC, Polygon\n\n"
        
        eth_result = await ethereum_wallet(address)
        results.append(("Ethereum", eth_result))
        
    elif address.startswith("T") and len(address) == 34:
        text += "🔗 *الشبكة:* TRON\n\n"
        
        tron_result = await usdt_balance(address, "tron")
        results.append(("TRON", tron_result))
        
    elif address.startswith("EQ") or address.startswith("UQ"):
        text += "🔗 *الشبكة:* TON\n\n"
        
        ton_result = await ton_wallet(address)
        results.append(("TON", ton_result))
        
    elif len(address) >= 26 and len(address) <= 35:
        if address.startswith("1") or address.startswith("3") or address.startswith("bc1"):
            text += "🔗 *الشبكة:* Bitcoin\n\n"
            
            btc_result = await bitcoin_wallet(address)
            results.append(("Bitcoin", btc_result))
    else:
        text += "❌ لم يتم التعرف على نوع العنوان\n"
        text += "\n*الأنواع المدعومة:*\n"
        text += "• Bitcoin (يبدأ بـ 1, 3, bc1)\n"
        text += "• Ethereum/BSC (يبدأ بـ 0x)\n"
        text += "• TON (يبدأ بـ EQ, UQ)\n"
        text += "• TRON (يبدأ بـ T)\n"
        return text
    
    for network, result in results:
        text += f"━━━ {network} ━━━\n"
        cleaned_result = result.replace("*", "").replace("`", "")
        for line in cleaned_result.split("\n")[2:]:
            if line.strip():
                text += f"{line}\n"
        text += "\n"
    
    return text
