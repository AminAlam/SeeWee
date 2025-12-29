import { proxy } from "@/lib/api";

export async function GET(req: Request, ctx: { params: { id: string } }) {
  return proxy(req, `/api/v1/variants/${ctx.params.id}/preview/pdf`);
}



