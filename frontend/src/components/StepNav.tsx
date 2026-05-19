"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
	{ label: "Home", href: "/" },
	{ label: "Step 1 · Resume", href: "/steps/step1" },
	{ label: "Step 2 · Dataset", href: "/steps/step2" },
	{ label: "Step 3 · Scoring", href: "/steps/step3" },
	{ label: "Step 4 · Assistant", href: "/steps/step4" },
];

/**
 * Small breadcrumb-style nav that stays consistent across all workflow pages.
 */
export function StepNav() {
	const pathname = usePathname();

	return (
		<nav className="flex flex-wrap items-center gap-2 text-xs text-slate-500">
			{LINKS.map((link, index) => {
				const active = pathname === link.href;
				return (
					<span key={link.href} className="flex items-center gap-2">
						<Link
							href={link.href}
							className={`rounded-full border px-3 py-1 font-medium transition ${
								active
									? "border-slate-900 bg-slate-900 text-white shadow-sm"
									: "border-slate-200 bg-white text-slate-700 hover:border-slate-400 hover:text-slate-900"
							}`}
						>
							{link.label}
						</Link>
						{index < LINKS.length - 1 && <span className="text-slate-300">/</span>}
					</span>
				);
			})}
		</nav>
	);
}

