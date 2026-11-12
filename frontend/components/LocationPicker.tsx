"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { Circle, Map as LeafletMap, Marker } from "leaflet";
import { Crosshair, Loader2, MapPin, Search, X } from "lucide-react";

type Place = { name: string; detail: string; lat: number; lon: number; kind?: string };
type PhotonFeature = {
  geometry: { coordinates: [number, number] };
  properties: { name?: string; city?: string; county?: string; state?: string; country?: string; type?: string; osm_value?: string };
};

const DEFAULT: [number, number] = [22.5726, 88.3639];
const cache = new Map<string, Place[]>();

async function searchPlaces(q: string, signal: AbortSignal): Promise<Place[]> {
  const key = q.toLowerCase();
  if (cache.has(key)) return cache.get(key)!;
  let places: Place[] = [];
  try {
    const r = await fetch(`https://photon.komoot.io/api/?q=${encodeURIComponent(q)}&limit=10&lang=en`, { signal });
    if (!r.ok) throw new Error("photon");
    const data = (await r.json()) as { features: PhotonFeature[] };
    places = data.features.map((f) => {
      const p = f.properties;
      const name = p.name || p.city || p.county || p.state || "Unnamed place";
      const detail = [p.city !== name ? p.city : "", p.state, p.country].filter(Boolean).join(", ");
      return { name, detail, lat: f.geometry.coordinates[1], lon: f.geometry.coordinates[0], kind: p.osm_value || p.type };
    });
  } catch (e) {
    if ((e as Error).name === "AbortError") throw e;
    const r = await fetch(`https://nominatim.openstreetmap.org/search?format=json&limit=6&q=${encodeURIComponent(q)}`, { signal, headers: { "Accept-Language": "en" } });
    const data = (await r.json()) as { lat: string; lon: string; display_name: string; type?: string }[];
    places = data.map((d) => {
      const [name, ...rest] = d.display_name.split(", ");
      return { name, detail: rest.join(", "), lat: +d.lat, lon: +d.lon, kind: d.type };
    });
  }
  const seen = new Set<string>();
  places = places.filter((p) => { const k = `${p.name}|${p.detail}`; if (seen.has(k)) return false; seen.add(k); return true; }).slice(0, 6);
  cache.set(key, places);
  return places;
}

async function reverseName(lat: number, lon: number): Promise<string | null> {
  try {
    const r = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}&zoom=14`, { headers: { "Accept-Language": "en" } });
    const d = (await r.json()) as { display_name?: string };
    return d.display_name ?? null;
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
    m.flyTo([lat, lon], zoom ?? Math.max(m.getZoom(), 12), { duration: 1.6, easeLinearity: 0.2 });
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
      const m = Lf.map(mapEl.current, { center: has ? [lat, lon] : DEFAULT, zoom: has ? 11 : 4, zoomControl: false, attributionControl: true, zoomSnap: 0.25, wheelPxPerZoomLevel: 90 });
      Lf.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
        className: "astro-tiles",
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> ',
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
    })();
    return () => { alive = false; map.current?.remove(); map.current = null; marker.current = null; ring.current = null; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // keep pin in sync with manually edited coordinates
  useEffect(() => {
    const lat = parseFloat(latitude), lon = parseFloat(longitude);
    if (!Number.isFinite(lat) || !Number.isFinite(lon) || !map.current) return;
    const cur = marker.current?.getLatLng();
    if (!cur || Math.abs(cur.lat - lat) > 1e-5 || Math.abs(cur.lng - lon) > 1e-5) placePin(lat, lon);
  }, [latitude, longitude, placePin]);

  // debounced as-you-type search
  useEffect(() => {
    const q = query.trim();
    if (q.length < 2 || query === committed.current) { setResults([]); return; }
    const ctl = new AbortController();
    const t = setTimeout(async () => {
      setBusy(true);
      try {
        const r = await searchPlaces(q, ctl.signal);
        setResults(r); setActive(0); setOpen(true);
        setError(r.length ? "" : "No places found — try a nearby town.");
      } catch (e) {
        if ((e as Error).name !== "AbortError") setError("Place search is unavailable right now.");
      } finally { setBusy(false); }
    }, 280);
    return () => { clearTimeout(t); ctl.abort(); };
  }, [query]);

  useEffect(() => {
    const close = (e: MouseEvent) => { if (!boxRef.current?.contains(e.target as Node)) setOpen(false); };
    document.addEventListener("mousedown", close);
    return () => document.removeEventListener("mousedown", close);
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
          onChange={(e) => { setQuery(e.target.value); onName(e.target.value); }}
          onFocus={() => results.length && setOpen(true)}
          onKeyDown={onKey}
          placeholder="Search birth place — city, town or village"
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
