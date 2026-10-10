#!/usr/bin/env python3
"""What two more of the provider's pages say: its developer help page and its guide to API keys, registered on
10 October 2026. Their cautions about the tree cover loss data, and their sentences about API keys, word for word.

    python 00_raw/05_forest_reference/_build_provider_cautions_2026-10-10.py

Why this file exists (10 Oct 2026). `provider_cautions.json`, beside this script, was made on 9 October 2026 from two
pages and is committed: a file in 00_raw/ at a commit is not edited. On 10 October the owner had two more pages of the
same provider registered - the two that the note on the overlay's unresolved terms quotes. Each page turned out to carry
the provider's whole help text, and in it cautions about the accuracy of the annual tree cover loss data that the first
extract does not have. They go into a new dated file, and the first is left as it is.

In      gfw_developer_help_page_2026-10-08.html   https://www.globalforestwatch.org/help/developers/
        gfw_api_key_guide_2026-10-08.html         https://www.globalforestwatch.org/help/developers/guides/create-and-use-an-api-key/
        Both are fetched files, saved by the fetch of 8 October 2026 that also saved the five pages registered on
        9 October: their address, bytes, sha256 and date are in ../data_manifest.csv, and they are not in git.
Out     provider_cautions_2026-10-10.json   the sentences, each under a name with the page or pages it stands in; the
                                            percentages those sentences state; this run's record (inputs with their
                                            hashes, the time in UTC)

How a page's text is read. Each page is a static save whose text sits in the page source as JSON inside the HTML. The
source is read with the escapes \\u003c, \\u003e, \\u0026, \\n and \\" turned into the characters they stand for, HTML
entities turned into characters, tags taken out, and runs of spaces and non-breaking spaces made one space. Nothing else
is changed: the quotation marks are the page's own.

What is checked here, and the run stops if one fails:
  - each of the two pages is the registered file (sha256);
  - every sentence written to the output stands, word for word, in each page it is said to stand in;
  - the percentages are read out of the sentences that state them, not typed.
What is NOT checked: that the pages still say this today (they were fetched on 8 October 2026); what the sentences mean
for any figure of this project - that is argued in docs/GAP.md and docs/DECISION_LAYER.md, not here; and whether the
tile service is among the endpoints the sentences about API keys speak of - nothing read says (scripts/layer_overlay.json).
"""
import datetime, hashlib, html, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEV = HERE / "gfw_developer_help_page_2026-10-08.html"
KEY = HERE / "gfw_api_key_guide_2026-10-08.html"
OUT = HERE / "provider_cautions_2026-10-10.json"
REGISTERED = {DEV: ("ad50f515ac6703c5c92564f93dccfedb7025ec8c103517bf945f234c8379aeb6", "https://www.globalforestwatch.org/help/developers/"),
              KEY: ("9a1057979c6fe095d16369d4dc2be225c55d3330d23f8039b9c1f5704b0c6d66", "https://www.globalforestwatch.org/help/developers/guides/create-and-use-an-api-key/")}
FETCHED_UTC = "2026-10-08T12:31:13Z"
NAMES = {DEV: "the provider's developer help page", KEY: "the provider's guide to API keys"}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

# name -> (the sentence or sentences, word for word; the pages it must stand in)
CAUTIONS = {
    "accuracy_varies": ("The accuracy of the data displayed on GNW is variable across datasets, and through space and time.", (DEV, KEY)),
    "errors_of_commission_and_omission": ("In summary, the authors evaluated the overall prevalence of false positives (commission errors) in the original dataset at 13%, and the prevalence of false negatives "
                                          "(omission errors) at 12%, though the accuracy varies by biome and thus may be higher or lower in any particular location.", (DEV, KEY)),
    "sub_tropical_areas": ("Specifically, sub-tropical areas have the lowest accuracies (around 20% for commission and omission errors).", (DEV, KEY)),
    "smallholder_landscapes": ("The model often misses disturbances in smallholder landscapes, resulting in lower accuracy of the data in locations such as sub-Saharan Africa, where this type of "
                               "disturbance is more common.", (DEV, KEY)),
    "method_changed_in_2015": ("For example, in 2015, the integration of Landsat 8 satellite data and updates to the loss detection algorithm from UMD resulted in better capturing of small-scale loss.", (DEV, KEY)),
    "tree_cover_is_not_forest": ("Accordingly, “tree cover” and “forest” should not be used interchangeably.", (DEV, KEY)),
    "loss_is_not_deforestation": ("“Tree cover loss” refers to the removal or mortality of tree cover and can be due to a variety of factors, including mechanical harvesting, fire, disease or storm damage. "
                                  "As such, “loss” does not equate to deforestation.", (DEV, KEY)),
}
ON_API_KEYS = {
    "some_endpoints_require_a_key": ("Some endpoints require users to include an API key with their request", (DEV,)),
    "most_requests_need_a_key": ("To make most requests to the GFW Data API using third-party applications (e.g., scripts or websites), you need an API key.", (KEY,)),
}


