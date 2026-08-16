import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);
  return worker.fetch(
    new Request("http://localhost/", { headers: { accept: "text/html" } }),
    { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
    { waitUntil() {}, passThroughOnException() {} },
  );
}

test("server-renders Hunar RecruitOS", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);
  const html = await response.text();
  assert.match(html, /<title>Hunar RecruitOS/);
  assert.match(html, /Good evening, Vardan/);
  assert.match(html, /Demo mode/);
  assert.match(html, /Hiring pipeline/);
  assert.doesNotMatch(html, /codex-preview|Your site is taking shape|react-loading-skeleton/);
});

test("keeps secrets and live-call claims out of the frontend source", async () => {
  const [page, app, layout] = await Promise.all([
    readFile(new URL("../app/page.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/recruit-os-app.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/layout.tsx", import.meta.url), "utf8"),
  ]);
  const source = `${page}\n${app}\n${layout}`;
  const liveKeyPrefix = ["hunar", "va", "live"].join("_");
  assert.equal(source.includes(liveKeyPrefix), false);
  assert.doesNotMatch(source, /HUNAR_API_KEY\s*=|APOLLO_API_KEY\s*=/);
  assert.match(source, /No phone call or paid API request will be made/);
  assert.match(source, /Demo transcript/);
  assert.match(source, /recruitos-campaign-state/);
  assert.match(source, /removeEventListener\("popstate"/);
  assert.match(source, /campaignTimers\.current\.forEach\(window\.clearTimeout\)/);
});
