import { proxyJson } from "@/lib/api";

export async function GET(req: Request, ctx: { params: { id: string } }) {
  return proxyJson(req, `/api/v1/variants/${ctx.params.id}/layout`);
}

export async function PUT(req: Request, ctx: { params: { id: string } }) {
  return proxyJson(req, `/api/v1/variants/${ctx.params.id}/layout`);
}

export async function DELETE(req: Request, ctx: { params: { id: string } }) {
  return proxyJson(req, `/api/v1/variants/${ctx.params.id}/layout`);
}

