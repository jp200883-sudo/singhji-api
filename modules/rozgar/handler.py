"""
💼 Singh Ji AI Ultra v8.0 — Rozgar/Jobs Module
(FIXED: keyword + country ab intersection hain, replacement nahi;
 KEYWORD_MAP ab portals/regional/govt search me bhi lagu)
"""
import os
import logging
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

KEYWORD_MAP = {
    "software": "Software Development",
    "developer": "Software Development",
    "coding": "Software Development",
    "programmer": "Software Development",
    "it": "Software Development",
    "data": "Data Science",
    "ai": "AI/ML",
    "machine learning": "AI/ML",
    "ml": "AI/ML",
    "security": "Cybersecurity",
    "cloud": "Cloud Computing",
    "devops": "DevOps",
    "mobile": "Mobile Development",
    "app": "Mobile Development",
    "web": "Web Development",
    "sarkari": "Government",
    "government": "Government",
    "govt": "Government",
    "bank": "Banking/Finance",
    "finance": "Banking/Finance",
    "doctor": "Healthcare",
    "nurse": "Healthcare",
    "medical": "Healthcare",
    "teacher": "Education",
    "professor": "Education",
    "engineer": "Engineering",
    "sales": "Sales",
    "marketing": "Marketing",
    "hr": "HR/Recruiting",
    "legal": "Legal",
    "lawyer": "Legal",
    "accounting": "Accounting",
    "consulting": "Consulting",
    "project": "Project Management",
    "data entry": "Data Entry",
    "customer": "Customer Service",
    "driver": "Logistics",
    "factory": "Manufacturing",
    "farm": "Agriculture",
    "construction": "Construction",
    "hotel": "Hospitality",
    "retail": "Retail",
    "remote": "Remote/Work From Home",
    "work from home": "Remote/Work From Home",
    "wfh": "Remote/Work From Home",
    "freelance": "Freelance",
    "part time": "Part-time",
    "part-time": "Part-time",
    "intern": "Internship",
    "internship": "Internship",
    "trainee": "Internship"
}

PORTALS = {
    "global": {
        "linkedin": {"name": "LinkedIn Jobs", "site": "linkedin.com/jobs", "type": "Professional", "regions": ["Worldwide"]},
        "indeed": {"name": "Indeed", "site": "indeed.com", "type": "Aggregator", "regions": ["US","UK","CA","AU","DE","FR","IN","BR","MX","JP","SG","AE","ZA","NG"]},
        "glassdoor": {"name": "Glassdoor", "site": "glassdoor.com", "type": "Reviews+Jobs", "regions": ["US","UK","CA","AU","DE","FR","IN"]},
        "monster": {"name": "Monster", "site": "monster.com", "type": "Job Board", "regions": ["US","UK","CA","AU","DE","FR","IN","SG","HK"]},
        "simplyhired": {"name": "SimplyHired", "site": "simplyhired.com", "type": "Aggregator", "regions": ["US","UK","CA","AU"]},
        "careerbuilder": {"name": "CareerBuilder", "site": "careerbuilder.com", "type": "Job Board", "regions": ["US","CA","UK","DE","FR","NL","SE"]},
        "ziprecruiter": {"name": "ZipRecruiter", "site": "ziprecruiter.com", "type": "AI Matching", "regions": ["US","CA","UK"]},
        "dice": {"name": "Dice", "site": "dice.com", "type": "Tech Jobs", "regions": ["US","UK"]},
        "angel": {"name": "AngelList/Wellfound", "site": "angel.co", "type": "Startup Jobs", "regions": ["US","UK","CA","Remote"]},
        "flexjobs": {"name": "FlexJobs", "site": "flexjobs.com", "type": "Remote/Flexible", "regions": ["US","Remote"]},
        "weworkremotely": {"name": "We Work Remotely", "site": "weworkremotely.com", "type": "Remote Only", "regions": ["Remote"]},
        "remoteok": {"name": "RemoteOK", "site": "remoteok.com", "type": "Remote Jobs", "regions": ["Remote"]}
    },
    "regional": {
        "US": {"usajobs": {"name": "USA Jobs (Federal)", "site": "usajobs.gov", "type": "Government"}, "snagajob": {"name": "Snagajob", "site": "snagajob.com", "type": "Hourly"}, "idealist": {"name": "Idealist", "site": "idealist.org", "type": "Non-profit"}},
        "UK": {"reed": {"name": "Reed.co.uk", "site": "reed.co.uk", "type": "General"}, "totaljobs": {"name": "Totaljobs", "site": "totaljobs.com", "type": "General"}, "cwjobs": {"name": "CWJobs", "site": "cwjobs.co.uk", "type": "IT"}},
        "CA": {"jobbank": {"name": "Job Bank Canada", "site": "jobbank.gc.ca", "type": "Government"}, "workopolis": {"name": "Workopolis", "site": "workopolis.com", "type": "General"}},
        "AU": {"seek": {"name": "SEEK", "site": "seek.com.au", "type": "General"}, "jora": {"name": "Jora", "site": "jora.com", "type": "General"}},
        "DE": {"stepstone": {"name": "StepStone", "site": "stepstone.de", "type": "General"}, "xing": {"name": "XING", "site": "xing.com", "type": "Professional"}, "arbeitsagentur": {"name": "Bundesagentur für Arbeit", "site": "arbeitsagentur.de", "type": "Government"}},
        "FR": {"pole_emploi": {"name": "Pôle emploi", "site": "pole-emploi.fr", "type": "Government"}, "apec": {"name": "APEC", "site": "apec.fr", "type": "Executive"}},
        "IN": {"ncs": {"name": "National Career Service", "site": "ncs.gov.in", "type": "Government"}, "naukri": {"name": "Naukri.com", "site": "naukri.com", "type": "General"}, "shine": {"name": "Shine.com", "site": "shine.com", "type": "General"}},
        "SG": {"mycareersfuture": {"name": "MyCareersFuture", "site": "mycareersfuture.gov.sg", "type": "Government"}, "jobstreet": {"name": "JobStreet", "site": "jobstreet.com.sg", "type": "General"}},
        "AE": {"bayt": {"name": "Bayt", "site": "bayt.com", "type": "General"}, "dubizzle": {"name": "Dubizzle Jobs", "site": "dubizzle.com", "type": "General"}},
        "JP": {"doda": {"name": "Doda", "site": "doda.jp", "type": "General"}, "rikunabi": {"name": "Rikunabi", "site": "rikunabi.com", "type": "New Grad"}},
        "BR": {"vagas": {"name": "Vagas.com.br", "site": "vagas.com.br", "type": "General"}, "infojobs": {"name": "InfoJobs", "site": "infojobs.com.br", "type": "General"}},
        "NG": {"jobberman": {"name": "Jobberman", "site": "jobberman.com", "type": "General"}, "hotnigerianjobs": {"name": "Hot Nigerian Jobs", "site": "hotnigerianjobs.com", "type": "General"}},
        "ZA": {"careers24": {"name": "Careers24", "site": "careers24.com", "type": "General"}, "pnet": {"name": "PNet", "site": "pnet.co.za", "type": "General"}}
    }
}

