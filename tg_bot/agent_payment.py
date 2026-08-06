# api/agent_payment.py
# Singh Ji AI Ultra — Agent Auto-Registration + Payment Split System
# FastAPI Router Version

import logging
import uuid
from datetime import datetime
from typing import Dict, Optional
import aiohttp
import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Commission Structure
COMMISSION_RATES = {
    "upi_payment": 0.0,
    "card_payment": 0.02,
    "wallet_payment": 0.015,
    "gram_panchayat_service": 0.10,
    "new_user_referral": 10.0,
    "premium_subscription": 0.20,
}

AGENT_LEVELS = {
    "Bronze":   {"min_earnings": 0,      "commission_boost": 1.0,  "badge": "🥉"},
    "Silver":   {"min_earnings": 1000,   "commission_boost": 1.1,  "badge": "🥈"},
    "Gold":     {"min_earnings": 5000,   "commission_boost": 1.25, "badge": "🥇"},
    "Platinum": {"min_earnings": 20000,  "commission_boost": 1.5,  "badge": "💎"},
    "Diamond":  {"min_earnings": 100000, "commission_boost": 2.0,  "badge": "👑"},
}

router = APIRouter(prefix="/agent", tags=["Agent"])

# ==========================================
# PYDANTIC MODELS
# ==========================================
class PaymentRequest(BaseModel):
    amount: float
    payment_type: str
    user_telegram_id: str
    agent_telegram_id: Optional[str] = None
    service_id: Optional[str] = None
    metadata: Optional[Dict] = None

class AgentRegisterRequest(BaseModel):
    telegram_id: str
    name: str
    phone: str
    gram_panchayat: str
    referred_by: Optional[str] = None

class WithdrawalRequest(BaseModel):
    agent_telegram_id: str
    amount: float
    upi_id: Optional[str] = None

