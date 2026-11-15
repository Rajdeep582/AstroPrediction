/** In-app page switches are instant (like a native app tab): no fade, no skeleton flash. */
export default function Template({ children }: { children: React.ReactNode }) {
  return <div className="page-view">{children}</div>;
}
