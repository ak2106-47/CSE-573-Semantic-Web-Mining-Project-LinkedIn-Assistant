import Link from "next/link";
import { GlassCard } from "@/components/GlassCard";

const STEPS = [
	{
		title: "Step 1 · Resume Intake",
		desc: "Upload a PDF/DOC/TXT resume and we’ll extract skills, experience, education, and estimate your θ ability.",
		href: "/steps/step1",
	},
	{
		title: "Step 2 · Job Dataset Search",
		desc: "Query the curated job dataset (linkedin_job_posts_insights.xlsx) with natural keywords to stage roles.",
		href: "/steps/step2",
	},
	{
		title: "Step 3 · Rasch/Guttman Scoring",
		desc: "Combine your profile with selected roles to see transparent fit probabilities and requirement-level evidence.",
		href: "/steps/step3",
	},
	{
		title: "Step 4 · Conversational Agent",
		desc: "Chat with the LinkedIn Assistant for tailored job suggestions, networking scripts, and resume polish ideas.",
		href: "/steps/step4",
	},
];

const STEP_STYLES = [
	{ gradient: "from-[#fde68a] via-[#fca5a5] to-[#fb7185]", badge: "bg-[#fef08a]/80 text-[#92400e]" },
	{ gradient: "from-[#bbe7ff] via-[#c4b5fd] to-[#e0b1ff]", badge: "bg-[#c7d2fe]/80 text-[#3730a3]" },
	{ gradient: "from-[#6ee7b7] via-[#a5f3fc] to-[#93c5fd]", badge: "bg-[#d1fae5]/90 text-[#065f46]" },
	{ gradient: "from-[#fecdd3] via-[#fda4af] to-[#f472b6]", badge: "bg-[#ffe4e6]/90 text-[#9d174d]" },
];

const HERO_STATS = [
	{ label: "Resumes parsed", value: "3K+", detail: "Structured skills + θ estimates" },
	{ label: "Curated roles", value: "31K", detail: "Excel dataset powered" },
	{ label: "Explained matches", value: "100%", detail: "Per requirement Rasch probabilities" },
];

const FLOW_STEPS = [
	{
		title: "Ingest & Normalize",
		body: "NER-powered parsing tags skills, education, and experience, then estimates θ (ability) used later in Rasch scoring.",
		color: "bg-amber-50 border-amber-200 text-amber-900",
	},
	{
		title: "Retrieve & Stage",
		body: "Keyword + fuzzy search over the provided Excel dataset surfaces diverse roles, feeding Step 3 automatically.",
		color: "bg-sky-50 border-sky-200 text-sky-900",
	},
	{
		title: "Explain & Coach",
		body: "Every suggestion lists requirement-level probabilities, plus networking nudges and resume polish tips in the chat agent.",
		color: "bg-rose-50 border-rose-200 text-rose-900",
	},
];