# ==========================================
# PAYMENT SPLITTER CLASS
# ==========================================
class PaymentSplitter:
    PLATFORM_CUT = 0.50
    AGENT_CUT = 0.40
    REFERRER_CUT = 0.10

    def __init__(self):
        self.supabase_url = SUPABASE_URL
        self.supabase_key = SUPABASE_KEY

    async def process_payment(
        self,
        amount: float,
        payment_type: str,
        user_telegram_id: str,
        agent_telegram_id: Optional[str] = None,
        service_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        transaction_id = f"SJ{uuid.uuid4().hex[:12].upper()}"
        timestamp = datetime.utcnow().isoformat()

        base_rate = COMMISSION_RATES.get(payment_type, 0)
        commission_amount = amount * base_rate if base_rate < 1 else base_rate

        agent_level = "Bronze"
        commission_boost = 1.0
        if agent_telegram_id:
            agent_data = await self._get_agent(agent_telegram_id)
            if agent_data:
                agent_level = agent_data.get("level", "Bronze")
                commission_boost = AGENT_LEVELS[agent_level]["commission_boost"]

        adjusted_commission = commission_amount * commission_boost

        platform_share = adjusted_commission * self.PLATFORM_CUT
        agent_share = adjusted_commission * self.AGENT_CUT
        referrer_share = 0

        referrer_id = await self._get_referrer(user_telegram_id)
        if referrer_id and referrer_id != agent_telegram_id:
            referrer_share = adjusted_commission * self.REFERRER_CUT
            agent_share -= referrer_share

        transaction = {
            "id": transaction_id,
            "timestamp": timestamp,
            "amount": amount,
            "payment_type": payment_type,
            "user_telegram_id": user_telegram_id,
            "agent_telegram_id": agent_telegram_id,
            "service_id": service_id,
            "commission": {
                "base_rate": base_rate,
                "boost": commission_boost,
                "total": round(adjusted_commission, 2),
                "platform": round(platform_share, 2),
                "agent": round(agent_share, 2),
                "referrer": round(referrer_share, 2),
            },
            "splits": {
                "platform": round(amount - adjusted_commission + platform_share, 2),
                "agent": round(agent_share, 2),
                "referrer": round(referrer_share, 2),
            },
            "status": "completed",
            "metadata": metadata or {}
        }

        await self._save_transaction(transaction)

        if agent_telegram_id:
            await self._update_agent_earnings(agent_telegram_id, agent_share)
            await self._check_level_upgrade(agent_telegram_id)

        if referrer_id and referrer_share > 0:
            await self._update_agent_earnings(referrer_id, referrer_share)

        logger.info(f"Payment split: {transaction_id} | Amount: ₹{amount} | Agent: ₹{agent_share}")
        return transaction

    async def auto_register_agent(
        self,
        telegram_id: str,
        name: str,
        phone: str,
        gram_panchayat: str,
        referred_by: Optional[str] = None
    ) -> Dict:
        agent_id = f"AG{uuid.uuid4().hex[:8].upper()}"

        agent_data = {
            "id": agent_id,
            "telegram_id": telegram_id,
            "name": name,
            "phone": phone,
            "gram_panchayat": gram_panchayat,
            "level": "Bronze",
            "total_earnings": 0,
            "month_earnings": 0,
            "total_referrals": 0,
            "referred_by": referred_by,
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "upi_id": f"singhji.{telegram_id}@sbi",
            "commission_rate": COMMISSION_RATES,
        }

        success = await self._save_agent(agent_data)

        if success and referred_by:
            await self._process_referral_bonus(referred_by, telegram_id)

        return {
            "success": success,
            "agent_id": agent_id,
            "upi_id": agent_data["upi_id"],
            "level": "Bronze",
            "referral_link": f"https://t.me/SinghJiAIBot?start=ref_{agent_id}"
        }

    async def process_withdrawal(
        self,
        agent_telegram_id: str,
        amount: float,
        upi_id: Optional[str] = None
    ) -> Dict:
        MIN_WITHDRAWAL = 100

        agent = await self._get_agent(agent_telegram_id)
        if not agent:
            return {"success": False, "error": "Agent not found"}

        available = agent.get("total_earnings", 0) - agent.get("total_withdrawn", 0)

        if amount < MIN_WITHDRAWAL:
            return {"success": False, "error": f"Minimum withdrawal is ₹{MIN_WITHDRAWAL}"}

        if amount > available:
            return {"success": False, "error": f"Insufficient balance. Available: ₹{available}"}

        withdrawal_id = f"WD{uuid.uuid4().hex[:10].upper()}"

        withdrawal = {
            "id": withdrawal_id,
            "agent_telegram_id": agent_telegram_id,
            "amount": amount,
            "upi_id": upi_id or agent.get("upi_id"),
            "status": "pending",
            "requested_at": datetime.utcnow().isoformat(),
            "processed_at": None
        }

        await self._save_withdrawal(withdrawal)
        await self._update_agent_withdrawn(agent_telegram_id, amount)

        return {
            "success": True,
            "withdrawal_id": withdrawal_id,
            "amount": amount,
            "status": "pending",
            "message": "Withdrawal queued. You'll receive UPI payment within 24 hours."
        }

    # ============ PRIVATE METHODS ============

    async def _get_agent(self, telegram_id: str) -> Optional[Dict]:
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "apikey": self.supabase_key,
                    "Authorization": f"Bearer {self.supabase_key}"
                }
                url = f"{self.supabase_url}/rest/v1/agents?telegram_id=eq.{telegram_id}&select=*"
                async with session.get(url, headers=headers) as resp:
                    data = await resp.json()
                    return data[0] if data else None
        except Exception as e:
            logger.error(f"Get agent failed: {e}")
        return None

    async def _save_agent(self, agent_data: Dict) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "apikey": self.supabase_key,
                    "Authorization": f"Bearer {self.supabase_key}",
                    "Content-Type": "application/json"
                }
                url = f"{self.supabase_url}/rest/v1/agents"
                async with session.post(url, json=agent_data, headers=headers) as resp:
                    return resp.status in [200, 201]
        except Exception as e:
            logger.error(f"Save agent failed: {e}")
        return False

    async def _save_transaction(self, transaction: Dict) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "apikey": self.supabase_key,
                    "Authorization": f"Bearer {self.supabase_key}",
                    "Content-Type": "application/json"
                }
                url = f"{self.supabase_url}/rest/v1/transactions"
                async with session.post(url, json=transaction, headers=headers) as resp:
                    return resp.status in [200, 201]
        except Exception as e:
            logger.error(f"Save transaction failed: {e}")
        return False

    async def _update_agent_earnings(self, telegram_id: str, amount: float):
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "apikey": self.supabase_key,
                    "Authorization": f"Bearer {self.supabase_key}",
                    "Content-Type": "application/json",
                    "Prefer": "return=minimal"
                }
                url = f"{self.supabase_url}/rest/v1/agents?telegram_id=eq.{telegram_id}"
                async with session.get(url, headers=headers) as resp:
                    data = await resp.json()
                    if data:
                        agent = data[0]
                        new_total = agent.get("total_earnings", 0) + amount
                        new_month = agent.get("month_earnings", 0) + amount
                        update_payload = {
                            "total_earnings": new_total,
                            "month_earnings": new_month
                        }
                        await session.patch(url, json=update_payload, headers=headers)
        except Exception as e:
            logger.error(f"Update earnings failed: {e}")

    async def _check_level_upgrade(self, telegram_id: str):
        agent = await self._get_agent(telegram_id)
        if not agent:
            return

        earnings = agent.get("total_earnings", 0)
        current_level = agent.get("level", "Bronze")

        new_level = current_level
        for level, info in sorted(AGENT_LEVELS.items(), 
                                   key=lambda x: x[1]["min_earnings"], 
                                   reverse=True):
            if earnings >= info["min_earnings"]:
                new_level = level
                break

        if new_level != current_level:
            try:
                async with aiohttp.ClientSession() as session:
                    headers = {
                        "apikey": self.supabase_key,
                        "Authorization": f"Bearer {self.supabase_key}",
                        "Content-Type": "application/json"
                    }
                    url = f"{self.supabase_url}/rest/v1/agents?telegram_id=eq.{telegram_id}"
                    await session.patch(url, json={"level": new_level}, headers=headers)

                logger.info(f"Agent {telegram_id} upgraded to {new_level}!")
            except Exception as e:
                logger.error(f"Level upgrade failed: {e}")

    async def _get_referrer(self, telegram_id: str) -> Optional[str]:
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "apikey": self.supabase_key,
                    "Authorization": f"Bearer {self.supabase_key}"
                }
                url = f"{self.supabase_url}/rest/v1/agents?telegram_id=eq.{telegram_id}&select=referred_by"
                async with session.get(url, headers=headers) as resp:
                    data = await resp.json()
                    if data and data[0].get("referred_by"):
                        return data[0]["referred_by"]
        except Exception as e:
            logger.error(f"Get referrer failed: {e}")
        return None

    async def _process_referral_bonus(self, referrer_id: str, new_agent_id: str):
        await self._update_agent_earnings(referrer_id, 10.0)
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "apikey": self.supabase_key,
                    "Authorization": f"Bearer {self.supabase_key}",
                    "Content-Type": "application/json"
                }
                url = f"{self.supabase_url}/rest/v1/agents?telegram_id=eq.{referrer_id}"
                async with session.get(url, headers=headers) as resp:
                    data = await resp.json()
                    if data:
                        new_count = data[0].get("total_referrals", 0) + 1
                        await session.patch(url, json={"total_referrals": new_count}, headers=headers)
        except Exception as e:
            logger.error(f"Referral bonus failed: {e}")

    async def _save_withdrawal(self, withdrawal: Dict) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "apikey": self.supabase_key,
                    "Authorization": f"Bearer {self.supabase_key}",
                    "Content-Type": "application/json"
                }
                url = f"{self.supabase_url}/rest/v1/withdrawals"
                async with session.post(url, json=withdrawal, headers=headers) as resp:
                    return resp.status in [200, 201]
        except Exception as e:
            logger.error(f"Save withdrawal failed: {e}")
        return False

    async def _update_agent_withdrawn(self, telegram_id: str, amount: float):
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "apikey": self.supabase_key,
                    "Authorization": f"Bearer {self.supabase_key}",
                    "Content-Type": "application/json"
                }
                url = f"{self.supabase_url}/rest/v1/agents?telegram_id=eq.{telegram_id}"
                async with session.get(url, headers=headers) as resp:
                    data = await resp.json()
                    if data:
                        new_withdrawn = data[0].get("total_withdrawn", 0) + amount
                        await session.patch(url, json={"total_withdrawn": new_withdrawn}, headers=headers)
        except Exception as e:
            logger.error(f"Update withdrawn failed: {e}")


