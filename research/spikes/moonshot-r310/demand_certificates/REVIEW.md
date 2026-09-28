# Independent review of the public demand certificates

The public source, fixture and proof note passed independent agent review
on 28 September 2026. All nine certificates are accepted for the scope
stated in [README.md](README.md): the specified H cannot equal `G − N[c]`
in a maximal triangle-free G with `degree(c) = 6`. This is a finite
exclusion, with no global Ramsey bound, catalogue-completeness, novelty or
human peer-review claim.

Source inspection confirms that the verifier checks simple triangle-free
graphs, distinct valid demand pairs, the strict covering inequality and
every required endpoint union. Its edge test removes each vertex in turn
and tests its neighbours among the remaining vertices, so every unordered
edge has an opportunity to be found. If every (M+1)-subset of demands has
an endpoint union containing an edge, no independent set can contain more
than M of them. Six such sets cannot cover more than 6M selected demands.
This argument needs no independence-number or minimum-degree assumption.

The verifier reserves the complete subset count before enumeration and
checks a shared CPU allowance. Invalid input is rejected; an exhausted
allowance reports `unknown`. The file reader bounds input size and rejects
duplicate JSON fields and nonfinite constants. Neither an LP nor a
maximal-independent-set census is needed for verification.

Every public adjacency array, labelled graph hash, selected demand array,
capacity bound and provenance label was matched exactly to the accepted
raw evidence. The earlier independent review of the nine certificates
used ordinary vertex sets rather than this verifier's bit masks and
checked all **150,902** endpoint unions separately. Its acceptance receipt
has SHA-256
`4ccf5ba7ea93a12b55c0719cad9b4103e6cc69efccc208b5b596c50797a53b69`.

The five public controls passed. They compare the capacity test with direct
independent-set enumeration on all 75 simple labelled graphs through order
four, exercise the six-cycle positive example and equality boundary, and
reject altered capacities, identities, graphs, demands, JSON values and
exhausted allowances. The standalone public verifier then accepted all
nine certificates and all **150,902** subsets. These exact focused commands
were run once by the implementation owner, and their retained results were
independently inspected and reconciled with the frozen sources:

```sh
python3 -B -m unittest discover -s research/spikes/moonshot-r310/demand_certificates -p 'test_verify.py' -v
python3 -B research/spikes/moonshot-r310/demand_certificates/verify.py
```

Both supervised processes exited zero and were collected. They used
0.051 and 0.072 child CPU seconds, respectively, under individual limits
of 10 CPU seconds, 15 wall seconds, 128 MiB sampled memory and 1 MiB per
file. Both completed before the first RSS sample, so no peak-memory
measurement is available. The verifier itself recorded 0.032 CPU seconds.

The reviewed public identities are:

| File | SHA-256 |
|---|---|
| `verify.py` | `897e545c9e3e74a067423bfd65238e985e150ab7f1e4a34abde8db7931f70ebb` |
| `test_verify.py` | `a4b17068ada732c9176a073efb7fc5f02d8f00413905ebc8baa7fc185fdc522d` |
| `certificates.json` | `b04e152fe80f1f4e6cda1c76dd432506cc70d221794b0dc99c9f6d7ca85eaa45` |
| `README.md` | `3871a5c5408c466366a0cfa8cf1d5258ee710cb7328a591be1d0df03cd16599a` |

Local validation evidence is retained in
`runs/moonshot-r310/public-demand-certificates-20260928-r1/`:

- `protocol.json`: `936eafd9c41b4f5612a93aedb68c4f392a2e75622c5a869adb4c21824e10d0f9`.
- `controls.log`: `2dc61ef979f4ded8b3bbbd0c799b352cfd8b1fd144879125203d4a818235129a`.
- `controls-process.json`: `368b13b9565c069d431908a2f853ef6315607163aef76d9b9d7b6fa7a8f0e4b3`.
- `verification.json`: `e914733e4ed05e13cf55b3d255d53b5d2a98b65c39f52a75876b55557f166da1`.
- `verification-process.json`: `6cd291d04b2deb9471c521f834575091cd2c2048413754f47b86338519b5e27a`.

All source, fixture, receipt and log identities matched during review.
The public bundle is self-contained: the local discovery records above
document its provenance but are unnecessary to replay its proof.
