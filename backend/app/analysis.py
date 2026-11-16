"""Kundli analysis: turns a calculated chart into a structured, readable report.

Every statement is derived from the chart produced by ``jyotish.build_chart`` using standard
Parashari rules (functional nature by lagna, dignity, house placement, Vimshottari dasha lords,
Avakhada/Panchang conventions). Nothing here alters calculated positions.
"""
from __future__ import annotations

from datetime import UTC, datetime

from . import jyotish as J
from . import meanings as M

SIGNS = J.SIGNS
ORD = {1: "1st", 2: "2nd", 3: "3rd"}


def ordn(n: int) -> str:
    return ORD.get(n, f"{n}th")


# ───────── reference tables (standard Jyotish conventions) ─────────
SIGN_PROFILE = {
    "Aries": (
        "Fire",
        "Movable",
        "pioneering, courageous, direct and energetic",
        "natural initiative, fearlessness in starting new ventures, decisive action, leadership during crises",
        "impatience, quick temper, leaving projects unfinished, headstrong reactions",
        "With Aries influencing this point, you approach life with an adventurous, pioneering spirit. You prefer to lead rather than follow, and you act swiftly when opportunities appear. You are honest, direct, and dislike beating around the bush.",
        "In relationships, you value honesty, passion, and mutual freedom. You express affection boldly, but need a partner who can match your energy without competing with your independence.",
        "Professionally, you excel in environments requiring initiative, rapid problem-solving, entrepreneurship, technology, or physical courage. You perform best when given autonomy to drive projects forward.",
        "Your health vitality is naturally robust, but you tend to run hot. Ensure regular physical exercise to channel excess energy, stay well hydrated, and make time to relax your nervous system.",
    ),
    "Taurus": (
        "Earth",
        "Fixed",
        "steady, sensual, reliable and grounded",
        "patience, loyalty, building lasting financial value, practical craftsmanship, dependable friendship",
        "stubbornness, resistance to change, possessiveness, over-indulgence in comfort or food",
        "With Taurus influencing this point, you radiate calm, stability, and enduring determination. You take your time to make up your mind, but once committed, you see things through with quiet persistence. You appreciate quality, beauty, and physical comfort.",
        "In partnerships, you are deeply loyal, affectionate, and protective. You seek long-term stability, shared domestic peace, and tangible expressions of care.",
        "In your career, you excel where consistency, financial acumen, aesthetics, agriculture, food, or real estate matter. You build assets slowly and securely rather than taking speculative gambles.",
        "Health is generally solid, with strong physical stamina. The primary focus is maintaining a balanced diet, watching weight or throat sensitivity, and incorporating gentle daily movement.",
    ),
    "Gemini": (
        "Air",
        "Dual",
        "curious, communicative, adaptable and witty",
        "intellectual versatility, sharp networking, engaging communication, quick learning, multifaceted skills",
        "restlessness, scattered focus, nervous exhaustion, difficulty with deep emotional commitment",
        "With Gemini at this position, your mind is perpetually active, agile, and eager for new information. You thrive on conversation, ideas, and varied social connections, bringing a youthful spark to every room you enter.",
        "In relationships, mental connection is paramount. You need a partner who can stimulate your mind, share humor, and participate in lively discussions across endless topics.",
        "Professionally, you flourish in media, writing, IT, digital communication, commerce, teaching, and consulting. You manage multiple streams of activity easily and bridge different groups seamlessly.",
        "Your nervous system and respiratory health require conscious care. Establish calming evening routines away from screens, practice deep breathing, and ensure you finish primary tasks before beginning new ones.",
    ),
    "Cancer": (
        "Water",
        "Movable",
        "nurturing, intuitive, protective and deeply feeling",
        "profound empathy, strong emotional memory, protective care for family, dedication to creating security",
        "moodiness, over-sensitivity, holding onto past hurts, defensive withdrawal under stress",
        "With Cancer influencing this point, your heart and intuition guide your steps. You have a natural radar for what others are feeling, and your instincts are remarkably reliable. Home, family, and trusted relationships are the bedrock of your world.",
        "In love, you give devoted, protective care and seek a deeply bonded, safe emotional sanctuary. You need reassurance and gentle communication, thriving when you feel completely accepted.",
        "In work, you excel in fields where human connection, hospitality, education, healthcare, real estate, or public goodwill make the difference. People instinctively trust your supportive presence.",
        "Your emotional state directly impacts your digestive and fluid wellness. Cultivate healthy boundaries, spend time near peaceful water or in quiet reflection, and practice letting go of past burdens.",
    ),
    "Leo": (
        "Fire",
        "Fixed",
        "dignified, warm-hearted, generous and commanding",
        "natural leadership, magnanimity, creative expression, unwavering confidence, loyalty to loved ones",
        "pride, susceptibility to flattery, difficulty admitting fault, craving external validation",
        "With Leo at this position, you carry natural majesty, warmth, and self-respect. You are open-hearted, generous to those in your circle, and desire to make a lasting, honorable mark on the world.",
        "In romantic life, you love grandly, passionately, and with complete loyalty. You want to feel proud of your partner, and you flourish when your efforts and devotion are appreciated openly.",
        "Professionally, you are built for executive authority, creative direction, management, government, or public leadership. You prefer having ownership of results and inspire teams through your optimism.",
        "Vitality and heart health are your biological strong suits, but chronic stress or intense pride can strain your circulation. Practice heart-healthy cardiovascular routines, eat clean foods, and share the spotlight willingly.",
    ),
    "Virgo": (
        "Earth",
        "Dual",
        "analytical, observant, precise and service-minded",
        "exceptional discernment, systematic organization, attention to practical detail, dedicated craftsmanship",
        "perfectionism, over-criticism of self and others, chronic worry, difficulty switching off",
        "With Virgo influencing this point, you possess an observant eye that notices subtleties others miss. You are quietly capable, modest about your skills, and take pride in doing things properly and efficiently.",
        "In relationships, you show love through helpful acts, practical reliability, and thoughtful problem-solving. You need a partner who values your dedication and helps you relax your high standards.",
        "In your career, you excel in analysis, research, accounting, medicine, engineering, editing, and service operations. Your work is meticulous, and organizations rely on your ability to bring order out of chaos.",
        "Your gut health, nervous balance, and digestion are sensitive to mental anxiety. Incorporate grounding routines, regular wholesome meals, and remember that 'done' is often far better than 'perfect'.",
    ),
    "Libra": (
        "Air",
        "Movable",
        "diplomatic, refined, charming and fair-minded",
        "natural sense of justice, aesthetic refinement, relationship mediation, gracious social presence",
        "indecisiveness, avoiding necessary conflict, dependence on others' approval, procrastination",
        "With Libra at this position, balance, aesthetics, and harmonious partnership are your guiding stars. You have an innate sense of proportion, speak with diplomacy, and dislike coarse or aggressive environments.",
        "In love, partnership is essential to your wellbeing. You are romantic, attentive, and strive for equality and mutual respect in your marriage and intimate collaborations.",
        "Professionally, you do well in law, diplomacy, public relations, design, architecture, luxury goods, and collaborative commerce. You negotiate win-win solutions that satisfy diverse parties.",
        "Keep your kidneys, lower back, and hydration balanced. Make conscious choices without second-guessing yourself indefinitely, and remember that healthy confrontation is sometimes the fastest path to genuine harmony.",
    ),
    "Scorpio": (
        "Water",
        "Fixed",
        "intense, perceptive, resilient and transformative",
        "unmatched emotional depth, forensic research ability, survival stamina in crisis, unshakeable loyalty",
        "secrecy, difficulty forgiving betrayal, jealousy, all-or-nothing emotional extremes",
        "With Scorpio influencing this point, you carry intense inner power, deep psychological perceptiveness, and a quiet charisma. You are not interested in superficial chatter; you want to know what lies beneath the surface.",
        "In intimate relationships, you love deeply, passionately, and with complete devotion. Trust is sacred to you; once earned, your loyalty is unbreakable, but betrayal is rarely forgotten.",
        "In your profession, you excel in research, medicine, surgery, psychology, crisis management, investigation, finance, and transformative leadership. You are at your best when the stakes are high.",
        "Protect reproductive, excretory, and emotional health. Practice forgiveness as an act of personal freedom, channel intense feelings into physical or creative outlets, and allow yourself to be vulnerable with trusted confidants.",
    ),
    "Sagittarius": (
        "Fire",
        "Dual",
        "optimistic, principled, adventurous and philosophical",
        "broad vision, inspiring enthusiasm, love of higher learning and travel, generosity of spirit",
        "blunt tactlessness, over-promising, restlessness, impatience with practical daily details",
        "With Sagittarius at this position, you walk through life with faith, humor, and a quest for deeper meaning. You love open horizons, philosophical inquiry, diverse cultures, and sharing uplifting ideas with others.",
        "In romance, you need a partner who is also a friend and fellow traveler. You thrive when given intellectual and physical freedom, and you value shared moral and spiritual values.",
        "Professionally, you do well in higher education, law, publishing, international business, advisory roles, and public coaching. Your optimism inspires others to believe in bigger possibilities.",
        "Watch hips, thighs, liver wellness, and avoid dietary over-indulgence. Anchor your sweeping visions with practical daily steps, and temper blunt honesty with compassionate timing.",
    ),
    "Capricorn": (
        "Earth",
        "Movable",
        "ambitious, disciplined, patient and strategic",
        "extraordinary endurance, structured long-term planning, executive responsibility, reliable maturity",
        "pessimism, emotional reserve, overwork, calculating relationships purely by utility",
        "With Capricorn influencing this point, you respect time, hard work, and earned achievement. You are willing to climb steep paths without complaint, and your capabilities grow stronger and more respected as years advance.",
        "In love, you take commitments seriously and express devotion through dependable support and security. While slow to open your heart, once pledged, your commitment is rock solid.",
        "In your career, you excel in executive administration, corporate governance, engineering, civil projects, and building lasting institutions. You manage resources with prudence and foresight.",
        "Keep your joints, knees, bones, and posture well looked after through regular mobility exercises. Balance rigorous professional duty with laughter, leisure, and warmth for your personal well-being.",
    ),
    "Aquarius": (
        "Air",
        "Fixed",
        "independent, visionary, humanitarian and original",
        "out-of-the-box thinking, progressive social conscience, intellectual detachment, collaborative innovation",
        "aloofness, stubborn contrarianism, emotional distance, rebel-without-a-cause mindset",
        "With Aquarius at this position, you march to the beat of your own drum. You care deeply about collective progress, justice, and modern ideas, combining intellectual detachment with genuine humanitarian warmth.",
        "In relationships, you treat your partner as an intellectual equal and best friend. You value independence and need space to pursue your causes without suffocating possessiveness.",
        "In work, you flourish in technology, scientific research, social entrepreneurship, community networks, and avant-garde projects. You see future trends before they become mainstream.",
        "Pay attention to circulation, nervous system rest, and lower leg health. Practice staying present in your emotional body rather than analyzing your feelings from an intellectual distance.",
    ),
    "Pisces": (
        "Water",
        "Dual",
        "compassionate, imaginative, spiritual and receptive",
        "profound artistic sensitivity, spiritual intuition, selfless kindness, mystical insight",
        "escapism, vague boundaries, vulnerability to deception, difficulty managing practical limits",
        "With Pisces influencing this point, your soul is poetic, compassionate, and attuned to the unseen dimensions of life. You have a tender heart that easily empathizes with all living beings, and your imagination is limitless.",
        "In love, you are romantic, self-giving, and seek a soulful, transcendent union. You need a gentle, grounded partner who respects your sensitivity and helps anchor practical daily life.",
        "Professionally, you excel in arts, music, creative writing, healing professions, photography, spiritual guidance, and philanthropic work. You bring heart and soul into everything you touch.",
        "Protect your feet, lymphatic balance, and emotional boundaries. Ground your rich inner dreams with tangible daily routines, and avoid escapist habits when everyday life feels demanding.",
    ),
}
LUCKY = {  # by lagna lord
    "Sun": ("Ruby", "Sunday", "Orange, gold", "1"), "Moon": ("Pearl", "Monday", "White, silver", "2"),
    "Mars": ("Red Coral", "Tuesday", "Red", "9"), "Mercury": ("Emerald", "Wednesday", "Green", "5"),
    "Jupiter": ("Yellow Sapphire", "Thursday", "Yellow", "3"), "Venus": ("Diamond / White Sapphire", "Friday", "White, pastel", "6"),
    "Saturn": ("Blue Sapphire", "Saturday", "Blue, black", "8"),
}
NAK_PROFILE = (
    ("Ashvini Kumaras", "Horse's head", "swift, healing, adventurous and pioneering"),
    ("Yama", "Yoni", "intense, disciplined, creative and transformative"),
    ("Agni", "Razor / flame", "sharp, purifying, determined and insightful"),
    ("Brahma", "Chariot", "charming, artistic, prosperous and nurturing"),
    ("Soma", "Deer's head", "curious, gentle, searching and affectionate"),
    ("Rudra", "Teardrop", "probing, transformative, passionate and resilient"),
    ("Aditi", "Quiver of arrows", "renewing, generous, optimistic and principled"),
    ("Brihaspati", "Cow's udder", "nourishing, dutiful, wise and spiritually blessed"),
    ("Nagas", "Coiled serpent", "perceptive, strategic, protective and insightful"),
    ("Pitris", "Royal throne", "noble, traditional, authoritative and proud"),
    ("Bhaga", "Front legs of a bed", "pleasure-loving, warm, creative and generous"),
    ("Aryaman", "Back legs of a bed", "helpful, loyal, principled and honourable"),
    ("Savitar", "Hand", "skilful, resourceful, witty and detail-oriented"),
    ("Vishvakarma", "Pearl / gem", "artistic, stylish, inventive and visually gifted"),
    ("Vayu", "Young shoot in wind", "independent, flexible, diplomatic and fair"),
    ("Indra-Agni", "Triumphal arch", "goal-driven, focused, ambitious and persistent"),
    ("Mitra", "Lotus", "devoted, friendly, organised and peacemaking"),
    ("Indra", "Earring / umbrella", "protective, senior, resourceful and commanding"),
    ("Nirriti", "Bundle of roots", "investigative, radical, unyielding and spiritual"),
    ("Apas", "Fan / winnowing basket", "invincible, persuasive, proud and strategic"),
    ("Vishvadevas", "Elephant's tusk", "righteous, persistent, victorious and noble"),
    ("Vishnu", "Ear", "attentive, learned, connected and wise listener"),
    ("Vasus", "Drum", "musical, wealthy, generous and rhythmic"),
    ("Varuna", "Empty circle", "healing, secretive, philosophical and mystical"),
    ("Aja Ekapada", "Front of funeral cot", "passionate, idealistic, intense and visionary"),
    ("Ahir Budhnya", "Back of funeral cot", "wise, calm, disciplined and deep-thinking"),
    ("Pushan", "Fish / drum", "nurturing, gentle, guiding and prosperous"),
)
VARNA = {3: "Brahmin", 7: "Brahmin", 11: "Brahmin", 0: "Kshatriya", 4: "Kshatriya", 8: "Kshatriya", 1: "Vaishya", 5: "Vaishya", 9: "Vaishya", 2: "Shudra", 6: "Shudra", 10: "Shudra"}
VASHYA = ("Chatushpada", "Chatushpada", "Manava", "Jalachara", "Vanachara", "Manava", "Manava", "Keeta", "Manava / Chatushpada", "Chatushpada / Jalachara", "Manava", "Jalachara")
YONI = ("Horse", "Elephant", "Sheep", "Serpent", "Serpent", "Dog", "Cat", "Sheep", "Cat", "Rat", "Rat", "Cow", "Buffalo", "Tiger", "Buffalo", "Tiger", "Deer", "Deer", "Dog", "Monkey", "Mongoose", "Monkey", "Lion", "Horse", "Lion", "Cow", "Elephant")
GANA = ("Deva", "Manushya", "Rakshasa", "Manushya", "Deva", "Manushya", "Deva", "Deva", "Rakshasa", "Rakshasa", "Manushya", "Manushya", "Deva", "Rakshasa", "Deva", "Rakshasa", "Deva", "Rakshasa", "Rakshasa", "Manushya", "Manushya", "Deva", "Rakshasa", "Rakshasa", "Manushya", "Manushya", "Deva")
NADI = ("Adi (Vata)", "Madhya (Pitta)", "Antya (Kapha)")
SYLLABLES = ("Chu Che Cho La", "Li Lu Le Lo", "A I U E", "O Va Vi Vu", "Ve Vo Ka Ki", "Ku Gha Ng Chha", "Ke Ko Ha Hi", "Hu He Ho Da", "Di Du De Do",
             "Ma Mi Mu Me", "Mo Ta Ti Tu", "Te To Pa Pi", "Pu Sha Na Tha", "Pe Po Ra Ri", "Ru Re Ro Ta", "Ti Tu Te To", "Na Ni Nu Ne", "No Ya Yi Yu",
             "Ye Yo Bha Bhi", "Bhu Dha Pha Dha", "Bhe Bho Ja Ji", "Ju Je Jo Gha", "Ga Gi Gu Ge", "Go Sa Si Su", "Se So Da Di", "Du Tha Jha Na", "De Do Cha Chi")

