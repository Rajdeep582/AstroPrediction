"use client";

export default function Error({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <main className="center-page" role="alert">
      <p className="eyebrow">Something went wrong</p>
      <h1 className="display">A cloud passed over the chart.</h1>
      <p className="lede">{error.message || "Unexpected error."}</p>
      <button className="btn btn-gold" onClick={reset}>Try again</button>
    </main>
  );
}
