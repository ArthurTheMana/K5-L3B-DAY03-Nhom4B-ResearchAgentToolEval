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

// Rule rieng cua nhom (them vao rule mac dinh cua thu vien).
// - SectionItem chi render duoc khi nam BEN TRONG SectionBlock. Parser cua
//   OpenUI "permissive": SectionItem dat truc tiep vao Card se bi bo qua,
//   chi con lai tieu de "Related Queries" va mat phan noi dung chinh.
//   => yeu cau model dung TextContent cho noi dung chinh, SectionBlock cho muc.
const teamRules = [
  "NOI DUNG CHIN: dung TextContent(...) truc tiep trong Card. KHONG dung SectionItem truc tiep trong Card.",
  "SectionItem chi duoc dat BEN TRONG SectionBlock(sections: [...]). Neu can nhieu muc con, hay gom chung mot SectionBlock.",
  "CardHeader la phan dau tien cua Card, FollowUpBlock va cac khoi sources dat cuoi Card.",
].join("\n");

const prompt = library.prompt({
  ...openuiChatPromptOptions,
  preamble,
  // `additionalRules` phai dat SAU `...openuiChatPromptOptions`, neu khong
  // promptOptions cua thu vien se ghi de va rule cua nhom bi mat.
  additionalRules: [teamRules, ...(openuiChatPromptOptions.additionalRules ?? [])],
  examples: openuiChatExamples,
});

writeFileSync(resolve(outDir, "openui_prompt.md"), prompt, "utf8");

console.log("spec.json bytes   :", JSON.stringify(spec).length);
console.log("prompt bytes      :", prompt.length);
console.log("component groups  :", (spec.componentGroups ?? []).length);
console.log("components        :", (spec.components ?? []).length);
console.log("root              :", spec.root);
console.log("written to        :", outDir);
