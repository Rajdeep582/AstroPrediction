export type Account = { id: string; username: string };

export type Profile = {
  id: string; name: string; birth_date: string; birth_time: string; birthplace: string;
  latitude: number; longitude: number; timezone: string; description?: string;
};

export type BirthForm = {
  name: string; birth_date: string; birth_time: string; birthplace: string; latitude: string; longitude: string;
  timezone: string; ayanamsa: string; chart_style: ChartStyle; node_type: string; house_system: string; profile_id?: string;
};

export type ChartStyle = "north" | "south" | "east";

export type Planet = {
  name: string; absolute_longitude: number; longitude: number; dms: string; sign: string; sign_index: number; sign_lord: string;
  house: number; bhava: number; nakshatra: string; pada: number; nakshatra_lord: string; retrograde: boolean; speed: number;
  dignity: string; combust: boolean;
};

export type VargaChart = {
  division: number; name: string; signifies: string; ascendant_sign: number;
  placements: { name: string; sign: string; sign_index: number; house: number }[];
};

export type DashaPeriod = {
  lord: string; start: string; end: string; years: number; level: number; current: boolean;
  interpretation?: string; children?: DashaPeriod[];
};

export type Yoga = { name: string; category: string; present: boolean; description: string; strength: string | null };
export type Dosha = { name: string; present: boolean; severity: string; score: number; details: string; cancellations: string[]; remedies: string[]; type?: string | null };
export type ShadbalaRow = { sthana: number; dig: number; kala: number; chesta: number; naisargika: number; drik: number; total_virupas: number; rupas: number; required: number; ratio: number; strong: boolean };
export type HouseAnalysis = { house: number; name: string; significations: string; sign: string; lord: string; lord_house: number; lord_dignity: string; occupants: string[]; aspects: string[]; sav: number; score: number; interpretation: string };
export type LifeArea = { score: number; houses: number[]; karakas: string[]; summary: string; outlook: string };
export type Remedy = { planet: string; reasons: string[]; gemstone: string | null; gem_note: string; metal: string; finger: string; mantra: string; mantra_count: number; day: string; charity: string; ritual: string; deity: string; purpose?: string };
export type TransitPlanet = { name: string; sign: string; degree: string; nakshatra: string; retrograde: boolean; house_from_moon: number; house_from_lagna: number; favourable: boolean; effect: string; conjunct_natal?: string[] };
export type Transits = { date: string; reference_moon_sign: string; planets: TransitPlanet[]; score: number };

export type Chart = {
  birth: { local_datetime: string; utc_datetime: string; timezone: string; latitude: number; longitude: number };
  ascendant: { sign: string; sign_index: number; absolute_longitude: number; longitude: number; dms: string; nakshatra: string; pada: number; nakshatra_lord: string; sign_lord: string };
  planets: Planet[];
  houses: { house: number; sign: string; lord: string; cusp: number; occupants: string[] }[];
  house_cusps: number[];
  vargas: Record<string, VargaChart>;
  ayanamsa_degrees: number;
  settings: { ayanamsa: string; node_type: string; house_system: string; chart_style?: ChartStyle };
  engine: string;
  moon_sign: string;
  birth_nakshatra: { name: string; pada: number; lord: string };
  dasha: { balance_at_birth: { lord: string; years: number }; mahadashas: DashaPeriod[]; current: { lord: string; start: string; end: string; level: number }[] };
  yogas: Yoga[];
  doshas: Dosha[];
  ashtakavarga: { signs: string[]; bhinnashtakavarga: Record<string, number[]>; bav_totals: Record<string, number>; sarvashtakavarga: number[]; total: number; by_house: { house: number; sign: string; points: number; strong: boolean }[] };
  shadbala: { planets: Record<string, ShadbalaRow>; ranking: string[]; method: string };
  house_analysis: HouseAnalysis[];
  life_areas: Record<string, LifeArea>;
  remedies: Remedy[];
  transits: Transits;
  analysis?: Analysis;
  profile?: Profile;
  record_id?: string;
};

export type SavedChart = { record_id: string; profile_id: string; profile_name: string; created_at: string; calculation: Partial<Chart> };

export const SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"] as const;
export const SIGN_SHORT = ["Ar", "Ta", "Ge", "Cn", "Le", "Vi", "Li", "Sc", "Sg", "Cp", "Aq", "Pi"];
export const PLANET_SHORT: Record<string, string> = { Sun: "Su", Moon: "Mo", Mars: "Ma", Mercury: "Me", Jupiter: "Ju", Venus: "Ve", Saturn: "Sa", Rahu: "Ra", Ketu: "Ke", Ascendant: "As" };
export const PLANET_GLYPH: Record<string, string> = { Sun: "☉", Moon: "☽", Mars: "♂", Mercury: "☿", Jupiter: "♃", Venus: "♀", Saturn: "♄", Rahu: "☊", Ketu: "☋" };
export const SIGN_GLYPH = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"];
export const VARGA_LIST = ["D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12", "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"];

export const fmtDate = (iso: string) => new Date(iso).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });

export type SignProfile = { sign: string; lord: string; element: string; modality: string; nature: string; strengths: string; challenges: string; lucky: { gemstone: string; day: string; colour: string; number: string } };
export type PlanetReading = { meaning?: { life: string; caution: string; dignity: string; verdict: string }; planet: string; house: number; sign: string; nakshatra: string; pada: number; dignity: string; retrograde: boolean; combust: boolean; functional: { role: string; rules: number[]; label: string }; score: number; tone: string; conditions: string[]; interpretation: string };
export type LifeEffect = { area: string; tone: string; via: string[]; text: string };
export type PeriodLite = { lord: string; start: string; end: string; current: boolean; score: number; tone: string };
export type AntardashaReading = { lord: string; start: string; end: string; current: boolean; score: number; tone: string; focus: string[]; summary: string;
  more?: { relationship: string; effects: LifeEffect[]; pratyantar: PeriodLite[]; advice: string } };
export type DashaReading = { lord: string; start: string; end: string; years: number; age_from: number; age_to: number; current: boolean; past: boolean; score: number; tone: string; functional: string; activates: number[]; summary: string; highlights: string[]; cautions: string[]; antardashas: AntardashaReading[]; plain?: string;
  more?: { effects: LifeEffect[]; remedy: { mantra: string; count: number; day: string; charity: string; practice: string; deity: string };
    houses: { house: number; theme: string; why: string }[]; best_sub: string | null; hard_sub: string | null } };
export type Analysis = {
  version: number;
  overview: { headline: string; strongest: string[]; weakest: string[]; yogakaraka: string[]; yoga_count: number; dosha_count: number; overall: number };
  ascendant: SignProfile & { nakshatra: string; pada: number; degree: string };
  moon: SignProfile;
  nakshatra: { name: string; pada: number; lord: string; deity: string; symbol: string; nature: string; gana: string; yoni: string; nadi: string };
  avakhada: { label: string; value: string; hint: string }[];
  panchang: { tithi: string; yoga: string; karana: string; vara: string; note: string };
  predictions: { area: string; score: number; text: string }[];
  planets: PlanetReading[];
  dashas: DashaReading[];
  lord_profiles?: Record<string, { label: string; value: string }[]>;
  house_meanings?: Record<string, string>;
  yoga_meanings?: Record<string, string>;
  dosha_meanings?: Record<string, { what: string; advice: string; status: string }>;
  methodology: string[];
};
