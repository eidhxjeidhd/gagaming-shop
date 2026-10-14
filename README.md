# Ga Gaming Get Key — starter

## What works
- Mobile-friendly static HTML page.
- Frontend calls a backend route for link creation.
- Worker keeps Link4M token server-side.
- Verification deliberately returns "not configured" until there is a real completion-verification mechanism and key database.

## Security first
The token shown in the screenshots was exposed. Revoke/rotate it in Link4M before using this project. Do not commit it to GitHub, put it in HTML, or send it in chat.

## GitHub Pages limitation
GitHub Pages hosts static files only. It cannot safely store API tokens, run a private server, or securely verify completion. Deploy `index.html` to GitHub Pages and deploy `worker.js` as a Cloudflare Worker (or use another backend).

## Configure Cloudflare Worker
1. Create a Worker in Cloudflare.
2. Paste `worker.js` into its editor and deploy.
3. Add secrets/variables in Worker settings:
   - Secret `LINK4M_API_TOKEN`: your rotated Link4M token.
   - Variable `LINK4M_DESTINATION`: your public Get Key page URL.
   - Variable `ALLOWED_ORIGIN`: your exact GitHub Pages origin, e.g. `https://USERNAME.github.io` (for a project site, browser Origin is still `https://USERNAME.github.io`).
4. Update `API_BASE` in `index.html` to the Worker URL, then redeploy the HTML.

## Important API response caveat
The screenshots show the Link4M endpoint pattern `/api-shorten/v2?api=...&url=...`, but not the full JSON response. In `worker.js`, the response fields are tentative examples. Compare them to Link4M's actual JSON sample and adjust the candidate fields. Do not guess if the API response differs.

## Critical completion-verification caveat
A shortened URL is not proof that a user completed the task. Before issuing a key, confirm Link4M officially supports a signed callback/webhook or another server-verifiable completion signal. If it does not, the system cannot securely auto-issue a key merely because someone returns to the page. Do not accept a client-supplied `?success=1` parameter as proof.