GOVT_SCHEMES = {
    "US": {"usajobs": {"name": "USA Jobs Portal", "type": "Federal", "site": "usajobs.gov"}, "americorps": {"name": "AmeriCorps", "type": "Service", "site": "americorps.gov"}},
    "UK": {"civil_service": {"name": "Civil Service Jobs", "type": "Government", "site": "civilservicejobs.gov.uk"}, "apprenticeships": {"name": "Apprenticeships", "type": "Skills", "site": "gov.uk/apply-apprenticeship"}},
    "CA": {"job_bank": {"name": "Job Bank", "type": "Federal", "site": "jobbank.gc.ca"}},
    "DE": {"arbeitsagentur": {"name": "Bundesagentur für Arbeit", "type": "Employment", "site": "arbeitsagentur.de"}, "make_it_in_germany": {"name": "Make it in Germany", "type": "Immigration", "site": "make-it-in-germany.com"}},
    "IN": {"mgnrega": {"name": "MGNREGA", "type": "Rural Jobs", "site": "nrega.nic.in"}, "pmkvy": {"name": "PM Kaushal Vikas Yojana", "type": "Skills", "site": "pmkvyofficial.org"}, "udyam": {"name": "Udyam Registration", "type": "MSME", "site": "udyamregistration.gov.in"}, "startup_india": {"name": "Startup India", "type": "Entrepreneurship", "site": "startupindia.gov.in"}},
    "AU": {"jobactive": {"name": "jobactive", "type": "Employment", "site": "jobsearch.gov.au"}},
    "SG": {"wsg": {"name": "Workforce Singapore", "type": "Employment", "site": "wsg.gov.sg"}, "skillsfuture": {"name": "SkillsFuture", "type": "Skills", "site": "skillsfuture.gov.sg"}}
}

CATEGORIES = ["Software Development", "Data Science", "AI/ML", "Cybersecurity", "Cloud Computing", "DevOps", "Mobile Development", "Web Development", "Government", "Banking/Finance", "Healthcare", "Education", "Engineering", "Sales", "Marketing", "HR/Recruiting", "Legal", "Accounting", "Consulting", "Project Management", "Data Entry", "Customer Service", "Logistics", "Manufacturing", "Agriculture", "Construction", "Hospitality", "Retail", "Remote/Work From Home", "Freelance", "Part-time", "Internship"]