def stop(m):
    print("NOT WRITTEN: " + m, file=sys.stderr)
    sys.exit(1)


def text_of(p):
    raw = p.read_text(encoding="utf-8", errors="replace")
    for a, b in (("\\u003c", "<"), ("\\u003e", ">"), ("\\u0026", "&"), ("\\n", " "), ('\\"', '"')):
        raw = raw.replace(a, b)
    return " ".join(re.sub(r"<[^>]+>", " ", html.unescape(raw)).replace(" ", " ").split())


def main():
    if OUT.exists():
        stop(f"{OUT.name} is there already: a file in 00_raw/ is not written twice")
    for p, (want, _) in REGISTERED.items():
        if not p.is_file():
            stop(f"{p.name} is not there: it is a fetched file (see ../data_manifest.csv)")
        if sha(p) != want:
            stop(f"{p.name} is not the registered file: sha256 {sha(p)}")
    text = {p: text_of(p) for p in REGISTERED}
    out = {"cautions_about_the_data": [], "on_api_keys": []}
    for group, table in (("cautions_about_the_data", CAUTIONS), ("on_api_keys", ON_API_KEYS)):
        for name, (sentence, pages) in table.items():
            for p in pages:
                if text[p].count(sentence) < 1:
                    stop(f"the sentence '{name}' does not stand word for word in {p.name}")
            out[group].append({"name": name, "text": sentence, "stands_in": [NAMES[p] for p in pages], "times_in_each_page": [text[p].count(sentence) for p in pages]})
    by = {c["name"]: c["text"] for c in out["cautions_about_the_data"]}
    pct = lambda s, pattern: re.search(pattern, s).group(1)
    stated = {"false_positives_pct": pct(by["errors_of_commission_and_omission"], r"\(commission errors\) in the original dataset at (\d+)%"),
              "false_negatives_pct": pct(by["errors_of_commission_and_omission"], r"\(omission errors\) at (\d+)%"),
              "sub_tropical_commission_and_omission_pct_about": pct(by["sub_tropical_areas"], r"around (\d+)% for commission and omission errors"),
              "year_the_method_changed": pct(by["method_changed_in_2015"], r"in (\d{4}), the integration of Landsat 8")}
    record = {"script": "00_raw/05_forest_reference/_build_provider_cautions_2026-10-10.py", "run_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
              "inputs": [{"path": f"00_raw/05_forest_reference/{p.name}", "bytes": p.stat().st_size, "sha256": sha(p), "source_url": url, "fetched_utc": FETCHED_UTC} for p, (_, url) in REGISTERED.items()],
              "what_this_is": "Sentences of two pages of Global Forest Watch (World Resources Institute), registered on 10 October 2026: its developer help page and its guide to API keys. "
                              "Each page carries the provider's whole help text. This file adds to provider_cautions.json of 9 October 2026, which is not changed; where the two repeat a figure "
                              "(the errors of commission and omission), this file's sentence is the help text's and that file's is the dataset record's",
              "how_a_page_is_read": "the page source with the escapes \\u003c, \\u003e, \\u0026, \\n and \\\" turned into their characters, HTML entities turned into characters, tags taken out, "
                                    "and runs of spaces and non-breaking spaces made one space; the quotation marks are the page's own",
              "cautions_about_the_data": out["cautions_about_the_data"], "on_api_keys": out["on_api_keys"], "stated_in_the_sentences": stated,
              "checks_passed": {"pages_are_the_registered_files": len(REGISTERED), "sentences_found_word_for_word": len(out["cautions_about_the_data"]) + len(out["on_api_keys"])},
              "not_checked": ["that the pages still say this today: they were fetched on 8 October 2026",
                              "whether the tile service is among the endpoints the sentences about API keys speak of: nothing read says"]}
    OUT.write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{OUT.name}: {record['checks_passed']['sentences_found_word_for_word']} sentences found word for word in {len(REGISTERED)} registered pages; stated: {stated}")


if __name__ == "__main__":
    main()
