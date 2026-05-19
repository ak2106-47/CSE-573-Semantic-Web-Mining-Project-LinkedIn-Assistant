"use client";

import { useState } from "react";
import Link from "next/link";
import { GlassCard } from "@/components/GlassCard";
import { StepNav } from "@/components/StepNav";
import { api } from "@/lib/api";
import { ChatMessage } from "@/lib/types";

const PROMPTS = [
    "Suggest remote data science roles with high Rasch fit",
    "How do I position my ML projects for product teams?",
    "Draft a networking message to a PayPal data lead",
    "Which skills should I upskill for senior analyst roles?",
];

const PLAYBOOK = [
    {
        title: "Job Suggestions",
        body: "Each recommendation cites requirement-level probabilities so you understand why it fits.",
        color: "bg-emerald-50 border-emerald-100 text-emerald-900",
    },
    {
        title: "Resume Enhancements",
        body: "Get bullet rewrites, quantified achievements, and ATS keyword mirrors from the dataset.",
        color: "bg-sky-50 border-sky-100 text-sky-900",
    },
    {
        title: "Networking & Outreach",
        body: "Ask for scripts, intros, and warm openers aligned to your target companies.",
        color: "bg-rose-50 border-rose-100 text-rose-900",
    },
];

/**
 * Step 4 — conversational assistant that references earlier steps.
 */
