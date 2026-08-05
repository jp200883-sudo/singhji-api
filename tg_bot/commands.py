# telegram/commands.py
import os
import logging
from datetime import datetime
from fastapi.concurrency import run_in_threadpool

from core.config import (
    GROQ_API_KEY, GEMINI_API_KEY, CEREBRAS_API_KEY, 
    AVAILABLE_KEYS, OPENWEATHER_API_KEY, MANDI_API_KEY, 
    MANDI_BASE_URL, ADMIN_USER_ID
)
from core.memory import _memory_save, _memory_get
from core.swarm import SMART_SWARM
from core.scheduler import USER_PREFERENCES, MASTER_SCHEDULER
from utils.helpers import _normalize_state, _calculate_tax
from tg_bot.helpers import send_message

logger = logging.getLogger(__name__)

# ==========================================
# HTTP CLIENT - GLOBAL
# ==========================================
HTTP_CLIENT = None

def set_http_client(client):
    global HTTP_CLIENT
    HTTP_CLIENT = client
    logger.info("✅ Telegram commands HTTP client set")

# ==========================================
# COMMAND HANDLER
# ==========================================
async def handle_command(chat_id, user_id, text):
    """सारे Telegram commands को handle करता है"""
    
    # ---- START ----
    if text == "/start":
        from utils.helpers import MAIN_KEYBOARD
        welcome = (
            "🌅 Welcome to Singh Ji AI Ultra v8.3!\n\n"
            "I'm your AI assistant. Use the buttons below or /help"
        )
        await send_message(chat_id, welcome, MAIN_KEYBOARD)
        return {"status": "ok"}

    # ---- HELP ----
    if text == "/help":
        help_text = (
            "📚 Commands:\n\n"
            "🌤️ /weather city - Get weather\n"
            "📰 /news - Latest news\n"
            "🌾 /mandi state - Mandi prices\n"
            "💰 /tax income - Tax calculation\n"
            "📊 /status - System status\n"
            "🤖 /ai question - AI chat\n"
            "🥇 /gold city - Gold rates\n"
            "⛽ /fuel city - Fuel prices\n"
            "🔮 /horoscope rashi - Daily horoscope\n"
            "💱 /currency USD INR 100 - Currency convert\n"
            "🔤 /translate en text - Translate\n"
            "🚨 /emergency type - Emergency numbers\n"
            "💳 /upi - UPI information\n"
            "🔍 /search query - Web search\n"
            "💼 /rozgar keyword country - Jobs\n"
            "📢 /broadcast message - Admin only"
        )
        await send_message(chat_id, help_text)
        return {"status": "ok"}

    # ---- STATUS ----
    if text == "/status":
        status = SMART_SWARM.get_status()
        api_count = sum(1 for v in AVAILABLE_KEYS.values() if v)
        status_text = (
            f"📊 Status\n\n"
            f"🤖 Agents: {status['currently_loaded']}/330\n"
            f"⚡ Active: {status['active_running']}\n"
            f"😴 Idle: {status['idle']}\n"
            f"🔌 APIs: {api_count}/{len(AVAILABLE_KEYS)}\n"
            f"👥 Users: {len(USER_PREFERENCES)}\n"
            f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}"
        )
        await send_message(chat_id, status_text)
        return {"status": "ok"}

    # ---- WEATHER ----
    if text.startswith("/weather "):
        city = text.replace("/weather ", "").strip()
        if not city:
            await send_message(chat_id, "❌ Please provide a city name. Example: /weather Delhi")
            return {"status": "ok"}
        
        if OPENWEATHER_API_KEY:
            try:
                url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
                resp = await HTTP_CLIENT.get(url, timeout=15)
                data = resp.json()
                if resp.status_code == 200:
                    weather_text = (
                        f"🌤️ Weather in {city}\n\n"
                        f"🌡️ Temp: {data['main']['temp']}°C\n"
                        f"💧 Humidity: {data['main']['humidity']}%\n"
                        f"🌬️ Wind: {data['wind']['speed']} m/s\n"
                        f"☁️ {data['weather'][0]['description'].title()}"
                    )
                    await send_message(chat_id, weather_text)
                else:
                    await send_message(chat_id, f"❌ City not found: {city}")
            except Exception as e:
                await send_message(chat_id, f"❌ Weather error: {str(e)[:100]}")
        else:
            await send_message(chat_id, "❌ Weather API key missing")
        return {"status": "ok"}

    # ---- NEWS ----
    if text == "/news":
        try:
            import modules.news.handler as news_module
            news_text = "📰 Latest News\n\n" + await news_module.get_news_digest_text(count=5)
            await send_message(chat_id, news_text)
        except Exception as e:
            await send_message(chat_id, f"❌ News error: {str(e)[:100]}")
        return {"status": "ok"}

       # ---- MANDI ----
    if text.startswith("/mandi"):
        raw_state = text.replace("/mandi", "").strip()
        if not raw_state:
            await send_message(chat_id, "❌ राज्य का नाम दें।\n\nउदाहरण:\n/mandi Punjab\n/mandi Haryana\n/mandi UP")
            return {"status": "ok"}
        
        state = _normalize_state(raw_state)
        if MANDI_API_KEY:
            try:
                params = {
                    "api-key": MANDI_API_KEY, 
                    "format": "json", 
                    "limit": 10, 
                    "filters[state.keyword]": state
                }
                resp = await HTTP_CLIENT.get(MANDI_BASE_URL, params=params, timeout=45)
                data = resp.json()

                if "error" in data:
                    await send_message(chat_id, f"❌ Mandi API error: {data.get('error', 'Unknown')}")
                    return {"status": "ok"}

                records = data.get("records", [])
                if not records:
                    await send_message(chat_id, f"❌ {state} के लिए डेटा नहीं मिला\n\nTry करें:\n/mandi Punjab\n/mandi Haryana\n/mandi UP")
                    return {"status": "ok"}

                mandi_text = f"🌾 Mandi Bhav — {state}\n\n"
                for i, record in enumerate(records[:5], 1):
                    commodity = record.get("commodity", "Unknown")
                    modal = record.get("modal_price", "N/A")
                    min_p = record.get("min_price", "N/A")
                    max_p = record.get("max_price", "N/A")
                    market = record.get("market", "N/A")
                    district = record.get("district", "N/A")
                    mandi_text += f"{i}. {commodity}\n"
                    mandi_text += f"   ₹{modal}/q (₹{min_p}-₹{max_p})\n"
                    mandi_text += f"   📍 {market}, {district}\n\n"
                await send_message(chat_id, mandi_text)
            except Exception as e:
                await send_message(chat_id, f"❌ Mandi error: {str(e)[:100]}")
        else:
            await send_message(chat_id, "❌ Mandi API key missing")
        return {"status": "ok"}
    # ---- TAX ----
    if text.startswith("/tax "):
        try:
            income = float(text.replace("/tax ", "").strip())
            r = _calculate_tax(income, "new")
            tax_text = (
                f"💰 Tax Calculation\n\n"
                f"Income: ₹{r['income']:,.0f}\n"
                f"Tax: ₹{r['tax']:,.2f}\n"
                f"Cess: ₹{r['cess']:,.2f}\n"
                f"Total Tax: ₹{r['total']:,.2f}\n"
                f"Take Home: ₹{r['take_home']:,.2f}"
            )
            await send_message(chat_id, tax_text)
        except ValueError:
            await send_message(chat_id, "❌ Invalid income. Example: /tax 500000")
        except Exception as e:
            await send_message(chat_id, f"❌ Tax error: {str(e)[:100]}")
        return {"status": "ok"}

    # ---- GOLD ----
    if text.startswith("/gold"):
        city = text.replace("/gold", "").strip() or "delhi"
        try:
            from modules.goldrate.handler import gold_rate_city
            resp = await gold_rate_city(city)
            import json
            body = json.loads(bytes(resp.body))
            d = body["data"]
            cr = d.get("city_rates", {})
            gold_text = (
                f"🥇 Gold Rate - {cr.get('city', city.title())}\n\n"
                f"24K (1g): ₹{cr.get('price_gram_24k', 'N/A')}\n"
                f"22K (1g): ₹{cr.get('price_gram_22k', 'N/A')}\n"
                f"24K (10g): ₹{cr.get('price_10g_24k', 'N/A')}\n"
                f"Updated: {d.get('last_updated', 'N/A')}"
            )
            await send_message(chat_id, gold_text)
        except Exception as e:
            await send_message(chat_id, f"❌ Gold error: {str(e)[:100]}")
        return {"status": "ok"}

    # ---- FUEL ----
    if text.startswith("/fuel"):
        city = text.replace("/fuel", "").strip() or "delhi"
        try:
            from modules.fuel.handler import fuel_price
            resp = await fuel_price(city)
            import json
            body = json.loads(bytes(resp.body))
            d = body["data"]
            fuel_text = (
                f"⛽ Fuel Price - {d.get('city', city.title())}\n\n"
                f"Petrol: ₹{d.get('petrol', 'N/A')}/L\n"
                f"Diesel: ₹{d.get('diesel', 'N/A')}/L\n"
                f"Updated: {d.get('last_updated', 'N/A')}"
            )
            await send_message(chat_id, fuel_text)
        except Exception as e:
            await send_message(chat_id, f"❌ Fuel error: {str(e)[:100]}")
        return {"status": "ok"}

    # ---- HOROSCOPE ----
    if text.startswith("/horoscope"):
        rashi = text.replace("/horoscope", "").strip() or "मेष"
        try:
            from modules.horoscope.handler import get_horoscope, format_telegram as _format_horoscope_telegram
            h = get_horoscope(rashi, "daily", "hi")
            horo_text = _format_horoscope_telegram(h)
            await send_message(chat_id, horo_text)
        except Exception as e:
            await send_message(chat_id, f"❌ Horoscope error: {str(e)[:100]}")
        return {"status": "ok"}

    # ---- CURRENCY ----
    if text.startswith("/currency"):
        parts = text.replace("/currency", "").strip().split()
        try:
            from modules.currency.handler import singhji_currency
            if len(parts) == 1:
                try:
                    amount = float(parts[0])
                    base, target = "USD", "INR"
                except ValueError:
                    base, target, amount = parts[0].upper(), "INR", 1.0
            else:
                base = parts[0].upper() if len(parts) > 0 else "USD"
                target = parts[1].upper() if len(parts) > 1 else "INR"
                amount = float(parts[2]) if len(parts) > 2 else 1.0
            
            result = await singhji_currency.convert(base, target, amount)
            cur_text = (
                f"💱 Currency Convert\n\n"
                f"{amount} {base} = {result.converted} {target}\n"
                f"Rate: 1 {base} = {result.rate} {target}"
            )
            await send_message(chat_id, cur_text)
        except Exception as e:
            await send_message(chat_id, f"❌ Currency error: {str(e)[:100]}")
        return {"status": "ok"}

    # ---- ROZGAR ----
    if text.startswith("/rozgar"):
        raw = text.replace("/rozgar", "").strip()
        try:
            from modules.rozgar import handler as rozgar_module
            parts = raw.split()
            known_countries = set(rozgar_module.PORTALS["regional"].keys())
            country = ""
            keyword_parts = []
            for p in parts:
                if p.upper() in known_countries and not country:
                    country = p.upper()
                else:
                    keyword_parts.append(p)
            keyword = " ".join(keyword_parts).strip().lower()
            search_term = rozgar_module.KEYWORD_MAP.get(keyword, keyword) if keyword else ""
            
            if keyword and country:
                result = rozgar_module._search_keyword(keyword, search_term)
                result = rozgar_module._filter_by_country(result, country)
            elif keyword:
                result = rozgar_module._search_keyword(keyword, search_term)
            elif country:
                result = rozgar_module._country_only(country)
            else:
                result = {"global": [], "regional": [], "govt": [], "categories": []}

            rozgar_text = "💼 Rozgar/Jobs\n\n"
            for section, label in [("govt", "🏛️ Government"), ("regional", "📍 Regional"), ("global", "🌐 Global")]:
                for entry in result.get(section, [])[:5]:
                    name = entry.get("name", "")
                    site = entry.get("site", "")
                    rozgar_text += f"{label}: {name} — {site}\n"
            
            if not any(result.get(s) for s in ("govt", "regional", "global")):
                rozgar_text += "No results found. Example: /rozgar software IN"
            await send_message(chat_id, rozgar_text[:4000])
        except Exception as e:
            await send_message(chat_id, f"❌ Rozgar error: {str(e)[:100]}")
        return {"status": "ok"}

    # ---- TRANSLATE ----
    if text.startswith("/translate "):
        parts = text.replace("/translate ", "").strip().split(" ", 1)
        try:
            from modules.language.handler import LanguageModule
            LANG_MODULE = LanguageModule()
            target_lang = parts[0].lower()
            to_translate = parts[1] if len(parts) > 1 else ""
            if not to_translate:
                await send_message(chat_id, "Format: /translate en Namaste kaise ho")
                return {"status": "ok"}
            
            result = await run_in_threadpool(LANG_MODULE.translate, to_translate, target_lang, "auto")
            if result.get("success"):
                await send_message(chat_id, f"🔤 Translation ({result.get('target_name', target_lang)})\n\n{result['translated']}")
            else:
                await send_message(chat_id, f"❌ Translate error: {result.get('error', 'unknown')[:100]}")
        except Exception as e:
            await send_message(chat_id, f"❌ Translate error: {str(e)[:100]}")
        return {"status": "ok"}

       # ---- SEARCH ----
    if text.startswith("/search"):
        query = text.replace("/search", "").strip()
        if not query:
            await send_message(chat_id, "❌ Search query दें।\n\nउदाहरण: /search AI news")
            return {"status": "ok"}
        
        try:
            import services.travily_search as travily_search_service
            results = await travily_search_service.search(query)
            search_text = f"🔍 Search: {query}\n\n"
            for i, r in enumerate(results[:5], 1):
                search_text += f"{i}. {r.get('title', 'No title')}\n   {r.get('url', '')}\n\n"
            if not results:
                search_text += "कोई result नहीं मिला"
            await send_message(chat_id, search_text)
        except Exception as e:
            await send_message(chat_id, f"❌ Search error: {str(e)[:100]}")
        return {"status": "ok"}
    # ---- EMERGENCY ----
    if text.startswith("/emergency"):
        type_ = text.replace("/emergency", "").strip().lower()
        try:
            from modules.emergency.handler import EMERGENCY_DATA
            if type_ and type_ in EMERGENCY_DATA:
                v = EMERGENCY_DATA[type_]
                emg_text = f"🚨 {type_.title()}\n\nNumber: {v['number']}"
                if v.get("alt"):
                    emg_text += f"\nAlt: {v['alt']}"
                emg_text += f"\n{v.get('info', '')}"
            else:
                emg_text = "🚨 Emergency Numbers\n\n"
                for k, v in EMERGENCY_DATA.items():
                    emg_text += f"{k.title()}: {v['number']}"
                    if v.get("alt"):
                        emg_text += f" / {v['alt']}"
                    emg_text += "\n"
            await send_message(chat_id, emg_text)
        except Exception as e:
            await send_message(chat_id, f"Emergency error: {str(e)[:100]}")
        return {"status": "ok"}

    # ---- UPI ----
    if text == "/upi":
        upi_id = os.getenv("UPI_ID", "jp200883@sbi")
        upi_text = (
            f"💳 UPI Info\n\n"
            f"UPI ID: {upi_id}\n"
            f"Apps: PhonePe, Google Pay, Paytm, BHIM\n"
            f"Daily Limit: ₹1,00,000"
        )
        await send_message(chat_id, upi_text)
        return {"status": "ok"}

    # ---- AI CHAT ----
    if text.startswith("/ai "):
        prompt = text.replace("/ai ", "").strip()
        if not prompt:
            await send_message(chat_id, "❌ Please provide a question. Example: /ai India ka capital kya hai?")
            return {"status": "ok"}
        
        if GROQ_API_KEY:
            try:
                from api.ai import _call_groq
                await send_message(chat_id, "🤔 Thinking...")
                ai_response = await _call_groq(prompt)
                await send_message(chat_id, f"🤖 AI Response:\n\n{ai_response[:4000]}")
                await _memory_save(
                    f"telegram_chat:{user_id}:{int(datetime.now().timestamp())}",
                    {"prompt": prompt, "response": ai_response}
                )
            except Exception as e:
                await send_message(chat_id, f"❌ AI Error: {str(e)[:100]}")
        else:
            await send_message(chat_id, "❌ Groq API key missing")
        return {"status": "ok"}

    # ---- BROADCAST (Admin only) ----
    if text.startswith("/broadcast "):
        if user_id != ADMIN_USER_ID:
            await send_message(chat_id, "⛔ Admin only command")
            return {"status": "ok"}
        
        broadcast_text = text.replace("/broadcast ", "").strip()
        if not broadcast_text:
            await send_message(chat_id, "❌ Please provide a message. Example: /broadcast Hello everyone!")
            return {"status": "ok"}
        
        if MASTER_SCHEDULER:
            await MASTER_SCHEDULER._broadcast_with_rate_limit(f"📢 Broadcast\n\n{broadcast_text}")
            await send_message(chat_id, f"✅ Broadcast sent to {len(USER_PREFERENCES)} users")
        else:
            await send_message(chat_id, "❌ Scheduler not initialized")
        return {"status": "ok"}

    # ---- STATUS (shortcut) ----
    if text == "/status":
        status = SMART_SWARM.get_status()
        api_count = sum(1 for v in AVAILABLE_KEYS.values() if v)
        status_text = (
            f"📊 Status\n\n"
            f"🤖 Agents: {status['currently_loaded']}/330\n"
            f"⚡ Active: {status['active_running']}\n"
            f"😴 Idle: {status['idle']}\n"
            f"🔌 APIs: {api_count}/{len(AVAILABLE_KEYS)}\n"
            f"👥 Users: {len(USER_PREFERENCES)}\n"
            f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}"
        )
        await send_message(chat_id, status_text)
        return {"status": "ok"}

    # ---- UNKNOWN COMMAND ----
    await send_message(chat_id, "❌ Unknown command. Type /help for available commands")
    return {"status": "ok"}