PLANET_GOOD = {
    "Sun": "confidence, leadership authority, self-respect and support from government or senior figures",
    "Moon": "emotional stability, peace of mind, public goodwill, warm relationships and domestic nourishment",
    "Mars": "decisive courage, energy, competitive success, technical mastery and achievements in property or enterprise",
    "Mercury": "sharp analytical intellect, eloquent speech, commercial success, learning and adaptable networking",
    "Jupiter": "wisdom, expansion, ethical clarity, good counsel, academic honors, children and lasting prosperity",
    "Venus": "harmony in partnerships, aesthetic refinement, artistic creativity, comfort, luxury and joyful marriage",
    "Saturn": "rock-solid discipline, endurance, methodical achievement, seniority and durable long-term success",
    "Rahu": "audacious ambition, unconventional breakthroughs, foreign links, technological acumen and innovative rise",
    "Ketu": "deep intuitive insight, research brilliance, spiritual awakening and freedom from petty distractions",
}
PLANET_HARD = {
    "Sun": "ego clashes, friction with authorities or father, pride and cardiovascular or eye strain",
    "Moon": "mood fluctuations, emotional anxiety, over-sensitivity and instability in domestic peace",
    "Mars": "rash haste, arguments, accident-proneness, conflicts over territory and inflammatory tendencies",
    "Mercury": "nervous exhaustion, overthinking, scattered commitments and miscommunication under pressure",
    "Jupiter": "unrealistic over-optimism, over-extension of resources, complacency and digestive or liver strain",
    "Venus": "indulgence in comfort, relationship imbalances, financial overspending and aesthetic superficiality",
    "Saturn": "frustrating delays, heavy burdens of duty, isolation, pessimism and joint or bone stiffness",
    "Rahu": "illusions, restlessness, obsession with status, risky shortcuts and sudden disorientations",
    "Ketu": "sudden separations, lack of practical direction, feeling misunderstood and unexpected closures",
}
HOUSE_THEME = {
    1: "self, health, vitality and personal life direction",
    2: "earned finances, family speech, values and savings",
    3: "personal initiative, siblings, creative skills and short journeys",
    4: "home sanctuary, mother, property, vehicles and emotional peace of mind",
    5: "creative intelligence, progeny, romance, higher judgment and past merit",
    6: "workplace routine, health resistance, managing competition and debts",
    7: "marriage, life partnerships, business alliances and public dealings",
    8: "deep transformation, research, joint finances, longevity and sudden transitions",
    9: "fortune, higher learning, father, ethical principles and spiritual guidance",
    10: "career authority, public reputation, leadership and life contribution",
    11: "steady income, social networks, realization of ambitions and supportive allies",
    12: "expenses, foreign travel, restorative solitude, sleep and spiritual liberation",
}
DIG_SCORE = {"exalted": 22, "moolatrikona": 16, "own": 14, "friendly": 6, "neutral": 0, "enemy": -8, "debilitated": -20}


