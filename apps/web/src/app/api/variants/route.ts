import { proxyJson } from "@/lib/api";

export async function GET(req: Request) {
  return proxyJson(req, "/api/v1/variants");
}

export async function POST(req: Request) {
  return proxyJson(req, "/api/v1/variants");
}


