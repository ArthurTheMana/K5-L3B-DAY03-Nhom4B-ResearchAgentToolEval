/**
 * Sinh spec.json + OpenUI Lang system prompt cho UI FastAPI.
 *
 * Chay 1 lan (khong phai build step cho UI, chi de tao prompt text):
 *
 *   node scripts/gen_openui_prompt.mjs
 *
 * Output (mac dinh): starter_v0/ui/openui_prompt.md va starter_v0/ui/spec.json
 * Override: dat OUT_DIR=<thu muc> truoc khi chay.
 *
 * Script dung @openuidev/react-ui nen can `npm install` truoc:
 *   npm install @openuidev/react-ui@0.18.5 @openuidev/react-lang@1.1.0 @openuidev/lang-core@1.1.0
 */
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  openuiChatLibrary,
  openuiChatAdditionalRules,
  openuiChatExamples,
  openuiChatPromptOptions,
} from "@openuidev/react-ui/genui-lib";

const here = dirname(fileURLToPath(import.meta.url));

// Thu muc goc repo: script nam o starter_v0/scripts/ -> len 2 cap de len repo root.
const repoRoot = resolve(here, "..", "..");
const outDir = process.env.OUT_DIR
  ? resolve(process.env.OUT_DIR)
  : resolve(repoRoot, "starter_v0", "ui");

mkdirSync(outDir, { recursive: true });

const library = openuiChatLibrary;
const spec = library.toSpec();
writeFileSync(resolve(outDir, "spec.json"), JSON.stringify(spec, null, 2), "utf8");

// Prompt dung OpenRouter (khong phai OpenUI Cloud):
// - `library.prompt(...)` tao system prompt day du cho component library.
// - Tool cua lab (lookup / timeline / ...) van do FastAPI gui nhu OpenAI tools,
//   nen phan tool-call cua agent KHONG thay doi — van dung nguyen system_prompt.md cua starter.
const preamble = [
  "Ban la research assistant cua lab Day 03.",
  "Tra loi bang OpenUI Lang: khai bao root = Card(...) va cac thanh phan ben trong.",
  "Chi dung cac component duoc phep trong component library nay.",
].join(" ");

const prompt = library.prompt({
  preamble,
  additionalRules: openuiChatAdditionalRules,
  examples: openuiChatExamples,
  ...openuiChatPromptOptions,
});

writeFileSync(resolve(outDir, "openui_prompt.md"), prompt, "utf8");

console.log("spec.json bytes   :", JSON.stringify(spec).length);
console.log("prompt bytes      :", prompt.length);
console.log("component groups  :", (spec.componentGroups ?? []).length);
console.log("components        :", (spec.components ?? []).length);
console.log("root              :", spec.root);
console.log("written to        :", outDir);
