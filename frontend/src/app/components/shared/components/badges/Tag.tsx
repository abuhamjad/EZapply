type TagProps = {
  label: string;
};

export function Tag({ label }: TagProps) {
  return (
    <span className="px-2.5 py-1 bg-secondary text-xs font-medium text-foreground rounded-md">
      {label}
    </span>
  );
}
