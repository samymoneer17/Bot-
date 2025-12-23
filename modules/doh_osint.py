#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌐 DNS over HTTPS (DoH) Lookup Module
وحدة استخراج سجلات DNS باستخدام بروتوكول DoH
"""

import httpx
import logging

logger = logging.getLogger(__name__)

async def doh_lookup(domain: str) -> str:
    """جلب سجلات DNS باستخدام Google DoH"""
    try:
        url = "https://dns.google/resolve"
        params = {"name": domain, "type": "ANY"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()
            
        if "Answer" not in data:
            return "❌ لم يتم العثور على سجلات DNS لهذا النطاق."
            
        text = f"🌐 *سجلات DNS (DoH) لنطاق:* `{domain}`\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━\n"
        
        types = {
            1: "A",
            2: "NS",
            5: "CNAME",
            6: "SOA",
            12: "PTR",
            15: "MX",
            16: "TXT",
            28: "AAAA",
            33: "SRV",
            257: "CAA"
        }
        
        for answer in data["Answer"]:
            type_name = types.get(answer["type"], f"TYPE {answer['type']}")
            text += f"• *{type_name}:* `{answer['data']}`\n"
            
        return text
    except Exception as e:
        logger.error(f"Error in doh_lookup: {e}")
        return f"❌ خطأ أثناء فحص DoH: {str(e)}"
