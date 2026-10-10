#!/usr/bin/env python3
"""The cautions the providers of Hansen's data attach to it, taken word for word from two registered pages.

    python 00_raw/05_forest_reference/_build_provider_cautions.py

Why this file exists (9 Oct 2026). The decision view subtracts recorded loss from the tree cover of 2000, and the
provider's own record of the data cautions against reading present cover from that. Until now those cautions were
quoted only in the registration of the optional map overlay; they belong to the data and must stay whether or not the
overlay is shipped. So the pages are registered here, and the sentences the layer and the documents quote are kept in one
small file that is made from them and checked against them.

In      gfw_dataset_record_umd_tree_cover_loss_2026-10-08.json    Global Forest Watch's record of the dataset (its Data API)
        umd_global_forest_change_2025_v1_13_page_2026-10-08.html   the University of Maryland's page for version 1.13
        Both are fetched files: their address, bytes, sha256 and date are in ../data_manifest.csv, and they are not in git.
        Three more pages are registered beside them for the record and are not read here: the provider's terms of service,
        the attribution page those terms point to, and the reference of the tile service.
Out     provider_cautions.json    the two fields of the dataset record, whole and as they are; the sentences quoted from
                                  them and from the University's page, each under a name; the four percentages those
                                  sentences state; and this run's record (inputs with their hashes, the time in UTC)

What is checked here, and the run stops if one fails:
  - each of the two pages is the registered file (sha256);
  - the dataset record is the record of umd_tree_cover_loss, says the data runs to 2025 and names version 1.13;
  - every sentence written to the output stands in its page word for word. The page's text is compared with runs of
    spaces and non-breaking spaces made one space, and nothing else changed: the quotation marks are the page's own;
  - the four percentages are read out of the sentences that state them, not typed.
What is NOT checked: that the pages still say this today (they were fetched on 8 October 2026); what the cautions mean
for any figure of this project - that is argued in docs/DECISION_LAYER.md, not here.
"""
import datetime, hashlib, html, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RECORD = HERE / "gfw_dataset_record_umd_tree_cover_loss_2026-10-08.json"
UMD = HERE / "umd_global_forest_change_2025_v1_13_page_2026-10-08.html"
OUT = HERE / "provider_cautions.json"
REGISTERED = {RECORD: ("d6fda9a9023de671aee5f71dc5e1a08da9c48de8df526bec14f866c777b00abd", "https://data-api.globalforestwatch.org/dataset/umd_tree_cover_loss"),
              UMD: ("4b2d38f20e6cb6dfd92801ec4870f49ea47dbf97c3b7b1fb3f64f09e0381e58e", "https://storage.googleapis.com/earthenginepartners-hansen/GFC-2025-v1.13/download.html")}
FETCHED_UTC = {RECORD: "2026-10-08T12:31:13Z", UMD: "2026-10-08T08:46:31Z"}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
one_space = lambda s: " ".join(s.replace(" ", " ").split())

# the sentences quoted, each under the name the layer and the documents ask for it by. From the dataset record:
FROM_RECORD = {
    "loss_is": ("overview", "Tree cover loss is defined as “stand replacement disturbance” which is considered to be clearing of at least half of tree cover within a 30-meter pixel."),
    "loss_threshold_varies": ("overview", "The exact threshold is variable both through space and time, and is biome-dependent."),
    "tree_cover_is": ("cautions", "In this data set, “tree cover” is defined as all vegetation greater than 5 meters in height, and may take the form of natural forests or plantations across a range of canopy densities."),
    "loss_is_not_deforestation": ("cautions", "“Loss” indicates the removal or mortality of tree cover and can be due to a variety of factors, including mechanical harvesting, fire, disease, or storm damage. As such, “loss” does not equate to deforestation."),
    "cover_today_is_not_cover_of_2000_less_loss": ("cautions", "Accordingly, “net” loss cannot be calculated by subtracting figures for tree cover gain from tree cover loss, and current (post-2000) tree cover cannot be determined by subtracting figures for annual tree cover loss from year 2000 tree cover."),
    "two_halves_of_the_record": ("cautions", "Comparisons between the original 2001-2010 data and the 2011-2025 update should be performed with caution."),
    "time_series": ("overview", "Since the entire historical timeseries was not reprocessed with the updated methodology, time-series assessments should be performed with caution."),
    "errors": ("cautions", "In the original publication, the authors evaluated the overall prevalence of false positives (commission errors) in this data at 13%, and the prevalence of false negatives (omission errors) at 12%, though the accuracy varies by biome and thus may be higher or lower in any particular location."),
    "year_of_loss": ("cautions", "Largely because of a delay between an actual disturbance and the event being observed by the satellite imagery, the authors are 75% confident that the loss occurred within the stated year, and 97% confident that it occurred within a year before or after."),
}
# from the University of Maryland's page:
FROM_UMD = {
    "umd_loss_is": "Forest loss during the period 2000-2025, defined as a stand-replacement disturbance, or a change from a forest to non-forest state.",
    "umd_tree_cover_is": "Tree cover in the year 2000, defined as canopy closure for all vegetation taller than 5m in height.",
    "umd_licence": "This work is licensed under a Creative Commons Attribution 4.0 International License",
    "umd_credit": "Source: Hansen/UMD/Google/USGS/NASA",
}


