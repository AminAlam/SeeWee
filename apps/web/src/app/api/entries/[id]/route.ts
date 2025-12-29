import { proxyJson } from "@/lib/api";

export async function GET(req: Request, ctx: { params: { id: string } }) {
  return proxyJson(req, `/api/v1/entries/${ctx.params.id}`);
}

export async function PUT(req: Request, ctx: { params: { id: string } }) {
  return proxyJson(req, `/api/v1/entries/${ctx.params.id}`);
}

export async function DELETE(req: Request, ctx: { params: { id: string } }) {
  return proxyJson(req, `/api/v1/entries/${ctx.params.id}`);
}



