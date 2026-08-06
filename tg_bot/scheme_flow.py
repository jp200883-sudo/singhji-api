# tg_bot/scheme_flow.py
"""
Scheme Swarm — raw webhook adapter
(asal handler.py python-telegram-bot/Update style mein tha,
 ise chat_id/user_id/text wale mojooda architecture mein badla gaya hai)
"""
import logging
from core.scheduler import USER_PREFERENCES
from core.memory import _memory_save, _memory_get
from tg_bot.helpers import send_message
from modules.scheme_swarm.eligibility import EligibilityEngine, UserProfile

logger = logging.getLogger(__name__)

_ENGINE = None

def _get_engine():
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = EligibilityEngine()
    return _ENGINE

CASTE_OK = {"SC", "ST", "OBC", "GENERAL", "EWS"}

STEP_PROMPTS = {
    1: "*Step 1/6:* Tumhari umar kya hai?\n_(Example: 25)_",
    2: "*Step 2/6:* Saalana income kitni hai?\n_(Example: 150000)_",
    3: "*Step 3/6:* Kaunse state mein ho?\n_(Example: Uttar Pradesh)_",
    4: "*Step 4/6:* Occupation kya hai?\n_(farmer / student / unemployed / self_employed / private_job / govt_job / housewife / daily_wage / artisan / business)_",
    5: "*Step 5/6:* Caste category?\n_(SC / ST / OBC / GENERAL / EWS)_",
    6: "*Step 6/6:* Family mein kitne log hain?\n_(Example: 4)_",
}


async def start_profile_builder(chat_id, user_id):
    USER_PREFERENCES.setdefault(user_id, {})["scheme_step"] = 1
    USER_PREFERENCES[user_id]["scheme_profile"] = {}
    await send_message(chat_id, f"📝 *Scheme Profile Builder*\n\n{STEP_PROMPTS[1]}")


async def handle_scheme_step(chat_id, user_id, text):
    """Agar user profile-wizard ke beech mein hai to step handle karo.
    True lautaye = handled ho gaya, aage kuch mat karo.
    False lautaye = yeh scheme-flow ka message nahi hai."""
    prefs = USER_PREFERENCES.get(user_id, {})
    step = prefs.get("scheme_step", 0)
    if not step:
        return False

    profile = prefs.get("scheme_profile", {})
    text = text.strip()

    if step == 1:
        if not text.isdigit() or not (1 <= int(text) <= 120):
            await send_message(chat_id, "❌ Sahi umar bhejo (1-120)")
            return True
        profile["age"] = int(text)
        prefs["scheme_step"] = 2

    elif step == 2:
        try:
            profile["annual_income"] = float(text.replace(",", ""))
        except ValueError:
            await send_message(chat_id, "❌ Number bhejo! Example: 150000")
            return True
        prefs["scheme_step"] = 3

    elif step == 3:
        profile["state"] = text
        prefs["scheme_step"] = 4

    elif step == 4:
        profile["occupation"] = text.lower()
        profile["is_farmer"] = profile["occupation"] == "farmer"
        profile["is_student"] = profile["occupation"] == "student"
        prefs["scheme_step"] = 5

    elif step == 5:
        caste = text.upper()
        if caste not in CASTE_OK:
            await send_message(chat_id, "❌ Sahi category bhejo: SC / ST / OBC / GENERAL / EWS")
            return True
        profile["caste_category"] = caste
        prefs["scheme_step"] = 6

    elif step == 6:
        if not text.isdigit():
            await send_message(chat_id, "❌ Number bhejo! Example: 4")
            return True
        profile["family_members"] = int(text)
        profile["gender"] = profile.get("gender", "other")
        prefs.pop("scheme_step", None)
        prefs["scheme_profile"] = profile
        USER_PREFERENCES[user_id] = prefs
        try:
            await _memory_save(f"scheme_profile:{user_id}", profile, table="user_memory")
        except Exception as e:
            logger.error(f"Scheme profile save fail: {e}")
        summary = (
            f"✅ *Profile Complete!* 🎉\n\n"
            f"• Age: {profile['age']}\n"
            f"• Income: ₹{profile['annual_income']:,.0f}\n"
            f"• State: {profile['state']}\n"
            f"• Occupation: {profile['occupation']}\n"
            f"• Caste: {profile['caste_category']}\n"
            f"• Family: {profile['family_members']}\n\n"
            f"Ab /schemes bhejo apne liye schemes dekhne ke liye! 🚀"
        )
        await send_message(chat_id, summary)
        return True

    prefs["scheme_profile"] = profile
    USER_PREFERENCES[user_id] = prefs
    await send_message(chat_id, STEP_PROMPTS[prefs["scheme_step"]])
    return True


async def handle_schemes_command(chat_id, user_id):
    prefs = USER_PREFERENCES.get(user_id, {})
    profile_data = prefs.get("scheme_profile")
    if not profile_data or "family_members" not in profile_data:
        try:
            cached = await _memory_get(f"scheme_profile:{user_id}", table="user_memory")
        except Exception:
            cached = None
        if cached:
            profile_data = cached

    if not profile_data or "family_members" not in profile_data:
        await send_message(
            chat_id,
            "🦁 *Singh Ji Scheme Swarm* 🏛️\n\nPehle apni profile banao — /scheme_profile bhejo."
        )
        return

    try:
        profile = UserProfile(
            age=profile_data["age"],
            gender=profile_data.get("gender", "other"),
            caste_category=profile_data["caste_category"],
            annual_income=profile_data["annual_income"],
            state=profile_data["state"],
            occupation=profile_data["occupation"],
            is_farmer=profile_data.get("is_farmer", False),
            is_student=profile_data.get("is_student", False),
            family_members=profile_data.get("family_members", 1),
        )
        matches = _get_engine().get_top_matches(profile, top_n=5)
    except Exception as e:
        logger.error(f"Scheme match error: {e}")
        await send_message(chat_id, f"❌ Scheme match mein error: {str(e)[:100]}")
        return

    if not matches:
        await send_message(chat_id, "❌ Abhi koi matching scheme nahi mili.")
        return

    text = f"🎯 *{len(matches)} Schemes Mil Gayi!*\n\n"
    for i, m in enumerate(matches, 1):
        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "✅"
        text += f"{emoji} *{m.scheme_name}* ({m.match_score}%)\n   💰 {m.benefits_summary}\n\n"
    text += "🔄 Profile update karne ke liye /scheme_profile bhejo."
    await send_message(chat_id, text[:4000])
