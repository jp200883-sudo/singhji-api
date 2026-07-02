"""
💼 Singh Ji AI Ultra v7.0 — Rozgar/Jobs Module
"""
import os
import logging
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

# 🔑 KEYWORD MAPPING — Fix for 0 results
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

async def handler(request: Request):
    try:
        params = dict(request.query_params)
        keyword = params.get("keyword", "").strip().lower()
        country = params.get("country", "").strip().upper()
        lang = params.get("lang", "hi")
        
        # 🌍 WORLD JOB PORTALS
        portals = {
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
        
        govt_schemes = {
            "US": {"usajobs": {"name": "USA Jobs Portal", "type": "Federal", "site": "usajobs.gov"}, "americorps": {"name": "AmeriCorps", "type": "Service", "site": "americorps.gov"}},
            "UK": {"civil_service": {"name": "Civil Service Jobs", "type": "Government", "site": "civilservicejobs.gov.uk"}, "apprenticeships": {"name": "Apprenticeships", "type": "Skills", "site": "gov.uk/apply-apprenticeship"}},
            "CA": {"job_bank": {"name": "Job Bank", "type": "Federal", "site": "jobbank.gc.ca"}},
            "DE": {"arbeitsagentur": {"name": "Bundesagentur für Arbeit", "type": "Employment", "site": "arbeitsagentur.de"}, "make_it_in_germany": {"name": "Make it in Germany", "type": "Immigration", "site": "make-it-in-germany.com"}},
            "IN": {"mgnrega": {"name": "MGNREGA", "type": "Rural Jobs", "site": "nrega.nic.in"}, "pmkvy": {"name": "PM Kaushal Vikas Yojana", "type": "Skills", "site": "pmkvyofficial.org"}, "udyam": {"name": "Udyam Registration", "type": "MSME", "site": "udyamregistration.gov.in"}, "startup_india": {"name": "Startup India", "type": "Entrepreneurship", "site": "startupindia.gov.in"}},
            "AU": {"jobactive": {"name": "jobactive", "type": "Employment", "site": "jobsearch.gov.au"}},
            "SG": {"wsg": {"name": "Workforce Singapore", "type": "Employment", "site": "wsg.gov.sg"}, "skillsfuture": {"name": "SkillsFuture", "type": "Skills", "site": "skillsfuture.gov.sg"}}
        }
        
        categories = ["Software Development", "Data Science", "AI/ML", "Cybersecurity", "Cloud Computing", "DevOps", "Mobile Development", "Web Development", "Government", "Banking/Finance", "Healthcare", "Education", "Engineering", "Sales", "Marketing", "HR/Recruiting", "Legal", "Accounting", "Consulting", "Project Management", "Data Entry", "Customer Service", "Logistics", "Manufacturing", "Agriculture", "Construction", "Hospitality", "Retail", "Remote/Work From Home", "Freelance", "Part-time", "Internship"]
        
        tips = {"resume": "Tailor resume for ATS", "linkedin": "Optimize LinkedIn profile", "networking": "80% jobs via networking", "remote": "Search 'remote' + skill", "visa": "Check visa sponsorship", "salary": "Research on Glassdoor/Payscale"}
        
        # 🔍 FILTER with KEYWORD MAPPING
        result = {"global": [], "regional": [], "govt": [], "categories": [], "tips": tips}
        
        # Map keyword if exists
        search_term = KEYWORD_MAP.get(keyword, keyword) if keyword else ""
        
        if keyword:
            # Search in global portals
            for k, v in portals["global"].items():
                if keyword in v["name"].lower() or keyword in k or keyword in v["type"].lower():
                    result["global"].append({**v, "id": k})
            
            # Search in regional portals
            for reg, pts in portals["regional"].items():
                for k, v in pts.items():
                    if keyword in v["name"].lower() or keyword in k:
                        result["regional"].append({**v, "id": k, "country": reg})
            
            # Search in govt schemes
            for reg, schemes in govt_schemes.items():
                for k, v in schemes.items():
                    if keyword in v["name"].lower() or keyword in k:
                        result["govt"].append({**v, "id": k, "country": reg})
            
            # Search categories with mapped keyword
            result["categories"] = [
                c for c in categories 
                if (search_term and search_term.lower() in c.lower()) 
                or (keyword and keyword in c.lower())
            ]
        
        if country:
            cu = country.upper()
            if cu in portals["regional"]:
                result["regional"] = [{**v, "id": k, "country": cu} for k, v in portals["regional"][cu].items()]
            if cu in govt_schemes:
                result["govt"] = [{**v, "id": k, "country": cu} for k, v in govt_schemes[cu].items()]
            result["global"] = [{**v, "id": k} for k, v in portals["global"].items() if cu in v["regions"] or "Worldwide" in v["regions"] or "Remote" in v["regions"]]
        
        total = len(result["global"]) + len(result["regional"]) + len(result["govt"]) + len(result["categories"])
        
        # 🎙️ TTS MESSAGE
        tts_msg = f"रोज़गार मॉड्यूल। कुल {total} परिणाम मिले।"
        if country: tts_msg += f" देश: {country}।"
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
            "countries_supported": list(portals["regional"].keys()),
            "categories": categories,
            "usage": "/api/rozgar?keyword=software&country=US"
        })
        
    except Exception as e:
        logger.error(f"Rozgar error: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e), "tts": "कोई त्रुटि हुई। कृपया पुनः प्रयास करें।"})