# ───────── functional nature ─────────
def functional_role(c: dict, planet: str) -> dict:
    if planet in ("Rahu", "Ketu"):
        disp = J.P(c, planet)["sign_lord"]
        return {"role": "shadow", "rules": [], "label": f"Node — gives results of its dispositor {disp}", "score": 0}
    rules = [h for h in range(1, 13) if J.lord_of_house(c, h) == planet]
    s = set(rules)
    if s & {1, 4, 7, 10} - {1} and s & {5, 9}:
        return {"role": "yogakaraka", "rules": rules, "label": "Yogakaraka — rules a kendra and a trikona; the most auspicious planet for this lagna", "score": 18}
    if 1 in s:
        return {"role": "benefic", "rules": rules, "label": "Lagna lord — always supportive of the native", "score": 10}
    if s & {5, 9}:
        if s & {6, 8, 12}:
            return {"role": "mixed", "rules": rules, "label": "Mixed — rules a trikona and a dusthana", "score": 2}
        return {"role": "benefic", "rules": rules, "label": "Functional benefic — trikona lord", "score": 10}
    if s & {3, 6, 11} and not s & {1, 5, 9}:
        return {"role": "malefic", "rules": rules, "label": "Functional malefic — lord of trishadaya (3/6/11)", "score": -8}
    if 8 in s:
        return {"role": "malefic", "rules": rules, "label": "Functional malefic — 8th lord", "score": -8}
    if s & {4, 7, 10} and planet in J.BENEFICS:
        return {"role": "neutral", "rules": rules, "label": "Neutral — natural benefic owning a kendra (kendradhipati)", "score": 0}
    if s & {4, 7, 10}:
        return {"role": "benefic", "rules": rules, "label": "Mildly benefic — natural malefic owning a kendra", "score": 5}
    if s & {2, 12}:
        return {"role": "neutral", "rules": rules, "label": "Neutral — gives results by association (2nd/12th lord)", "score": 0}
    return {"role": "neutral", "rules": rules, "label": "Neutral", "score": 0}


def planet_strength(c: dict, name: str) -> int:
    p = J.P(c, name)
    fr = functional_role(c, name)
    s = 50 + DIG_SCORE[p["dignity"]] + fr["score"]
    s += 8 if p["house"] in J.KENDRA | J.TRIKONA else -10 if p["house"] in J.DUSTHANA else 3
    if p["combust"]:
        s -= 12
    sb = c.get("shadbala", {}).get("planets", {}).get(name)
    if sb:
        s += max(-12, min(12, round((sb["ratio"] - 1) * 25)))
    return max(5, min(98, round(s)))


def tone(score: int) -> str:
    return "excellent" if score >= 75 else "favourable" if score >= 60 else "mixed" if score >= 45 else "challenging"


