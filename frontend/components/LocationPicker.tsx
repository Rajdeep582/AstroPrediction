"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { Circle, Map as LeafletMap, Marker } from "leaflet";
import { Crosshair, Loader2, MapPin, Search, X } from "lucide-react";
import { api } from "@/lib/api";

type Place = { name: string; detail: string; lat: number; lon: number; kind?: string };

const DEFAULT: [number, number] = [28.6139, 77.2090];
const cache = new Map<string, Place[]>();

const COMMON_PLACES: Place[] = [
  { name: "New Delhi", detail: "Delhi, India", lat: 28.6139, lon: 77.2090, kind: "city" },
  { name: "Delhi", detail: "Delhi, India", lat: 28.6328, lon: 77.2198, kind: "city" },
  { name: "Mumbai", detail: "Maharashtra, India", lat: 19.0760, lon: 72.8777, kind: "city" },
  { name: "Kolkata", detail: "West Bengal, India", lat: 22.5726, lon: 88.3639, kind: "city" },
  { name: "Bengaluru", detail: "Karnataka, India", lat: 12.9716, lon: 77.5946, kind: "city" },
  { name: "Hyderabad", detail: "Telangana, India", lat: 17.3850, lon: 78.4867, kind: "city" },
  { name: "Chennai", detail: "Tamil Nadu, India", lat: 13.0827, lon: 80.2707, kind: "city" },
  { name: "Ahmedabad", detail: "Gujarat, India", lat: 23.0225, lon: 72.5714, kind: "city" },
  { name: "Pune", detail: "Maharashtra, India", lat: 18.5204, lon: 73.8567, kind: "city" },
  { name: "Jaipur", detail: "Rajasthan, India", lat: 26.9124, lon: 75.7873, kind: "city" },
  { name: "Lucknow", detail: "Uttar Pradesh, India", lat: 26.8467, lon: 80.9462, kind: "city" },
  { name: "Varanasi", detail: "Uttar Pradesh, India", lat: 25.3176, lon: 82.9739, kind: "city" },
  { name: "Patna", detail: "Bihar, India", lat: 25.5941, lon: 85.1376, kind: "city" },
  { name: "Surat", detail: "Gujarat, India", lat: 21.1702, lon: 72.8311, kind: "city" },
  { name: "Kanpur", detail: "Uttar Pradesh, India", lat: 26.4499, lon: 80.3319, kind: "city" },
  { name: "Nagpur", detail: "Maharashtra, India", lat: 21.1458, lon: 79.0882, kind: "city" },
  { name: "Indore", detail: "Madhya Pradesh, India", lat: 22.7196, lon: 75.8577, kind: "city" },
  { name: "Bhopal", detail: "Madhya Pradesh, India", lat: 23.2599, lon: 77.4126, kind: "city" },
  { name: "Chandigarh", detail: "Punjab/Haryana, India", lat: 30.7333, lon: 76.7794, kind: "city" },
  { name: "Ludhiana", detail: "Punjab, India", lat: 30.9010, lon: 75.8573, kind: "city" },
  { name: "Amritsar", detail: "Punjab, India", lat: 31.6340, lon: 74.8723, kind: "city" },
  { name: "Agra", detail: "Uttar Pradesh, India", lat: 27.1767, lon: 78.0081, kind: "city" },
  { name: "Prayagraj", detail: "Uttar Pradesh, India", lat: 25.4358, lon: 81.8463, kind: "city" },
  { name: "Dehradun", detail: "Uttarakhand, India", lat: 30.3165, lon: 78.0322, kind: "city" },
  { name: "Haridwar", detail: "Uttarakhand, India", lat: 29.9457, lon: 78.1642, kind: "city" },
  { name: "Ranchi", detail: "Jharkhand, India", lat: 23.3441, lon: 85.3096, kind: "city" },
  { name: "Bhubaneswar", detail: "Odisha, India", lat: 20.2961, lon: 85.8245, kind: "city" },
  { name: "Guwahati", detail: "Assam, India", lat: 26.1445, lon: 91.7362, kind: "city" },
  { name: "Visakhapatnam", detail: "Andhra Pradesh, India", lat: 17.6868, lon: 83.2185, kind: "city" },
  { name: "Vijayawada", detail: "Andhra Pradesh, India", lat: 16.5062, lon: 80.6480, kind: "city" },
  { name: "Coimbatore", detail: "Tamil Nadu, India", lat: 11.0168, lon: 76.9558, kind: "city" },
  { name: "Madurai", detail: "Tamil Nadu, India", lat: 9.9252, lon: 78.1198, kind: "city" },
  { name: "Kochi", detail: "Kerala, India", lat: 9.9312, lon: 76.2673, kind: "city" },
  { name: "Thiruvananthapuram", detail: "Kerala, India", lat: 8.5241, lon: 76.9366, kind: "city" },
  { name: "Noida", detail: "Uttar Pradesh, India", lat: 28.5355, lon: 77.3910, kind: "city" },
  { name: "Gurugram", detail: "Haryana, India", lat: 28.4595, lon: 77.0266, kind: "city" },
  { name: "Faridabad", detail: "Haryana, India", lat: 28.4089, lon: 77.3178, kind: "city" },
  { name: "Ghaziabad", detail: "Uttar Pradesh, India", lat: 28.6692, lon: 77.4538, kind: "city" },
  { name: "Vadodara", detail: "Gujarat, India", lat: 22.3072, lon: 73.1812, kind: "city" },
  { name: "Rajkot", detail: "Gujarat, India", lat: 22.3039, lon: 70.8022, kind: "city" },
  { name: "Nashik", detail: "Maharashtra, India", lat: 19.9975, lon: 73.7898, kind: "city" },
  { name: "Thane", detail: "Maharashtra, India", lat: 19.2183, lon: 72.9781, kind: "city" },
  { name: "Jodhpur", detail: "Rajasthan, India", lat: 26.2389, lon: 73.0243, kind: "city" },
  { name: "Udaipur", detail: "Rajasthan, India", lat: 24.5854, lon: 73.7125, kind: "city" },
  { name: "Raipur", detail: "Chhattisgarh, India", lat: 21.2514, lon: 81.6296, kind: "city" },
  { name: "Srinagar", detail: "Jammu & Kashmir, India", lat: 34.0837, lon: 74.7973, kind: "city" },
  { name: "Shimla", detail: "Himachal Pradesh, India", lat: 31.1048, lon: 77.1734, kind: "city" },
  { name: "London", detail: "Greater London, United Kingdom", lat: 51.5074, lon: -0.1278, kind: "city" },
  { name: "New York", detail: "New York, United States", lat: 40.7128, lon: -74.0060, kind: "city" },
  { name: "San Francisco", detail: "California, United States", lat: 37.7749, lon: -122.4194, kind: "city" },
  { name: "Los Angeles", detail: "California, United States", lat: 34.0522, lon: -118.2437, kind: "city" },
  { name: "Chicago", detail: "Illinois, United States", lat: 41.8781, lon: -87.6298, kind: "city" },
  { name: "Dallas", detail: "Texas, United States", lat: 32.7767, lon: -96.7970, kind: "city" },
  { name: "Toronto", detail: "Ontario, Canada", lat: 43.6532, lon: -79.3832, kind: "city" },
  { name: "Vancouver", detail: "British Columbia, Canada", lat: 49.2827, lon: -123.1207, kind: "city" },
  { name: "Dubai", detail: "United Arab Emirates", lat: 25.2048, lon: 55.2708, kind: "city" },
  { name: "Singapore", detail: "Singapore", lat: 1.3521, lon: 103.8198, kind: "city" },
  { name: "Sydney", detail: "New South Wales, Australia", lat: -33.8688, lon: 151.2093, kind: "city" },
  { name: "Melbourne", detail: "Victoria, Australia", lat: -37.8136, lon: 144.9631, kind: "city" },
];

