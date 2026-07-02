import os
import logging
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

async def handler(request: Request):
    try:
        params = dict(request.query_params)
        keyword = params.get("keyword", "").strip().lower()
        country = params.get("country", "").strip().upper()  # US, UK, CA, AU, DE, etc.
        category = params.get("category", "").strip().lower()
        
        # 🌍 WORLD WIDE JOB PORTALS — 50+ COUNTRIES
        rozgar_data = {
            "global_portals": {
                "linkedin": {
                    "name": "LinkedIn Jobs",
                    "site": "linkedin.com/jobs",
                    "regions": ["Worldwide"],
                    "type": "Professional Network"
                },
                "indeed": {
                    "name": "Indeed",
                    "site": "indeed.com",
                    "regions": ["US", "UK", "CA", "AU", "DE", "FR", "IN", "BR", "MX", "JP", "SG", "AE", "ZA", "NG"],
                    "type": "Job Aggregator"
                },
                "glassdoor": {
                    "name": "Glassdoor",
                    "site": "glassdoor.com",
                    "regions": ["US", "UK", "CA", "AU", "DE", "FR", "IN"],
                    "type": "Company Reviews + Jobs"
                },
                "monster": {
                    "name": "Monster Worldwide",
                    "site": "monster.com",
                    "regions": ["US", "UK", "CA", "AU", "DE", "FR", "IN", "SG", "HK"],
                    "type": "Job Board"
                },
                "simplyhired": {
                    "name": "SimplyHired",
                    "site": "simplyhired.com",
                    "regions": ["US", "UK", "CA", "AU"],
                    "type": "Job Aggregator"
                },
                "careerbuilder": {
                    "name": "CareerBuilder",
                    "site": "careerbuilder.com",
                    "regions": ["US", "CA", "UK", "DE", "FR", "NL", "SE"],
                    "type": "Job Board"
                },
                "ziprecruiter": {
                    "name": "ZipRecruiter",
                    "site": "ziprecruiter.com",
                    "regions": ["US", "CA", "UK"],
                    "type": "AI Job Matching"
                },
                "dice": {
                    "name": "Dice",
                    "site": "dice.com",
                    "regions": ["US", "UK"],
                    "type": "Tech Jobs"
                },
                "angel": {
                    "name": "AngelList / Wellfound",
                    "site": "angel.co",
                    "regions": ["US", "UK", "CA", "Remote"],
                    "type": "Startup Jobs"
                },
                "flexjobs": {
                    "name": "FlexJobs",
                    "site": "flexjobs.com",
                    "regions": ["US", "Remote Worldwide"],
                    "type": "Remote/Flexible"
                },
                "we_work_remotely": {
                    "name": "We Work Remotely",
                    "site": "weworkremotely.com",
                    "regions": ["Remote Worldwide"],
                    "type": "Remote Only"
                },
                "remoteok": {
                    "name": "RemoteOK",
                    "site": "remoteok.com",
                    "regions": ["Remote Worldwide"],
                    "type": "Remote Jobs"
                }
            },
            
            # 🌏 REGION-SPECIFIC PORTALS
            "regional_portals": {
                "US": {
                    "usajobs": {"name": "USA Jobs (Federal)", "site": "usajobs.gov", "type": "Government"},
                    "snagajob": {"name": "Snagajob", "site": "snagajob.com", "type": "Hourly/Part-time"},
                    "idealist": {"name": "Idealist", "site": "idealist.org", "type": "Non-profit"},
                    "hired": {"name": "Hired", "site": "hired.com", "type": "Tech"}
                },
                "UK": {
                    "reed": {"name": "Reed.co.uk", "site": "reed.co.uk", "type": "General"},
                    "totaljobs": {"name": "Totaljobs", "site": "totaljobs.com", "type": "General"},
                    "cwjobs": {"name": "CWJobs", "site": "cwjobs.co.uk", "type": "IT/Tech"},
                    "guardian_jobs": {"name": "Guardian Jobs", "site": "jobs.theguardian.com", "type": "Professional"}
                },
                "CA": {
                    "jobbank": {"name": "Job Bank Canada", "site": "jobbank.gc.ca", "type": "Government"},
                    "workopolis": {"name": "Workopolis", "site": "workopolis.com", "type": "General"},
                    "eluta": {"name": "Eluta", "site": "eluta.ca", "type": "Canada's Top Employers"}
                },
                "AU": {
                    "seek": {"name": "SEEK", "site": "seek.com.au", "type": "General"},
                    "jora": {"name": "Jora", "site": "jora.com", "type": "General"},
                    "careerone": {"name": "CareerOne", "site": "careerone.com.au", "type": "General"}
                },
                "DE": {
                    "stepstone": {"name": "StepStone", "site": "stepstone.de", "type": "General"},
                    "xing": {"name": "XING", "site": "xing.com", "type": "Professional Network"},
                    "arbeitsagentur": {"name": "Bundesagentur für Arbeit", "site": "arbeitsagentur.de", "type": "Government"}
                },
                "FR": {
                    "pole_emploi": {"name": "Pôle emploi", "site": "pole-emploi.fr", "type": "Government"},
                    "apec": {"name": "APEC", "site": "apec.fr", "type": "Executive"},
                    "lesjeudis": {"name": "LesJeudis", "site": "lesjeudis.com", "type": "IT"}
                },
                "IN": {
                    "ncs": {"name": "National Career Service", "site": "ncs.gov.in", "type": "Government"},
                    "naukri": {"name": "Naukri.com", "site": "naukri.com", "type": "General"},
                    "shine": {"name": "Shine.com", "site": "shine.com", "type": "General"},
                    "freshersworld": {"name": "Freshersworld", "site": "freshersworld.com", "type": "Entry Level"}
                },
                "SG": {
                    "mycareersfuture": {"name": "MyCareersFuture", "site": "mycareersfuture.gov.sg", "type": "Government"},
                    "jobstreet": {"name": "JobStreet", "site": "jobstreet.com.sg", "type": "General"},
                    "jobsdb": {"name": "JobsDB", "site": "jobsdb.com", "type": "General"}
                },
                "AE": {
                    "bayt": {"name": "Bayt", "site": "bayt.com", "type": "General"},
                    "dubizzle": {"name": "Dubizzle Jobs", "site": "dubizzle.com", "type": "General"},
                    "naukrigulf": {"name": "NaukriGulf", "site": "naukrigulf.com", "type": "General"}
                },
                "JP": {
                    "doda": {"name": "Doda", "site": "doda.jp", "type": "General"},
                    "rikunabi": {"name": "Rikunabi", "site": "rikunabi.com", "type": "New Grad"},
                    "mynavi": {"name": "Mynavi", "site": "mynavi.jp", "type": "General"}
                },
                "BR": {
                    "vagas": {"name": "Vagas.com.br", "site": "vagas.com.br", "type": "General"},
                    "infojobs": {"name": "InfoJobs", "site": "infojobs.com.br", "type": "General"},
                    "catho": {"name": "Catho", "site": "catho.com.br", "type": "General"}
                },
                "NG": {
                    "jobberman": {"name": "Jobberman", "site": "jobberman.com", "type": "General"},
                    "hotnigerianjobs": {"name": "Hot Nigerian Jobs", "site": "hotnigerianjobs.com", "type": "General"},
                    "ngcareers": {"name": "NGCareers", "site": "ngcareers.com", "type": "General"}
                },
                "ZA": {
                    "careers24": {"name": "Careers24", "site": "careers24.com", "type": "General"},
                    "jobmail": {"name": "Job Mail", "site": "jobmail.co.za", "type": "General"},
                    "pnet": {"name": "PNet", "site": "pnet.co.za", "type": "General"}
                }
            },
            
            # 🏛️ WORLD GOVT SCHEMES (Not just India)
            "govt_schemes": {
                "US": {
                    "usajobs": {"name": "USA Jobs Portal", "type": "Federal Employment", "site": "usajobs.gov"},
                    "americorps": {"name": "AmeriCorps", "type": "Service/Volunteer", "site": "americorps.gov"},
                    "usda_jobs": {"name": "USDA Jobs", "type": "Agriculture", "site": "usda.gov"}
                },
                "UK": {
                    "civil_service": {"name": "Civil Service Jobs", "type": "Government", "site": "civilservicejobs.gov.uk"},
                    "apprenticeships": {"name": "Apprenticeships", "type": "Skills Training", "site": "gov.uk/apply-apprenticeship"}
                },
                "CA": {
                    "job_bank": {"name": "Job Bank", "type": "Federal Jobs", "site": "jobbank.gc.ca"},
                    "youth_employment": {"name": "Youth Employment Strategy", "type": "Youth", "site": "canada.ca/youth"}
                },
                "DE": {
                    "arbeitsagentur": {"name": "Bundesagentur für Arbeit", "type": "Employment Agency", "site": "arbeitsagentur.de"},
                    "make_it_in_germany": {"name": "Make it in Germany", "type": "Skilled Immigration", "site": "make-it-in-germany.com"}
                },
                "IN": {
                    "mgnrega": {"name": "MGNREGA", "type": "Rural Jobs", "site": "nrega.nic.in"},
                    "pmkvy": {"name": "PM Kaushal Vikas Yojana", "type": "Skill Training", "site": "pmkvyofficial.org"},
                    "udyam": {"name": "Udyam Registration", "type": "MSME", "site": "udyamregistration.gov.in"},
                    "startup_india": {"name": "Startup India", "type": "Entrepreneurship", "site": "startupindia.gov.in"}
                },
                "AU": {
                    "jobactive": {"name": "jobactive", "type": "Employment Services", "site": "jobsearch.gov.au"},
                    "apprenticeships_au": {"name": "Australian Apprenticeships", "type": "Skills", "site": "australianapprenticeships.gov.au"}
                },
                "SG": {
                    "wsg": {"name": "Workforce Singapore", "type": "Employment", "site": "wsg.gov.sg"},
                    "skillsfuture": {"name": "SkillsFuture", "type": "Skills Training", "site": "skillsfuture.gov.sg"}
                }
            },
            
            # 🎯 GLOBAL CATEGORIES
            "categories": [
                "Software Development", "Data Science", "AI/ML", "Cybersecurity",
                "Cloud Computing", "DevOps", "Mobile Development", "Web Development",
                "Government", "Banking/Finance", "Healthcare", "Education",
                "Engineering", "Sales", "Marketing", "HR/Recruiting",
                "Legal", "Accounting", "Consulting", "Project Management",
                "Data Entry", "Customer Service", "Logistics", "Manufacturing",
                "Agriculture", "Construction", "Hospitality", "Retail",
                "Remote/Work From Home", "Freelance", "Part-time", "Internship"
            ],
            
            # 💡 TIPS FOR JOB SEEKERS
            "tips": {
                "resume": "Tailor resume for ATS (Applicant Tracking Systems)",
                "linkedin": "Optimize LinkedIn profile with keywords",
                "networking": "80% jobs filled through networking - attend meetups",
                "remote": "Search 'remote' + your skill for worldwide opportunities",
                "visa": "Check visa sponsorship options for target country",
                "salary": "Research salary benchmarks on Glassdoor/Payscale"
            }
        }
        
        # 🔍 FILTER LOGIC
        results = {
            "global_portals": [],
            "regional_portals": [],
            "govt_schemes": [],
            "tips": []
        }
        
        # Filter by keyword
        if keyword:
            # Search global portals
            for key, portal in rozgar_data["global_portals"].items():
                if (keyword in portal["name"].lower() or 
                    keyword in key or 
                    keyword in portal["type"].lower() or
                    any(keyword in r.lower() for r in portal["regions"])):
                    results["global_portals"].append({**portal, "id": key})
            
            # Search regional portals
            for region, portals in rozgar_data["regional_portals"].items():
                for key, portal in portals.items():
                    if (keyword in portal["name"].lower() or 
                        keyword in key or
                        keyword in region.lower()):
                        results["regional_portals"].append({**portal, "id": key, "country": region})
            
            # Search govt schemes
            for region, schemes in rozgar_data["govt_schemes"].items():
                for key, scheme in schemes.items():
                    if (keyword in scheme["name"].lower() or 
                        keyword in key or
                        keyword in region.lower()):
                        results["govt_schemes"].append({**scheme, "id": key, "country": region})
        
        # Filter by country
        if country:
            country_upper = country.upper()
            # Get regional portals for that country
            if country_upper in rozgar_data["regional_portals"]:
                results["regional_portals"] = [
                    {**v, "id": k, "country": country_upper} 
                    for k, v in rozgar_data["regional_portals"][country_upper].items()
                ]
            # Get govt schemes for that country
            if country_upper in rozgar_data["govt_schemes"]:
                results["govt_schemes"] = [
                    {**v, "id": k, "country": country_upper} 
                    for k, v in rozgar_data["govt_schemes"][country_upper].items()
                ]
            # Filter global portals that support this country
            results["global_portals"] = [
                {**v, "id": k} 
                for k, v in rozgar_data["global_portals"].items()
                if country_upper in v["regions"] or "Worldwide" in v["regions"] or "Remote Worldwide" in v["regions"]
            ]
        
        # Filter by category
        if category:
            matched_cats = [c for c in rozgar_data["categories"] if category in c.lower()]
            results["categories"] = matched_cats
        
        # Return results
        if keyword or country or category:
            total = (len(results["global_portals"]) + 
                    len(results["regional_portals"]) + 
                    len(results["govt_schemes"]))
            
            return JSONResponse(content={
                "success": True,
                "filters": {
                    "keyword": keyword or None,
                    "country": country or None,
                    "category": category or None
                },
                "results": results,
                "total": total,
                "message": f"🦁 Found {total} resources for your search!"
            })
        
        # Default response — ALL DATA
        return JSONResponse(content={
            "success": True,
            "message": "🦁 Singh Ji AI - World Wide Rozgar/Jobs",
            "stats": {
                "global_portals": len(rozgar_data["global_portals"]),
                "countries_covered": len(rozgar_data["regional_portals"]),
                "govt_schemes_countries": len(rozgar_data["govt_schemes"]),
                "categories": len(rozgar_data["categories"])
            },
            "countries": list(rozgar_data["regional_portals"].keys()),
            "global_portals": rozgar_data["global_portals"],
            "sample_regional": {k: list(v.keys()) for k, v in list(rozgar_data["regional_portals"].items())[:3]},
            "categories": rozgar_data["categories"],
            "tips": rozgar_data["tips"],
            "usage": {
                "search": "/api/rozgar?keyword=software",
                "country": "/api/rozgar?country=US",
                "category": "/api/rozgar?category=remote",
                "combined": "/api/rozgar?country=DE&keyword=tech"
            }
        })
        
    except Exception as e:
        logger.error(f"Rozgar error: {e}")
        return JSONResponse(status_code=500, content={
            "success": False, 
            "error": str(e),
            "message": "🦁 Singh Ji AI - Try again with different parameters"
        })