export default function HomePage() {
	return (
		<main className="relative min-h-screen overflow-hidden bg-gradient-to-br from-[#eef2ff] via-white to-[#fdf2f8] text-slate-900">
			<div className="pointer-events-none absolute inset-0">
				<div className="floating-orb left-[5%] top-[10%] h-64 w-64 bg-[#c4b5fd]/60" />
				<div className="floating-orb right-[12%] top-[20%] h-72 w-72 bg-[#fda4af]/60 animation-delay-2000" />
				<div className="floating-orb left-[30%] bottom-[5%] h-80 w-80 bg-[#6ee7b7]/50 animation-delay-1000" />
			</div>

			<section className="relative mx-auto flex max-w-6xl flex-col gap-12 px-4 py-20">
				<header className="relative overflow-hidden rounded-[40px] border border-white/60 bg-gradient-to-br from-white via-[#fef3c7] to-[#fbcfe8] p-10 shadow-2xl">
					<div className="absolute -left-10 top-6 h-36 w-36 rounded-full bg-[#c7d2fe]/70 blur-3xl" />
					<div className="absolute bottom-0 right-[-20px] h-52 w-52 rounded-full bg-[#fca5a5]/60 blur-3xl" />
					<div className="relative space-y-6 text-center md:text-left">
						<p className="inline-flex items-center gap-2 rounded-full bg-white/80 px-4 py-1 text-xs font-semibold uppercase tracking-[0.3em] text-slate-700">
							Rasch-ready job search
						</p>
						<h1 className="hero-title text-5xl font-extrabold leading-tight text-slate-900 sm:text-6xl md:text-7xl">
							Your{" "}
							<span className="hero-title-gradient">
								LinkedIn Assistant
							</span>{" "}
							for transparent career moves
						</h1>
						<p className="mx-auto max-w-3xl text-base text-slate-600 md:text-lg">
							A luminous job-search agent that parses resumes, mines a 30K+ role dataset, scores every requirement with
							Rasch/Guttman math, and chats about next steps—applications, networking, and upskilling—all in one place.
						</p>
						<div className="flex flex-wrap justify-center gap-4 text-sm md:justify-start">
							<Link
								href="/steps/step1"
								className="rounded-full bg-slate-900 px-7 py-3 font-semibold text-white shadow-lg shadow-slate-900/20 transition hover:-translate-y-0.5 hover:bg-slate-800"
							>
								Start with your resume
							</Link>
							<Link
								href="/steps/step2"
								className="rounded-full border border-slate-300/70 px-7 py-3 font-semibold text-slate-900 transition hover:-translate-y-0.5 hover:border-slate-400"
							>
								Skip to job search
							</Link>
						</div>
					</div>
					<dl className="mt-10 grid gap-6 rounded-2xl bg-white/70 p-5 text-left shadow-inner sm:grid-cols-3">
						{HERO_STATS.map((item) => (
							<div key={item.label} className="space-y-1">
								<dt className="text-xs uppercase tracking-widest text-slate-500">{item.label}</dt>
								<dd className="text-3xl font-black text-slate-900">{item.value}</dd>
								<p className="text-sm text-slate-600">{item.detail}</p>
							</div>
						))}
					</dl>
				</header>

				<section className="grid gap-6 md:grid-cols-2">
					{STEPS.map((step, idx) => (
						<GlassCard key={step.href} variant="bright" className="relative flex h-full flex-col justify-between overflow-hidden p-6">
							<div className={`pointer-events-none absolute inset-0 bg-gradient-to-br ${STEP_STYLES[idx % STEP_STYLES.length].gradient} opacity-25 blur-3xl`} />
							<div className="relative space-y-3">
								<span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${STEP_STYLES[idx % STEP_STYLES.length].badge}`}>
									{step.title.split("·")[0].trim()}
								</span>
								<p className="text-lg font-semibold text-slate-900">{step.title}</p>
								<p className="text-sm text-slate-600">{step.desc}</p>
							</div>
							<Link
								href={step.href}
								className="relative mt-8 inline-flex items-center text-sm font-semibold text-slate-900 transition hover:-translate-y-0.5"
							>
								Go to {step.title.split("·")[0].trim()} →
							</Link>
						</GlassCard>
					))}
				</section>

				<GlassCard variant="bright" className="p-8">
					<div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
						<div>
							<p className="text-xs font-semibold uppercase tracking-[0.5em] text-slate-500">Playbook</p>
							<h2 className="mt-2 text-2xl font-bold text-slate-900">How the assistant orchestrates your search</h2>
							<p className="mt-2 max-w-2xl text-sm text-slate-600">
								Each phase uses different signals—resume structure, curated dataset context, and LLM-guided coaching—yet everything stays
								explainable and auditable.
							</p>
						</div>
						<div className="grid grid-cols-2 gap-3 text-xs text-slate-600 sm:text-sm">
							<div className="rounded-2xl border border-emerald-100 bg-emerald-50 px-4 py-3 font-semibold text-emerald-900">
								θ estimation built-in
							</div>
							<div className="rounded-2xl border border-indigo-100 bg-indigo-50 px-4 py-3 font-semibold text-indigo-900">
								Guttman-style difficulty ladder
							</div>
							<div className="rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 font-semibold text-rose-900">
								Chatbot resume + networking tips
							</div>
							<div className="rounded-2xl border border-sky-100 bg-sky-50 px-4 py-3 font-semibold text-sky-900">
								Lucid per-item probabilities
							</div>
						</div>
					</div>

					<div className="mt-8 grid gap-4 md:grid-cols-3">
						{FLOW_STEPS.map((item) => (
							<div key={item.title} className={`rounded-3xl border px-5 py-6 ${item.color}`}>
								<p className="text-sm font-semibold">{item.title}</p>
								<p className="mt-3 text-xs text-slate-600">{item.body}</p>
							</div>
						))}
					</div>
				</GlassCard>
			</section>
		</main>
	);
}

