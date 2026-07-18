import type { PropsWithChildren } from "react";

type CardProps = PropsWithChildren<{
  className?: string;
}>;

export function Card({ children, className = "" }: CardProps) {
  return (
    <div className={`bg-card border border-border rounded-xl p-6 ${className}`}>
      {children}
    </div>
  );
}
