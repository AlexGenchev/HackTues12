# backend/data/municipalities.py
# Lookup dictionary mapping Bulgarian village/city names (lowercase) to their
# region and municipality. Derived from the original
# dictionary_villages_cities_Water.txt file.
#
# Usage:
#   from backend.data.municipalities import MUNICIPALITY_MAP
#   info = MUNICIPALITY_MAP.get("ботевград")
#   # -> {"region": "София", "municipality": "Ботевград"}

MUNICIPALITY_MAP = {
    # --- Божурище ---
    "божурище":   {"region": "София", "municipality": "Божурище"},
    "гурмазово":  {"region": "София", "municipality": "Божурище"},
    "златуша":    {"region": "София", "municipality": "Божурище"},
    "пожарево":   {"region": "София", "municipality": "Божурище"},
    "пролеша":    {"region": "София", "municipality": "Божурище"},
    "росоман":    {"region": "София", "municipality": "Божурище"},
    "хераково":   {"region": "София", "municipality": "Божурище"},
    "храбърско":  {"region": "София", "municipality": "Божурище"},

    # --- Ботевград ---
    "ботевград":  {"region": "София", "municipality": "Ботевград"},
    "врачеш":     {"region": "София", "municipality": "Ботевград"},
    "гурково":    {"region": "София", "municipality": "Ботевград"},
    "елов дол":   {"region": "София", "municipality": "Ботевград"},
    "краево":     {"region": "София", "municipality": "Ботевград"},
    "липница":    {"region": "София", "municipality": "Ботевград"},
    "литаково":   {"region": "София", "municipality": "Ботевград"},
    "новачене":   {"region": "София", "municipality": "Ботевград"},
    "радотина":   {"region": "София", "municipality": "Ботевград"},
    "рашково":    {"region": "София", "municipality": "Ботевград"},
    "скравена":   {"region": "София", "municipality": "Ботевград"},
    "трудовец":   {"region": "София", "municipality": "Ботевград"},

    # --- Годеч ---
    "годеч":      {"region": "София", "municipality": "Годеч"},
    "браковци":   {"region": "София", "municipality": "Годеч"},
    "букоровци":  {"region": "София", "municipality": "Годеч"},
    "бърля":      {"region": "София", "municipality": "Годеч"},
    "връдловци":  {"region": "София", "municipality": "Годеч"},
    "върбница":   {"region": "София", "municipality": "Годеч"},
    "гинци":      {"region": "София", "municipality": "Годеч"},
    "голеш":      {"region": "София", "municipality": "Годеч"},
    "губеш":      {"region": "София", "municipality": "Годеч"},
    "каленовци":  {"region": "София", "municipality": "Годеч"},
    "комщица":    {"region": "София", "municipality": "Годеч"},
    "лопушня":    {"region": "София", "municipality": "Годеч"},
    "мургаш":     {"region": "София", "municipality": "Годеч"},
    "равна":      {"region": "София", "municipality": "Годеч"},
    "разбоище":   {"region": "София", "municipality": "Годеч"},
    "ропот":      {"region": "София", "municipality": "Годеч"},
    "смолча":     {"region": "София", "municipality": "Годеч"},

    # --- Горна Малина ---
    "горна малина":    {"region": "Горна Малина", "municipality": "Горна Малина"},
    "априлово":        {"region": "Горна Малина", "municipality": "Горна Малина"},
    "байлово":         {"region": "Горна Малина", "municipality": "Горна Малина"},
    "белопопци":       {"region": "Горна Малина", "municipality": "Горна Малина"},
    "гайтанево":       {"region": "Горна Малина", "municipality": "Горна Малина"},
    "горно камарци":   {"region": "Горна Малина", "municipality": "Горна Малина"},
    "долна малина":    {"region": "Горна Малина", "municipality": "Горна Малина"},
    "долно камарци":   {"region": "Горна Малина", "municipality": "Горна Малина"},
    "макоцево":        {"region": "Горна Малина", "municipality": "Горна Малина"},
    "негушево":        {"region": "Горна Малина", "municipality": "Горна Малина"},
    "осоица":          {"region": "Горна Малина", "municipality": "Горна Малина"},
    "саранци":         {"region": "Горна Малина", "municipality": "Горна Малина"},
    "стъргел":         {"region": "Горна Малина", "municipality": "Горна Малина"},
    "чеканчево":       {"region": "Горна Малина", "municipality": "Горна Малина"},

    # --- Долна Баня ---
    "долна баня":  {"region": "Долна Баня", "municipality": "Долна Баня"},
    "гуцал":       {"region": "Долна Баня", "municipality": "Долна Баня"},
    "марица":      {"region": "Долна Баня", "municipality": "Долна Баня"},
    "радуил":      {"region": "Долна Баня", "municipality": "Долна Баня"},
    "свети спас":  {"region": "Долна Баня", "municipality": "Долна Баня"},

    # --- Драгоман ---
    "драгоман":        {"region": "Драгоман", "municipality": "Драгоман"},
    "беренде":         {"region": "Драгоман", "municipality": "Драгоман"},
    "беренде извор":   {"region": "Драгоман", "municipality": "Драгоман"},
    "вишан":           {"region": "Драгоман", "municipality": "Драгоман"},
    "владиславци":     {"region": "Драгоман", "municipality": "Драгоман"},
    "габер":           {"region": "Драгоман", "municipality": "Драгоман"},
    "големо малово":   {"region": "Драгоман", "municipality": "Драгоман"},
    "грълска падина":  {"region": "Драгоман", "municipality": "Драгоман"},
    "калотина":        {"region": "Драгоман", "municipality": "Драгоман"},
    "камбелевци":      {"region": "Драгоман", "municipality": "Драгоман"},
    "круша":           {"region": "Драгоман", "municipality": "Драгоман"},
    "липинци":         {"region": "Драгоман", "municipality": "Драгоман"},
    "мало малово":     {"region": "Драгоман", "municipality": "Драгоман"},
    "несла":           {"region": "Драгоман", "municipality": "Драгоман"},
    "ново бърдо":      {"region": "Драгоман", "municipality": "Драгоман"},
    "раяновци":        {"region": "Драгоман", "municipality": "Драгоман"},
    "табан":           {"region": "Драгоман", "municipality": "Драгоман"},

    # --- Елин Пелин ---
    "елин пелин":       {"region": "Елин Пелин", "municipality": "Елин Пелин"},
    "голяма раковица":  {"region": "Елин Пелин", "municipality": "Елин Пелин"},
    "григорево":        {"region": "Елин Пелин", "municipality": "Елин Пелин"},
    "доганово":         {"region": "Елин Пелин", "municipality": "Елин Пелин"},
    "елешница":         {"region": "Елин Пелин", "municipality": "Елин Пелин"},
    "караполци":        {"region": "Елин Пелин", "municipality": "Елин Пелин"},

    # --- Ихтиман ---
    "ихтиман":     {"region": "Ихтиман", "municipality": "Ихтиман"},
    "белица":      {"region": "Ихтиман", "municipality": "Ихтиман"},
    "боерица":     {"region": "Ихтиман", "municipality": "Ихтиман"},
    "борика":      {"region": "Ихтиман", "municipality": "Ихтиман"},
    "вакарел":     {"region": "Ихтиман", "municipality": "Ихтиман"},
    "венковец":    {"region": "Ихтиман", "municipality": "Ихтиман"},
    "веринско":    {"region": "Ихтиман", "municipality": "Ихтиман"},
    "живково":     {"region": "Ихтиман", "municipality": "Ихтиман"},
    "мирово":      {"region": "Ихтиман", "municipality": "Ихтиман"},
    "мухово":      {"region": "Ихтиман", "municipality": "Ихтиман"},
    "пауново":     {"region": "Ихтиман", "municipality": "Ихтиман"},
    "полянци":     {"region": "Ихтиман", "municipality": "Ихтиман"},
    "стамболово":  {"region": "Ихтиман", "municipality": "Ихтиман"},
    "черньово":    {"region": "Ихтиман", "municipality": "Ихтиман"},

    # --- Костенец ---
    "вили костенец":    {"region": "Костенец", "municipality": "Костенец"},
    "костенец":         {"region": "Костенец", "municipality": "Костенец"},
    "момин проход":     {"region": "Костенец", "municipality": "Костенец"},
    "махала геджова":   {"region": "Костенец", "municipality": "Костенец"},
    "махала нова":      {"region": "Костенец", "municipality": "Костенец"},
    "махала пердова":   {"region": "Костенец", "municipality": "Костенец"},
    "горна василица":   {"region": "Костенец", "municipality": "Костенец"},
    "голак":            {"region": "Костенец", "municipality": "Костенец"},
    "долна василица":   {"region": "Костенец", "municipality": "Костенец"},
    "очуша":            {"region": "Костенец", "municipality": "Костенец"},
    "подгорие":         {"region": "Костенец", "municipality": "Костенец"},
    "пчелин":           {"region": "Костенец", "municipality": "Костенец"},
    "пчелински бани":   {"region": "Костенец", "municipality": "Костенец"},

    # --- Костинброд ---
    "костинброд":     {"region": "Костинброд", "municipality": "Костинброд"},
    "безден":         {"region": "Костинброд", "municipality": "Костинброд"},
    "богьовци":       {"region": "Костинброд", "municipality": "Костинброд"},
    "бучин проход":   {"region": "Костинброд", "municipality": "Костинброд"},
    "голяновци":      {"region": "Костинброд", "municipality": "Костинброд"},
    "градец":         {"region": "Костинброд", "municipality": "Костинброд"},
    "драговищица":    {"region": "Костинброд", "municipality": "Костинброд"},
    "дреново":        {"region": "Костинброд", "municipality": "Костинброд"},
    "дръмша":         {"region": "Костинброд", "municipality": "Костинброд"},
    "опицвет":        {"region": "Костинброд", "municipality": "Костинброд"},
    "петърч":         {"region": "Костинброд", "municipality": "Костинброд"},
    "царичина":       {"region": "Костинброд", "municipality": "Костинброд"},
    "чибаовци":       {"region": "Костинброд", "municipality": "Костинброд"},

    # --- Своге ---
    "своге":           {"region": "Своге", "municipality": "Своге"},
    "бакьово":         {"region": "Своге", "municipality": "Своге"},
    "батулия":         {"region": "Своге", "municipality": "Своге"},
    "бов":             {"region": "Своге", "municipality": "Своге"},
    "брезе":           {"region": "Своге", "municipality": "Своге"},
    "брезовдол":       {"region": "Своге", "municipality": "Своге"},
    "буковец":         {"region": "Своге", "municipality": "Своге"},
    "владо тричков":   {"region": "Своге", "municipality": "Своге"},
    "габровница":      {"region": "Своге", "municipality": "Своге"},
    "гара бов":        {"region": "Своге", "municipality": "Своге"},
    "гара лакатник":   {"region": "Своге", "municipality": "Своге"},
    "губислав":        {"region": "Своге", "municipality": "Своге"},
    "добравица":       {"region": "Своге", "municipality": "Своге"},
    "добърчин":        {"region": "Своге", "municipality": "Своге"},
    "дружево":         {"region": "Своге", "municipality": "Своге"},
    "еленов дол":      {"region": "Своге", "municipality": "Своге"},
    "завидовци":       {"region": "Своге", "municipality": "Своге"},

    # --- Сливница ---
    "сливница":    {"region": "Сливница", "municipality": "Сливница"},
    "алдомировци": {"region": "Сливница", "municipality": "Сливница"},
    "братушково":  {"region": "Сливница", "municipality": "Сливница"},
    "бърложница":  {"region": "Сливница", "municipality": "Сливница"},
    "гургулят":    {"region": "Сливница", "municipality": "Сливница"},
    "гълъбовци":   {"region": "Сливница", "municipality": "Сливница"},
    "драготинци":  {"region": "Сливница", "municipality": "Сливница"},
    "извор":       {"region": "Сливница", "municipality": "Сливница"},
    "повалиръж":   {"region": "Сливница", "municipality": "Сливница"},
    "радуловци":   {"region": "Сливница", "municipality": "Сливница"},
    "ракита":      {"region": "Сливница", "municipality": "Сливница"},
}


def lookup_municipality(location_text: str) -> dict | None:
    """Return municipality info for a location string, or None if not found.

    The lookup is case-insensitive and strips leading/trailing whitespace.
    """
    if not location_text:
        return None
    return MUNICIPALITY_MAP.get(location_text.strip().lower())