# ==========================================
# ROUTER ENDPOINTS
# ==========================================
splitter = PaymentSplitter()

@router.post("/payment/split")
async def api_process_payment(request: PaymentRequest):
    """Process payment with auto-split"""
    result = await splitter.process_payment(
        amount=request.amount,
        payment_type=request.payment_type,
        user_telegram_id=request.user_telegram_id,
        agent_telegram_id=request.agent_telegram_id,
        service_id=request.service_id,
        metadata=request.metadata
    )
    return {"success": True, "data": result}

@router.post("/register")
async def api_register_agent(request: AgentRegisterRequest):
    """Auto-register new agent"""
    result = await splitter.auto_register_agent(
        telegram_id=request.telegram_id,
        name=request.name,
        phone=request.phone,
        gram_panchayat=request.gram_panchayat,
        referred_by=request.referred_by
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail="Registration failed")
    return {"success": True, "data": result}

@router.post("/withdraw")
async def api_withdraw(request: WithdrawalRequest):
    """Process withdrawal"""
    result = await splitter.process_withdrawal(
        agent_telegram_id=request.agent_telegram_id,
        amount=request.amount,
        upi_id=request.upi_id
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"success": True, "data": result}

@router.get("/{telegram_id}")
async def api_get_agent(telegram_id: str):
    """Get agent details"""
    agent = await splitter._get_agent(telegram_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"success": True, "data": agent}

@router.get("/{telegram_id}/earnings")
async def api_get_earnings(telegram_id: str):
    """Get agent earnings report"""
    agent = await splitter._get_agent(telegram_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    available = agent.get("total_earnings", 0) - agent.get("total_withdrawn", 0)

    return {
        "success": True,
        "data": {
            "total_earnings": agent.get("total_earnings", 0),
            "total_withdrawn": agent.get("total_withdrawn", 0),
            "available_balance": available,
            "month_earnings": agent.get("month_earnings", 0),
            "level": agent.get("level", "Bronze"),
            "total_referrals": agent.get("total_referrals", 0)
        }
    }
