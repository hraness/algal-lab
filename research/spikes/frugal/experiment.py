"""A bounded, data-only small-model conjecture pilot with an enumerative control.

Run archives retain prompts, responses, failures and source identities. A replay
recomputes arithmetic and selection, without another provider call.
"""
from __future__ import annotations

import argparse
from decimal import Decimal
import hashlib
import itertools
import json
import os
from pathlib import Path
import random
import time
import urllib.error
import urllib.request

from research.survivor_order import admit_claim, judge

ROOT = Path(__file__).resolve().parents[3]
PROTOCOL = Path(__file__).with_name("protocol.json")
SOURCES = ["research/spikes/frugal/protocol.json", "research/spikes/frugal/experiment.py", "research/survivor_order.py"]
URL = "https://ai-gateway.vercel.sh/v1/chat/completions"
CATALOG_URL = "https://ai-gateway.vercel.sh/v1/models/alibaba/qwen-3-14b/endpoints"
MAX_CATALOG_BYTES = 2_000_000
EXPRESSIONS = ["sum_adjacent_vs_crossing", "sum_crossing_vs_nested", "product_adjacent_vs_crossing", "product_crossing_vs_nested"]
PROMPT = """Study this precise probability model. Vertices have positive integer rates w.
Delete one remaining vertex with probability proportional to its rate, repeat
until k vertices survive. q_ij is the probability that BOTH i and j survive.
For ANY four distinct vertices a,b,c,d with w_a<=w_b<=w_c<=w_d, compare:
sum_adjacent_vs_crossing: q_ab+q_cd versus q_ac+q_bd;
sum_crossing_vs_nested: q_ac+q_bd versus q_ad+q_bc;
product_adjacent_vs_crossing: q_ab*q_cd versus q_ac*q_bd;
product_crossing_vs_nested: q_ac*q_bd versus q_ad*q_bc.
Choose exactly 3 distinct, falsifiable claims likely true for ALL admitted
environments (n=4..9, integer rates 1..12). relation ge means left>=right;
le means left<=right. horizons all means 2<=k<=n-2, pair means k=2,
interior means 3<=k<=n-2. Prefer broad useful claims and varied expressions.
This is conjecturing, not a proof. Return only {\"claims\":[{\"expression\":...,
\"relation\":...,\"horizons\":...}, ...]}. No explanations or code. /no_think"""


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def sources():
    return {p: digest(ROOT / p) for p in SOURCES}


