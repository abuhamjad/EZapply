type ChartLegendItem = {
  label: string;
  color: string;
  type?: "line" | "box";
};

type ChartLegendProps = {
  items: ChartLegendItem[];
};

export function ChartLegend({ items }: ChartLegendProps) {
  return (
    <div className="flex items-center gap-4 text-xs text-muted-foreground">
      {items.map((item) => (
        <span key={item.label} className="flex items-center gap-1.5">
          {item.type === "box" ? (
            <span
              className="w-3 h-2.5 rounded inline-block"
              style={{ backgroundColor: item.color }}
            />
          ) : (
            <span
              className="w-3 h-0.5 inline-block rounded"
              style={{ backgroundColor: item.color }}
            />
          )}
          {item.label}
        </span>
      ))}
    </div>
  );
}
