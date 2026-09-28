import { constants } from "node:fs";
import { lstat, open, realpath } from "node:fs/promises";
import { dirname, isAbsolute } from "node:path";

async function parent(path: string) {
  if (!isAbsolute(path)) throw Error("Use an absolute private path");
  const dir = dirname(path), info = await lstat(dir);
  if (!info.isDirectory() || info.uid !== process.getuid?.() || (info.mode & 0o077) !== 0 || await realpath(dir) !== dir) throw Error("Parent must be owned, physical and private");
}
export async function readPrivateJson(path: string, maximum = 16_777_216): Promise<unknown> {
  await parent(path);
  const file = await open(path, constants.O_RDONLY | constants.O_NOFOLLOW);
  try {
    const info = await file.stat();
    if (!info.isFile() || info.uid !== process.getuid?.() || info.nlink !== 1 || (info.mode & 0o077) !== 0 || info.size > maximum) throw Error("Unsafe or oversized private input");
    const buffer = Buffer.alloc(maximum + 1); let offset = 0;
    while (offset < buffer.length) { const { bytesRead } = await file.read(buffer, offset, buffer.length - offset, null); if (!bytesRead) break; offset += bytesRead; }
    if (offset > maximum) throw Error("Private input grew beyond bound");
    return JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(buffer.subarray(0, offset)));
  } finally { await file.close(); }
}
export async function writePrivateJson(path: string, value: unknown) {
  await parent(path); const text = JSON.stringify(value);
  if (Buffer.byteLength(text) > 16_777_216) throw Error("Private output exceeds bound");
  const file = await open(path, constants.O_WRONLY | constants.O_CREAT | constants.O_EXCL | constants.O_NOFOLLOW, 0o600);
  try { await file.writeFile(text); await file.sync(); } finally { await file.close(); }
}
