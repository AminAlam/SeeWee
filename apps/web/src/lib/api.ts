import { NextResponse } from "next/server";

function apiBaseUrl() {
  return process.env.API_BASE_URL ?? "http://localhost:8000";
}

export async function proxy(req: Request, path: string) {
  const url = `${apiBaseUrl()}${path}`;
  const res = await fetch(url, {
    method: req.method,
    headers: {
      "content-type": req.headers.get("content-type") ?? "application/json"
    },
    body: ["GET", "HEAD"].includes(req.method) ? undefined : await req.arrayBuffer(),
    cache: "no-store"
  });

  const buf = await res.arrayBuffer();
  const headers: Record<string, string> = {};
  const contentType = res.headers.get("content-type");
  const contentDisposition = res.headers.get("content-disposition");
  if (contentType) headers["content-type"] = contentType;
  if (contentDisposition) headers["content-disposition"] = contentDisposition;

  return new NextResponse(buf, { status: res.status, headers });
}

export async function proxyJson(req: Request, path: string) {
  return proxy(req, path);
}


