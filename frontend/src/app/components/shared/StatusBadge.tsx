export function StatusBadge({ status }: { status: string }) {
  const map: Record<string, { dot: string; text: string; bg: string }> = {
    sent: { dot: "bg-blue-400", text: "text-blue-600", bg: "bg-blue-50" },
    viewed: { dot: "bg-amber-400", text: "text-amber-600", bg: "bg-amber-50" },
    responded: {
      dot: "bg-emerald-400",
      text: "text-emerald-700",
      bg: "bg-emerald-50",
    },
    rejected: { dot: "bg-red-400", text: "text-red-600", bg: "bg-red-50" },
  };
  const s = map[status] ?? map.sent;
  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium ${s.bg} ${s.text}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${s.dot}`} />
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
}
