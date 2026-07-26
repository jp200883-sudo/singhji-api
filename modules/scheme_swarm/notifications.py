"""
Automated reminders and notifications for schemes
"""

from datetime import datetime, timedelta
from typing import List
import asyncio

class SchemeNotifier:
    """Send notifications for scheme deadlines, status updates, etc."""
    
    async def check_deadlines(self, db_pool):
        """Check for upcoming deadlines and notify users"""
        async with db_pool.acquire() as conn:
            # Find schemes with deadlines in next 7 days
            rows = await conn.fetch("""
                SELECT sa.*, s.name, s.deadline, u.telegram_id
                FROM scheme_applications sa
                JOIN schemes s ON sa.scheme_id = s.id
                JOIN users u ON sa.user_id = u.id
                WHERE s.deadline <= NOW() + INTERVAL '7 days'
                AND s.deadline > NOW()
                AND sa.status = 'applied'
                AND NOT EXISTS (
                    SELECT 1 FROM scheme_notifications sn
                    WHERE sn.user_id = sa.user_id
                    AND sn.scheme_id = sa.scheme_id
                    AND sn.type = 'deadline'
                    AND sn.sent_at > NOW() - INTERVAL '1 day'
                )
            """)
            
            for row in rows:
                days_left = (row["deadline"] - datetime.now().date()).days
                message = (
                    f"⏰ *Deadline Alert!*\n\n"
                    f"Scheme: *{row['name']}*\n"
                    f"Application ID: `{row['application_id']}`\n"
                    f"Deadline: {row['deadline'].strftime('%d-%m-%Y')}\n"
                    f"Days Left: *{days_left}*\n\n"
                    f"Jaldi complete karo! 🏃"
                )
                
                # Send notification
                await self.send_telegram_message(row["telegram_id"], message)
                
                # Log notification
                await conn.execute("""
                    INSERT INTO scheme_notifications (user_id, scheme_id, type, message, sent_at)
                    VALUES ($1, $2, 'deadline', $3, NOW())
                """, row["user_id"], row["scheme_id"], message)
    
    async def notify_new_schemes(self, db_pool, new_schemes: List[Dict]):
        """Notify eligible users about newly added schemes"""
        for scheme in new_schemes:
            # Find eligible users
            async with db_pool.acquire() as conn:
                users = await conn.fetch("""
                    SELECT u.id, u.telegram_id, sp.*
                    FROM users u
                    JOIN scheme_profiles sp ON u.id = sp.user_id
                    WHERE sp.state = $1 OR $1 IS NULL
                """, scheme.get("state"))
                
                for user in users:
                    # Quick eligibility check
                    engine = EligibilityEngine()
                    profile = UserProfile(
                        age=user["age"],
                        gender=user["gender"],
                        caste_category=user["caste_category"],
                        annual_income=user["annual_income"],
                        state=user["state"],
                        occupation=user["occupation"]
                    )
                    
                    match = engine.check_eligibility(profile, scheme)
                    if match.match_score >= 70:
                        message = (
                            f"🆕 *Nayi Scheme Aayi!*\n\n"
                            f"*{scheme['name']}*\n"
                            f"Benefit: {match.benefits_summary}\n"
                            f"Match Score: {match.match_score}%\n\n"
                            f"Details ke liye /schemes command use karo!"
                        )
                        await self.send_telegram_message(user["telegram_id"], message)
    
    async def send_telegram_message(self, chat_id: int, message: str):
        """Send message via Telegram Bot API"""
        # Integration with existing bot
        from bot import application
        await application.bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode="Markdown"
        )
