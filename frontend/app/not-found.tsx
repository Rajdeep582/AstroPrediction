import Link from "next/link";

export default function NotFound() {
  return (
    <main className="center-page">
      <p className="eyebrow">404 · Beyond the zodiac</p>
      <h1 className="display">This house is empty.</h1>
      <p className="lede">The page you were looking for isn&apos;t in our chart.</p>
      <Link href="/" className="btn btn-gold">Return home</Link>
    </main>
  );
}
