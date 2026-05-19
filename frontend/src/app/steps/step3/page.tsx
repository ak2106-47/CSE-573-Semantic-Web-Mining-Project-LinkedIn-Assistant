"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { GlassCard } from "@/components/GlassCard";
import { StepNav } from "@/components/StepNav";
import { api } from "@/lib/api";
import { SuggestionOut } from "@/lib/types";

/**
 * Step 3 — compute Rasch/Guttman fits for the staged job set.
 */
export default function Step3Page() {
	const [suggestions, setSuggestions] = useState<SuggestionOut | null>(null);
	const [loading, setLoading] = useState(false);
	const [message, setMessage] = useState<string | null>(null);

	useEffect(() => {
		handleRefresh(true);
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, []);

	async function handleRefresh(silent = false) {
		try {
			setLoading(true);
			if (!silent) setMessage(null);
			const data = await api.getSuggestions();
			setSuggestions(data);
			if (!silent) {
				setMessage(data.recommendations.length ? "Updated with the latest dataset jobs." : "No matches yet. Run Step 2 first.");
			}
		} catch (error) {
			setMessage("Unable to compute suggestions. Ensure Step 1 & Step 2 are completed.");
		} finally {
			setLoading(false);
		}
	}

	return (
		<main className="min-h-screen bg-gradient-to-br from-[#eef2ff] via-white to-[#fdf2f8] px-4 py-10 text-slate-900">
			<section className="mx-auto flex max-w-5xl flex-col gap-10">
				<StepNav />

				<header className="space-y-3 rounded-[32px] border border-white/70 bg-white/70 p-8 shadow-lg shadow-slate-200/70">
					<p className="text-xs font-semibold uppercase tracking-[0.4em] text-fuchsia-600">Step 3</p>
					<h1 className="text-3xl font-semibold text-slate-900">Rasch/Guttman Fit Scoring</h1>
					<p className="text-sm text-slate-600">
						We compare your θ (ability) against each job requirement’s difficulty (b). Probabilities expose exactly where you align—and where
						upskilling might boost your odds.
					</p>
				</header>

				<GlassCard variant="bright" className="p-6">
					<div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
						<div>
							<p className="text-sm font-semibold text-slate-900">Current job matches</p>
							<p className="text-xs text-slate-500">
								Top Rasch/Guttman results from the jobs you surfaced in Step 2.
							</p>
						</div>
						<button
							onClick={() => handleRefresh()}
							disabled={loading}
							className="rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-900 shadow-sm hover:-translate-y-0.5 hover:border-slate-400 disabled:opacity-50"
						>
							{loading ? "Scoring…" : "Refresh suggestions"}
						</button>
					</div>
					{message && <p className="mt-3 text-xs text-slate-500">{message}</p>}

					<div className="mt-6 space-y-4">
						{suggestions?.recommendations.map((rec, idx) => (
							<div
								key={rec.job.id ?? idx}
								className="rounded-2xl border border-slate-100 bg-white/90 p-5 text-sm shadow-[0_12px_30px_rgba(15,23,42,0.08)]"
							>
								<div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
									<div>
										<p className="text-base font-semibold text-slate-900">
											{rec.job.title || "Untitled role"}
										</p>
										<p className="text-xs text-slate-500">
											{rec.job.company || "Unknown company"} · {rec.job.location || "Location n/a"}
										</p>
									</div>
									<div className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-emerald-800">
										Fit {(rec.score * 100).toFixed(0)}%
									</div>
								</div>
								<div className="mt-3 grid gap-2 text-xs text-slate-600 md:grid-cols-2">
									{rec.item_scores.slice(0, 4).map((item, idx2) => (
										<div key={`${rec.job.id}-item-${idx2}`} className="rounded-xl border border-slate-100 bg-slate-50 px-3 py-2">
											<p className="font-semibold text-slate-900">
												{item.kind.toUpperCase()}: {item.value}
											</p>
											<p className="text-[11px] text-slate-500">
												P={(item.probability ?? 0).toFixed(2)} · b={(item.difficulty ?? 0).toFixed(2)}
											</p>
										</div>
									))}
								</div>
							</div>
						))}
						{!suggestions?.recommendations.length && !loading && (
							<p className="text-xs text-slate-500">
								No matches yet. Complete Step 1 (resume) and Step 2 (dataset search), then refresh.
							</p>
						)}
					</div>
				</GlassCard>

				<div className="flex flex-wrap justify-between gap-4 text-xs text-slate-500">
					<Link href="/steps/step2" className="font-semibold text-slate-600 underline decoration-slate-300 hover:text-slate-900">
						← Back to Step 2
					</Link>
					<Link href="/steps/step4" className="rounded-full bg-slate-900 px-4 py-2 font-semibold text-white shadow-lg shadow-slate-900/20">
						Continue to Step 4 →
					</Link>
				</div>
			</section>
		</main>
	);
}