async function searchPlaces(q: string, signal?: AbortSignal): Promise<Place[]> {
  const norm = q.trim().toLowerCase();
  if (cache.has(norm)) return cache.get(norm)!;

  // 1. Instant local matches for common places
  const localMatches = COMMON_PLACES.filter(
    (p) => p.name.toLowerCase().includes(norm) || p.detail.toLowerCase().includes(norm)
  );

  // 2. Query backend geocoding proxy
  let remoteMatches: Place[] = [];
  try {
    const res = await api<{ places: Place[] }>(`/api/location/search?q=${encodeURIComponent(q)}`, {
      signal,
      retries: 0,
    });
    if (res?.places && Array.isArray(res.places)) {
      remoteMatches = res.places;
    }
  } catch {
    // If backend proxy fails or request aborted, continue with local matches
  }

  // Combine and deduplicate
  const combined = [...remoteMatches];
  for (const loc of localMatches) {
    if (!combined.some((c) => Math.abs(c.lat - loc.lat) < 0.05 && Math.abs(c.lon - loc.lon) < 0.05)) {
      combined.push(loc);
    }
  }

  const results = combined.slice(0, 8);
  if (results.length > 0) {
    cache.set(norm, results);
  }
  return results;
}

async function reverseName(lat: number, lon: number): Promise<string | null> {
  try {
    const res = await api<{ name: string | null }>(`/api/location/reverse?lat=${lat}&lon=${lon}`, { retries: 0 });
    return res.name ?? null;
  } catch {
    return null;
  }
}