# ───────── sections ─────────
def birth_panchang(c: dict) -> dict:
    sun, moon = J.P(c, "Sun")["absolute_longitude"], J.P(c, "Moon")["absolute_longitude"]
    diff = (moon - sun) % 360
    tithi, paksha = J.tithi_name(int(diff // 12))
    yoga = J.YOGAS27[int(((sun + moon) % 360) // (360 / 27))]
    karana = J.karana_name(int(diff // 6))
    local = datetime.fromisoformat(c["birth"]["local_datetime"])
    return {"tithi": f"{paksha} {tithi}", "yoga": yoga, "karana": karana, "vara": J.VARAS[(local.weekday() + 1) % 7],
            "note": "Weekday shown by civil date; traditional vara changes at sunrise."}


def avakhada(c: dict) -> list[dict]:
    m = J.P(c, "Moon")
    ni = J.NAKSHATRAS.index(m["nakshatra"])
    si = m["sign_index"]
    el = SIGN_PROFILE[m["sign"]][0]

    varna_expl = {
        "Brahmin": "Intellectual and introspective temperament; you seek knowledge, wisdom and deeper meaning.",
        "Kshatriya": "Leadership and dynamic spirit; you have courage, a protective nature and take charge naturally.",
        "Vaishya": "Resourceful and commercial acumen; you understand value, networking and practical exchange.",
        "Shudra": "Grounded, hard-working and dedicated; you excel in skilled execution, service and reliability.",
    }
    vashya_expl = {
        "Chatushpada": "Four-legged (quadruped): steadfast, patient, loyal and grounded in material reality.",
        "Manava": "Human: intellectual, sociable, capable of refined diplomacy and abstract thought.",
        "Jalachara": "Water-dwelling: deeply feeling, adaptable, intuitive and emotionally receptive.",
        "Keeta": "Insect (Scorpio): intensely private, self-protective, resilient and transformative.",
        "Vanachara": "Wild (forest lion): authoritative, independent and commanding in presence.",
    }
    gana_expl = {
        "Deva": "Divine (Deva): noble, gentle, peace-loving and naturally generous in disposition.",
        "Manushya": "Human (Manushya): ambitious, balanced between worldly duties and moral ideals.",
        "Rakshasa": "Fierce (Rakshasa): independent, bold, intuitive and resilient against external pressure.",
    }
    nadi_expl = {
        "Adi (Vata)": "Vata constitution: quick mind, agile perception, sensitive nervous system; benefits from grounding warmth.",
        "Madhya (Pitta)": "Pitta constitution: decisive drive, sharp intellect, active metabolism; benefits from calming cooling routines.",
        "Antya (Kapha)": "Kapha constitution: steady endurance, deep patience, stable emotional reservoir; benefits from active stimulation.",
    }

    varn_val = VARNA[si]
    vash_val = VASHYA[si]
    gana_val = GANA[ni]
    nadi_val = NADI[nadi_index(ni)]

    return [
        {"label": "Moon sign (Rashi)", "value": m["sign"], "hint": f"Lord {m['sign_lord']} · Shapes your emotional baseline and subconscious instincts."},
        {"label": "Nakshatra – Pada", "value": f"{m['nakshatra']} – {m['pada']}", "hint": f"Lord {m['nakshatra_lord']} · Governs your innate gifts, mind rhythm and the starting dasha."},
        {"label": "Varna", "value": varn_val, "hint": f"{varna_expl.get(varn_val, 'Temperament category by Moon sign.')} Used in relationship matching to gauge life orientation."},
        {"label": "Vashya", "value": vash_val, "hint": f"{vashya_expl.get(vash_val, 'Mode of influence.')} Reflects how easily you harmonize with and influence others."},
        {"label": "Yoni", "value": YONI[ni], "hint": f"Animal symbol ({YONI[ni]}). Reflects instinctive physical nature and instinctual compatibility in marriage."},
        {"label": "Gana", "value": gana_val, "hint": f"{gana_expl.get(gana_val, 'Temperament frequency.')} Essential in matching to ensure mutual emotional wavelength."},
        {"label": "Nadi", "value": nadi_val, "hint": f"{nadi_expl.get(nadi_val, 'Ayurvedic constitution.')} Crucial in Kundli matching for genetic health and physical harmony."},
        {"label": "Tatva", "value": el, "hint": f"Primary element ({el}). Informs your core energy: Fire inspires, Earth grounds, Air communicates, Water feels."},
        {"label": "Name syllables", "value": SYLLABLES[ni].split()[m["pada"] - 1], "hint": f"Auspicious starting sound for your pada. All syllables for {m['nakshatra']}: {SYLLABLES[ni]}."},
    ]


def nadi_index(ni: int) -> int:
    return (0, 1, 2, 2, 1, 0, 0, 1, 2)[ni % 9]


def sign_profile(sign: str, lord: str) -> dict:
    prof = SIGN_PROFILE[sign]
    el, mod, nature, plus, minus = prof[0], prof[1], prof[2], prof[3], prof[4]
    gem, day, colour, num = LUCKY[lord]
    overview = prof[5] if len(prof) > 5 else f"With {sign} rising, you approach life with a {nature} disposition."
    rel_style = prof[6] if len(prof) > 6 else "In relationships, you seek mutual respect and sincere loyalty."
    career_style = prof[7] if len(prof) > 7 else "In your profession, your strengths lie in steady dedication and focus."
    health_style = prof[8] if len(prof) > 8 else "Your physical vitality benefits from regular routines and balanced living."

    return {
        "sign": sign, "lord": lord, "element": el, "modality": mod, "nature": nature,
        "strengths": plus, "challenges": minus,
        "description": overview,
        "relationships": rel_style,
        "career_style": career_style,
        "health_style": health_style,
        "lucky": {"gemstone": gem, "day": day, "colour": colour, "number": num},
    }


def planet_reading(c: dict, name: str) -> dict:
    p = J.P(c, name)
    fr = functional_role(c, name)
    score = planet_strength(c, name)
    h = p["house"]
    cond = []
    if p["retrograde"] and name not in ("Rahu", "Ketu"):
        cond.append("retrograde — results come through review, patience, repetition or second attempts")
    if p["combust"]:
        cond.append("combust — its outer significations are overshadowed by the Sun; requires inner cultivation")
    weak_dig = p["dignity"] in ("enemy", "debilitated") or p["combust"]

    # Paragraph 1: Cosmic position and core domain
    p1 = (f"{name} occupies the {ordn(h)} house in {p['sign']} ({p['nakshatra']} pada {p['pada']}), "
          f"where it is classically {J.DIG_WORD[p['dignity']]} ({p['dignity']}). "
          f"This placement concentrates {name}'s core energies directly into the sphere of {HOUSE_THEME[h]}. ")
    if fr["rules"]:
        rules_str = ", ".join(ordn(x) for x in fr["rules"])
        linked_themes = " and ".join(HOUSE_THEME[x].split(",")[0] for x in fr["rules"])
        p1 += f"As the lord of your {rules_str} house{'s' if len(fr['rules']) > 1 else ''}, it weaves matters of {linked_themes} into this domain. "

    # Paragraph 2: Functional nature and manifestation
    planet_support_note = {
        "Sun": "You can draw upon this solar vitality to lead projects with confidence and earned authority.",
        "Moon": "This placement enriches your emotional composure and helps you cultivate warm, supportive relationships.",
        "Mars": "Your focused courage and disciplined drive will turn ambitious plans into tangible achievements.",
        "Mercury": "Your sharp analytical discernment and articulate communication will open lucrative doors.",
        "Jupiter": "Its benevolent wisdom acts as an enduring protective shield, attracting helpful mentors and sound judgment.",
        "Venus": "This graceful signature brings aesthetic joy, social warmth, and harmonious partnership milestones.",
        "Saturn": "Your patience and unswerving work ethic build unshakeable professional foundations over time.",
        "Rahu": "Embracing innovative methods and bold visions accelerates your worldly advancement.",
        "Ketu": "Cultivating quiet contemplation and research uncovers profound inner wisdom and clarity.",
    }
    planet_caution_note = {
        "Sun": "Tempering pride, practicing humility with mentors, and honoring the Sun on Sundays bring valuable stabilization.",
        "Moon": "Establishing grounding daily routines, staying near peaceful water, and calming evening rest restore emotional equilibrium.",
        "Mars": "Channeling fiery energy into regular physical exercise and measured speech protects against rash disputes.",
        "Mercury": "Structuring your daily schedule and setting screen-free breaks protect your nervous system from overthinking.",
        "Jupiter": "Practicing ethical moderation, realistic financial planning, and honoring Thursday charities soothe this planetary pressure.",
        "Venus": "Cultivating relationship maturity, financial budgeting, and artistic simplicity restores balanced harmony.",
        "Saturn": "Exercising unhurried patience, respecting service staff, and looking after joint health yield gradual, enduring turnaround.",
        "Rahu": "Staying strictly grounded in ethical practices and avoiding speculative shortcuts prevent disorienting illusions.",
        "Ketu": "Embracing spiritual simplicity, meditation, and letting go of past burdens illuminate your inner path.",
    }
    if score >= 62 and not weak_dig:
        p2 = (f"Functionally {fr['label'].split(' — ')[0].lower()}, {name} operates with solid strength (score {score}/100). "
              f"It provides reliable support for {PLANET_GOOD[name]}. {planet_support_note.get(name, '')}")
    elif score >= 45:
        p2 = (f"Holding a mixed strength score of {score}/100, {name}'s influence brings both opportunities and lessons. "
              f"While it can deliver {PLANET_GOOD[name]}, its {p['dignity']} condition suggests occasional "
              f"{PLANET_HARD[name].split(',')[0]} that requires patient steering.")
    else:
        p2 = (f"Placed under strain with a score of {score}/100, {name} asks for conscious mindfulness. "
              f"Its more demanding tendencies—such as {PLANET_HARD[name]}—can show up when you rush or act without foresight. "
              f"{planet_caution_note.get(name, 'Disciplined habits and patient self-care help balance this influence.')}")

    # Paragraph 3: Lived expression and holistic synthesis
    life, caution = M.PLANET_IN_HOUSE[name][h]
    p3 = (f"In your day-to-day experience, having {name} situated in the {ordn(h)} house ({p['sign']}) directs your instincts toward "
          f"{HOUSE_THEME[h].split(',')[0]}. When operating at its best, this placement allows you to approach this domain with "
          f"{NAT_KARAKA[name].split(',')[0]} and purposeful focus. The key to mastering this placement lies in conscious balance—expressing "
          f"{name}'s strengths while remaining mindful of {PLANET_HARD[name].split(',')[0]}.")

    text = f"{p1}\n\n{p2}\n\n{p3}"

    if score >= 62 and not weak_dig:
        verdict = "On balance, the constructive and uplifting side of this placement dominates your life."
    elif score >= 45:
        verdict = "You will experience both sides; the constructive side flourishes with intentional conscious effort."
    else:
        verdict = "The cautionary side requires attention; practical patience and remedies bring valuable stabilization."

    meaning = {"life": life, "caution": caution, "dignity": M.DIGNITY_NOTE.get(p["dignity"], ""), "verdict": verdict}
    return {
        "meaning": meaning, "planet": name, "house": h, "sign": p["sign"], "nakshatra": p["nakshatra"],
        "pada": p["pada"], "dignity": p["dignity"], "retrograde": p["retrograde"], "combust": p["combust"],
        "functional": fr, "score": score, "tone": tone(score), "conditions": cond, "interpretation": text,
    }


def _period_score(c: dict, lord: str, sub: str | None = None) -> int:
    s = planet_strength(c, lord)
    if sub and sub != lord:
        rel = J.house_from(J.P(c, sub)["sign_index"], J.P(c, lord)["sign_index"])
        s = round(s * 0.6 + planet_strength(c, sub) * 0.4)
        s += 6 if rel in (1, 5, 9, 10, 11) else -6 if rel in (6, 8, 12) else 0
        s += 4 if J.relation(lord, sub) == "friend" else -4 if J.relation(lord, sub) == "enemy" else 0
    return max(5, min(98, s))


def _activated(c: dict, lord: str) -> list[int]:
    fr = functional_role(c, lord)
    hs = list(fr["rules"]) + [J.P(c, lord)["house"]]
    return sorted(set(hs))


AREA_HOUSES = {
    "Career & status": {10, 6, 11}, "Wealth & income": {2, 11, 5, 9}, "Marriage & partnerships": {7, 2, 5},
    "Health & vitality": {1, 6, 8}, "Home, mother & property": {4}, "Learning & children": {5, 9, 4},
    "Travel & foreign links": {3, 9, 12}, "Spiritual growth": {9, 12, 8},
}
AREA_GOOD = {
    "Career & status": "recognition, promotion, leadership responsibilities and public respect for your expertise",
    "Wealth & income": "steady growth in earnings, successful savings habits and access to new revenue streams",
    "Marriage & partnerships": "deeper harmony, mutual loyalty, constructive collaboration and shared life joy",
    "Health & vitality": "strong physical stamina, robust recuperative power and consistent daily wellness",
    "Home, mother & property": "peace of mind at home, affectionate family relationships and gains in property or vehicles",
    "Learning & children": "academic achievements, creative breakthroughs and fulfilling experiences through children",
    "Travel & foreign links": "enriching journeys, productive overseas connections and expanding horizons",
    "Spiritual growth": "clarity of conscience, deep contemplative insight and helpful guidance from mentors",
}
AREA_HARD = {
    "Career & status": "workplace politics, heavier obligations, delays in promotion or friction with superiors",
    "Wealth & income": "fluctuating cash flow, unforeseen household expenses or need to avoid speculative risks",
    "Marriage & partnerships": "communication friction, differing expectations or emotional distance requiring patience",
    "Health & vitality": "fatigue from overwork, digestive or nervous sensitivity; maintain strict rest routines",
    "Home, mother & property": "domestic disagreements, maintenance obligations or delays in property transactions",
    "Learning & children": "scattered intellectual focus, academic hurdles or concerns requiring care for children",
    "Travel & foreign links": "tiring journeys, travel delays or feeling unanchored while away from home",
    "Spiritual growth": "restless searching or inner dissatisfaction that pushes you to seek deeper answers",
}
NAT_KARAKA = {
    "Sun": "father, government, vitality and soul direction",
    "Moon": "mother, mind, emotional comfort and public reception",
    "Mars": "siblings, land, courage, technical skill and energy",
    "Mercury": "speech, commerce, intellect, learning and writing",
    "Jupiter": "children, wisdom, higher mentors and wealth",
    "Venus": "spouse, romance, luxury, arts and vehicles",
    "Saturn": "profession, longevity, discipline, service and endurance",
    "Rahu": "foreign links, innovation, technology, ambition and breakthroughs",
    "Ketu": "spirituality, research, deep detachment and liberation",
}


def _aspects_cast(c: dict, planet: str) -> list[int]:
    h = J.P(c, planet)["house"]
    return sorted({(h + x - 2) % 12 + 1 for x in J.aspects_houses(planet)})


def _conjunctions(c: dict, planet: str) -> list[str]:
    s = J.P(c, planet)["sign_index"]
    return [p["name"] for p in c["planets"] if p["sign_index"] == s and p["name"] != planet]


def life_effects(c: dict, lord: str, score: int, sub: str | None = None) -> list[dict]:
    acts = set(_activated(c, lord)) | (set(_activated(c, sub)) if sub else set())
    out = []
    for area, hs in AREA_HOUSES.items():
        hit = sorted(acts & hs)
        if not hit:
            continue
        hard = score < 50 or (all(x in J.DUSTHANA for x in hit) and area not in ("Spiritual growth", "Health & vitality"))
        t = "challenging" if hard and score < 45 else "mixed" if hard else "favourable" if score < 70 else "excellent"
        via = ", ".join(ordn(x) for x in hit)
        out.append({
            "area": area, "tone": t, "via": [ordn(x) for x in hit],
            "text": ("Possible " + AREA_HARD[area] if hard else "Likely " + AREA_GOOD[area]) + f" (operating through your {via} house" + ("s" if len(hit) > 1 else "") + ").",
        })
    return out


def lord_profile(c: dict, lord: str) -> dict:
    p = J.P(c, lord)
    sb = c.get("shadbala", {}).get("planets", {}).get(lord)
    fr = functional_role(c, lord)
    l1 = c["ascendant"]["sign_lord"]
    rel_l1 = J.house_from(p["sign_index"], J.P(c, l1)["sign_index"]) if lord != l1 else 1
    dig = p["dignity"].title()
    if p["retrograde"] and lord not in ("Rahu", "Ketu"):
        dig += " · retrograde"
    if p["combust"]:
        dig += " · combust"
    link = "supportive and cooperative" if rel_l1 in (1, 4, 5, 7, 9, 10, 11) else "demanding and growth-testing"
    facts = [
        {"label": "Placement", "value": f"{ordn(p['house'])} house · {p['sign']} {p['dms']}"},
        {"label": "Nakshatra", "value": f"{p['nakshatra']} pada {p['pada']} (ruled by {p['nakshatra_lord']})"},
        {"label": "Dignity", "value": dig},
        {"label": "Governs houses", "value": ", ".join(ordn(h) for h in fr["rules"]) or f"None directly (lunar node; manifests for {p['sign_lord']})"},
        {"label": "Aspects houses", "value": ", ".join(ordn(h) for h in _aspects_cast(c, lord))},
        {"label": "Conjunct with", "value": ", ".join(_conjunctions(c, lord)) or "None"},
        {"label": "Natural significator of", "value": NAT_KARAKA[lord]},
        {"label": "Relationship with Lagna lord", "value": f"{ordn(rel_l1)} from {l1}: {link} link with your personal self"},
    ]
    if sb:
        facts.append({"label": "Shadbala strength", "value": f"{sb['rupas']} / {sb['required']} rupas (" + ("sufficient strength" if sb["strong"] else "requires support") + ")"})
    return {"facts": facts, "aspects": _aspects_cast(c, lord), "conjunctions": _conjunctions(c, lord)}


def lord_remedy(lord: str) -> dict:
    r = J.REMEDY_DB[lord]
    return {"mantra": r["mantra"], "count": r["count"], "day": r["day"], "charity": r["charity"], "practice": r["ritual"], "deity": r["deity"]}


def _ad_more(c: dict, lord: str, ad: dict, sc: int, birth) -> dict:
    al = ad["lord"]
    dist = J.house_from(J.P(c, al)["sign_index"], J.P(c, lord)["sign_index"])
    rel = J.relation(lord, al)
    pds = []
    for pd in ad.get("children", []):
        if datetime.fromisoformat(pd["end"]) < birth:
            continue
        ps = _period_score(c, al, pd["lord"])
        pds.append({"lord": pd["lord"], "start": pd["start"][:10], "end": pd["end"][:10], "current": pd["current"], "score": ps, "tone": tone(ps)})
    if dist in (1, 4, 5, 7, 9, 10):
        angle = "kendra/trikona alignment: cooperative harmony, goals flow with natural ease"
    elif dist in (6, 8, 12):
        angle = "shashtashtaka/dwirdwadasa (6/8 or 2/12): dynamic tension, progress calls for conscious perseverance"
    else:
        angle = "neutral angle: results match your everyday initiative"
    word = {"friend": "a friend", "enemy": "an adversary", "neutral": "neutral", "same": "itself"}[rel]
    day = J.REMEDY_DB[al]["day"]
    advice = (f"This phase rewards leaning into {PLANET_GOOD[al].split(',')[0]}. Schedule important initiatives on {day}s and maintain proactive momentum." if sc >= 55
              else f"Move thoughtfully on major financial or contractual commitments. Practicing {al}'s supportive guidance ({J.REMEDY_DB[al]['ritual'].lower()}) provides helpful balance.")
    return {
        "relationship": f"{al} sits {ordn(dist)} from {lord} ({angle}). Classically, {lord} regards {al} as {word}.",
        "effects": life_effects(c, lord, sc, al), "pratyantar": pds, "advice": advice,
    }


def dasha_analysis(c: dict) -> list[dict]:
    now = datetime.now(UTC)
    birth = datetime.fromisoformat(c["birth"]["utc_datetime"])
    out = []
    for md in c["dasha"]["mahadashas"]:
        start, end = datetime.fromisoformat(md["start"]), datetime.fromisoformat(md["end"])
        if end < birth:
            continue
        lord = md["lord"]
        p = J.P(c, lord)
        score = _period_score(c, lord)
        acts = _activated(c, lord)
        fr = functional_role(c, lord)
        good = score >= 55

        # Rich multi-sentence summary
        acts_str = ", ".join(HOUSE_THEME[h].split(",")[0] for h in acts)
        theme_body = J.DASHA_THEMES[lord]
        prefix = f"During the {lord} Mahadasha ({md['years']} years), "
        if theme_body.startswith(prefix):
            theme_body = theme_body[len(prefix):]
            theme_body = theme_body[0].upper() + theme_body[1:] if theme_body else ""
        dasha_good_note = {
            "Sun": "With favorable solar backing, this period rewards stepping into executive leadership and acting with dignified integrity.",
            "Moon": "With supportive lunar grace, this period nourishes your emotional peace of mind, family milestones, and public goodwill.",
            "Mars": "With strong Martian vitality, this period turns decisive initiative, courage, and technical enterprise into tangible victories.",
            "Mercury": "With sharp Mercurial clarity, this period rewards commercial skill, analytical learning, and versatile networking.",
            "Jupiter": "With benevolent Jupiterian support, this period brings expansive wisdom, academic honors, and lasting prosperity.",
            "Venus": "With gracious Venusian blessings, this period enhances relationship harmony, creative arts, and refined material comforts.",
            "Saturn": "With steady Saturnian endurance, this period rewards patient discipline, methodical effort, and building lasting structures.",
            "Rahu": "With dynamic Rahu energy, this period opens unconventional breakthroughs, modern technologies, and rapid worldly advancement.",
            "Ketu": "With profound Ketu insight, this period fosters research breakthroughs, spiritual clarity, and freedom from unnecessary attachments.",
        }
        dasha_challenging_note = {
            "Sun": "Navigating this period calls for tempering pride, managing stress, and practicing diplomatic humility with authority figures.",
            "Moon": "This period asks for emotional grounding, gentle self-care, and avoiding impulsive decisions during mood fluctuations.",
            "Mars": "Channeling this energy requires patience, regular physical exercise, and avoiding hasty arguments or reckless speed.",
            "Mercury": "Staying balanced calls for periodic mental rest, avoiding overthinking, and keeping daily commitments well organized.",
            "Jupiter": "Navigating this phase rewards realistic expectations, avoiding over-optimism, and maintaining dietary moderation.",
            "Venus": "This period invites emotional maturity, mindful budgeting, and avoiding superficial relationship expectations.",
            "Saturn": "Persevering through this phase requires unhurried patience, looking after joint health, and trusting in gradual results.",
            "Rahu": "Guarding against risky shortcuts, illusions, or speculative ventures ensures that your ambition yields genuine success.",
            "Ketu": "Navigating sudden shifts calls for spiritual equanimity, staying grounded in daily routines, and letting go of outlived patterns.",
        }
        note = dasha_good_note.get(lord, "") if good else dasha_challenging_note.get(lord, "")
        summary = (
            f"The {lord} Mahadasha spans {md['years']} years, turning the primary momentum of your life toward {acts_str}. "
            f"In your Kundli, {lord} acts as a {fr['label'].split(' — ')[0].lower()} planet, occupying the {ordn(p['house'])} house "
            f"in {p['sign']} ({p['dignity']}). "
            f"{theme_body} {note}"
        )

        highlights = [f"Productive advancement in {HOUSE_THEME[h]}" for h in acts if h not in J.DUSTHANA][:3] or [f"Inner transformation and wisdom through {HOUSE_THEME[acts[0]]}"]
        cautions = [f"Mindful attention required around {HOUSE_THEME[h]}" for h in acts if h in J.DUSTHANA][:2]
        if not good:
            cautions.append(f"{lord}'s sensitive condition invites caution regarding {PLANET_HARD[lord]}")

        ads = []
        for ad in md.get("children", []):
            a_end = datetime.fromisoformat(ad["end"])
            if a_end < birth:
                continue
            sc = _period_score(c, lord, ad["lord"])
            sub_acts = _activated(c, ad["lord"])
            sub_focus = [HOUSE_THEME[h].split(",")[0] for h in sub_acts][:3]
            sub_focus_str = ", ".join(sub_focus)
            if sc >= 55:
                ad_summary = (
                    f"The {ad['lord']} Antardasha within {lord} Mahadasha activates matters of {sub_focus_str}, "
                    f"bringing favorable opportunities for {PLANET_GOOD[ad['lord']].split(',')[0]} and constructive progress."
                )
            else:
                ad_summary = (
                    f"The {ad['lord']} Antardasha within {lord} Mahadasha activates matters of {sub_focus_str}, "
                    f"calling for patient discernment regarding {PLANET_HARD[ad['lord']].split(',')[0]}."
                )
            ads.append({
                "lord": ad["lord"], "start": ad["start"], "end": ad["end"], "current": ad["current"],
                "score": sc, "tone": tone(sc), "more": _ad_more(c, lord, ad, sc, birth),
                "focus": sub_focus, "summary": ad_summary,
            })

        age_from = max(0.0, (start - birth).days / J.YEAR_DAYS)
        age_to = round((end - birth).days / J.YEAR_DAYS, 1)

        out.append({
            "lord": lord, "start": md["start"], "end": md["end"], "years": md["years"],
            "age_from": round(age_from, 1), "age_to": age_to, "current": md["current"],
            "past": end < now, "score": score, "tone": tone(score), "functional": fr["label"],
            "activates": acts, "summary": summary, "highlights": highlights, "cautions": cautions,
            "antardashas": ads,
            "plain": M.dasha_plain(lord, tone(score), acts),
            "more": {
                "effects": life_effects(c, lord, score), "remedy": lord_remedy(lord),
                "houses": [{"house": h, "theme": HOUSE_THEME[h], "why": "occupied" if h == p["house"] else "governed"} for h in acts],
                "best_sub": max(ads, key=lambda x: x["score"])["lord"] if ads else None,
                "hard_sub": min(ads, key=lambda x: x["score"])["lord"] if ads else None,
            },
        })
        if (start - birth).days / J.YEAR_DAYS > 100:
            break
    return out


LAGNA_LORD_LIFE_PURPOSE: dict[int, str] = {
    1: "Having your Lagna lord seated in the first house is a strong blessing for self-reliance, physical vitality, and clear personal identity. You are the chief architect of your own destiny, preferring to lead from the front with dignity and self-assurance. Your life unfolds through personal enterprise, and you command natural respect wherever you go.",
    2: "With your Lagna lord seated in the second house, your core life purpose is intimately tied to family heritage, values, and creating lasting financial stability. You derive genuine fulfillment from protecting loved ones, speaking with wisdom and sincerity, and carefully building tangible assets that outlast temporary trends.",
    3: "With your Lagna lord placed in the third house, your life journey is driven by personal courage, initiative, and creative communication. You are someone who refuses to rely passively on good luck; instead, you carve out your own path through persistent self-effort, hands-on enterprise, and the lively sharing of ideas.",
    4: "Having your Lagna lord residing in the fourth house roots your personal fulfillment deeply in home, family peace, and emotional contentment. You have an enduring bond with your mother or ancestral lineage, and you thrive best when your domestic sanctuary is harmonious, secure, and surrounded by quiet comforts.",
    5: "With your Lagna lord placed in the fifth house, your vital life energy expresses itself through creative intelligence, higher learning, and joyful mentorship. You possess a sharp, reflective intellect with an intuitive grasp of ethics and good judgment. Your life gains deep meaning through creative contributions and guiding the next generation.",
    6: "With your Lagna lord situated in the sixth house, your life purpose is forged through dedication, problem-solving, and overcoming real-world obstacles. You possess strong mental resilience, not backing down from competition or hard work. You shine in service-oriented vocations where bringing order to difficult situations makes an immediate difference.",
    7: "Having your Lagna lord stationed in the seventh house indicates that your personal growth is mirror-reflected through relationships, partnerships, and public engagement. You thrive in collaboration, learning the deepest truths about yourself through marriage and meaningful alliances. Your diplomacy and ability to connect with diverse minds are key life assets.",
    8: "With your Lagna lord positioned in the eighth house, your life is marked by profound inner resilience, transformative transitions, and a natural instinct for uncovering hidden truths. Rather than settling for superficial comforts, you are drawn to deep inquiry, psychological insight, and research. Significant turning points in life regularly renew your strength.",
    9: "With your Lagna lord placed in the auspicious ninth house, your life orientation is guided by moral principles, higher knowledge, and a pursuit of wisdom. You have natural respect for mentors, diverse cultures, and lifelong learning. Good fortune and spiritual clarity accompany you when you remain true to your ethical compass.",
    10: "Having your Lagna lord commanding the tenth house is a premier signature for professional prominence, social responsibility, and visible contribution. You carry an innate desire to leave an honorable mark on your chosen field. You are built for leadership, earning public respect through sustained craftsmanship and ethical conduct.",
    11: "With your Lagna lord located in the eleventh house, your life purpose flourishes through collective networks, long-term aspirations, and steady material achievement. You possess a gift for building friendships with knowledgeable allies and turning ambitious visions into tangible success. Your efforts yield reliable gains and social goodwill.",
    12: "With your Lagna lord residing in the twelfth house, your life journey carries a reflective, contemplative depth, often drawing you toward foreign connections, spiritual study, or meaningful work behind the scenes. You find profound peace in quiet solitude, possessing an innate generosity and freedom from petty worldly rivalries.",
}

CAREER_LORD_HOUSE: dict[int, str] = {
    1: "Your career ruler placed in the first house brings your professional identity directly into your personal presence. You excel in vocations where you are the public face of your work, thriving in independent ventures, consultancy, or roles where your personal initiative and reputation drive the entire enterprise forward.",
    2: "With your career lord seated in the second house, your vocation is closely tied to finance, speech, consulting, or family enterprise. You do exceptionally well in fields requiring persuasive communication, wealth advisory, or administrative stewardship, where your voice and reliability build lasting professional trust.",
    3: "Having your career lord in the third house favors vocations demanding hands-on initiative, writing, digital media, commerce, or technical communication. You perform best in dynamic work environments that involve short travel, constant coordination, and the freedom to experiment with fresh strategies.",
    4: "Your career lord placed in the fourth house directs your professional talents toward real estate, education, infrastructure, agriculture, or human resource welfare. You excel in creating secure, supportive systems for organizations, often achieving your greatest vocational satisfaction in familiar or domestic-facing domains.",
    5: "With your career ruler in the fifth house, your professional calling is fueled by intellectual innovation, strategic counsel, teaching, or creative arts. You have natural instincts for problem-solving and mentoring, shining when allowed to design new solutions rather than executing repetitive routines.",
    6: "Having your career lord positioned in the sixth house aligns your profession with service, healthcare, legal analysis, auditing, or crisis management. You are a tireless problem-solver who earns respect by tackling complex operational difficulties that others avoid, rising steadily through discipline and resilience.",
    7: "With your career ruler occupying the seventh house, your professional success is intimately tied to public relations, partnerships, client management, or international trade. You thrive in negotiation, mediation, and customer-facing roles, where mutual collaboration and tactful diplomacy open lucrative doors.",
    8: "Your career lord situated in the eighth house draws your vocation toward specialized research, forensic investigation, data analytics, tax advisory, or esoteric sciences. You excel at unearthing hidden value, steering organizations through confidential transitions, and solving intricate problems requiring quiet, dedicated concentration.",
    9: "Having your career ruler in the ninth house points toward high-level advisory roles, higher education, legal practice, publishing, or international consultancy. Your career is guided by strong ethical values and vision, earning you honor through mentorship, specialized wisdom, and cross-cultural collaborations.",
    10: "With your career lord reigning in its own tenth house, you possess outstanding executive potential, institutional leadership, and natural professional authority. You are capable of carrying heavy organizational responsibilities, earning sustained public recognition through disciplined competence and unwavering integrity.",
    11: "Having your career ruler seated in the eleventh house ensures that your professional efforts translate into substantial gains, influential industry networks, and corporate achievements. You excel in leading large teams, managing client networks, and turning strategic projects into profitable, recognized realities.",
    12: "With your career lord in the twelfth house, your professional path frequently connects with foreign organizations, multinational firms, research laboratories, or institutions operating away from the public eye. You achieve significant success through international assignments, behind-the-scenes strategy, or philanthropic projects.",
}

WEALTH_LORD_HOUSE: dict[int, str] = {
    1: "Your wealth ruler seated in the first house indicates that your earning capacity is driven entirely by your personal skill, reputation, and direct initiative. You have the ability to generate income through your own craftsmanship, and your financial standing rises hand-in-hand with your personal standing in life.",
    2: "With your wealth lord strong in the second house, you possess natural financial intelligence and a steady instinct for capital preservation. You believe in methodical accumulation, prudent cash-flow management, and creating tangible assets that offer lasting security to your family across generations.",
    3: "Having your wealth lord in the third house connects your earnings with personal initiative, commercial trade, writing, digital skills, or enterprise. Your financial prosperity grows as you proactively take calculated risks, market your skills, and leverage modern communication channels.",
    4: "With your wealth ruler resting in the fourth house, your financial assets accumulate securely through real estate, residential property, ancestral resources, and vehicle investments. You prioritize domestic stability and building a debt-free home base that provides enduring peace of mind.",
    5: "Your wealth lord positioned in the fifth house blesses you with sharp investment acumen, creative revenue ideas, and gains through intellectual capital. You have an instinct for spotting emerging opportunities, but build the most durable wealth when balancing calculated investments with disciplined diversification.",
    6: "With your wealth lord in the sixth house, your finances grow steadily through professional service, disciplined day-to-day work, and careful budgeting. You are cautious with debt and manage operational costs with precision, steadily turning regular savings into substantial long-term wealth.",
    7: "Having your wealth ruler in the seventh house indicates that financial growth is enhanced through joint ventures, marriage, business alliances, or commercial trade. You benefit greatly from transparent partnership agreements and customer-focused commerce that builds enduring goodwill.",
    8: "With your wealth ruler placed in the eighth house, financial milestones often come through unexpected avenues, family inheritances, joint holdings, insurance, or strategic restructuring. Maintaining absolute transparency in tax and joint financial records ensures your resources remain secure and resilient against sudden shifts.",
    9: "Having your wealth lord stationed in the ninth house is an auspicious mark of righteous prosperity, ethical commerce, and gains through higher learning or international dealings. You enjoy financial luck when your business practices honor moral principles and you invest in expanding your horizons.",
    10: "With your wealth lord commanding the tenth house, your earnings flow directly from your professional standing, government links, or executive leadership. You earn honorable remuneration for high-level contributions, and your commercial reputation serves as your greatest financial asset.",
    11: "Your wealth lord residing in the eleventh house creates a potent combination for ongoing capital growth, varied income streams, and fruitful financial networks. Your savings habits combine harmoniously with your ability to monetize opportunities, resulting in substantial long-term accumulation.",
    12: "With your wealth ruler in the twelfth house, financial management calls for conscious budgeting, prudent tax planning, and guarding against leakage through impulsive expenditures. You do well with international investments, institutional funds, and charitable contributions that bring meaningful satisfaction.",
}

MARRIAGE_LORD_HOUSE: dict[int, str] = {
    1: "With your partnership lord seated in your first house, your spouse is deeply devoted to you, bringing a lively, magnetic presence into your life. Your partner desires to be an equal participant in your personal ambitions, and your marital happiness flourishes when you make decisions together as a unified team.",
    2: "Having your marriage lord in the second house indicates that partnership significantly enriches your family life and financial stability. Your spouse is likely to be family-oriented, eloquent, and supportive of domestic traditions, contributing constructively to household savings and shared prosperity.",
    3: "With your 7th lord positioned in the third house, your relationship thrives on intellectual friendship, shared travels, and lively everyday banter. Your partner is dynamic, encouraging your personal initiatives and standing beside you as an enthusiastic confidant in all life ventures.",
    4: "Having your partnership ruler in the fourth house roots marital happiness in domestic comfort, emotional security, and shared home peace. Your spouse values a tranquil home environment and shares deep respect for family welfare, helping to create a welcoming, emotionally grounded sanctuary.",
    5: "With your marriage lord placed in the fifth house, your relationship is blessed with romance, mutual creative appreciation, and shared joy through children. You are drawn to a partner who possesses warmth, intellectual sparkle, and a refined sense of humor, keeping the romance fresh over the years.",
    6: "Having your 7th lord in the sixth house suggests that partnership dynamics require conscious patience, practical teamwork, and clear boundaries. Your spouse is hard-working and dutiful, but daily workplace stress can occasionally spill into home life; resolving minor differences through calm communication prevents lingering friction.",
    7: "With your marriage lord dignified in its own seventh house, you are blessed with an honorable, capable, and supportive life companion. Your spouse commands natural respect, values marital fidelity, and shares your vision for a balanced, dignified partnership built on reciprocal admiration.",
    8: "Your partnership ruler situated in the eighth house points to a deeply bonding, emotionally transformative union that evolves significantly over time. Your spouse brings deep intuition and shared financial acumen into your life; cultivating mutual vulnerability and open trust ensures an unbreakable connection.",
    9: "Having your 7th lord in the ninth house indicates a noble, cultured partner who brings good fortune, ethical grounding, and higher perspective into your life. Your spouse may come from a distinct cultural or intellectual background, inspiring you toward spiritual growth and expanded horizons.",
    10: "With your marriage lord occupying the tenth house, your spouse is ambitious, professionally accomplished, and commands genuine public respect. Your marital partnership enhances your social standing, and you thrive when actively encouraging each other's vocational milestones.",
    11: "Having your partnership ruler in the eleventh house promises a relationship that feels like an enduring, supportive friendship. Your spouse shares your long-term dreams, introduces you to inspiring social circles, and helps turn your shared aspirations into tangible reality.",
    12: "With your 7th lord residing in the twelfth house, your marital bond carries a private, gentle, and deeply spiritual tone. Your spouse may have international ties or an introspective nature, and your relationship flourishes best away from external interference, thriving on quiet mutual understanding and compassion.",
}

HEALTH_CONSTITUTION: dict[int, str] = {
    1: "Having your vitality ruler well placed in the first house provides a naturally robust constitution, quick recuperative ability, and high physical stamina. Your body responds promptly to clean living; maintaining regular physical exercise and adequate hydration keeps your energy radiant throughout the seasons.",
    2: "With your vitality lord in the second house, constitutional balance is intimately linked to your diet, throat health, and speech patterns. Maintaining regular, nourishing meal times and avoiding overly rich or spicy foods protects your vocal cords and digestive tract from undue irritation.",
    3: "Having your health ruler in the third house bestows agile nervous stamina and physical dexterity, though restlessness can sometimes cause energy dips. Mindful care of your shoulders, arms, and upper respiratory tract—along with periodic screen-free rest—preserves your vitality.",
    4: "With your vitality lord resting in the fourth house, physical health is directly influenced by emotional serenity and domestic peace of mind. Cultivating restful sleep habits, gentle cardiovascular exercise, and spending time in serene environments protects your chest and digestive equilibrium.",
    5: "Your vitality ruler in the fifth house supports good metabolic vitality and digestive fire, though mental over-exertion can strain the stomach. Balancing intellectual work with joyful outdoor recreation and maintaining clean eating habits keeps your vital energy well regulated.",
    6: "Having your vitality lord in the sixth house gives your immune system an active capacity to combat seasonal ailments, though chronic stress from overwork is your primary vulnerability. Prioritizing structured daily rest, gut health, and avoiding unnecessary tension keeps your stamina strong and resilient.",
    7: "With your vitality ruler placed in the seventh house, your physical well-being benefits greatly from social harmony and balanced relationships. Paying mindful attention to your kidneys, lower back, and daily water intake ensures that your bodily fluids and energy flow smoothly.",
    8: "Having your vitality lord situated in the eighth house confers deep recuperative longevity and survival stamina through physical turning points. It is essential to manage chronic stress, protect excretory and reproductive health, and avoid extreme physical exhaustion through disciplined moderation.",
    9: "With your vitality ruler in the ninth house, your constitutional vitality is strong, supported by an active lifestyle and an optimistic disposition. Mindful care of your hips, thighs, and liver health through wholesome nutrition and regular walking helps you sustain long-term physical vigor.",
    10: "Having your health ruler commanding the tenth house supports strong physical stamina adapted for sustained professional activity. However, you must be careful not to sacrifice proper sleep or regular meals for work obligations; caring for your joints, knees, and posture ensures enduring stamina.",
    11: "With your vitality lord in the eleventh house, physical energy remains generally favorable and responsive to healthy habits. Gentle daily walks, keeping circulation active in your calves and ankles, and socializing with uplifting friends keep your vitality buoyant.",
    12: "Having your vitality ruler residing in the twelfth house suggests a sensitive constitution that absorbs external environmental stress quickly. Ensuring quality sleep, practicing calming breathwork (pranayama), and protecting your feet and lymphatic balance provide essential restoration for your nervous system.",
}

EDUCATION_INTELLECT: dict[int, str] = {
    1: "Your ruler of intellect placed in the first house gives a brilliant, curious mind that grasps concepts quickly and enjoys independent inquiry. You learn best when you can apply theoretical knowledge to real-life situations, excelling in self-directed study and innovative intellectual pursuits.",
    2: "With your 5th lord in the second house, your learning style is thorough, methodical, and verbally gifted. You possess strong memory retention and an aptitude for languages, economics, mathematics, or classical subjects, communicating your knowledge with natural clarity and poise.",
    3: "Having your ruler of intellect situated in the third house endows you with mental agility, sharp analytical reasoning, and hands-on technical skills. You flourish in modern communications, digital technologies, creative writing, and practical research where diverse streams of data are synthesized.",
    4: "With your 5th lord resting in the fourth house, your intellectual growth is nurtured by deep foundational study, traditional academia, and reflective contemplation. You absorb complex principles thoroughly when studying in a quiet, peaceful environment that fosters deep concentration.",
    5: "Having your ruler of intellect dignified in its own fifth house is an exceptional mark of creative genius, strategic foresight, and profound scholarship. Your analytical reasoning is penetrating, allowing you to master intricate subjects, mentor others effortlessly, and produce original intellectual work.",
    6: "With your 5th lord positioned in the sixth house, your intellect shines in critical analysis, diagnostic problem-solving, medicine, law, and technical troubleshooting. You are not intimidated by detail-heavy or challenging syllabi, deriving genuine satisfaction from solving complex puzzles that stump others.",
    7: "Having your ruler of intellect in the seventh house indicates a collaborative learning orientation. You absorb concepts fastest through intellectual debate, peer discussions, and interactive seminars, excelling in fields involving public psychology, international affairs, and commercial negotiation.",
    8: "With your 5th lord seated in the eighth house, your intellectual mind is forensic, probing, and naturally drawn to uncover hidden mechanisms. You excel in deep academic research, data science, psychological analysis, and advanced technical or esoteric inquiries where patience unlocks hidden discoveries.",
    9: "Having your ruler of intellect in the ninth house is a supreme blessing for higher learning, philosophical depth, and academic distinction. You are naturally drawn to university education, law, ethics, and cross-disciplinary research, absorbing wisdom easily under the guidance of knowledgeable professors and mentors.",
    10: "With your 5th lord in the tenth house, your educational achievements directly feed your professional authority and vocational standing. You excel in applied sciences, executive management, governance, and specialized professional certifications that earn tangible industry recognition.",
    11: "Having your ruler of intellect placed in the eleventh house ensures that your knowledge and analytical abilities translate into fruitful group collaborations and intellectual networks. You learn eagerly from knowledgeable peers and excel in large-scale research initiatives, technology forums, and future-oriented studies.",
    12: "With your 5th lord in the twelfth house, your intellectual gifts flourish in creative imagination, deep reflective contemplation, and behind-the-scenes research. You do exceptionally well in foreign universities, independent scholarly writing, or fields requiring intuitive insight beyond standard textbooks.",
}


def key_predictions(c: dict, planets: list[dict], dashas: list[dict]) -> list[dict]:
    la = c["life_areas"]
    asc = c["ascendant"]
    sp = SIGN_PROFILE[asc["sign"]]
    l1 = J.P(c, asc["sign_lord"])
    moon = J.P(c, "Moon")
    cur = next((d for d in dashas if d["current"]), None)
    nxt = next((d for d in dashas if not d["past"] and not d["current"]), None)

    # 1. Personality — 4 rich paragraphs
    p_p1 = (f"With {asc['sign']} rising (Ascendant at {asc['dms']}), the first impression you give to the world is of someone who is {sp[2]}. "
            f"You carry yourself with natural dignity, and people readily notice your authenticity and quiet capability. "
            f"{sp[5]}")
    p_p2 = (f"Your chart's ruling planet (Lagna lord), {asc['sign_lord']}, sits in the {ordn(l1['house'])} house ({l1['sign']}, {l1['dignity']}). "
            f"This directs your primary life vitality and inner drive toward {HOUSE_THEME[l1['house']].split(',')[0]}. "
            f"{LAGNA_LORD_LIFE_PURPOSE[l1['house']]}")
    p_p3 = (f"On an emotional and psychological level, having your Moon in {moon['sign']} within {moon['nakshatra']} nakshatra "
            f"(ruled by {moon['nakshatra_lord']}) endows you with a {NAK_PROFILE[J.NAKSHATRAS.index(moon['nakshatra'])][2]} emotional nature. "
            f"You find inner contentment when your surroundings are harmonious and your emotional roots feel secure.")
    p_p4 = (f"In everyday action, you operate with {sp[3]}. "
            f"The primary area for conscious balance is {sp[4]}. Grounding daily routines, quiet self-reflection, and unhurried patience will always serve you best.")
    personality_text = f"{p_p1}\n\n{p_p2}\n\n{p_p3}\n\n{p_p4}"

    items = [{"area": "Personality", "score": planet_strength(c, asc["sign_lord"]), "text": personality_text}]

    # 2. Career — 4 rich paragraphs
    car_a = la["career"]
    car_desc = car_a["summary"].split("\n\n")[-1]
    c10 = c["houses"][9]
    l10 = J.P(c, c10["lord"])
    c_p1 = (f"Your professional life is governed primarily by the 10th house ({c10['sign']}, ruled by {c10['lord']}), "
            f"supported by the 6th house of daily work and the 11th house of achievements. "
            f"Overall vocational outlook is rated {car_a['outlook']} (score {car_a['score']}/100). "
            f"{car_desc}")
    c_p2 = (f"Your 10th lord {c10['lord']} occupies the {ordn(l10['house'])} house ({l10['sign']}, {l10['dignity']}). "
            f"{CAREER_LORD_HOUSE[l10['house']]}")
    c_p3 = (f"Natural career significators Sun, Saturn, and Mercury indicate that your work thrives on clear responsibility, professional ethics, and autonomy. "
            f"You excel when given space to solve problems systematically and take pride in the quality of your output. "
            f"Collaborative alliances and maintaining professional ethics provide your greatest long-term stability.")
    c_p4 = (f"To build durable career success, keep your long-term vision clear and avoid rash moves during temporary workplace stress. "
            + (f"Because your running planetary period energizes career houses, this is a pivotal chapter for taking purposeful initiative and consolidating your standing."
               if cur and any(h in cur["activates"] for h in (10, 6, 11)) else
               "Focus on continuous skill refinement and cultivating trustworthy professional networks, which will yield substantial rewards in coming career cycles."))
    items.append({"area": "Career", "score": car_a["score"], "text": f"{c_p1}\n\n{c_p2}\n\n{c_p3}\n\n{c_p4}"})

    # 3. Wealth (Finance) — 4 rich paragraphs
    fin_a = la["finance"]
    fin_desc = fin_a["summary"].split("\n\n")[-1]
    c2 = c["houses"][1]
    c11 = c["houses"][10]
    l2 = J.P(c, c2["lord"])
    w_p1 = (f"Financial prosperity in your Kundli combines accumulated savings (2nd house in {c2['sign']}), "
            f"regular revenue (11th house in {c11['sign']}), and the blessings of past merit (5th and 9th houses). "
            f"Your wealth potential is assessed as {fin_a['outlook']} (score {fin_a['score']}/100). "
            f"{fin_desc}")
    w_p2 = (f"Your 2nd lord of savings and assets, {c2['lord']}, sits in the {ordn(l2['house'])} house ({l2['sign']}, {l2['dignity']}). "
            f"{WEALTH_LORD_HOUSE[l2['house']]}")
    w_p3 = (f"Your financial temperament naturally leans toward creating dependable, long-term security. "
            f"You are resourceful and appreciate quality, but should stay vigilant against speculative shortcuts or emotional spending during high-stress periods. "
            f"Diversifying your savings into secure instruments and tangible assets protects your family across cycles.")
    w_p4 = (f"To maximize your prosperity, maintain orderly bookkeeping and build a reliable contingency fund. "
            + (f"Your current dasha actively stimulates your wealth axis, making this an ideal window for methodical capital accumulation and prudent investments."
               if cur and any(h in cur["activates"] for h in (2, 11, 5, 9)) else
               "Steady compounding and prudent financial habits established now will blossom fully in the upcoming prosperity cycles."))
    items.append({"area": "Wealth", "score": fin_a["score"], "text": f"{w_p1}\n\n{w_p2}\n\n{w_p3}\n\n{w_p4}"})

    # 4. Marriage & relationships — 4 rich paragraphs
    rel_a = la["relationships"]
    rel_desc = rel_a["summary"].split("\n\n")[-1]
    c7 = c["houses"][6]
    l7 = J.P(c, c7["lord"])
    r_p1 = (f"Partnership and marriage are read primarily from the 7th house ({c7['sign']}, ruled by {c7['lord']}), "
            f"supported by the 5th house of affection and the 2nd house of family harmony. "
            f"The general relationship outlook is rated {rel_a['outlook']} (score {rel_a['score']}/100). "
            f"{rel_desc}")
    r_p2 = (f"Your 7th lord of partnership, {c7['lord']}, is positioned in the {ordn(l7['house'])} house ({l7['sign']}, {l7['dignity']}). "
            f"{MARRIAGE_LORD_HOUSE[l7['house']]}")
    r_p3 = (f"In close relationships, you value genuine emotional safety, mutual loyalty, and open communication. "
            f"When friction occurs, it is usually because expectations remain unspoken or personal boundaries feel stretched. "
            f"Giving each other breathing room and speaking with gentle honesty keeps your companionship warm and vibrant.")
    r_p4 = (f"Practical relationship advice: nurture shared interests, celebrate small moments of domestic joy, and avoid turning everyday differences into matters of personal pride. "
            + (f"Your running dasha actively influences your relationship houses, bringing personal connections into sharp, rewarding focus."
               if cur and any(h in cur["activates"] for h in (7, 2, 5)) else
               "Patient understanding and mutual respect remain the enduring pillars of your long-term marital happiness."))
    items.append({"area": "Marriage & relationships", "score": rel_a["score"], "text": f"{r_p1}\n\n{r_p2}\n\n{r_p3}\n\n{r_p4}"})

    # 5. Health — 4 rich paragraphs
    hea_a = la["health"]
    hea_desc = hea_a["summary"].split("\n\n")[-1]
    c6 = c["houses"][5]
    l1 = J.P(c, asc["sign_lord"])
    h_p1 = (f"Physical vitality in your chart is anchored by your Ascendant constitution, biological resistance (6th house in {c6['sign']}), "
            f"and longevity indicators. "
            f"Your baseline vitality is rated {hea_a['outlook']} (score {hea_a['score']}/100). "
            f"{hea_desc}")
    h_p2 = (f"Your vitality ruler, {asc['sign_lord']}, sits in the {ordn(l1['house'])} house ({l1['sign']}, {l1['dignity']}). "
            f"{HEALTH_CONSTITUTION[l1['house']]}")
    h_p3 = (f"Mindful wellness habits to cultivate: listen closely to your body's early signals of fatigue, stay well hydrated throughout the day, and maintain regular sleep timings. "
            f"{sp[8]} "
            f"Avoid burning the candle at both ends, and establish consistent sleep and meal timings.")
    h_p4 = (f"Physical exercise suited to your constitution—such as brisk outdoor walking, gentle yoga, and deep pranayama breathing—clears accumulated stress and revitalizes your nervous system. "
            + (f"During your running dasha, pay extra attention to restorative rest and avoid chronic physical overwork."
               if cur and any(h in cur["activates"] for h in (6, 8, 1)) else
               "Consistent daily routines and a nourishing, wholesome diet form your strongest shield against seasonal ailments."))
    items.append({"area": "Health", "score": hea_a["score"], "text": f"{h_p1}\n\n{h_p2}\n\n{h_p3}\n\n{h_p4}"})

    # 6. Education — 4 rich paragraphs
    edu_a = la["education"]
    edu_desc = edu_a["summary"].split("\n\n")[-1]
    c5 = c["houses"][4]
    c9 = c["houses"][8]
    l5 = J.P(c, c5["lord"])
    e_p1 = (f"Your intellectual growth combines foundational schooling (4th house), analytical intelligence (5th house in {c5['sign']}), "
            f"and higher wisdom (9th house in {c9['sign']}). "
            f"Your academic potential is assessed as {edu_a['outlook']} (score {edu_a['score']}/100). "
            f"{edu_desc}")
    e_p2 = (f"Your 5th lord of intellect, {c5['lord']}, resides in the {ordn(l5['house'])} house ({l5['sign']}, {l5['dignity']}). "
            f"{EDUCATION_INTELLECT[l5['house']]}")
    e_p3 = (f"You absorb knowledge with greatest depth when concepts connect with practical reality or philosophical meaning, rather than dry memorization. "
            f"Mercury blesses you with swift comprehension, while Jupiter enriches your perspective with enduring ethical wisdom.")
    e_p4 = (f"Lifelong learning keeps your mind youthful; dedicate regular time to reading, independent research, or acquiring modern certifications in your field. "
            + (f"Your running dasha actively stimulates your intellectual houses, making this a prime window for academic achievement and expanding your knowledge base."
               if cur and any(h in cur["activates"] for h in (5, 9, 4)) else
               "Channel your intellectual curiosity into focused research, and share your insights generously with others through mentorship."))
    items.append({"area": "Education", "score": edu_a["score"], "text": f"{e_p1}\n\n{e_p2}\n\n{e_p3}\n\n{e_p4}"})

    # 7. Current period (Running Dasha) — 4 rich paragraphs
    if cur:
        ad = next((x for x in cur["antardashas"] if x["current"]), None)
        cur_score = ad["score"] if ad else cur["score"]
        ad_str = f" and {ad['lord']} Antardasha (active until {ad['end'][:10]})" if ad else ""
        cp_p1 = (f"You are currently traversing the {cur['lord']} Mahadasha{ad_str}. "
                 f"In this life chapter, {cur['lord']}'s overarching influence sets your broad life trajectory, while "
                 + (f"{ad['lord']}'s sub-period governs immediate day-to-day priorities. " if ad else "your daily affairs reflect its direct planetary rhythm. ")
                 + f"Together, this period concentrates cosmic energy primarily upon your {', '.join(HOUSE_THEME[h].split(',')[0] for h in cur['activates'][:3])}.")
        cp_p2 = (f"The prevailing tone of this phase is {cur['tone']}. "
                 f"When navigated with conscious awareness, {cur['lord']}'s influence encourages personal maturity, purposeful initiative, and aligning your actions with noble principles.")
        cp_p3 = (f"To make the best of this window, maintain unhurried discipline and keep your focus aligned with {cur['lord']}'s natural wisdom. "
                 + (f"Remain mindful around {cur['cautions'][0].lower()}." if cur["cautions"] else "Avoid impulsive shortcuts during stressful weeks."))
        lord_name = cur["lord"]
        day = J.REMEDY_DB.get(lord_name, {}).get("day", "favorable")
        cp_p4 = (f"Practical guidance: establishing regularity in your work and taking quiet moments of contemplation on {day}s brings grounding stability and peace of mind.")
        items.append({"area": "Current period", "score": cur_score, "text": f"{cp_p1}\n\n{cp_p2}\n\n{cp_p3}\n\n{cp_p4}"})

    # 8. Next major period — 3 rich paragraphs
    if nxt:
        next_acts_str = ", ".join(HOUSE_THEME[h].split(",")[0] for h in nxt["activates"][:3])
        np_p1 = (f"Looking ahead, your next major life chapter will be the {nxt['lord']} Mahadasha, commencing on {nxt['start'][:10]} "
                 f"(around age {nxt['age_from']:.0f}) and extending over {nxt['years']} years. "
                 f"This transition marks an organic evolution in your life's primary focus, turning cosmic momentum toward your {next_acts_str}.")
        np_p2 = (f"Anticipated as a {nxt['tone']} phase, this upcoming chapter will open fresh doors for personal maturation, new responsibilities, and meaningful achievements.")
        np_p3 = (f"Preparation guidance: utilize the remaining span of your current dasha to resolve lingering obligations and build solid foundations. "
                 f"Welcoming the {nxt['lord']} period with quiet confidence, ethical clarity, and patient resolve will ensure a smooth and rewarding transition.")
        items.append({"area": "Next major period", "score": nxt["score"], "text": f"{np_p1}\n\n{np_p2}\n\n{np_p3}"})

    return items


def build_analysis(c: dict) -> dict:
    asc = c["ascendant"]
    moon = J.P(c, "Moon")
    planets = [planet_reading(c, n) for n in J.NINE]
    dashas = dasha_analysis(c)
    ranked = sorted((p for p in planets if p["planet"] not in ("Rahu", "Ketu")), key=lambda x: -x["score"])
    ni = J.NAKSHATRAS.index(moon["nakshatra"])
    deity, symbol, nature = NAK_PROFILE[ni]
    present_yogas = [y for y in c["yogas"] if y["present"]]
    active_doshas = [d for d in c["doshas"] if d["present"]]
    yk = [p["planet"] for p in planets if p["functional"]["role"] == "yogakaraka"]
    return {
        "version": 2,
        "overview": {
            "headline": f"{asc['sign']} ascendant · {moon['sign']} Moon · {moon['nakshatra']} nakshatra",
            "strongest": [p["planet"] for p in ranked[:3]], "weakest": [p["planet"] for p in ranked[-2:]],
            "yogakaraka": yk, "yoga_count": len(present_yogas), "dosha_count": len(active_doshas),
            "overall": round(sum(a["score"] for a in c["life_areas"].values()) / len(c["life_areas"])),
        },
        "ascendant": sign_profile(asc["sign"], asc["sign_lord"]) | {"nakshatra": asc["nakshatra"], "pada": asc["pada"], "degree": asc["dms"]},
        "moon": sign_profile(moon["sign"], moon["sign_lord"]),
        "nakshatra": {"name": moon["nakshatra"], "pada": moon["pada"], "lord": moon["nakshatra_lord"], "deity": deity, "symbol": symbol, "nature": nature,
                      "gana": GANA[ni], "yoni": YONI[ni], "nadi": NADI[nadi_index(ni)]},
        "avakhada": avakhada(c),
        "panchang": birth_panchang(c),
        "predictions": key_predictions(c, planets, dashas),
        "planets": planets,
        "dashas": dashas,
        "lord_profiles": {n: lord_profile(c, n)["facts"] for n in J.NINE},
        "house_meanings": {str(h["house"]): M.house_meaning(h["house"], h["score"], h["lord"], h["lord_house"], h["occupants"]) for h in c["house_analysis"]},
        "yoga_meanings": {y["name"]: M.yoga_meaning(y["category"], y["name"]) for y in c["yogas"] if y["present"]},
        "dosha_meanings": {d["name"]: {"what": M.DOSHA_PLAIN.get(d["name"], ("", ""))[0], "advice": M.DOSHA_PLAIN.get(d["name"], ("", ""))[1],
                                       "status": ("Present" + (f" ({d['severity']})" if d.get("severity") else "") + (" but partly cancelled" if d.get("cancellations") else "")) if d["present"] else "Not present in your chart — no action needed."}
                           for d in c["doshas"]},
        "methodology": [
            f"Sidereal zodiac, {c['settings']['ayanamsa'].replace('_', ' ').title()} ayanamsa ({c['ayanamsa_degrees']:.4f}°), {c['settings']['node_type']} node.",
            f"Houses: {c['settings']['house_system'].replace('_', ' ')}; planetary positions from {c['engine']}.",
            "Vimshottari dasha from the Moon's nakshatra, year = 365.2425 days.",
            "Functional nature by lagna (Parashari), dignity, house placement and Shadbala combine into the strength scores shown.",
            "Interpretations describe tendencies for reflection — not certainties, and not medical, legal or financial advice.",
        ],
    }
