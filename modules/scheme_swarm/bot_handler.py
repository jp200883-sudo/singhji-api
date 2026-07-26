"""
Singh Ji AI — Scheme Swarm Telegram Bot Handlers
Integrates with existing bot architecture
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import requests
import json
import logging

logger = logging.getLogger(__name__)

# Import from main bot (adjust path as needed)
from ..eligibility import EligibilityEngine, UserProfile

API_BASE_URL = "https://singhji.ai/api"  # Adjust to your API URL


# ═══════════════════════════════════════════════════════
# COMMAND HANDLERS
# ═══════════════════════════════════════════════════════

async def cmd_schemes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main /schemes command — shows matched schemes for user"""
    user_id = update.effective_user.id

    # Check if profile exists via API
    try:
        response = requests.post(
            f"{API_BASE_URL}/modules/scheme_swarm/match",
            json={"user_id": user_id},
            timeout=15
        )
        result = response.json()
        matches = result.get("matches", [])

        if result.get("error") == "Profile not found" or not matches:
            # Start profile builder
            await update.message.reply_text(
                "🦁 *Singh Ji Scheme Swarm* 🏛️\n\n"
                "Pehle apni profile banao taaki main tumhare liye "
                "*perfect schemes* dhoondh sakoon!\n\n"
                "👉 /scheme_profile shuru karo",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        # Show top matches
        text = f"🎯 *{len(matches)} Schemes Mil Gayi!*\n\n"
        text += f"🏆 *Top {min(5, len(matches))} Schemes:*\n\n"

        for i, m in enumerate(matches[:5], 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "✅"
            text += f"{emoji} *{m['name']}*\n"
            text += f"   Match: {m['score']}%\n"
            text += f"   💰 {m['benefits']}\n\n"

        keyboard = []
        for m in matches[:5]:
            keyboard.append([InlineKeyboardButton(
                f"📋 {m['name'][:28]}...",
                callback_data=f"scheme_detail:{m['id']}"
            )])

        keyboard.append([
            InlineKeyboardButton("🔄 Profile Update", callback_data="scheme_profile"),
            InlineKeyboardButton("📊 All Matches", callback_data="scheme_all")
        ])
        keyboard.append([
            InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
        ])

        await update.message.reply_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    except Exception as e:
        logger.error(f"Schemes command error: {e}")
        await update.message.reply_text(
            "❌ Error! Baad mein try karo!\n"
            "Profile check karo: /scheme_profile",
            parse_mode=ParseMode.MARKDOWN
        )


async def cmd_scheme_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start 6-step profile builder wizard"""
    user_id = update.effective_user.id

    # Reset any existing flow
    context.user_data["scheme_step"] = 1
    context.user_data["scheme_profile"] = {}

    await update.message.reply_text(
        "📝 *Scheme Profile Builder*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "6 simple steps mein tumhari profile complete!\n\n"
        "*Step 1/6: Tumhari umar kya hai?*\n"
        "_(Example: 25)_",
        parse_mode=ParseMode.MARKDOWN
    )


async def cmd_scheme_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check application status"""
    args = context.args
    if not args:
        await update.message.reply_text(
            "📊 *Scheme Status Check*\n\n"
            "Usage: /scheme_status <application_id>\n"
            "Example: /scheme_status PMKISAN12345",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    app_id = args[0]
    await update.message.reply_text(
        f"⏳ Status check kar raha hoon...\n"
        f"Application ID: `{app_id}`",
        parse_mode=ParseMode.MARKDOWN
    )
    # TODO: Implement actual status tracking


# ═══════════════════════════════════════════════════════
# PROFILE BUILDER FLOW (called from text handler)
# ═══════════════════════════════════════════════════════

async def handle_scheme_profile_step(update: Update, context: ContextTypes.DEFAULT_TYPE, user_text: str):
    """Handle each step of profile builder — call this from main text_chat_handler"""
    step = context.user_data.get("scheme_step", 0)
    profile = context.user_data.get("scheme_profile", {})
    user_id = update.effective_user.id

    if step == 1:  # Age
        try:
            age = int(user_text.strip())
            if age < 1 or age > 120:
                await update.message.reply_text("❌ Sahi umar bhejo! (1-120)")
                return False
            profile["age"] = age
            context.user_data["scheme_profile"] = profile
            context.user_data["scheme_step"] = 2

            await update.message.reply_text(
                f"✅ Age: {age}\n\n"
                f"*Step 2/6: Saala Income?*\n"
                f"_(Example: 150000)_",
                parse_mode=ParseMode.MARKDOWN
            )
            return True
        except ValueError:
            await update.message.reply_text("❌ Number bhejo! Example: 25")
            return False

    elif step == 2:  # Income
        try:
            income = float(user_text.replace(",", "").strip())
            profile["income"] = income
            context.user_data["scheme_profile"] = profile
            context.user_data["scheme_step"] = 3

            await update.message.reply_text(
                f"✅ Income: ₹{income:,.0f}\n\n"
                f"*Step 3/6: Kaunse State?*\n"
                f"_(Example: Uttar Pradesh, Bihar, Maharashtra)_",
                parse_mode=ParseMode.MARKDOWN
            )
            return True
        except ValueError:
            await update.message.reply_text("❌ Number bhejo! Example: 150000")
            return False

    elif step == 3:  # State
        profile["state"] = user_text.strip()
        context.user_data["scheme_profile"] = profile
        context.user_data["scheme_step"] = 4

        await update.message.reply_text(
            f"✅ State: {profile['state']}\n\n"
            f"*Step 4/6: Occupation?*\n"
            f"_(farmer / student / unemployed / self_employed / private_job / govt_job / housewife / daily_wage / artisan / business)_",
            parse_mode=ParseMode.MARKDOWN
        )
        return True

    elif step == 4:  # Occupation
        profile["occupation"] = user_text.strip().lower()
        context.user_data["scheme_profile"] = profile
        context.user_data["scheme_step"] = 5

        await update.message.reply_text(
            f"✅ Occupation: {profile['occupation']}\n\n"
            f"*Step 5/6: Caste Category?*\n"
            f"_(SC / ST / OBC / GENERAL / EWS)_",
            parse_mode=ParseMode.MARKDOWN
        )
        return True

    elif step == 5:  # Caste
        caste = user_text.strip().upper()
        if caste not in ["SC", "ST", "OBC", "GENERAL", "EWS"]:
            await update.message.reply_text(
                "❌ Sahi category bhejo!\n"
                "SC / ST / OBC / GENERAL / EWS"
            )
            return False
        profile["caste"] = caste
        context.user_data["scheme_profile"] = profile
        context.user_data["scheme_step"] = 6

        await update.message.reply_text(
            f"✅ Caste: {caste}\n\n"
            f"*Step 6/6: Family mein kitne log?*\n"
            f"_(Example: 4)_",
            parse_mode=ParseMode.MARKDOWN
        )
        return True

    elif step == 6:  # Family size
        try:
            family = int(user_text.strip())
            profile["family_members"] = family

            # Save to API
            try:
                response = requests.post(
                    f"{API_BASE_URL}/modules/scheme_swarm/save-profile",
                    json={
                        "user_id": user_id,
                        "profile": profile
                    },
                    timeout=15
                )

                if response.status_code == 200:
                    # Clear flow
                    context.user_data.pop("scheme_step", None)
                    context.user_data.pop("scheme_profile", None)

                    await update.message.reply_text(
                        f"✅ *Profile Complete!* 🎉\n\n"
                        f"📋 Summary:\n"
                        f"• Age: {profile['age']}\n"
                        f"• Income: ₹{profile['income']:,.0f}\n"
                        f"• State: {profile['state']}\n"
                        f"• Occupation: {profile['occupation']}\n"
                        f"• Caste: {profile['caste']}\n"
                        f"• Family: {profile['family_members']}\n\n"
                        f"Ab /schemes se apne liye *schemes check karo!* 🚀",
                        parse_mode=ParseMode.MARKDOWN
                    )
                    return True
                else:
                    await update.message.reply_text(
                        "❌ Profile save nahi hua! Dobara try karo."
                    )
                    return False

            except Exception as e:
                logger.error(f"Save profile error: {e}")
                await update.message.reply_text(
                    "❌ Network error! Baad mein try karo."
                )
                return False

        except ValueError:
            await update.message.reply_text("❌ Number bhejo! Example: 4")
            return False

    return False


# ═══════════════════════════════════════════════════════
# CALLBACK HANDLERS
# ═══════════════════════════════════════════════════════

async def scheme_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
    """Handle scheme-related callbacks — call from main button_callback"""
    query = update.callback_query
    user_id = update.effective_user.id

    if data == "schemes_menu" or data == "scheme_back":
        # Show schemes menu
        await cmd_schemes(update, context)
        return True

    elif data == "scheme_profile":
        await cmd_scheme_profile(update, context)
        return True

    elif data == "scheme_all":
        # Show all matches
        try:
            response = requests.post(
                f"{API_BASE_URL}/modules/scheme_swarm/match",
                json={"user_id": user_id, "limit": 20},
                timeout=15
            )
            matches = response.json().get("matches", [])

            text = f"📊 *All {len(matches)} Matching Schemes*\n\n"
            for i, m in enumerate(matches, 1):
                text += f"{i}. *{m['name']}* — {m['score']}% match\n"
                text += f"   💰 {m['benefits']}\n\n"
                if len(text) > 3500:
                    text += "... aur bhi hain!"
                    break

            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="schemes_menu")]]
            await query.edit_message_text(
                text, parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return True

        except Exception as e:
            logger.error(f"All schemes error: {e}")
            await query.edit_message_text("❌ Error! Baad mein try karo.")
            return True

    elif data.startswith("scheme_detail:"):
        scheme_id = data.split(":")[1]
        try:
            response = requests.get(
                f"{API_BASE_URL}/modules/scheme_swarm/scheme/{scheme_id}",
                timeout=10
            )
            scheme = response.json()

            text = f"📋 *{scheme['name']}*\n"
            text += f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            text += f"📝 {scheme['description']}\n\n"
            text += f"💰 *Benefits:* {scheme.get('benefits_summary', 'N/A')}\n"
            text += f"🏛️ *Ministry:* {scheme.get('ministry', 'N/A')}\n\n"

            # Eligibility
            text += f"🎯 *Eligibility:*\n"
            rules = scheme.get("eligibility_rules", {})
            if "age" in rules:
                text += f"• Age: {rules['age'].get('min', 'Any')} - {rules['age'].get('max', 'Any')} years\n"
            if "income" in rules:
                text += f"• Income: Up to ₹{rules['income'].get('max', 'N/A'):,}/year\n"
            if "caste" in rules:
                text += f"• Caste: {', '.join(rules['caste'])}\n"
            if "occupation" in rules:
                text += f"• Occupation: {', '.join(rules['occupation'][:3])}...\n"

            text += f"\n📄 *Documents Required:*\n"
            for doc in scheme.get("documents", [])[:5]:
                text += f"  • {doc}\n"
            if len(scheme.get("documents", [])) > 5:
                text += f"  ... aur {len(scheme['documents']) - 5} aur\n"

            keyboard = [
                [InlineKeyboardButton("🌐 Official Website", url=scheme.get("url", "#"))],
                [InlineKeyboardButton("📋 Document Checklist", callback_data=f"scheme_docs:{scheme_id}")],
                [InlineKeyboardButton("🔙 Back to Matches", callback_data="schemes_menu")]
            ]

            await query.edit_message_text(
                text, parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return True

        except Exception as e:
            logger.error(f"Scheme detail error: {e}")
            await query.edit_message_text("❌ Scheme details nahi mila!")
            return True

    elif data.startswith("scheme_docs:"):
        scheme_id = data.split(":")[1]
        try:
            response = requests.get(
                f"{API_BASE_URL}/modules/scheme_swarm/scheme/{scheme_id}",
                timeout=10
            )
            scheme = response.json()

            text = f"📋 *Document Checklist*\n"
            text += f"*{scheme['name']}*\n"
            text += f"━━━━━━━━━━━━━━━━━━━━━━\n\n"

            for i, doc in enumerate(scheme.get("documents", []), 1):
                text += f"{i}. {doc}\n"

            text += f"\n💡 *Tip:* In documents ko ready rakho "
            text += f"aur official website pe apply karo!"

            keyboard = [
                [InlineKeyboardButton("🌐 Apply Now", url=scheme.get("url", "#"))],
                [InlineKeyboardButton("🔙 Back", callback_data=f"scheme_detail:{scheme_id}")]
            ]

            await query.edit_message_text(
                text, parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return True

        except Exception as e:
            logger.error(f"Docs error: {e}")
            await query.edit_message_text("❌ Error!")
            return True

    return False  # Not handled


# ═══════════════════════════════════════════════════════
# INLINE KEYBOARD FOR MAIN MENU
# ═══════════════════════════════════════════════════════

def get_scheme_menu_button():
    """Returns button for main menu keyboard"""
    return InlineKeyboardButton("🏛️ Schemes", callback_data="schemes_menu")