const zoomFor = (kind?: string) =>
  kind && /country/.test(kind) ? 5 : kind && /state|region|province/.test(kind) ? 7 : kind && /city|county|district/.test(kind) ? 11 : 13;

export default function LocationPicker({
  value, latitude, longitude, onLocation, onName, onCoords,
}: {
  value: string; latitude: string; longitude: string;
  onLocation: (name: string, lat: number, lon: number) => void;
  onName: (name: string) => void;
  onCoords: (lat: string, lon: string) => void;
}) {
  const boxRef = useRef<HTMLDivElement>(null);
  const mapEl = useRef<HTMLDivElement>(null);
  const map = useRef<LeafletMap | null>(null);
  const marker = useRef<Marker | null>(null);
  const ring = useRef<Circle | null>(null);
  const L = useRef<typeof import("leaflet") | null>(null);
  const resizeObs = useRef<ResizeObserver | null>(null);
  const props = useRef({ onLocation, onName, onCoords });
  props.current = { onLocation, onName, onCoords };

  const [query, setQuery] = useState(value);
  const committed = useRef(value);
  const [results, setResults] = useState<Place[]>([]);
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(0);
  const [busy, setBusy] = useState(false);
  const [locating, setLocating] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => { if (value !== query) { committed.current = value; setQuery(value); } }, [value]); // eslint-disable-line react-hooks/exhaustive-deps

  const placePin = useCallback((lat: number, lon: number, zoom?: number) => {
    const m = map.current, Lf = L.current;
    if (!m || !Lf) return;
    ring.current?.remove(); ring.current = null;
    if (!marker.current) {
      const icon = Lf.divIcon({ className: "astro-pin", html: '<span class="astro-pin-pulse"></span><span class="astro-pin-dot"></span>', iconSize: [22, 22], iconAnchor: [11, 11] });
      marker.current = Lf.marker([lat, lon], { icon, draggable: true }).addTo(m);
      marker.current.on("dragend", async () => {
        const p = marker.current!.getLatLng();
        props.current.onCoords(p.lat.toFixed(6), p.lng.toFixed(6));
        const n = await reverseName(p.lat, p.lng);
        if (n) { committed.current = n; props.current.onName(n); }
      });
    } else marker.current.setLatLng([lat, lon]);
    const z = zoom ?? Math.max(m.getZoom(), 12);
    // long fly only for far jumps; short hops just pan (feels instant on phones)
    if (m.getCenter().distanceTo([lat, lon]) > 50000) m.flyTo([lat, lon], z, { duration: 1.1, easeLinearity: 0.25 });
    else m.setView([lat, lon], z, { animate: true });
  }, []);

  // init map once
  useEffect(() => {
    let alive = true;
    (async () => {
      const Lf = (await import("leaflet")).default;
      if (!alive || !mapEl.current || map.current) return;
      L.current = Lf;
      const lat = parseFloat(latitude), lon = parseFloat(longitude);
      const has = Number.isFinite(lat) && Number.isFinite(lon);
      const m = Lf.map(mapEl.current, { center: has ? [lat, lon] : DEFAULT, zoom: has ? 11 : 4, zoomControl: false, attributionControl: true, zoomSnap: 0.5, wheelPxPerZoomLevel: 90, tapTolerance: 15, bounceAtZoomLimits: false });
      // Esri World Street Map: Google-style default road map with English labels, no API key
      Lf.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}", {
        className: "astro-tiles",
        maxZoom: 19,
        maxNativeZoom: 18,
        keepBuffer: 4,
        updateWhenZooming: false,
        crossOrigin: true,
        attribution: "Tiles &copy; Esri",
      }).addTo(m);
      Lf.control.zoom({ position: "bottomright" }).addTo(m);
      m.attributionControl.setPrefix(false);
      m.on("click", async (e) => {
        const { lat: a, lng: b } = e.latlng;
        props.current.onCoords(a.toFixed(6), b.toFixed(6));
        placePin(a, b, m.getZoom() < 10 ? 11 : m.getZoom());
        const n = await reverseName(a, b);
        if (n) { committed.current = n; props.current.onName(n); }
      });
      map.current = m;
      if (has) placePin(lat, lon, 11);
      // Leaflet must be told when its box changes size (rotation, keyboard, layout shifts), else tiles go grey / half-loaded
      const ro = new ResizeObserver(() => m.invalidateSize({ pan: false }));
      ro.observe(mapEl.current);
      resizeObs.current = ro;
      requestAnimationFrame(() => m.invalidateSize());
    })();
    return () => { alive = false; resizeObs.current?.disconnect(); map.current?.remove(); map.current = null; marker.current = null; ring.current = null; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // keep pin in sync with manually edited coordinates
  useEffect(() => {
    const lat = parseFloat(latitude), lon = parseFloat(longitude);
    if (!Number.isFinite(lat) || !Number.isFinite(lon) || !map.current) return;
    const cur = marker.current?.getLatLng();
    if (!cur || Math.abs(cur.lat - lat) > 1e-5 || Math.abs(cur.lng - lon) > 1e-5) placePin(lat, lon);
  }, [latitude, longitude, placePin]);

  // debounced as-you-type search with instant local results
  useEffect(() => {
    const q = query.trim();
    if (q.length < 2 || query === committed.current) { setResults([]); return; }

    // Instant local matches so there's zero buffering
    const local = COMMON_PLACES.filter(
      (p) => p.name.toLowerCase().includes(q.toLowerCase()) || p.detail.toLowerCase().includes(q.toLowerCase())
    );
    if (local.length > 0) {
      setResults(local.slice(0, 6));
      setOpen(true);
    }

    const ctl = new AbortController();
    const t = setTimeout(async () => {
      setBusy(true);
      try {
        const r = await searchPlaces(q, ctl.signal);
        if (r.length > 0) {
          setResults(r);
          setActive(0);
          setOpen(true);
          setError("");
        } else if (local.length === 0) {
          setError("No places found — try a nearby town.");
        }
      } catch (e) {
        if ((e as Error).name !== "AbortError" && local.length === 0) {
          setError("Place search is unavailable right now.");
        }
      } finally { setBusy(false); }
    }, 320);
    return () => { clearTimeout(t); ctl.abort(); };
  }, [query]);

  useEffect(() => {
    const close = (e: MouseEvent) => { if (!boxRef.current?.contains(e.target as Node)) setOpen(false); };
    document.addEventListener("pointerdown", close);
    return () => document.removeEventListener("pointerdown", close);
  }, []);

  function choose(p: Place) {
    const label = p.detail ? `${p.name}, ${p.detail}` : p.name;
    committed.current = label; setQuery(label); setOpen(false); setResults([]); setError("");
    props.current.onLocation(label, p.lat, p.lon);
    placePin(p.lat, p.lon, zoomFor(p.kind));
  }

  function locate() {
    if (!("geolocation" in navigator)) { setError("Your browser doesn't support location access."); return; }
    if (!window.isSecureContext) { setError("Location needs HTTPS or localhost."); return; }
    setLocating(true); setError("");
    const ok = async (pos: GeolocationPosition) => {
      const { latitude: a, longitude: b, accuracy } = pos.coords;
      props.current.onCoords(a.toFixed(6), b.toFixed(6));
      placePin(a, b, accuracy > 2000 ? 11 : accuracy > 300 ? 14 : 16);
      if (L.current && map.current) ring.current = L.current.circle([a, b], { radius: accuracy, className: "astro-accuracy" }).addTo(map.current);
      setLocating(false);
      const n = await reverseName(a, b);
      if (n) { committed.current = n; props.current.onName(n); setQuery(n); }
    };
    const fail = (e: GeolocationPositionError) => {
      setLocating(false);
      setError(e.code === 1 ? "Location permission denied — allow it in the browser's site settings." : "Couldn't get your location. Search for the place instead.");
    };
    navigator.geolocation.getCurrentPosition(ok, (e) => {
      if (e.code === 1) return fail(e);
      navigator.geolocation.getCurrentPosition(ok, fail, { enableHighAccuracy: false, timeout: 15000, maximumAge: 300000 });
    }, { enableHighAccuracy: true, timeout: 8000, maximumAge: 0 });
  }

  function onKey(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "ArrowDown") { e.preventDefault(); setOpen(true); setActive((i) => Math.min(i + 1, results.length - 1)); }
    else if (e.key === "ArrowUp") { e.preventDefault(); setActive((i) => Math.max(i - 1, 0)); }
    else if (e.key === "Enter") { e.preventDefault(); if (results[active]) choose(results[active]); }
    else if (e.key === "Escape") setOpen(false);
  }

  const hasCoords = Number.isFinite(parseFloat(latitude)) && Number.isFinite(parseFloat(longitude));

  return (
    <div className="loc">
      <div className="loc-search" ref={boxRef}>
        <Search size={17} className="loc-icon" />
        <input
          value={query}
          onChange={(e) => { setQuery(e.target.value); onName(e.target.value); if (error) setError(""); }}
          onFocus={() => results.length && setOpen(true)}
          onKeyDown={onKey}
          placeholder="Search birth place"
          inputMode="search" enterKeyHint="search" spellCheck={false}
          autoComplete="off" role="combobox" aria-expanded={open} aria-controls="loc-list" aria-label="Birth place"
        />
        {busy ? <Loader2 size={16} className="loc-spin" /> : query && (
          <button type="button" className="loc-clear" aria-label="Clear" onClick={() => { setQuery(""); onName(""); onCoords("", ""); setResults([]); }}><X size={15} /></button>
        )}
        <button type="button" className="loc-locate" onClick={locate} disabled={locating} title="Use my current location">
          {locating ? <Loader2 size={15} className="loc-spin" /> : <Crosshair size={15} />}<span>{locating ? "Locating" : "Locate me"}</span>
        </button>
        {open && results.length > 0 && (
          <ul className="loc-list" id="loc-list" role="listbox">
            {results.map((p, i) => (
              <li key={`${p.lat},${p.lon},${i}`} role="option" aria-selected={i === active}
                className={i === active ? "on" : ""} onMouseEnter={() => setActive(i)} onMouseDown={(e) => { e.preventDefault(); choose(p); }}>
                <MapPin size={15} /><div><b>{p.name}</b>{p.detail && <small>{p.detail}</small>}</div>
              </li>
            ))}
          </ul>
        )}
      </div>
      {error && <p className="loc-error" role="status">{error}</p>}
      <div className="loc-map" data-lenis-prevent>
        <div ref={mapEl} className="loc-canvas" aria-label="Birth place map — click to drop a pin" />
        {hasCoords && <span className="loc-chip">{(+latitude).toFixed(4)}°, {(+longitude).toFixed(4)}°</span>}
      </div>
    </div>
  );
}