def stop(m):
    sys.exit("NOT WRITTEN: " + m)


for p, (want, url) in REGISTERED.items():
    if not p.is_file():
        stop(f"{p.name} is not there: it is a fetched file ({url}); see ../data_manifest.csv")
    if sha(p) != want:
        stop(f"{p.name} is not the registered file (sha256 {sha(p)})")
rec = json.loads(RECORD.read_text(encoding="utf-8"))
if rec.get("status") != "success" or rec["data"].get("dataset") != "umd_tree_cover_loss":
    stop("the dataset record is not the record of umd_tree_cover_loss")
meta = rec["data"]["metadata"]
fields = {k: one_space(meta[k]) for k in ("overview", "cautions")}
if "includes loss up to 2025 (Version 1.13)" not in fields["overview"]:
    stop("the dataset record does not say that the data runs to 2025 in version 1.13")
sentences = {}
for name, (field, text) in FROM_RECORD.items():
    if text not in fields[field]:
        stop(f"the sentence '{name}' is not in the field '{field}' of the dataset record word for word")
    sentences[name] = {"from": f"the dataset record, field '{field}'", "text": text}
raw = UMD.read_text(encoding="utf-8", errors="replace")
umd_text = one_space(html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"(?s)<script.*?</script>|<style.*?</style>", " ", raw))))
if "User Notes for Version 1.13 Update" not in umd_text or "new 2025 loss-year" not in umd_text:
    stop("the University of Maryland's page is not the page of version 1.13")
for name, text in FROM_UMD.items():
    if text not in umd_text:
        stop(f"the sentence '{name}' is not in the University of Maryland's page word for word")
    sentences[name] = {"from": "the University of Maryland's page for version 1.13", "text": text}
m_err = re.search(r"false positives \(commission errors\) in this data at (\d+)%, and the prevalence of false negatives \(omission errors\) at (\d+)%", sentences["errors"]["text"])
m_year = re.search(r"are (\d+)% confident that the loss occurred within the stated year, and (\d+)% confident that it occurred within a year before or after", sentences["year_of_loss"]["text"])
if not m_err or not m_year:
    stop("the percentages could not be read out of the sentences that state them")
out = {"script": "00_raw/05_forest_reference/_build_provider_cautions.py",
       "run_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
       "inputs": [{"path": "00_raw/05_forest_reference/" + p.name, "bytes": p.stat().st_size, "sha256": sha(p), "source_url": REGISTERED[p][1], "fetched_utc": FETCHED_UTC[p]} for p in (RECORD, UMD)],
       "what_this_is": "Global Forest Watch's record of the dataset 'Tree cover loss' (umd_tree_cover_loss), and the University of Maryland's page for Global Forest Change version 1.13. The record is the tile and "
                       "statistics provider's, not the data producer's; the unit tables of this project are built from the University's data through Earth Engine.",
       "record": {"dataset": rec["data"]["dataset"], "title": meta["title"], "metadata_updated_on": meta["updated_on"], "licence_as_the_record_gives_it": meta["license"], "learn_more": meta["learn_more"]},
       "fields_whole": {"overview": meta["overview"], "cautions": meta["cautions"]},
       "fields_whole_are": "exactly as the record has them, non-breaking spaces and line breaks included",
       "sentences": sentences,
       "sentences_are": "word for word; compared with the page's text after runs of spaces and non-breaking spaces were made one space; the quotation marks are the page's own",
       "percentages_read_from_the_sentences": {"false_positives_pct": int(m_err.group(1)), "false_negatives_pct": int(m_err.group(2)),
                                               "loss_within_the_stated_year_confidence_pct": int(m_year.group(1)), "loss_within_a_year_either_side_confidence_pct": int(m_year.group(2))},
       "checks_passed": {"pages_are_the_registered_files": 2, "sentences_found_word_for_word": len(sentences), "record_says_loss_to_2025_in_version_1_13": True},
       "not_checked": ["that the pages still say this today: they were fetched on 8 October 2026", "what the cautions mean for any figure of this project"]}
OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"{OUT.name}: {len(sentences)} sentences held word for word against 2 registered pages; false positives {m_err.group(1)} %, false negatives {m_err.group(2)} %; "
      f"year of loss {m_year.group(1)} % and {m_year.group(2)} %")