export default function Step4Page() {
    const [input, setInput] = useState("");
    const [history, setHistory] = useState<ChatMessage[]>([]);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState<string | null>(null);

    async function handleSend(customInput?: string) {
        const content = (customInput ?? input).trim();
        if (!content) return;
        const updatedHistory = [...history, { role: "user", content }];
        setHistory(updatedHistory);
        if (!customInput) setInput("");
        try {
            setLoading(true);
            setMessage(null);
            const response = await api.chat(updatedHistory);
            setHistory([...updatedHistory, { role: "assistant", content: response.answer }]);
        } catch (error) {
            setMessage("Chat request failed. Make sure the backend is running.");
        } finally {
            setLoading(false);
        }
    }

    function handleQuickPrompt(prompt: string) {
        setInput(prompt);
        handleSend(prompt);
    }

    return (
        <main className="min-h-screen bg-gradient-to-br from-[#eef2ff] via-white to-[#fdf2f8] px-4 py-10 text-slate-900">
            <section className="mx-auto flex max-w-5xl flex-col gap-10">
                <StepNav />

                <header className="space-y-3 rounded-[32px] border border-white/70 bg-white/70 p-8 shadow-lg shadow-slate-200/70">
                    <p className="text-xs font-semibold uppercase tracking-[0.4em] text-purple-600">Step 4</p>
                    <h1 className="text-3xl font-semibold text-slate-900">Conversational LinkedIn Assistant</h1>
                    <p className="text-sm text-slate-600">
                        Ask for job suggestions, resume upgrades, networking scripts, or upskilling roadmaps. Responses reference your parsed profile,
                        dataset jobs, and Rasch/Guttman evidence.
                    </p>
                </header>

                <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
                    <GlassCard variant="bright" className="flex min-h-[640px] flex-col p-6">
                        <div className="mb-4 flex items-center justify-between text-sm text-slate-500">
                            <p>Conversation</p>
                            <button
                                onClick={() => setHistory([])}
                                className="rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-semibold text-slate-600 hover:border-slate-400"
                            >
                                Clear chat
                            </button>
                        </div>

                        <div className="flex-1 space-y-3 overflow-y-auto pr-2 text-sm">
                            {history.length === 0 && (
                                <p className="text-xs text-slate-500">
                                    Start with "Suggest remote data science roles" or "How can I tailor my resume for product marketing?".
                                </p>
                            )}
                            {history.map((msg, idx) => {
                                const isAssistant = msg.role === "assistant";
                                return (
                                    <div
                                        key={`${msg.role}-${idx}`}
                                        className={`rounded-2xl border px-4 py-3 text-sm leading-relaxed ${
                                            isAssistant
                                                ? "border-emerald-100 bg-emerald-50 text-emerald-900"
                                                : "border-slate-200 bg-white text-slate-900 shadow-sm"
                                        }`}
                                    >
                                        <p className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                                            {isAssistant ? "Assistant" : "You"}
                                        </p>
                                        
                                        {/* Enhanced formatting for assistant responses */}
                                        {isAssistant ? (
                                            <div className="space-y-2">
                                                {msg.content.split('\n').map((line, lIdx) => {
                                                    // Headers (bold text between **)
                                                    if (line.includes('**')) {
                                                        const formatted = line.replace(/\*\*(.+?)\*\*/g, '<strong class="text-emerald-800 font-bold">$1</strong>');
                                                        return (
                                                            <p 
                                                                key={lIdx} 
                                                                className="text-sm text-slate-700 mt-3 first:mt-0"
                                                                dangerouslySetInnerHTML={{ __html: formatted }}
                                                            />
                                                        );
                                                    }
                                                    
                                                    // Bullet points
                                                    if (line.trim().startsWith('-')) {
                                                        return (
                                                            <div key={lIdx} className="flex gap-2 text-sm pl-2">
                                                                <span className="text-emerald-600 font-bold">•</span>
                                                                <span className="flex-1 text-slate-700">
                                                                    {line.trim().substring(1).trim()}
                                                                </span>
                                                            </div>
                                                        );
                                                    }
                                                    
                                                    // Regular text
                                                    if (line.trim()) {
                                                        return (
                                                            <p key={lIdx} className="text-sm text-slate-700">
                                                                {line}
                                                            </p>
                                                        );
                                                    }
                                                    
                                                    return null;
                                                })}
                                            </div>
                                        ) : (
                                            <p className="whitespace-pre-wrap">{msg.content}</p>
                                        )}
                                    </div>
                                );
                            })}
                            {loading && (
                                <div className="rounded-2xl border border-emerald-100 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
                                    Assistant is thinking…
                                </div>
                            )}
                        </div>

                        <div className="mt-4 space-y-3">
                            <textarea
                                value={input}
                                onChange={(event) => setInput(event.target.value)}
                                onKeyDown={(event) => {
                                    if (event.key === "Enter" && !event.shiftKey) {
                                        event.preventDefault();
                                        handleSend();
                                    }
                                }}
                                rows={4}
                                placeholder="Ask for job recommendations, networking scripts, resume rewrite tips..."
                                className="w-full rounded-2xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-slate-500 focus:outline-none"
                            />
                            <div className="flex flex-wrap items-center justify-between gap-3 text-xs text-slate-500">
                                {message && <p className="text-rose-500">{message}</p>}
                                <button
                                    onClick={() => handleSend()}
                                    disabled={loading || !input.trim()}
                                    className="rounded-full bg-gradient-to-r from-purple-500 to-pink-500 px-6 py-2 text-sm font-semibold text-white shadow-lg shadow-pink-200/60 transition hover:-translate-y-0.5 disabled:opacity-40"
                                >
                                    {loading ? "Sending…" : "Send"}
                                </button>
                            </div>
                            <div className="flex flex-wrap gap-2">
                                {PROMPTS.map((prompt) => (
                                    <button
                                        key={prompt}
                                        onClick={() => handleQuickPrompt(prompt)}
                                        className="rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-semibold text-slate-600 hover:border-slate-400"
                                    >
                                        {prompt}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </GlassCard>

                    <GlassCard variant="bright" className="p-6 space-y-6">
                        <div>
                            <p className="text-xs font-semibold uppercase tracking-[0.5em] text-slate-500">Guided nudges</p>
                            <h2 className="mt-2 text-2xl font-bold text-slate-900">What can I ask?</h2>
                            <p className="mt-2 text-sm text-slate-600">
                                Mix resume feedback, job clarity, and networking steps. The assistant keeps everything grounded in your parsed profile +
                                dataset.
                            </p>
                        </div>
                        <div className="space-y-3">
                            {PLAYBOOK.map((item) => (
                                <div key={item.title} className={`rounded-2xl border px-4 py-3 text-xs ${item.color}`}>
                                    <p className="text-sm font-semibold">{item.title}</p>
                                    <p className="mt-1 text-slate-600">{item.body}</p>
                                </div>
                            ))}
                        </div>
                        <div className="rounded-2xl border border-slate-100 bg-slate-50 px-4 py-3 text-xs text-slate-600">
                            <p className="font-semibold text-slate-900">Tip</p>
                            <p className="mt-1">
                                If you want the assistant to cite specific evidence, mention it (e.g., "reference my Azure experience" or "explain the b
                                value for SQL").
                            </p>
                        </div>
                    </GlassCard>
                </div>

                <div className="flex flex-wrap justify-between gap-4 text-xs text-slate-500">
                    <Link href="/steps/step3" className="font-semibold text-slate-600 underline decoration-slate-300 hover:text-slate-900">
                        ← Back to Step 3
                    </Link>
                    <Link href="/" className="rounded-full bg-slate-900 px-4 py-2 font-semibold text-white shadow-lg shadow-slate-900/20">
                        Return home →
                    </Link>
                </div>
            </section>
        </main>
    );
}
