import { proxyJson } from "@/lib/api";

export async function GET(req: Request) {
  const url = new URL(req.url);
  const qs = url.searchParams.toString();
  return proxyJson(req, `/api/v1/entries${qs ? `?${qs}` : ""}`);
}

export async function POST(req: Request) {
  return proxyJson(req, "/api/v1/entries");
}


