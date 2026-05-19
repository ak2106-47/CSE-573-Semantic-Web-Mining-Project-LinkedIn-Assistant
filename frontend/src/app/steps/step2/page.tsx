"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { GlassCard } from "@/components/GlassCard";
import { StepNav } from "@/components/StepNav";
import { api } from "@/lib/api";
import { JobOut } from "@/lib/types";

/**
 * Step 2 — query the Excel dataset and stage jobs for Rasch scoring.
 */
export default function Step2Page() {
	const [query, setQuery] = useState("data scientist");
	const [jobs, setJobs] = useState<JobOut[]>([]);
	const [loading, setLoading] = useState(false);
	const [message, setMessage] = useState<string | null>(null);

	// On mount, pre-populate with default query
	useEffect(() => {
		handleSearch(query, true);
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, []);

	async function handleSearch(term: string, silent = false) {
		const q = term.trim();
		if (!q) {
			setMessage("Enter a search phrase (e.g., “product manager california”).");
			return;
		}
		try {
			setLoading(true);
			if (!silent) setMessage(null);
			const data = await api.searchDatasetJobs(q);
			setJobs(data);
			setQuery(q);
			if (!silent) {
				setMessage(data.length ? `Found ${data.length} roles.` : "No dataset matches for that query.");
			}
		} catch (error) {
			setMessage("Dataset search failed. Backend might be offline.");
		} finally {
			setLoading(false);
		}
	}

	return (
		<main className="min-h-screen bg-gradient-to-br from-[#eef2ff] via-white to-[#fdf2f8] px-4 py-10 text-slate-900">
			<section className="mx-auto flex max-w-5xl flex-col gap-10">
				<StepNav />

				<header className="space-y-3 rounded-[32px] border border-white/70 bg-white/70 p-8 shadow-lg shadow-slate-200/70">
					<p className="text-xs font-semibold uppercase tracking-[0.4em] text-sky-600">Step 2</p>
					<h1 className="text-3xl font-semibold text-slate-900">Curated Job Dataset Search</h1>
					<p className="text-sm text-slate-600">
						Query the provided <span className="font-semibold text-slate-900">linkedin_job_posts_insights.xlsx</span> data. These results
						become the job set for Step 3’s Rasch/Guttman scoring.
					</p>
				</header>

				<GlassCard variant="bright" className="p-6">
					<div className="flex flex-col gap-3 sm:flex-row">
						<input
							type="text"
							value={query}
							onChange={(event) => setQuery(event.target.value)}
							onKeyDown={(event) => {
								if (event.key === "Enter") handleSearch(event.currentTarget.value);
							}}
							placeholder='Try "marketing manager remote" or "cloud engineer seattle"'
							className="flex-1 rounded-2xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-slate-500 focus:outline-none"
						/>
						<button
							onClick={() => handleSearch(query)}
							disabled={loading}
							className="rounded-2xl bg-gradient-to-r from-amber-300 to-orange-400 px-5 py-2 text-sm font-semibold text-slate-900 shadow-lg shadow-amber-200/60 transition hover:-translate-y-0.5 disabled:opacity-50"
						>
							{loading ? "Searching…" : "Search dataset"}
						</button>
					</div>
					{message && <p className="mt-3 text-xs text-slate-500">{message}</p>}

					<div className="mt-6 grid max-h-[420px] gap-4 overflow-y-auto pr-2 text-sm">
						{jobs.map((job, idx) => (
							<div
								key={`job-${job.id ?? idx}`}
								className="rounded-2xl border border-slate-100 bg-white/90 p-4 text-slate-800 shadow-[0_12px_30px_rgba(15,23,42,0.08)]"
							>
								<div className="flex items-center justify-between gap-3">
									<div>
										<p className="text-base font-semibold text-slate-900">{job.title || "Untitled role"}</p>
										<p className="text-xs text-slate-500">
											{job.company || "Unknown company"} · {job.location || "Location n/a"}
										</p>
									</div>
									<span className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-[11px] uppercase tracking-wide text-slate-500">
										Dataset
									</span>
								</div>
								{job.description && (
									<p className="mt-3 text-xs text-slate-500 line-clamp-2">{job.description}</p>
								)}
								{job.requirements?.length ? (
									<div className="mt-3 flex flex-wrap gap-2">
										{job.requirements.slice(0, 3).map((req, idx) => (
											<span
												key={`${job.id}-req-${idx}`}
												className="rounded-full bg-slate-100 px-3 py-1 text-[10px] uppercase tracking-wide text-slate-600"
											>
												{req.value}
											</span>
										))}
									</div>
								) : null}
							</div>
						))}
						{!jobs.length && !loading && (
							<p className="text-xs text-slate-500">No results yet. Try another keyword combination.</p>
						)}
					</div>
				</GlassCard>

				<div className="flex flex-wrap justify-between gap-4 text-xs text-slate-500">
					<Link href="/steps/step1" className="font-semibold text-slate-600 underline decoration-slate-300 hover:text-slate-900">
						← Back to Step 1
					</Link>
					<Link href="/steps/step3" className="rounded-full bg-slate-900 px-4 py-2 font-semibold text-white shadow-lg shadow-slate-900/20">
						Continue to Step 3 →
					</Link>
				</div>
			</section>
		</main>
	);
}

