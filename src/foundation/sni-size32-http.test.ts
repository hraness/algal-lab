import { test } from "bun:test";

// SPENT v3 fixture: exact test SHA-256 b0e26949530c35656f4c4a5517c288b47ec309ead83eab605d404226b3625272
// was executed once at PR #140 head 851b842f85af988675ba933a6758d34202db1708.
// Its cancel case failed; the failure-inclusive log and receipt remain in ignored runs/.
// Never re-enable or rerun v3 to obtain a pass. V4 uses a new frozen protocol and fixture.
test.skip("spent SNI size32 HTTP v3 fixture (failed; do not replay)", () => {});
