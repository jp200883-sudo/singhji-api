import os
import logging
import requests

logger = logging.getLogger(__name__)

DATA_GOV_API_KEY = os.environ.get("DATAGOVINDIA_API_KEY", "")
BASE_URL = "https://api.data.gov.in/resource/"

# सभी योजनाओं की resource_id सूची
SCHEMES = {
    "pmkisan": {
        "title": "PM Kisan Samman Nidhi (Districtwise Beneficiaries)",
        "resource_id": "47a0970a-9fef-427d-8cdd-767085fda87b"
    },
    "shg": {
        "title": "Village-wise Self Help Group (SHG) and Members Count",
        "resource_id": "d4206736-a28b-4552-8900-7e0c23c707ac"
    },
    "pmay_gramin": {
        "title": "Pradhan Mantri Awas Yojana (Grameen)",
        "resource_id": "9fed1fd9-f22f-4eed-976a-ba4b8bec6d6a"
    },
    "pmay_urban": {
        "title": "PMAY-Urban Central Assistance Released (2019-20 to 2023-24)",
        "resource_id": "adf5ebaa-f53d-41fd-8a17-13e178208074"
    },
    "ujjwala": {
        "title": "Pradhan Mantri Ujjwala Yojana (PMUY) Beneficiaries",
        "resource_id": "6f8b9f96-8608-4849-95b4-04488e502ac9"
    },
    "fasal_bima": {
        "title": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
        "resource_id": "102819a6-2e35-4f2a-9281-1a23c4d35918"
    },
    "mnrega": {
        "title": "District-wise MGNREGA Data at a Glance",
        "resource_id": "ee03643a-ee4c-48c2-ac30-9f2ff26ab722"
    },
    "jandhan": {
        "title": "Pradhan Mantri Jan-Dhan Yojana (PMJDY) Accounts",
        "resource_id": "57f2a52d-a74f-43ff-ac2d-2de810f46369"
    },
    "ayushman": {
        "title": "AB-PMJAY Central Funds Released (2018-19 to 2020-21)",
        "resource_id": "ed2aab60-db97-4dcb-9fa5-060f5b6e418f"
    },
    "saubhagya": {
        "title": "Saubhagya Scheme Grant Disbursed",
        "resource_id": "a462d196-c420-4e6e-84cb-6d5fe2d2f09d"
    },
    "mudra": {
        "title": "Pradhan Mantri Mudra Yojana (PMMY) Loans",
        "resource_id": "f004f414-6fb7-4772-a301-5a56d6a2023f"
    },
    "udyam": {
        "title": "List of MSME Registered Units under UDYAM",
        "resource_id": "8b68ae56-84cf-4728-a0a6-1be11028dea7"
    },
}


def fetch_scheme_data(scheme_key: str, filters: dict = None, limit: int = 20, offset: int = 0):
    """
    किसी भी योजना (scheme_key) का ताज़ा डेटा data.gov.in से लाता है।
    filters: {"state": "Uttar Pradesh"} जैसा dict, dataset के field name पर निर्भर करता है
    """
    if not DATA_GOV_API_KEY:
        return {"success": False, "error": "DATAGOVINDIA_API_KEY not set in environment"}

    scheme = SCHEMES.get(scheme_key)
    if not scheme:
        return {
            "success": False,
            "error": f"Unknown scheme '{scheme_key}'",
            "available_schemes": list(SCHEMES.keys())
        }

    url = f"{BASE_URL}{scheme['resource_id']}"
    params = {
        "api-key": DATA_GOV_API_KEY,
        "format": "json",
        "limit": limit,
        "offset": offset,
    }
    if filters:
        for field, value in filters.items():
            params[f"filters[{field}]"] = value

    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return {
                "success": True,
                "scheme": scheme_key,
                "title": scheme["title"],
                "records": data.get("records", data)
            }
        return {"success": False, "error": f"status {resp.status_code}", "body": resp.text[:300]}
    except Exception as e:
        logger.error(f"schemes fetch error [{scheme_key}]: {e}")
        return {"success": False, "error": str(e)}


def list_schemes():
    """सभी उपलब्ध योजनाओं की सूची (key + title)"""
    return [{"key": k, "title": v["title"]} for k, v in SCHEMES.items()]
