from typing import Optional

DEPARTMENT_EMAILS: dict[str, dict[str, str]] = {
    "WATER_SUPPLY": {
        "Божурище":    "obshtina@bozhurishte.bg",
        "Ботевград":   "obshtina@botevgrad.org",
        "Годеч":       "office@godech.bg",
        "Горна Малина":"gmalina@gornamalina.bg",
        "Долна Баня":  "obshtinadb@abv.bg",
        "Драгоман":    "obshtina_dragoman@abv.bg",
        "Елин Пелин":  "obshtina@elinpelin.org",
        "Ихтиман":     "obshtina_ihtiman@mail.bg",
        "Костенец":    "kostenetz_adm@kostenetz.com",
        "Костинброд":  "cao@kostinbrod.bg",
        "Своге":       "delovodstvo@svoge.bg",
        "Сливница":    "slivnitsa@slivnitsa.bg",
    },
    "ELECTRICITY": {
        "Божурище":    "obshtina@bozhurishte.bg",
        "Ботевград":   "obshtina@botevgrad.org",
        "Годеч":       "office@godech.bg",
        "Горна Малина":"gmalina@gornamalina.bg",
        "Долна Баня":  "obshtinadb@abv.bg",
        "Драгоман":    "obshtina_dragoman@abv.bg",
        "Елин Пелин":  "obshtina@elinpelin.org",
        "Ихтиман":     "obshtina_ihtiman@mail.bg",
        "Костенец":    "kostenetz_adm@kostenetz.com",
        "Костинброд":  "cao@kostinbrod.bg",
        "Своге":       "delovodstvo@svoge.bg",
        "Сливница":    "slivnitsa@slivnitsa.bg",
    },
    "ROADS": {
        "Божурище":    "obshtina@bozhurishte.bg",
        "Ботевград":   "obshtina@botevgrad.org",
        "Годеч":       "office@godech.bg",
        "Горна Малина":"gmalina@gornamalina.bg",
        "Долна Баня":  "obshtinadb@abv.bg",
        "Драгоман":    "obshtina_dragoman@abv.bg",
        "Елин Пелин":  "info@bkd-elinpelin.com",
        "Ихтиман":     "obshtina_ihtiman@mail.bg",
        "Костенец":    "kostenetz_adm@kostenetz.com",
        "Костинброд":  "cao@kostinbrod.bg",
        "Своге":       "delovodstvo@svoge.bg",
        "Сливница":    "slivnitsa@slivnitsa.bg",
    },
    "WASTE_MANAGEMENT": {
        "Божурище":    "obshtina@bozhurishte.bg",
        "Ботевград":   "obshtina@botevgrad.org",
        "Годеч":       "office@godech.bg",
        "Горна Малина":"gmalina@gornamalina.bg",
        "Долна Баня":  "obshtinadb@abv.bg",
        "Драгоман":    "obshtina_dragoman@abv.bg",
        "Елин Пелин":  "info@bkd-elinpelin.com",
        "Ихтиман":     "obshtina_ihtiman@mail.bg",
        "Костенец":    "kostenetz_adm@kostenetz.com",
        "Костинброд":  "cao@kostinbrod.bg",
        "Своге":       "delovodstvo@svoge.bg",
        "Сливница":    "slivnitsa@slivnitsa.bg",
    },
    "PUBLIC_ORDER": {
        "Божурище":    "obshtina@bozhurishte.bg",
        "Ботевград":   "obshtina@botevgrad.org",
        "Годеч":       "office@godech.bg",
        "Горна Малина":"gmalina@gornamalina.bg",
        "Долна Баня":  "obshtinadb@abv.bg",
        "Драгоман":    "obshtina_dragoman@abv.bg",
        "Елин Пелин":  "obshtina@elinpelin.org",
        "Ихтиман":     "obshtina_ihtiman@mail.bg",
        "Костенец":    "kostenetz_adm@kostenetz.com",
        "Костинброд":  "inspektorat.kb@gmail.com",
        "Своге":       "delovodstvo@svoge.bg",
        "Сливница":    "slivnitsa@slivnitsa.bg",
    },
    "GREEN_SPACES": {
        "Божурище":    "obshtina@bozhurishte.bg",
        "Ботевград":   "obshtina@botevgrad.org",
        "Годеч":       "office@godech.bg",
        "Горна Малина":"gmalina@gornamalina.bg",
        "Долна Баня":  "obshtinadb@abv.bg",
        "Драгоман":    "obshtina_dragoman@abv.bg",
        "Елин Пелин":  "info@bkd-elinpelin.com",
        "Ихтиман":     "obshtina_ihtiman@mail.bg",
        "Костенец":    "kostenetz_adm@kostenetz.com",
        "Костинброд":  "cao@kostinbrod.bg",
        "Своге":       "delovodstvo@svoge.bg",
        "Сливница":    "slivnitsa@slivnitsa.bg",
    },
    "ADMINISTRATIVE": {
        "Божурище":    "obshtina@bozhurishte.bg",
        "Ботевград":   "obshtina@botevgrad.org",
        "Годеч":       "office@godech.bg",
        "Горна Малина":"gmalina@gornamalina.bg",
        "Долна Баня":  "obshtinadb@abv.bg",
        "Драгоман":    "obshtina_dragoman@abv.bg",
        "Елин Пелин":  "cao_elinpelin@abv.bg",
        "Ихтиман":     "obshtina_ihtiman@mail.bg",
        "Костенец":    "kostenetz_adm@kostenetz.com",
        "Костинброд":  "cao@kostinbrod.bg",
        "Своге":       "delovodstvo@svoge.bg",
        "Сливница":    "slivnitsa@slivnitsa.bg",
    },
    "OTHER": {
        "Божурище":    "obshtina@bozhurishte.bg",
        "Ботевград":   "obshtina@botevgrad.org",
        "Годеч":       "office@godech.bg",
        "Горна Малина":"gmalina@gornamalina.bg",
        "Долна Баня":  "obshtinadb@abv.bg",
        "Драгоман":    "obshtina_dragoman@abv.bg",
        "Елин Пелин":  "obshtina@elinpelin.org",
        "Ихтиман":     "obshtina_ihtiman@mail.bg",
        "Костенец":    "kostenetz_adm@kostenetz.com",
        "Костинброд":  "cao@kostinbrod.bg",
        "Своге":       "delovodstvo@svoge.bg",
        "Сливница":    "slivnitsa@slivnitsa.bg",
    },
}

