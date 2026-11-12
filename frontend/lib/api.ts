export const API = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8800";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

function detailMessage(body: unknown, fallback: string): string {
  if (!body || typeof body !== "object") return fallback;
  const detail = (body as { detail?: unknown }).detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((d) => {
        const item = d as { loc?: (string | number)[]; msg?: string };
        const field = item.loc?.filter((x) => x !== "body").join(".");
        return field ? `${field}: ${item.msg}` : item.msg;
      })
      .join("; ");
  }
  return fallback;
}

type ApiInit = Omit<RequestInit, "body"> & { body?: unknown; retries?: number };

/** JSON fetch with cookies, readable errors and retry on network failure / 502 / 504. */
export async function api<T>(path: string, init: ApiInit = {}): Promise<T> {
  const { body, retries = (init.method ?? "GET") === "GET" ? 2 : 0, headers, ...rest } = init;
  let attempt = 0;
  for (;;) {
    try {
      const res = await fetch(`${API}${path}`, {
        credentials: "include",
        ...rest,
        headers: body !== undefined ? { "Content-Type": "application/json", ...headers } : headers,
        body: body !== undefined ? JSON.stringify(body) : undefined,
      });
      const text = await res.text();
      const data = text ? JSON.parse(text) : null;
      if (!res.ok) {
        if ((res.status === 502 || res.status === 504) && attempt < retries) throw new TypeError("retry");
        throw new ApiError(detailMessage(data, `Request failed (${res.status})`), res.status);
      }
      return data as T;
    } catch (err) {
      if (err instanceof ApiError) throw err;
      if (attempt >= retries) throw new ApiError("Cannot reach the Jyotish API. Is the backend running?", 0);
      attempt += 1;
      await new Promise((r) => setTimeout(r, 400 * 2 ** attempt));
    }
  }
}
