/*
 * Cloudflare Worker starter for Ga Gaming.
 * Secrets must be set with `wrangler secret put LINK4M_API_TOKEN`.
 *
 * IMPORTANT:
 * - This starter intentionally does NOT claim that Link4M shortener API
 *   proves a user completed the shortlink. Confirm Link4M's official
 *   callback/webhook or completion-verification support before issuing keys.
 * - Configure LINK4M_DESTINATION as your own public Get Key return page.
 * - Review Link4M's exact JSON response schema before relying on this parser.
 */
export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "";
    const allowed = (env.ALLOWED_ORIGIN || "").split(",").map(x => x.trim()).filter(Boolean);
    const corsOrigin = allowed.includes(origin) ? origin : "";
    const headers = {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
      ...(corsOrigin ? {
        "Access-Control-Allow-Origin": corsOrigin,
        "Vary": "Origin",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
      } : {})
    };
    const json = (body, status=200) => new Response(JSON.stringify(body), {status, headers});
    const url = new URL(request.url);

    if (request.method === "OPTIONS") return new Response(null, {status:204, headers});
    if (request.method !== "POST") return json({error:"Method not allowed"},405);

    if (url.pathname === "/create-link") {
      if (!env.LINK4M_API_TOKEN || !env.LINK4M_DESTINATION) {
        return json({error:"Backend chưa cấu hình secrets/destination."},500);
      }
      // Use the official documented Link4M endpoint server-side.
      // Do not place LINK4M_API_TOKEN in frontend JavaScript.
      const endpoint = new URL("https://link4m.com/api-shorten/v2");
      endpoint.searchParams.set("api", env.LINK4M_API_TOKEN);
      endpoint.searchParams.set("url", env.LINK4M_DESTINATION);

      try {
        const upstream = await fetch(endpoint.toString(), {method:"GET"});
        const raw = await upstream.text();
        let data;
        try { data = JSON.parse(raw); }
        catch { return json({error:"Link4M trả về phản hồi không phải JSON. Kiểm tra tài liệu API."},502); }

        // Adapt these field names only after confirming the real Link4M JSON example.
        const candidate = data.shortenedUrl || data.short_url || data.url;
        if (!upstream.ok || data.status === "error" || !candidate) {
          return json({error:"Chưa đọc được URL rút gọn từ phản hồi Link4M. Cần đối chiếu JSON mẫu chính thức."},502);
        }
        let shortUrl;
        try { shortUrl = new URL(candidate); } catch { return json({error:"Link4M response URL không hợp lệ."},502); }
        if (shortUrl.protocol !== "https:" || !shortUrl.hostname.endsWith("link4m.com")) {
          return json({error:"Link rút gọn trả về không thuộc tên miền Link4M được mong đợi."},502);
        }
        return json({url:shortUrl.toString()});
      } catch {
        return json({error:"Không kết nối được Link4M."},502);
      }
    }

    if (url.pathname === "/verify-key") {
      // Do not trust a key sent from the browser without checking a database.
      // Implement this route only after adding a database and verified completion callback.
      return json({error:"Chưa cấu hình kho key và xác minh hoàn thành Link4M.", valid:false},501);
    }
    return json({error:"Not found"},404);
  }
};
