import { Skeleton } from "@/components/ui";

export default function Loading() {
  return (
    <div className="stack" aria-busy="true" aria-label="Loading page">
      <Skeleton h={14} w={120} />
      <Skeleton h={52} w="50%" />
      <div className="dash-grid"><Skeleton h={180} r={16} /><Skeleton h={180} r={16} /><Skeleton h={180} r={16} /></div>
      <Skeleton h={260} r={16} />
    </div>
  );
}
