# backend/data/department_emails.py
# Maps complaint category + municipality name to the responsible department
# email address. If a specific municipality is not listed, the "default"
# address for that category is used as a fallback.

from typing import Optional

DEPARTMENT_EMAILS: dict[str, dict[str, str]] = {
    "WATER_SUPPLY": {
        "default":       "water@municipality.bg",
        "Божурище":      "water@bozhurishte.bg",
        "Ботевград":     "water@botevgrad.bg",
        "Годеч":         "water@godech.bg",
        "Горна Малина":  "water@gornamalina.bg",
        "Долна Баня":    "water@dolnabanya.bg",
        "Драгоман":      "water@dragoman.bg",
        "Елин Пелин":    "water@elinpelin.bg",
        "Ихтиман":       "water@ihtiman.bg",
        "Костенец":      "water@kostenets.bg",
        "Костинброд":    "water@kostinbrod.bg",
        "Своге":         "water@svoge.bg",
        "Сливница":      "water@slivnitsa.bg",
    },
    "ELECTRICITY": {
        "default":       "electricity@municipality.bg",
        "Божурище":      "electricity@bozhurishte.bg",
        "Ботевград":     "electricity@botevgrad.bg",
        "Годеч":         "electricity@godech.bg",
        "Горна Малина":  "electricity@gornamalina.bg",
        "Долна Баня":    "electricity@dolnabanya.bg",
        "Драгоман":      "electricity@dragoman.bg",
        "Елин Пелин":    "electricity@elinpelin.bg",
        "Ихтиман":       "electricity@ihtiman.bg",
        "Костенец":      "electricity@kostenets.bg",
        "Костинброд":    "electricity@kostinbrod.bg",
        "Своге":         "electricity@svoge.bg",
        "Сливница":      "electricity@slivnitsa.bg",
    },
    "ROADS": {
        "default":       "roads@municipality.bg",
        "Божурище":      "roads@bozhurishte.bg",
        "Ботевград":     "roads@botevgrad.bg",
        "Годеч":         "roads@godech.bg",
        "Горна Малина":  "roads@gornamalina.bg",
        "Долна Баня":    "roads@dolnabanya.bg",
        "Драгоман":      "roads@dragoman.bg",
        "Елин Пелин":    "roads@elinpelin.bg",
        "Ихтиман":       "roads@ihtiman.bg",
        "Костенец":      "roads@kostenets.bg",
        "Костинброд":    "roads@kostinbrod.bg",
        "Своге":         "roads@svoge.bg",
        "Сливница":      "roads@slivnitsa.bg",
    },
    "WASTE_MANAGEMENT": {
        "default":       "waste@municipality.bg",
        "Божурище":      "waste@bozhurishte.bg",
        "Ботевград":     "waste@botevgrad.bg",
        "Годеч":         "waste@godech.bg",
        "Горна Малина":  "waste@gornamalina.bg",
        "Долна Баня":    "waste@dolnabanya.bg",
        "Драгоман":      "waste@dragoman.bg",
        "Елин Пелин":    "waste@elinpelin.bg",
        "Ихтиман":       "waste@ihtiman.bg",
        "Костенец":      "waste@kostenets.bg",
        "Костинброд":    "waste@kostinbrod.bg",
        "Своге":         "waste@svoge.bg",
        "Сливница":      "waste@slivnitsa.bg",
    },
    "PUBLIC_ORDER": {
        "default":       "publicorder@municipality.bg",
        "Божурище":      "publicorder@bozhurishte.bg",
        "Ботевград":     "publicorder@botevgrad.bg",
        "Годеч":         "publicorder@godech.bg",
        "Горна Малина":  "publicorder@gornamalina.bg",
        "Долна Баня":    "publicorder@dolnabanya.bg",
        "Драгоман":      "publicorder@dragoman.bg",
        "Елин Пелин":    "publicorder@elinpelin.bg",
        "Ихтиман":       "publicorder@ihtiman.bg",
        "Костенец":      "publicorder@kostenets.bg",
        "Костинброд":    "publicorder@kostinbrod.bg",
        "Своге":         "publicorder@svoge.bg",
        "Сливница":      "publicorder@slivnitsa.bg",
    },
    "GREEN_SPACES": {
        "default":       "greenspaces@municipality.bg",
        "Божурище":      "greenspaces@bozhurishte.bg",
        "Ботевград":     "greenspaces@botevgrad.bg",
        "Годеч":         "greenspaces@godech.bg",
        "Горна Малина":  "greenspaces@gornamalina.bg",
        "Долна Баня":    "greenspaces@dolnabanya.bg",
        "Драгоман":      "greenspaces@dragoman.bg",
        "Елин Пелин":    "greenspaces@elinpelin.bg",
        "Ихтиман":       "greenspaces@ihtiman.bg",
        "Костенец":      "greenspaces@kostenets.bg",
        "Костинброд":    "greenspaces@kostinbrod.bg",
        "Своге":         "greenspaces@svoge.bg",
        "Сливница":      "greenspaces@slivnitsa.bg",
    },
    "ADMINISTRATIVE": {
        "default":       "admin@municipality.bg",
        "Божурище":      "admin@bozhurishte.bg",
        "Ботевград":     "admin@botevgrad.bg",
        "Годеч":         "admin@godech.bg",
        "Горна Малина":  "admin@gornamalina.bg",
        "Долна Баня":    "admin@dolnabanya.bg",
        "Драгоман":      "admin@dragoman.bg",
        "Елин Пелин":    "admin@elinpelin.bg",
        "Ихтиман":       "admin@ihtiman.bg",
        "Костенец":      "admin@kostenets.bg",
        "Костинброд":    "admin@kostinbrod.bg",
        "Своге":         "admin@svoge.bg",
        "Сливница":      "admin@slivnitsa.bg",
    },
    "OTHER": {
        "default":       "info@municipality.bg",
        "Божурище":      "info@bozhurishte.bg",
        "Ботевград":     "info@botevgrad.bg",
        "Годеч":         "info@godech.bg",
        "Горна Малина":  "info@gornamalina.bg",
        "Долна Баня":    "info@dolnabanya.bg",
        "Драгоман":      "info@dragoman.bg",
        "Елин Пелин":    "info@elinpelin.bg",
        "Ихтиман":       "info@ihtiman.bg",
        "Костенец":      "info@kostenets.bg",
        "Костинброд":    "info@kostinbrod.bg",
        "Своге":         "info@svoge.bg",
        "Сливница":      "info@slivnitsa.bg",
    },
}


def get_department_email(category: str, municipality: Optional[str]) -> str:
    """Return the responsible department email for a category and municipality.

    Falls back to the category default if the municipality is not found.
    Falls back to the global default if the category itself is unknown.
    """
    category_map = DEPARTMENT_EMAILS.get(category, DEPARTMENT_EMAILS["OTHER"])
    if municipality and municipality in category_map:
        return category_map[municipality]
    return category_map.get("default", "info@municipality.bg")
