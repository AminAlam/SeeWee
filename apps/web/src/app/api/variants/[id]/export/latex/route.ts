import { proxy } from "@/lib/api";

export async function POST(req: Request, ctx: { params: { id: string } }) {
  return proxy(req, `/api/v1/variants/${ctx.params.id}/export/latex`);
}


