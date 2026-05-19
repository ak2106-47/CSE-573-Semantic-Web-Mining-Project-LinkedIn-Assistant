import { NextRequest } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || "http://127.0.0.1:8000";

type RouteContext = {
	params: Promise<{ slug: string[] }> | { slug: string[] };
};

async function handleProxy(req: NextRequest, context: RouteContext) {
	const resolvedParams = await context.params;
	const path = resolvedParams.slug.join("/");
	const target = `${BACKEND_URL}/${path}${req.nextUrl.search}`;

	const headers = new Headers(req.headers);
	headers.delete("host");
	headers.set("origin", BACKEND_URL);

	const init: RequestInit = {
		method: req.method,
		headers,
	};

	if (req.method !== "GET" && req.method !== "HEAD") {
		// @ts-ignore Node fetch streaming
		init.duplex = "half";
		init.body = req.body;
	}

	try {
		const res = await fetch(target, init);
		const responseHeaders = new Headers(res.headers);
		responseHeaders.delete("content-encoding");
		return new Response(res.body, {
			status: res.status,
			headers: responseHeaders,
		});
	} catch (error) {
		return new Response(JSON.stringify({ error: "Proxy request failed" }), {
			status: 500,
			headers: { "Content-Type": "application/json" },
		});
	}
}

export const GET = handleProxy;
export const POST = handleProxy;
export const PUT = handleProxy;
export const PATCH = handleProxy;
export const DELETE = handleProxy;

