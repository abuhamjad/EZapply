type KeywordBadgeProps = {
  keyword: string;
  variant?: "include" | "exclude";
};

export function KeywordBadge({
  keyword,
  variant = "include",
}: KeywordBadgeProps) {
  const styles = {
    include: "bg-emerald-50 text-emerald-700 border-emerald-200",
    exclude: "bg-red-50 text-red-600 border-red-200",
  };

  return (
    <span
      className={`px-2.5 py-1 text-xs font-medium rounded-md border ${styles[variant]}`}
    >
      {keyword}
    </span>
  );
}
