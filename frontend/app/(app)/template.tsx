/** Route enter: a 140ms CSS opacity fade (no JS animation library on every navigation). */
export default function Template({ children }: { children: React.ReactNode }) {
  return <div className="route-fade">{children}</div>;
}
