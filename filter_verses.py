import json
import re

# Load the original verses
with open('verses.json', 'r', encoding='utf-8') as f:
    verses = json.load(f)

# Books to exclude entirely (too difficult to filter safely)
EXCLUDE_BOOKS = {
    'Revelation',
    '2 Peter',
    'Jude',
}

# Psalms imprecatory and war psalms to exclude
EXCLUDE_PSALMS = {
    2, 3, 5, 7, 9, 10, 12, 13, 14, 15, 17, 18, 19,  # War/military themes
    20, 21, 25, 26, 28, 29, 30, 31, 32, 33, 34, 35,  # Mixed, many exclude
    36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50,  # Mixed
    51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66,  # Heavy judgment
    67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89,  # Mix
    90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100,  # Mostly okay
    101, 102, 103, 104, 105, 106, 107, 108, 109, 110,  # Mix
    111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121,  # Mostly okay
    122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150
}

# Safe Psalms to keep
SAFE_PSALMS = {
    23, 27, 46, 91, 100, 103, 121, 139, 145,
    84, 87, 92, 95, 96, 97, 98, 99, 104, 113, 115, 117, 118, 122, 125, 131, 133, 148, 150
}

# Entire books to prefer (minimal filtering needed)
PREFERRED_BOOKS = {
    'Luke',
    'John',
    'Philippians',
    'Ephesians',
    'Colossians',
    '1 John',
}

# Specific chapters to prefer (only these from the book)
PREFERRED_CHAPTERS = {
    'Matthew': {5, 6, 7},
    'Romans': {8},
    '1 Corinthians': {13},
    'Hebrews': {4, 10, 11, 12, 13},
}

# Cautious/difficult books
DIFFICULT_BOOKS = {
    'Acts', '2 Thessalonians', '1 Timothy', '2 Timothy', 'Titus',
    'Galatians', '2 Corinthians', 'James', '2 John', '3 John',
    'Philippians', 'Colossians',  # Actually safer, but with some warnings
}

# Strong negative indicators
STRONG_EXCLUDE_PATTERNS = [
    r'\b(slay|slain|kill|killing|smite|struck)\b',
    r'\b(war|warfare|battle|sword|spear|arrow)\b',
    r'\b(blood|bloodshed|violence|violent)\b',
    r'\b(wrath|anger|wrathful|furious)\b',
    r'\b(destroy|destruction|destroyer|destroyed)\b',
    r'\b(curse|cursed|cursing|accursed)\b',
    r'\b(gnashing of teeth|outer darkness|lake of fire|second death)\b',
    r'\b(enemy|enemies|foe|adversary|adversaries)\b',
    r'\b(vengeance|revenge|avenge|avenging)\b',
    r'\b(plague|pestilence|famine)\b',
    r'\b(shall perish|shall not stand|shall be cut off|everlasting fire)\b',
    r'\b(death|dead|grave|burial)\b',
    r'\b(demon|demons|devil|serpent)\b',
    r'\b(damnation|damn|damned|hell)\b',
    r'\b(condemnation|condemn|condemned)\b',
    r'\b(shame|shameful|disgrace)\b',
]

# Moderate negative indicators (more context-dependent)
MODERATE_EXCLUDE_PATTERNS = [
    r'\b(judgment|judge|judged)\b',
    r'\b(punishment|punish|punished)\b',
    r'\b(sin|sins|sinner|sinners|transgress|transgression|iniquity)\b',
    r'\b(ungodly|wicked|evil)\b',
    r'\b(fear|afraid|terror)\b',
    r'\b(suffering|suffer|torment|pain|anguish)\b',
    r'\b(weeping|weep|lament|lamentation|mourn|mourning|sorrow)\b',
    r'\b(sick|sickness|disease|weakness|weak)\b',
    r'\b(forsaken|abandoned|desolate)\b',
]

# Positive indicators that override moderate negatives (context matters)
POSITIVE_INDICATORS = [
    r'\b(love|loved|loving|beloved)\b',
    r'\b(grace|gracious|graceful)\b',
    r'\b(mercy|merciful)\b',
    r'\b(peace|peaceful|peacemaker)\b',
    r'\b(joy|joyful|rejoice|rejoicing|glad|gladness|happiness|happy)\b',
    r'\b(comfort|comforted|comforting)\b',
    r'\b(hope|hopeful|confident)\b',
    r'\b(faith|faithful|trust|trusting)\b',
    r'\b(light|bright|brightness)\b',
    r'\b(strength|strong|strengthen|mighty)\b',
    r'\b(wisdom|wise|understanding)\b',
    r'\b(kindness|kind|gentle|gentleness)\b',
    r'\b(blessing|blessed|bless)\b',
    r'\b(praise|praising|exalt|exalted)\b',
    r'\b(beauty|beautiful|beautiful)\b',
    r'\b(eternal|everlasting|forever|eternal life)\b',
]

def has_strong_negatives(text):
    """Check for strong negative patterns"""
    for pattern in STRONG_EXCLUDE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def has_moderate_negatives(text):
    """Check for moderate negative patterns"""
    for pattern in MODERATE_EXCLUDE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def has_positive_indicators(text):
    """Check for positive indicators"""
    for pattern in POSITIVE_INDICATORS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def should_exclude(verse):
    """Determine if a verse should be excluded"""
    
    book = verse.get('b', '')
    chapter = verse.get('c', 0)
    text = verse.get('t', '').lower()
    
    # Exclude entire books
    if book in EXCLUDE_BOOKS:
        return True
    
    # Special handling for Psalms
    if book == 'Psalms':
        if chapter not in SAFE_PSALMS:
            return True
    
    # Exclude strong negatives unconditionally
    if has_strong_negatives(text):
        return True
    
    # For preferred books, be lenient
    if book in PREFERRED_BOOKS:
        # Still exclude strong negatives, but allow moderate ones if positive indicators present
        if has_moderate_negatives(text):
            if has_positive_indicators(text):
                return False  # Allow if has positive
            # Exclude if it's pure negative (no positive indicators)
            if not has_positive_indicators(text):
                return False  # Actually allow most content from preferred books
        return False
    
    # For books with specific preferred chapters
    if book in PREFERRED_CHAPTERS:
        if chapter not in PREFERRED_CHAPTERS[book]:
            return True
        # Still check for strong negatives
        if has_strong_negatives(text):
            return True
        return False
    
    # For difficult books, be more strict
    if book in DIFFICULT_BOOKS:
        # Only allow if has positive indicators and no moderate negatives
        if has_moderate_negatives(text):
            return True
        if not has_positive_indicators(text):
            return True
        return False
    
    # Default: exclude verses with moderate negatives unless they have strong positive indicators
    if has_moderate_negatives(text):
        if has_positive_indicators(text):
            return False
        return True
    
    return False

def filter_verses():
    """Filter verses according to criteria"""
    
    filtered = []
    
    for verse in verses:
        if not should_exclude(verse):
            filtered.append(verse)
    
    return filtered

# Process the filtering
filtered_verses = filter_verses()

# Output the filtered JSON
output_json = json.dumps(filtered_verses, ensure_ascii=False)
print(output_json)

# Also save to file for reference
with open('verses_filtered.json', 'w', encoding='utf-8') as f:
    f.write(output_json)
