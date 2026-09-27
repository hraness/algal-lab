# Live task comparison, September 27, 2026

Labeled examples matched the more expensive feedback arm on this small response
decision study. The fixed task made two unwanted responses across three repeats
of the same 12 audit cases; the other arms made none. This supports keeping labeled
examples as a cheap baseline before adding revision rounds.

| Arm | Correct audit decisions | Invalid outputs | Unwanted responses | Total model calls | Estimated USD |
| --- | ---: | ---: | ---: | ---: | ---: |
| Fixed | 34/36 | 0 | 2 | 132 | $0.0035544 |
| Labeled examples | 36/36 | 0 | 0 | 180 | $0.0064924 |
| Predefined prompt grid | 36/36 | 0 | 0 | 180 | $0.0066148 |
| Training feedback | 36/36 | 0 | 0 | 231 | $0.0095752 |

The run used Vercel AI Gateway's `openai/gpt-6-luna`, restricted to the OpenAI
provider. Its 723 calls reported 204,928 input tokens and 11,488 output tokens.
At the September 27 catalog's standard uncached prices, the total estimate is
**$0.0262368**. That includes selection, proposals, losing candidates, and final
evaluation. It is not an invoice amount. Per-call median elapsed times ranged
from 808 to 857 ms; 95th percentiles ranged from 1,231 to 1,314 ms on a shared
machine. These observations do not establish a model or host latency advantage.

All 12 arm reports reproduced exactly offline from saved effects, including
candidate selection, proposal results, accounting, and audit outputs. This is
execution evidence. Generated archives stay outside Git under the repository's
artifact policy; [the runner and inspector](README.md) document reproduction.

The feedback report digests for ordering seeds 11, 23, and 37 are:

```text
sha256:df074c5dca09d6f66a5971bf57b5a932bc94678451d9c542a8a9f50d948644e4
sha256:dfe1c368511d1f4c6cfda913b2edf24e4e83423795a020f7130ad7119aea7a5d
sha256:e20f11935b15c7e1429d17732b3846cbd94ae93826ac15198f5e6102b0838a9e
```

## Limits

The 36 decisions repeat 12 cases; they are not 36 independent examples. The corpus
is synthetic, the original instructions already perform well, and the labels
express this study's policy. Temperature was left at the provider default and fresh model outputs varied. Demonstration ordering is the only seed-controlled variable.

The prompt-grid arm does not test every ALGAL search method, and the feedback arm
does not reproduce Imp's full GEPA implementation. This result establishes no
production Textbutler benefit, cumulative learning advantage, or reason to change
the VM. A harder, source-disjoint task is needed to test whether feedback's extra
calls buy useful generalization.
