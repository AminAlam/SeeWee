import { proxyJson } from "@/lib/api";

export async function GET(req: Request) {
  return proxyJson(req, "/api/v1/profile");
}

export async function PUT(req: Request) {
  return proxyJson(req, "/api/v1/profile");
}



