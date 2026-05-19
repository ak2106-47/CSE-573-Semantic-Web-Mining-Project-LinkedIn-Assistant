import { ReactNode } from "react";

type Props = {
	children: ReactNode;
	className?: string;
	variant?: "dark" | "bright";
};

const VARIANT_CLASSES: Record<NonNullable<Props["variant"]>, string> = {
	dark: "rounded-3xl border border-white/10 bg-gradient-to-br from-slate-900/80 via-slate-900/40 to-slate-900/10 text-slate-100 shadow-[0_20px_60px_rgba(2,6,23,0.6)] backdrop-blur-2xl",
	bright: "rounded-3xl border border-white/60 bg-white/90 text-slate-900 shadow-[0_25px_70px_rgba(15,23,42,0.12)] backdrop-blur-xl",
};

/**
 * Shared container that gives every section the same glassmorphism treatment (light or dark).
 */
export function GlassCard({ children, className = "", variant = "dark" }: Props) {
	return <div className={`${VARIANT_CLASSES[variant]} ${className}`}>{children}</div>;
}

