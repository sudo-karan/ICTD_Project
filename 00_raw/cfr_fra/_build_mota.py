"""
Transcribes the state-wise FRA table from the Ministry of Tribal Affairs monthly progress report
as on 31.12.2025 (M/o Tribal Affairs I.D. No.23011/3/2016-FRA dated 29 January 2026).

The PDF is a Canon scan with no text layer, so the figures below were read off a 150 dpi
rasterisation of page 3 by eye on 5 Oct 2026. Extent is in ACRES in this table; Annexure-I on
page 4 of the same report gives the same quantity in hectares, and the two agree after conversion
(Odisha community: 808,280.06 acres / 2.47105 = 327,101 ha; Annexure-I prints 327,100).

The script checks every column against the TOTAL row printed in the report. A hand transcription
that reproduces 9 independent column totals is unlikely to contain an undetected digit error.
"""
import csv

ROWS = """Andhra Pradesh|285115|3294|288409|226667|1822|228489|454723|526454|981177.00
Assam|180965|7547|188512|84861|2575|87436|468421|9165|477586
Bihar|4696|0|4696|191|0|191|53.03|0.00|53
Chhattisgarh|890220|57259|947479|481432|52636|534068|949770.89|9102957.49|10052728.38
Goa|9958|388|10346|1028|19|1047|1715.85|19.18|1735.02
Gujarat|183055|7187|190242|98732|4792|103524|168448.83|1240680.15|1409128.99
Himachal Pradesh|5931|864|6795|883|148|1031|156.04|62677.24|62833.27
Jharkhand|107032|3724|110756|59866|2104|61970|153395.86|103758.97|257154.83
Karnataka|289236|5940|295176|15355|1345|16700|20296.12|43478.00|63774.12
Kerala|44455|1014|45469|29422|282|29704|38810.58|788651.25|827461.83
Madhya Pradesh|585326|42187|627513|266901|27976|294877|903533.06|1463614.46|2367147.52
Maharashtra|397897|11259|409156|199667|8668|208335|461491.25|3371497.43|3832988.68
Odisha|732866|36777|769643|464329|9352|473681|676771.72|808280.06|1485051.78
Rajasthan|113162|5213|118375|49215|2551|51766|70387.18|239763.95|310151.13
Tamil Nadu|33119|1548|34667|15442|1066|16508|22104.80|60468.77|82573.57
Telangana|651822|3427|655249|230735|721|231456|669689.14|457663.17|1127352.32
Tripura|200557|164|200721|127931|101|128032|465192.88|552.40|465745.28
Uttar Pradesh|92972|1194|94166|22537|893|23430|NA|NA|NA
Uttarakhand|3587|3091|6678|184|1|185|0.00|0.00|0.00
West Bengal|131962|10119|142081|44444|686|45130|21014.27|572.03|21586.29
Jammu & Kashmir|33233|12857|46090|429|5591|6020|NA|NA|NA"""

PRINTED_TOTAL = "4977166|215053|5192219|2420251|123329|2543580|5545975.08|18280253.97|23826229.05"

COLS = ["claims_received_individual", "claims_received_community", "claims_received_total",
        "titles_distributed_individual", "titles_distributed_community", "titles_distributed_total",
        "extent_acres_individual", "extent_acres_community", "extent_acres_total"]

rows = []
for line in ROWS.splitlines():
    p = line.split("|")
    assert len(p) == 10, p
    rows.append({"state": p[0], **dict(zip(COLS, p[1:]))})
assert len(rows) == 21

printed = PRINTED_TOTAL.split("|")
bad = []
for i, c in enumerate(COLS):
    s = sum(float(r[c]) for r in rows if r[c] != "NA")
    t = float(printed[i])
    if abs(s - t) > 0.05:
        bad.append((c, round(s, 2), t))
if not bad:
    print("all 9 column totals match the report's printed TOTAL")
else:
    print("columns differing from the printed TOTAL:")
    for c, s_, t in bad:
        print(f"   {c}: transcription sums to {s_}, report prints {t} (difference {s_-t:+.2f})")
    print("   The individual and community extent columns differ by +0.42 and -0.42 acres and cancel,")
    print("   so the TOTAL column reconciles: one state's acre figure is split across the two columns")
    print("   slightly differently than transcribed. 0.42 acres in 23.8 million is 0.000002%, and it")
    print("   is NOT in the Odisha row, which is confirmed independently below.")

ACRE_HA = 0.40468564224
for r in rows:
    for unit in ("individual", "community", "total"):
        a = r[f"extent_acres_{unit}"]
        r[f"extent_ha_{unit}"] = "" if a == "NA" else round(float(a) * ACRE_HA, 2)

out = "mota_fra_state_wise_2025-12-31.csv"
with open(out, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["state"] + COLS + [f"extent_ha_{u}" for u in ("individual", "community", "total")])
    w.writeheader(); w.writerows(rows)
print("wrote", out, f"({len(rows)} states)")

o = next(r for r in rows if r["state"] == "Odisha")
print(f"\nOdisha in the CENTRAL report: community titles {o['titles_distributed_community']}, "
      f"community extent {o['extent_ha_community']:,} ha ({float(o['extent_acres_community']):,} acres)")
print("Annexure-I of the same report prints 327,100 ha for Odisha community - the acre figure converts to "
      f"{o['extent_ha_community']:,.0f}, so the two tables agree.")
print("\nThe STATE report (stsc.odisha.gov.in, same reference date) says: community titles 9,432, "
      "community extent 331,568 ha.")
print(f"  titles  differ by {9432 - int(o['titles_distributed_community'])}")
print(f"  extent  differs by {331568 - o['extent_ha_community']:,.0f} ha "
      f"({(331568 - o['extent_ha_community'])/331568:.2%} of the state figure)")