TIPS = {"resume": "Tailor resume for ATS", "linkedin": "Optimize LinkedIn profile", "networking": "80% jobs via networking", "remote": "Search 'remote' + skill", "visa": "Check visa sponsorship", "salary": "Research on Glassdoor/Payscale"}


def _matches(term: str, name: str, key: str, type_: str = "") -> bool:
    term = term.lower()
    return term in name.lower() or term in key.lower() or (type_ and term in type_.lower())


def _search_keyword(keyword: str, search_term: str) -> dict:
    """Keyword (aur uska mapped search_term, dono) se global/regional/govt/categories khoje."""
    out = {"global": [], "regional": [], "govt": [], "categories": []}
    terms = {keyword} if not search_term or search_term == keyword else {keyword, search_term}

    for k, v in PORTALS["global"].items():
        if any(_matches(t, v["name"], k, v["type"]) for t in terms):
            out["global"].append({**v, "id": k})

    for reg, pts in PORTALS["regional"].items():
        for k, v in pts.items():
            if any(_matches(t, v["name"], k) for t in terms):
                out["regional"].append({**v, "id": k, "country": reg})

    for reg, schemes in GOVT_SCHEMES.items():
        for k, v in schemes.items():
            if any(_matches(t, v["name"], k) for t in terms):
                out["govt"].append({**v, "id": k, "country": reg})

    out["categories"] = [c for c in CATEGORIES if any(t.lower() in c.lower() for t in terms)]
    return out


def _filter_by_country(data: dict, country: str) -> dict:
    """Diye gaye result set ko sirf ek desh tak seemit karta hai — keyword hits ko replace nahi, unhi ko chhaanta hai."""
    cu = country.upper()
    return {
        "global": [p for p in data["global"] if cu in PORTALS["global"].get(p["id"], {}).get("regions", []) or "Worldwide" in PORTALS["global"].get(p["id"], {}).get("regions", []) or "Remote" in PORTALS["global"].get(p["id"], {}).get("regions", [])],
        "regional": [p for p in data["regional"] if p.get("country") == cu],
        "govt": [p for p in data["govt"] if p.get("country") == cu],
        "categories": data["categories"],
    }


def _country_only(country: str) -> dict:
    cu = country.upper()
    return {
        "global": [{**v, "id": k} for k, v in PORTALS["global"].items() if cu in v["regions"] or "Worldwide" in v["regions"] or "Remote" in v["regions"]],
        "regional": [{**v, "id": k, "country": cu} for k, v in PORTALS["regional"].get(cu, {}).items()],
        "govt": [{**v, "id": k, "country": cu} for k, v in GOVT_SCHEMES.get(cu, {}).items()],
        "categories": [],
    }


async def handler(request: Request):
    try:
        method = request.method
        if method == "GET":
            params = dict(request.query_params)
        else:
            params = await request.json()

        keyword = str(params.get("keyword", "")).strip().lower()
        country = str(params.get("country", "")).strip().upper()

        search_term = KEYWORD_MAP.get(keyword, keyword) if keyword else ""

        if keyword and country:
            # Dono diye gaye hain -> pehle keyword se khojo, phir country tak seemit karo (intersection)
            result = _search_keyword(keyword, search_term)
            result = _filter_by_country(result, country)
        elif keyword:
            result = _search_keyword(keyword, search_term)
        elif country:
            result = _country_only(country)
        else:
            result = {"global": [], "regional": [], "govt": [], "categories": []}

        result["tips"] = TIPS
        total = len(result["global"]) + len(result["regional"]) + len(result["govt"]) + len(result["categories"])

        tts_msg = f"रोज़गार मॉड्यूल। कुल {total} पोर्टल-सुझाव मिले।"
        if country:
            tts_msg += f" देश: {country}।"
        if keyword:
            mapped = f" (मैप्ड: {search_term})" if search_term != keyword and search_term else ""
            tts_msg += f" कीवर्ड: {keyword}{mapped}।"
        if result["categories"]:
            tts_msg += f" श्रेणियाँ: {', '.join(result['categories'][:3])}।"

        return JSONResponse({
            "success": True,
            "tts": tts_msg,
            "filters": {"keyword": keyword or None, "country": country or None, "mapped_keyword": search_term if search_term != keyword else None},
            "results": result,
            "total": total,
            "countries_supported": list(PORTALS["regional"].keys()),
            "categories": CATEGORIES,
            "usage": "/api/rozgar?keyword=software&country=US"
        })

    except Exception as e:
        logger.error(f"Rozgar error: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e), "tts": "कोई त्रुटि हुई। कृपया पुनः प्रयास करें।"})
