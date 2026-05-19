"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { GlassCard } from "@/components/GlassCard";
import { StepNav } from "@/components/StepNav";
import { api } from "@/lib/api";
import { Profile } from "@/lib/types";

/**
 * Step 1 — handles resume uploads and displays parsed profile stats.
 */
export default function Step1Page() {
	const [profile, setProfile] = useState<Profile | null>(null);
	const [profileLoading, setProfileLoading] = useState(false);
	const [resumeFile, setResumeFile] = useState<File | null>(null);
	const [uploading, setUploading] = useState(false);
	const [message, setMessage] = useState<string | null>(null);

	useEffect(() => {
		handleLoadProfile();
	}, []);

	async function handleLoadProfile() {
		try {
			setProfileLoading(true);
			const data = await api.getProfile();
			setProfile(data);
		} catch (error) {
			setMessage("Unable to load profile. Make sure the backend is running.");
		} finally {
			setProfileLoading(false);
		}
	}

	async function handleUpload() {
		if (!resumeFile) {
			setMessage("Choose a resume file first.");
			return;
		}
		try {
			setUploading(true);
			setMessage(null);
			const data = await api.uploadResume(resumeFile);
			setProfile(data);
			setMessage("Resume parsed successfully!");
		} catch (error) {
			setMessage("Upload failed. Check the file type or restart the backend.");
		} finally {
			setUploading(false);
		}
	}

	return (
		<main className="min-h-screen bg-gradient-to-br from-[#eef2ff] via-white to-[#fdf2f8] px-4 py-10 text-slate-900">
			<section className="mx-auto flex max-w-5xl flex-col gap-10">
				<StepNav />

				<header className="space-y-3 rounded-[32px] border border-white/70 bg-white/70 p-8 shadow-lg shadow-slate-200/70">
					<p className="text-xs font-semibold uppercase tracking-[0.4em] text-emerald-600">Step 1</p>
					<h1 className="text-3xl font-semibold text-slate-900">Resume Intake & θ Estimation</h1>
					<p className="text-sm text-slate-600">
						Upload a PDF, DOCX, or TXT resume. We extract skills, experiences, and education before estimating your initial θ (ability) for
						Rasch/Guttman scoring.
					</p>
				</header>

				<GlassCard variant="bright" className="p-6">
					<div className="grid gap-6 md:grid-cols-2">
						<div>
							<p className="text-sm font-semibold text-slate-900">Upload Resume</p>
							<p className="mt-2 text-xs text-slate-500">
								Drag-and-drop or click below. We support PDF, DOCX, DOC, and TXT.
							</p>
							<label className="mt-4 flex min-h-[200px] cursor-pointer flex-col items-center justify-center rounded-2xl border border-dashed border-slate-200 bg-white px-4 py-6 text-center text-sm text-slate-600 transition hover:border-emerald-300">
								<span className="mb-2 text-base font-semibold text-slate-900">Select resume file</span>
								<span className="text-xs text-slate-500">
									{resumeFile ? resumeFile.name : "No file chosen"}
								</span>
								<input
									type="file"
									accept=".pdf,.doc,.docx,.txt"
									className="hidden"
									onChange={(event) => {
										const file = event.target.files?.[0];
										setResumeFile(file ?? null);
									}}
								/>
							</label>
							<button
								onClick={handleUpload}
								disabled={!resumeFile || uploading}
								className="mt-4 w-full rounded-2xl bg-gradient-to-r from-emerald-400 to-emerald-500 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-emerald-200/50 transition hover:-translate-y-0.5 disabled:opacity-40"
							>
								{uploading ? "Parsing..." : "Upload & Parse"}
							</button>
							{message && <p className="mt-3 text-xs text-slate-500">{message}</p>}
						</div>

						<div>
							<div className="flex items-center justify-between text-sm text-slate-500">
								<p>Parsed Profile</p>
								<p>{profileLoading ? "Loading…" : profile ? "Ready" : "Not found"}</p>
							</div>
							<div className="mt-4 rounded-2xl border border-slate-100 bg-white p-5 text-sm shadow-inner">
								{profile ? (
									<div className="space-y-3">
										<div>
											<p className="text-base font-semibold text-slate-900">
												{profile.full_name || "Unnamed Candidate"}
											</p>
											<p className="text-xs text-slate-500">{profile.email || "Email unavailable"}</p>
										</div>
										<div className="text-xs text-slate-500">
											{profile.experiences.length} experience entries · {profile.educations.length} education entries
										</div>
										<div>
											<p className="text-xs uppercase text-slate-500">
												Skills ({profile.skills.length})
											</p>
											<p className="text-sm text-slate-900">
												{profile.skills.map((s) => s.name).join(", ") || "No skills detected"}
											</p>
										</div>
									</div>
								) : (
									<p className="text-xs text-slate-500">
										Upload a resume to see extracted skills and the θ estimate used in later steps.
									</p>
								)}
							</div>
						</div>
					</div>
				</GlassCard>

				<div className="flex flex-wrap justify-between gap-4 text-xs text-slate-500">
					<Link href="/" className="font-semibold text-slate-600 underline decoration-slate-300 hover:text-slate-900">
						← Back to overview
					</Link>
					<Link href="/steps/step2" className="rounded-full bg-slate-900 px-4 py-2 font-semibold text-white shadow-lg shadow-slate-900/20">
						Continue to Step 2 →
					</Link>
				</div>
			</section>
		</main>
	);
}

