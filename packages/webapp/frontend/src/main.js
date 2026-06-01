import { mount } from "svelte";
import App from "./App.svelte";

const target = document.getElementById("app");

try {
  mount(App, { target });
} catch (error) {
  if (target) {
    target.innerHTML = `<pre style="padding:16px;color:#991b1b;background:#fef2f2;border:1px solid #fecaca;border-radius:8px;white-space:pre-wrap;">UI bootstrap error:\n${String(error?.stack || error)}</pre>`;
  }
  throw error;
}