# ============================================================
# QUICK REFERENCE: Official websites & alternative emails
# ============================================================
MUNICIPALITY_META: dict[str, dict[str, Optional[str]]] = {
    "Божурище":    {"site": "bozhurishte.bg",         "alt": None},
    "Ботевград":   {"site": "botevgrad.bg",            "alt": None},
    "Годеч":       {"site": "godech.bg",               "alt": "obshtina_godech@abv.bg"},
    "Горна Малина":{"site": "gornamalina.bg",          "alt": "gmalina@abv.bg"},
    "Долна Баня":  {"site": "dolna-banya.net",         "alt": None},
    "Драгоман":    {"site": "dragoman.bg",             "alt": None},
    "Елин Пелин":  {"site": "elinpelin.org",           "alt": "obshtina@elinpelin.org"},
    "Ихтиман":     {"site": "ihtiman-obshtina.com",    "alt": "obshtina_ixtiman@mail.bg"},
    "Костенец":    {"site": "kostenetz.com",           "alt": "kostenetz_adm@yahoo.com"},
    "Костинброд":  {"site": "kostinbrod.bg",           "alt": None},
    "Своге":       {"site": "svoge.bg",                "alt": "kmet@svoge.bg"},
    "Сливница":    {"site": "slivnitsa.bg",            "alt": None},
}

def get_department_email(category: str, municipality: Optional[str]) -> str:
    """Return the responsible department email for a category and municipality.

    Falls back to the global default if the category itself is unknown or if the
    municipality is missing/unrecognized.
    """
    category_map = DEPARTMENT_EMAILS.get(category, DEPARTMENT_EMAILS["OTHER"])
    
    if municipality and municipality in category_map:
        return category_map[municipality]
        
    # If municipality fails, grab the first fallback email available from OTHER
    return DEPARTMENT_EMAILS["OTHER"]["Своге"]

