"""Rule-based validation helpers for farmer advisory queries."""

import re
import string
import unicodedata


MIN_QUERY_LENGTH = 15

GREETING_QUERIES = {
    "hi",
    "hello",
    "hey",
    "how are you",
    "good morning",
}

TRIVIAL_QUERIES = {
    "tell me a joke",
    "python",
    "123456",
    "123456789",
    "abcdef",
    "qwerty",
}

AGRICULTURE_KEYWORDS = {
    # General farming
    "agriculture", "agricultural", "farm", "farmer", "farming", "field",
    "crop", "crops", "plant", "plants", "planting", "grow", "growing",
    "cultivate", "cultivation", "sow", "sowing", "seed", "seedling",
    "harvest", "harvesting", "yield", "season", "greenhouse", "orchard",
    # Soil, water, nutrients, and weather
    "soil", "compost", "manure", "fertilizer", "fertiliser", "nutrient",
    "irrigation", "irrigate", "water", "watering", "rain", "rainfall",
    "weather", "temperature", "drought", "flood", "frost", "humidity",
    # Crop health
    "pest", "pests", "insect", "insects", "disease", "diseases", "fungus",
    "fungal", "weed", "weeds", "spray", "pesticide", "herbicide", "wilt",
    "wilting", "leaf", "leaves", "root", "roots", "stem", "fruit",
    "flower", "spots", "spot", "yellow", "yellowing", "brown", "black",
    "blight", "rot", "dry", "dying",
    # Agricultural markets
    "market", "price", "prices", "sell", "selling", "buyer", "commodity",
    # Common crops
    "wheat", "rice", "corn", "maize", "tomato", "tomatoes", "potato",
    "potatoes", "cotton", "sugarcane", "mango", "onion", "garlic",
    "chili", "pepper", "soybean", "barley", "oats", "sunflower",
    "mustard", "lentil", "chickpea", "pea", "spinach", "carrot",
    "cauliflower", "cucumber", "millet", "cassava", "yam", "banana",
    "orange", "apple", "grape", "watermelon", "pumpkin", "eggplant",
    "okra", "cabbage", "radish", "pineapple", "papaya", "guava",
    "ginger", "turmeric", "groundnut",
    # Roman Urdu / Hinglish crop and farming terms
    "gandum", "gundum", "gehu", "gehun", "chawal", "makai", "fasal",
    "kheti", "kasht", "zameen", "zamin", "mitti", "beej", "poda",
    "poday", "pattay", "patte", "patti", "pani", "barish", "mausam",
    "dhoop", "garmi", "sardi", "khad", "khaad", "keera", "keeray",
    "bemari", "bimari", "peela", "peeli", "peelay", "sookh", "sukh",
    "ugao", "ugaon", "ugana", "lagao", "kaatna", "katai", "mandi",
}

ADVISORY_INTENT_KEYWORDS = {
    "advice", "advise", "recommend", "suggest", "should", "when", "what",
    "how", "why", "which", "use", "apply", "treat", "control", "prevent",
    "manage", "fix", "improve", "need", "help", "problem", "issue",
    "disease", "pest", "spots", "yellow", "brown", "wilting", "dying",
    "irrigate", "harvest", "fertilizer", "fertiliser", "price", "market",
    # Roman Urdu / Hinglish advisory intent terms
    "kya", "kia", "kaise", "kaisay", "kesay", "kese", "kab", "kyun",
    "q", "chahiye", "karun", "karon", "karain", "karein", "batao",
    "batain", "madad", "mashwara", "ilaj", "ilaaj", "bachao", "behtar",
}

NON_ADVISORY_PHRASES = {
    "my favourite word",
    "my favorite word",
    "favorite word",
    "favourite word",
}


def _normalize(value: str) -> str:
    """Normalize spacing, Unicode variants, and letter case for comparison."""
    normalized = unicodedata.normalize("NFKC", value or "").casefold()
    return " ".join(normalized.split())


def _strip_outer_punctuation(value: str) -> str:
    """Remove punctuation around a normalized phrase for exact comparisons."""
    return value.strip(string.whitespace + string.punctuation)


def _words(value: str) -> set[str]:
    """Return alphabetic words from normalized text."""
    return set(re.findall(r"[^\W\d_]+", value, flags=re.UNICODE))


def is_valid_agriculture_query(value: str) -> bool:
    """Return True only for meaningful agriculture-related advisory input."""
    query = _normalize(value)
    phrase = _strip_outer_punctuation(query)
    if not query or len(query) < MIN_QUERY_LENGTH:
        return False

    if phrase in GREETING_QUERIES or phrase in TRIVIAL_QUERIES:
        return False

    if any(non_advisory in phrase for non_advisory in NON_ADVISORY_PHRASES):
        return False

    compact = re.sub(r"\s+", "", query)
    if compact and len(set(compact)) == 1:
        return False

    if compact in TRIVIAL_QUERIES:
        return False

    if not any(ch.isalpha() for ch in query):
        return False

    words = _words(query)
    # NOTE: Previously this required BOTH an agriculture-topic word AND a
    # separate "question intent" word (how/why/kesay/kya/etc). That
    # rejected perfectly valid farmer input that states a problem rather
    # than asking a question - e.g. "potato k pattay peelay horahay hain"
    # (potato leaves are turning yellow) or "fasal mein keeray lag gaye
    # hain" (pests have appeared in the crop) both correctly match
    # agriculture vocabulary but contain no question word, since farmers
    # often describe symptoms as statements, not questions, in any
    # language. Requiring agriculture-topic vocabulary alone (already
    # covering English + Roman Urdu/Hinglish terms above) is sufficient:
    # genuinely unrelated input (greetings, small talk, spam) won't match
    # any agriculture keyword either, so this still filters out off-topic
    # text without rejecting real symptom reports.
    has_agriculture_context = bool(words.intersection(AGRICULTURE_KEYWORDS))
    return has_agriculture_context