def save(path, obj):
    with Path(path).open("x", encoding="utf-8") as f:
        f.write(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def environments(spec):
    rng = random.Random(spec["seed"])
    return [{"weights": sorted(rng.randint(1, spec["rateCeiling"]) for _ in range(n))}
            for n in spec["nodes"] for _ in range(spec["environmentsPerSize"])]


def admit_plan(plan):
    """Hard limits survive accidental edits to the human-readable protocol."""
    fields = {"contract", "model", "provider", "inputUsdPerToken", "outputUsdPerToken",
              "modelContextTokens", "maximumCalls", "maximumOutputTokens", "maximumRequestBytes",
              "maximumResponseBytes", "maximumEstimatedUsd", "timeoutSeconds", "temperature",
              "replicates", "arms", "claimsPerCall", "development", "holdout", "primary",
              "baseline", "chronology", "interpretation"}
    if type(plan) is not dict or set(plan) != fields or plan["contract"] != "algal.lab.frugal-conjectures.plan.v1":
        raise ValueError("unexpected protocol fields or contract")
    if (plan["model"] != "alibaba/qwen-3-14b" or plan["provider"] != "deepinfra"
            or type(plan["maximumCalls"]) is not int or plan["maximumCalls"] != 6
            or type(plan["maximumOutputTokens"]) is not int or not 1 <= plan["maximumOutputTokens"] <= 1024
            or type(plan["modelContextTokens"]) is not int or plan["modelContextTokens"] != 40960
            or not 0 < Decimal(plan["maximumEstimatedUsd"]) <= Decimal("0.05")
            or Decimal(plan["inputUsdPerToken"]) <= 0
            or Decimal(plan["outputUsdPerToken"]) <= 0
            or type(plan["maximumRequestBytes"]) is not int or not 1 <= plan["maximumRequestBytes"] <= 12000
            or type(plan["maximumResponseBytes"]) is not int or not 1 <= plan["maximumResponseBytes"] <= 65536
            or type(plan["timeoutSeconds"]) is not int or not 1 <= plan["timeoutSeconds"] <= 60
            or type(plan["temperature"]) not in (int, float) or not 0 <= plan["temperature"] <= 2):
        raise ValueError("protocol exceeds fixed model, route, or budget limits")
    if (type(plan["replicates"]) is not list or plan["replicates"] != [1, 2]
            or any(type(r) is not int for r in plan["replicates"])
            or type(plan["arms"]) is not list or len(plan["arms"]) != 2
            or set(plan["arms"]) != {"no-feedback", "counterexample-feedback"}
            or plan["claimsPerCall"] != 3):
        raise ValueError("protocol changes the frozen experiment design")
    for name in ("development", "holdout"):
        spec = plan[name]
        if (type(spec) is not dict or set(spec) != {"nodes", "rateCeiling", "environmentsPerSize", "seed"}
                or type(spec["nodes"]) is not list or not 1 <= len(spec["nodes"]) <= 6
                or any(type(n) is not int or not 4 <= n <= 9 for n in spec["nodes"])
                or type(spec["rateCeiling"]) is not int or not 1 <= spec["rateCeiling"] <= 12
                or type(spec["environmentsPerSize"]) is not int or not 1 <= spec["environmentsPerSize"] <= 32
                or type(spec["seed"]) is not int or not 0 <= spec["seed"] < 2 ** 64):
            raise ValueError("protocol panel exceeds judge bounds")
    if plan["development"]["seed"] == plan["holdout"]["seed"]:
        raise ValueError("development and holdout seeds must differ")


def preflight_catalog(plan, opener):
    """Read bounded public model metadata before any paid dispatch."""
    request = urllib.request.Request(CATALOG_URL, method="GET")
    with opener.open(request, timeout=plan["timeoutSeconds"]) as response:
        raw = response.read(MAX_CATALOG_BYTES + 1)
    if len(raw) > MAX_CATALOG_BYTES:
        raise ValueError("model catalog exceeds byte bound")
    catalog = json.loads(raw)
    data = catalog.get("data") if type(catalog) is dict else None
    if type(data) is not dict or data.get("id") != plan["model"] or type(data.get("endpoints")) is not list:
        raise ValueError("endpoint catalog has no matching model")
    found = [m for m in data["endpoints"] if type(m) is dict and m.get("provider_name") == plan["provider"]]
    if len(found) != 1:
        raise ValueError("pinned model absent or duplicated in public catalog")
    model = found[0]
    pricing = model.get("pricing")
    if type(pricing) is not dict:
        raise ValueError("model catalog has no pricing")
    context, output = model.get("context_length"), model.get("max_completion_tokens")
    if (model.get("status") != 0 or type(context) is not int or context != plan["modelContextTokens"]
            or type(output) is not int or output < plan["maximumOutputTokens"]
            or not 0 <= Decimal(str(pricing["prompt"])) <= Decimal(plan["inputUsdPerToken"])
            or not 0 <= Decimal(str(pricing["completion"])) <= Decimal(plan["outputUsdPerToken"])
            or Decimal(str(pricing.get("request", "0"))) != 0):
        raise ValueError("catalog limits or prices exceed frozen reservation")
    return {"url": CATALOG_URL, "model": plan["model"], "provider": plan["provider"], "contextWindow": context,
            "maximumOutputTokens": output,
            "inputUsdPerToken": str(pricing["prompt"]),
            "outputUsdPerToken": str(pricing["completion"]),
            "catalogSha256": hashlib.sha256(raw).hexdigest()}


def validate_preflight_record(plan, record):
    if (type(record) is not dict or record.get("url") != CATALOG_URL
            or record.get("model") != plan["model"]
            or record.get("provider") != plan["provider"]
            or type(record.get("contextWindow")) is not int
            or record["contextWindow"] != plan["modelContextTokens"]
            or type(record.get("maximumOutputTokens")) is not int
            or record["maximumOutputTokens"] < plan["maximumOutputTokens"]
            or not 0 <= Decimal(record["inputUsdPerToken"]) <= Decimal(plan["inputUsdPerToken"])
            or not 0 <= Decimal(record["outputUsdPerToken"]) <= Decimal(plan["outputUsdPerToken"])
            or len(record.get("catalogSha256", "")) != 64):
        raise ValueError("catalog preflight record mismatch")


def parse_proposal(value):
    if not isinstance(value, dict) or set(value) != {"claims"}:
        raise ValueError("proposal must have exactly claims")
    claims = value["claims"]
    if not isinstance(claims, list) or len(claims) != 3:
        raise ValueError("proposal must have three claims")
    for claim in claims:
        admit_claim(claim)
    if len({canonical(c) for c in claims}) != 3:
        raise ValueError("duplicate claim")
    return claims


def request_body(plan, context):
    claim_schema = {"type": "object", "additionalProperties": False,
                    "required": ["expression", "relation", "horizons"],
                    "properties": {"expression": {"type": "string", "enum": EXPRESSIONS},
                                   "relation": {"type": "string", "enum": ["ge", "le"]},
                                   "horizons": {"type": "string", "enum": ["all", "pair", "interior"]}}}
    schema = {"type": "object", "additionalProperties": False, "required": ["claims"],
              "properties": {"claims": {"type": "array", "minItems": 3, "maxItems": 3, "items": claim_schema}}}
    return {"model": plan["model"], "messages": [{"role": "system", "content": PROMPT},
             {"role": "user", "content": canonical(context)}],
            "max_tokens": plan["maximumOutputTokens"], "temperature": plan["temperature"],
            "reasoning": {"effort": "none"},
            "providerOptions": {"gateway": {"only": [plan["provider"]]}},
            "response_format": {"type": "json_schema", "json_schema": {
                "name": "survival_conjectures", "strict": True, "schema": schema}}}


def usage_summary(response, plan):
    """Provider usage is unknown unless both token counts are valid."""
    usage = response.get("usage") if type(response) is dict else None
    if type(usage) is not dict:
        return {"status": "unknown"}
    inputs, outputs = usage.get("prompt_tokens"), usage.get("completion_tokens")
    if (type(inputs) is not int or inputs < 0 or type(outputs) is not int or outputs < 0):
        return {"status": "unknown"}
    estimate = (Decimal(inputs) * Decimal(plan["inputUsdPerToken"])
                + Decimal(outputs) * Decimal(plan["outputUsdPerToken"]))
    return {"status": "reported", "inputTokens": inputs, "outputTokens": outputs,
            "estimatedUsdFromUsage": str(estimate)}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Gateway:
    def __init__(self, plan, directory):
        admit_plan(plan)
        self.plan, self.directory, self.calls = plan, directory, 0
        self.uncertain = False
        self.key = os.environ.get("AI_GATEWAY_API_KEY", "")
        if not 16 <= len(self.key) <= 8192 or any(x.isspace() for x in self.key):
            raise ValueError("AI_GATEWAY_API_KEY is required")
        self.reserve = (Decimal(plan["inputUsdPerToken"]) * plan["modelContextTokens"]
                        + Decimal(plan["outputUsdPerToken"]) * plan["maximumOutputTokens"])
        if self.reserve * plan["maximumCalls"] > Decimal(plan["maximumEstimatedUsd"]):
            raise ValueError("declared full-context cost exceeds budget")
        self.opener = urllib.request.build_opener(NoRedirect)

    def call(self, label, context):
        if self.uncertain or self.calls >= self.plan["maximumCalls"]:
            raise RuntimeError("no further dispatch is permitted")
        p = self.plan
        body = request_body(p, context)
        encoded = canonical(body).encode()
        if len(encoded) > p["maximumRequestBytes"]:
            raise ValueError("request byte bound")
        self.calls += 1
        record = {"label": label, "number": self.calls, "request": body,
                  "reservedUsd": str(self.reserve), "status": "dispatched", "claims": []}
        save(self.directory / f"call-{self.calls}-intent.json", record)
        started = time.monotonic()
        request = urllib.request.Request(URL, data=encoded, method="POST", headers={
            "Authorization": "Bearer " + self.key, "Content-Type": "application/json"})
        try:
            with self.opener.open(request, timeout=p["timeoutSeconds"]) as response:
                raw = response.read(p["maximumResponseBytes"] + 1)
            if len(raw) > p["maximumResponseBytes"]:
                raise ValueError("response byte bound")
            text = raw.decode("utf-8")
            if self.key in text or json.dumps(self.key)[1:-1] in text:
                raise ValueError("credential echo")
            result = json.loads(text)
            if type(result) is not dict:
                raise ValueError("response must be an object")
            record["response"] = result
            if result.get("model") not in [p["model"], p["model"].split("/")[1]]:
                raise ValueError("model mismatch")
            choices = result.get("choices")
            if not isinstance(choices, list) or len(choices) != 1:
                raise ValueError("choice count")
            choice = choices[0]
            message = choice.get("message", {})
            if choice.get("finish_reason") != "stop" or message.get("tool_calls") or message.get("function_call"):
                raise ValueError("incomplete or tool response")
            record["claims"] = parse_proposal(json.loads(message["content"]))
            record["status"] = "completed"
        except urllib.error.HTTPError as e:
            record.update(status="failed", failure="http", httpStatus=e.code)
            e.close()
        except (urllib.error.URLError, TimeoutError, OSError):
            self.uncertain = True
            record.update(status="failed", failure="transport", uncertain=True)
        except (ValueError, TypeError, KeyError, AttributeError, UnicodeError):
            record.update(status="failed", failure="invalid_response")
        finally:
            record["elapsedSeconds"] = time.monotonic() - started
            record["usage"] = usage_summary(record.get("response"), p)
            usage = record["usage"]
            if (usage["status"] == "reported" and
                    (usage["inputTokens"] > p["modelContextTokens"]
                     or usage["outputTokens"] > p["maximumOutputTokens"]
                     or Decimal(usage["estimatedUsdFromUsage"]) > self.reserve)):
                record["budgetUncertain"] = True
                self.uncertain = True
            save(self.directory / f"call-{self.calls}-result.json", record)
        return record


def check_claims(claims, panel):
    output = []
    for claim in claims:
        judgment = judge(panel, claim)
        if judgment["status"] == "counterexample":
            example = judgment["counterexample"]
            example["weights"] = panel[example["environmentIndex"]]["weights"]
            example["left"], example["right"] = str(example["left"]), str(example["right"])
        output.append({"claim": claim, "judgment": judgment})
    return output


def universe():
    return [{"expression": e, "relation": r, "horizons": h}
            for e, r, h in itertools.product(EXPRESSIONS, ["ge", "le"], ["all", "pair", "interior"])]


def evaluate(portfolios, development, holdout):
    rows = []
    for p in portfolios:
        dev, test = check_claims(p["claims"], development), check_claims(p["claims"], holdout)
        passing = { (a["claim"]["expression"], a["claim"]["relation"])
                    for a, b in zip(dev, test)
                    if a["claim"]["horizons"] in ("all", "interior")
                    and a["judgment"]["status"] == b["judgment"]["status"] == "passed"
                    and a["judgment"]["passedCount"] > 0 and b["judgment"]["passedCount"] > 0 }
        rows.append({**p, "development": dev, "holdout": test,
                     "primaryPassingLaws": [list(v) for v in sorted(passing)],
                     "primaryCount": len(passing)})
    return rows


def build_portfolios(plan, development, call):
    """The same deterministic selection logic drives execution and replay."""
    portfolios = []
    stopped = False
    for replicate in plan["replicates"]:
        order = plan["arms"] if replicate % 2 else list(reversed(plan["arms"]))
        if stopped:
            portfolios.extend({"replicate": replicate, "arm": arm, "status": "skipped-uncertain",
                               "claims": [], "initialCall": None, "finalCall": None} for arm in order)
            continue
        initial = call(f"initial-{replicate}", {"replicate": replicate, "stage": "initial"})
        if initial["status"] != "completed":
            stopped = bool(initial.get("uncertain") or initial.get("budgetUncertain"))
            portfolios.extend({"replicate": replicate, "arm": arm, "status": "skipped-initial-failed",
                               "claims": [], "initialCall": initial["number"], "finalCall": None}
                              for arm in order)
            continue
        initial_claims = initial["claims"]
        feedback = check_claims(initial_claims, development)
        stopped = bool(initial.get("budgetUncertain"))
        for arm in order:
            if stopped:
                portfolios.append({"replicate": replicate, "arm": arm, "status": "skipped-uncertain",
                                   "claims": [], "initialCall": initial["number"], "finalCall": None})
                continue
            context = {"replicate": replicate, "stage": "final", "previousClaims": initial_claims}
            if arm == "counterexample-feedback":
                context["exactDevelopmentFeedback"] = feedback
            context["instruction"] = "Select your final three conjectures; you may retain or revise previous claims."
            result = call(f"{arm}-{replicate}", context)
            portfolios.append({"replicate": replicate, "arm": arm, "status": result["status"],
                               "claims": result["claims"], "initialCall": initial["number"],
                               "finalCall": result["number"]})
            stopped = bool(result.get("uncertain") or result.get("budgetUncertain"))
    enumeration = check_claims(universe(), development)
    accepted = [x["claim"] for x in enumeration if x["judgment"]["status"] == "passed"]
    portfolios.append({"replicate": None, "arm": "enumeration", "status": "completed",
                       "claims": accepted})
    return portfolios, enumeration


def cost_summary(plan, records, portfolios):
    price_in = Decimal(plan["inputUsdPerToken"])
    price_out = Decimal(plan["outputUsdPerToken"])
    reserve = price_in * plan["modelContextTokens"] + price_out * plan["maximumOutputTokens"]
    observed = sum((Decimal(r["usage"]["estimatedUsdFromUsage"]) for r in records
                    if r["usage"]["status"] == "reported"), Decimal(0))
    unknown = [r["number"] for r in records if r["usage"]["status"] != "reported"]
    by_number = {r["number"]: r for r in records}
    arms = []
    for portfolio in portfolios:
        if portfolio["arm"] == "enumeration":
            continue
        numbers = sorted({number for number in (portfolio["initialCall"], portfolio["finalCall"])
                          if number is not None})
        known = sum((Decimal(by_number[n]["usage"]["estimatedUsdFromUsage"])
                     for n in numbers if by_number[n]["usage"]["status"] == "reported"), Decimal(0))
        arms.append({"replicate": portfolio["replicate"], "arm": portfolio["arm"],
                     "callNumbers": numbers, "standaloneReservedUsd": str(reserve * len(numbers)),
                     "knownEstimatedUsdFromUsage": str(known),
                     "unknownUsageCalls": [n for n in numbers if by_number[n]["usage"]["status"] != "reported"]})
    return {"dispatchedCalls": len(records), "actualDispatchedReservedUsd": str(reserve * len(records)),
            "fullRunReservedUsd": str(reserve * plan["maximumCalls"]),
            "knownEstimatedUsdFromUsage": str(observed), "unknownUsageCalls": unknown,
            "allUsageReported": not unknown, "standaloneArms": arms,
            "attribution": "Shared initial calls are charged once in actual totals and fully to each standalone arm; usage cost is an estimate from reported tokens, not a provider invoice."}


def run(out):
    plan = json.loads(PROTOCOL.read_text())
    admit_plan(plan)
    out.mkdir(parents=True, exist_ok=False)
    save(out / "manifest.json", {"plan": plan, "sourceIdentities": sources()})
    gateway = Gateway(plan, out)
    catalog = preflight_catalog(plan, gateway.opener)
    save(out / "catalog-preflight.json", catalog)
    development = environments(plan["development"])
    records = []
    def call(label, context):
        result = gateway.call(label, context)
        records.append(result)
        return result
    portfolios, enumeration = build_portfolios(plan, development, call)
    save(out / "frozen.json", {"portfolios": portfolios, "enumerationDevelopment": enumeration})
    holdout = environments(plan["holdout"])
    results = evaluate(portfolios, development, holdout)
    summary = cost_summary(plan, records, portfolios)
    save(out / "results.json", {"portfolios": results, "cost": summary})
    print(canonical({"status": "completed", "calls": gateway.calls, "out": str(out),
                     "unknownUsageCalls": summary["unknownUsageCalls"]}))


def replay(out):
    manifest = json.loads((out / "manifest.json").read_text())
    if manifest["sourceIdentities"] != sources() or manifest["plan"] != json.loads(PROTOCOL.read_text()):
        raise ValueError("source or protocol mismatch")
    plan = manifest["plan"]
    admit_plan(plan)
    validate_preflight_record(plan, json.loads((out / "catalog-preflight.json").read_text()))
    frozen = json.loads((out / "frozen.json").read_text())
    development, holdout = environments(plan["development"]), environments(plan["holdout"])
    records = []
    reserve = str(Decimal(plan["inputUsdPerToken"]) * plan["modelContextTokens"]
                  + Decimal(plan["outputUsdPerToken"]) * plan["maximumOutputTokens"])
    def call(label, context):
        number = len(records) + 1
        intent = json.loads((out / f"call-{number}-intent.json").read_text())
        record = json.loads((out / f"call-{number}-result.json").read_text())
        expected = {"label": label, "number": number, "request": request_body(plan, context),
                    "reservedUsd": reserve, "status": "dispatched", "claims": []}
        if intent != expected or any(record.get(k) != v for k, v in expected.items()
                                     if k not in ("status", "claims")):
            raise ValueError("call request or intent mismatch")
        if record.get("status") not in ("completed", "failed"):
            raise ValueError("call status mismatch")
        if record.get("usage") != usage_summary(record.get("response"), plan):
            raise ValueError("call usage mismatch")
        usage = record["usage"]
        over_budget = (usage["status"] == "reported" and
                       (usage["inputTokens"] > plan["modelContextTokens"]
                        or usage["outputTokens"] > plan["maximumOutputTokens"]
                        or Decimal(usage["estimatedUsdFromUsage"]) > Decimal(reserve)))
        if bool(record.get("budgetUncertain")) != over_budget:
            raise ValueError("billing bound mismatch")
        if record["status"] == "completed":
            response = record["response"]
            if response.get("model") not in [plan["model"], plan["model"].split("/")[1]]:
                raise ValueError("response model mismatch")
            choices = response["choices"]
            if (type(choices) is not list or len(choices) != 1
                    or choices[0].get("finish_reason") != "stop"
                    or choices[0].get("message", {}).get("tool_calls")
                    or choices[0].get("message", {}).get("function_call")):
                raise ValueError("response choice mismatch")
            claims = parse_proposal(json.loads(choices[0]["message"]["content"]))
            if claims != record["claims"]:
                raise ValueError("proposal mismatch")
        elif record.get("claims") != []:
            raise ValueError("failed call has claims")
        if bool(record.get("uncertain")) != (record.get("failure") == "transport"):
            raise ValueError("transport uncertainty mismatch")
        records.append(record)
        return record
    portfolios, enumeration = build_portfolios(plan, development, call)
    if frozen != {"portfolios": portfolios, "enumerationDevelopment": enumeration}:
        raise ValueError("frozen selection mismatch")
    expected_files = {f"call-{n}-{suffix}.json" for n in range(1, len(records) + 1)
                      for suffix in ("intent", "result")}
    if {p.name for p in out.glob("call-*.json")} != expected_files:
        raise ValueError("unexpected or missing call record")
    results = {"portfolios": evaluate(portfolios, development, holdout),
               "cost": cost_summary(plan, records, portfolios)}
    if results != json.loads((out / "results.json").read_text()):
        raise ValueError("numerical mismatch")
    save(out / "reproduction.json", {"status": "matched", "resultsSha256": digest(out / "results.json"),
                                     "sourceIdentities": sources(), "modelCallsRepeated": False})
    print(canonical({"status": "matched", "out": str(out)}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["run", "replay"])
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    (run if args.command == "run" else replay)(args.out)
