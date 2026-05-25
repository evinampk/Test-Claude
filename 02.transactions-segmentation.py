# STREAM 01 — Retail Transaction Preparation → Customer KPIs
# Source:  Local flat file (CSV / delimited text)
# Output:  One row per CardID with spend KPIs, payment behaviour, tenure
#
# Canvas layout:
#  ROW 1 (y=200): src→fil→sel→TxHour→MERGE→Tenure→PMonth→TimeBand→
#                 Is_DC→Is_CC→Is_CA→TxBand
#  BRANCH (y=400): dis_tenure→flt_tenure
#  ROW 2 (y=600): Season→WeekDay→Is_Weekend→Aggregate→
#                 AvgSpend→DC_Ratio→Segment→Sort→Table
#
# *** BEFORE RUNNING: update full_filename and parameters below ***

import modeler.api

stream = modeler.script.stream()

# Clear canvas
for node in list(stream.getNodes()):
    node.delete()

# Stream parameters — observation window
stream.setParameterValue("start_date", "2024-01-01")
stream.setParameterValue("end_date",   "2024-07-01")

# ROW 1 — y=200

# NODE 1 — Local file source
src = stream.createAt("variablefile", "Retail Transactions", 100, 200)
src.setPropertyValue("full_filename",    "C:\\Users\\empakodima\\OneDrive - Predicta SA\\Documents\\Training\\Modeler\\EXAMPLE\\Transactions example\\TRANSACTIONS_FILE.TXT")
src.setPropertyValue("read_field_names", True)
src.setPropertyValue("delimit_comma",    True)
src.setPropertyValue("delimit_tab",      False)
src.setPropertyValue("delimit_space",    False)
src.setPropertyValue("delimit_other",    False)

# NODE 2 — Replace nulls
fil = stream.createAt("filler", "Fill Nulls", 200, 200)
fil.setPropertyValue("fields",       ["Amount", "ItemNumber"])
fil.setPropertyValue("replace_mode", "BlankAndNull")
fil.setPropertyValue("replace_with", "0")

# NODE 3 — Valid records only
sel_valid = stream.createAt("select", "Valid Records", 300, 200)
sel_valid.setPropertyValue("mode",      "Include")
sel_valid.setPropertyValue("condition",
    "not(@NULL(CardID)) and not(@NULL(TransactionID)) and Amount > 0")

# NODE 4 — Hour of day
drv_hour = stream.createAt("derive", "TxHour", 400, 200)
drv_hour.setPropertyValue("new_name",     "TxHour")
drv_hour.setPropertyValue("formula_expr", "datetime_hour(TimeStamp)")

# NODE 5 — Merge: adds First_Tx_Date to every transaction row
# ✅ VERIFIED: "merge" type string, "method", "key_fields"
merge_tenure = stream.createAt("merge", "Merge First Tx", 500, 200)
merge_tenure.setPropertyValue("method",     "Keys")
merge_tenure.setPropertyValue("key_fields", ["CardID"])

# NODE 6 — Tenure in months: calendar months from first transaction to end of observation window
# date_months_difference returns Real — int() gives clean integer months
drv_tenure = stream.createAt("derive", "Tenure", 600, 200)
drv_tenure.setPropertyValue("new_name", "Tenure_Months")
drv_tenure.setPropertyValue("formula_expr",
    "date_months_difference(First_Tx_Date, '$P-end_date')")

# NODE 7 — Payment month (YYYYMM)
drv_month = stream.createAt("derive", "PMonth", 700, 200)
drv_month.setPropertyValue("new_name",     "PMonth")
drv_month.setPropertyValue("formula_expr",
    "datetime_year(TimeStamp) * 100 + datetime_month(TimeStamp)")

# NODE 8 — Time of day band
drv_timeband = stream.createAt("derive", "TimeBand", 800, 200)
drv_timeband.setPropertyValue("new_name", "TimeBand")
drv_timeband.setPropertyValue("formula_expr",
    "if TxHour < 12 then 'Morning' elseif TxHour < 18 then 'Afternoon' else 'Evening' endif")

# NODE 9 — Debit card flag
drv_dc = stream.createAt("derive", "Is_DC", 900, 200)
drv_dc.setPropertyValue("new_name",     "Is_DC")
drv_dc.setPropertyValue("formula_expr",
    "if PaymentMethod = 'DC' then 1 else 0 endif")

# NODE 10 — Credit card flag
drv_cc = stream.createAt("derive", "Is_CC", 1000, 200)
drv_cc.setPropertyValue("new_name",     "Is_CC")
drv_cc.setPropertyValue("formula_expr",
    "if PaymentMethod = 'CC' then 1 else 0 endif")

# NODE 11 — Cash flag
drv_ca = stream.createAt("derive", "Is_CA", 1100, 200)
drv_ca.setPropertyValue("new_name",     "Is_CA")
drv_ca.setPropertyValue("formula_expr",
    "if PaymentMethod = 'CA' then 1 else 0 endif")

# NODE 12 — Transaction size band
drv_band = stream.createAt("derive", "TxBand", 1200, 200)
drv_band.setPropertyValue("new_name", "TxBand_Num")
drv_band.setPropertyValue("formula_expr",
    "if Amount < 20 then 1 elseif Amount < 50 then 2 elseif Amount < 100 then 3 else 4 endif")

# TENURE BRANCH — y=400, between row 1 and row 2

# NODE B1 — Distinct: first record per CardID by earliest TimeStamp
# ✅ VERIFIED: "fields", "sort_keys", "mode"
dis_tenure = stream.createAt("distinct", "First Tx Distinct", 300, 400)
dis_tenure.setPropertyValue("fields",    ["CardID"])
dis_tenure.setPropertyValue("sort_keys", [["TimeStamp", "Ascending"]])
dis_tenure.setPropertyValue("mode",      "Include")

# NODE B2 — Filter: keep CardID + rename TimeStamp to First_Tx_Date
# ✅ VERIFIED: "default_include", keyed "include", keyed "new_name"
flt_tenure = stream.createAt("filter", "First Tx Filter", 500, 400)
flt_tenure.setPropertyValue("default_include", False)
flt_tenure.setKeyedPropertyValue("include",  "CardID",    True)
flt_tenure.setKeyedPropertyValue("include",  "TimeStamp", True)
flt_tenure.setKeyedPropertyValue("new_name", "TimeStamp", "First_Tx_Date")

# ROW 2 — y=600

# NODE 13 — Season
drv_season = stream.createAt("derive", "Season", 100, 600)
drv_season.setPropertyValue("new_name", "Season")
drv_season.setPropertyValue("formula_expr",
    "if datetime_month(TimeStamp) = 12 or datetime_month(TimeStamp) <= 2 then 'Winter' elseif datetime_month(TimeStamp) <= 5 then 'Spring' elseif datetime_month(TimeStamp) <= 8 then 'Summer' else 'Autumn' endif")

# NODE 14 — Day of week
drv_weekday = stream.createAt("derive", "WeekDay", 200, 600)
drv_weekday.setPropertyValue("new_name",     "WeekDay")
drv_weekday.setPropertyValue("formula_expr", "datetime_weekday(TimeStamp)")

# NODE 15 — Weekend flag
drv_weekend = stream.createAt("derive", "Is_Weekend", 300, 600)
drv_weekend.setPropertyValue("new_name", "Is_Weekend")
drv_weekend.setPropertyValue("formula_expr",
    "if WeekDay = 6 or WeekDay = 7 then 1 else 0 endif")

# NODE 16 — Aggregate to customer level
agg = stream.createAt("aggregate", "Customer Level", 400, 600)
agg.setPropertyValue("keys",             ["CardID"])
agg.setPropertyValue("inc_record_count", True)
agg.setPropertyValue("count_field",      "Tx_Count")
agg.setKeyedPropertyValue("aggregates", "Amount",        ["Sum", "Mean", "Max"])
agg.setKeyedPropertyValue("aggregates", "Is_DC",         ["Sum"])
agg.setKeyedPropertyValue("aggregates", "Is_CC",         ["Sum"])
agg.setKeyedPropertyValue("aggregates", "Is_CA",         ["Sum"])
agg.setKeyedPropertyValue("aggregates", "TxBand_Num",    ["Mean"])
agg.setKeyedPropertyValue("aggregates", "ItemNumber",    ["Sum", "Mean"])
agg.setKeyedPropertyValue("aggregates", "Is_Weekend",    ["Sum", "Mean"])
# Tenure_Months is same value for all rows of a CardID — Max preserves it
agg.setKeyedPropertyValue("aggregates", "Tenure_Months", ["Max"])

# NODE 17 — Average monthly spend
drv_avg = stream.createAt("derive", "AvgMonthlySpend", 500, 600)
drv_avg.setPropertyValue("new_name", "Avg_Monthly_Spend")
drv_avg.setPropertyValue("formula_expr",
    "if Tenure_Months_Max > 0 then Amount_Sum / Tenure_Months_Max else 0 endif")

# NODE 18 — DC ratio
drv_dc_band = stream.createAt("derive", "DC_Band", 600, 600)
drv_dc_band.setPropertyValue("new_name", "DC_Ratio_Band")
drv_dc_band.setPropertyValue("formula_expr",
    "if Tx_Count > 0 then Is_DC_Sum / Tx_Count else 0 endif")

# NODE 19 — Spending segment
drv_seg = stream.createAt("derive", "SpendSegment", 700, 600)
drv_seg.setPropertyValue("new_name", "Spending_Segment")
drv_seg.setPropertyValue("formula_expr",
    "if Amount_Sum < 100 then 'Low' elseif Amount_Sum < 500 then 'Mid' elseif Amount_Sum < 2000 then 'High' else 'Premium' endif")

# NODE 20 — Sort by total spend descending
srt = stream.createAt("sort", "Sort by Spend", 800, 600)
srt.setPropertyValue("keys", [["Amount_Sum", "Descending"]])

# NODE 21 — Table output (KPI view)
tbl = stream.createAt("table", "Customer KPIs", 900, 600)

# ROW 3 — y=900 — Segmentation branch from drv_seg
# drv_seg feeds both srt (KPI table) and sel_active (segmentation) simultaneously

# NODE 22 — Filter: only customers with meaningful history for clustering
sel_active = stream.createAt("select", "Active Customers", 700, 900)
sel_active.setPropertyValue("mode",      "Include")
sel_active.setPropertyValue("condition",
    "Tenure_Months_Max >= 2 and Tx_Count >= 3")

# NODE 22 — Filter: whitelist only the fields for K-Means clustering
# ✅ VERIFIED filter syntax
flt_kmeans = stream.createAt("filter", "KMeans Fields", 800, 900)
flt_kmeans.setPropertyValue("default_include", False)
flt_kmeans.setKeyedPropertyValue("include", "CardID",            True)
flt_kmeans.setKeyedPropertyValue("include", "Tx_Count",          True)
flt_kmeans.setKeyedPropertyValue("include", "Amount_Sum",        True)
flt_kmeans.setKeyedPropertyValue("include", "Amount_Mean",       True)
flt_kmeans.setKeyedPropertyValue("include", "Avg_Monthly_Spend", True)
flt_kmeans.setKeyedPropertyValue("include", "Tenure_Months_Max", True)
flt_kmeans.setKeyedPropertyValue("include", "DC_Ratio_Band",     True)
flt_kmeans.setKeyedPropertyValue("include", "ItemNumber_Mean",   True)
flt_kmeans.setKeyedPropertyValue("include", "Is_Weekend_Mean",   True)

# NODE 23 — Type node: required by K-Means to instantiate field metadata
# No property settings needed — just create, link, and run it first
# type_node.run([]) = scripting equivalent of clicking "Read Values" in the GUI
type_node = stream.createAt("type", "Set Roles", 850, 900)

# NODE 24 — K-Means (5 clusters)
km = stream.createAt("kmeans", "K-Means Segmentation", 950, 900)
km.setPropertyValue("num_clusters", 5)

# LINKS — all at end, upstream to downstream

# Tenure branch
stream.link(sel_valid,    dis_tenure)
stream.link(dis_tenure,   flt_tenure)

# Row 1
stream.link(src,          fil)
stream.link(fil,          sel_valid)
stream.link(sel_valid,    drv_hour)
stream.link(drv_hour,     merge_tenure)
stream.link(flt_tenure,   merge_tenure)
stream.link(merge_tenure, drv_tenure)
stream.link(drv_tenure,   drv_month)
stream.link(drv_month,    drv_timeband)
stream.link(drv_timeband, drv_dc)
stream.link(drv_dc,       drv_cc)
stream.link(drv_cc,       drv_ca)
stream.link(drv_ca,       drv_band)

# Row 1 → Row 2 wrap
stream.link(drv_band,     drv_season)

# Row 2
stream.link(drv_season,   drv_weekday)
stream.link(drv_weekday,  drv_weekend)
stream.link(drv_weekend,  agg)
stream.link(agg,          drv_avg)
stream.link(drv_avg,      drv_dc_band)
stream.link(drv_dc_band,  drv_seg)
stream.link(drv_seg,      srt)
stream.link(srt,          tbl)

# Row 2 → Row 3: segmentation branch from drv_seg downward
stream.link(drv_seg,      sel_active)
stream.link(sel_active,   flt_kmeans)
stream.link(flt_kmeans,   type_node)
stream.link(type_node,    km)

# Run type node first — equivalent of clicking "Read Values" in the GUI
# This instantiates field metadata so K-Means can run
type_node.run([])

# Run K-Means (terminal node — cannot link before running)
# Run K-Means and capture the generated nugget
# Run K-Means
# Run K-Means
km.run([])

# The K-Means nugget is already created on the canvas.
# Get the generated nugget by label.
nugget = None

for node in stream.getNodes():
    if node.getLabel() == "K-Means Segmentation" and node != km:
        nugget = node
        break


# K-Means output field
km_field = "$KM-K-Means Segmentation"

# NODE A — Aggregate by cluster
agg_cluster = stream.createAt("aggregate", "Agg by Cluster", 1100, 850)
agg_cluster.setPropertyValue("keys",             [km_field])
agg_cluster.setPropertyValue("inc_record_count", True)
agg_cluster.setPropertyValue("count_field",      "Record_Count")
agg_cluster.setKeyedPropertyValue("aggregates", "Tx_Count",          ["Mean"])
agg_cluster.setKeyedPropertyValue("aggregates", "Amount_Sum",        ["Mean"])
agg_cluster.setKeyedPropertyValue("aggregates", "Amount_Mean",       ["Mean"])
agg_cluster.setKeyedPropertyValue("aggregates", "Avg_Monthly_Spend", ["Mean"])
agg_cluster.setKeyedPropertyValue("aggregates", "Tenure_Months_Max", ["Mean"])
agg_cluster.setKeyedPropertyValue("aggregates", "DC_Ratio_Band",     ["Mean"])
agg_cluster.setKeyedPropertyValue("aggregates", "ItemNumber_Mean",   ["Mean"])
agg_cluster.setKeyedPropertyValue("aggregates", "Is_Weekend_Mean",   ["Mean"])

# NODE B — Grand means
agg_total = stream.createAt("aggregate", "Grand Means", 1100, 950)
agg_total.setPropertyValue("inc_record_count", True)
agg_total.setPropertyValue("count_field",      "Record_Count")
agg_total.setKeyedPropertyValue("aggregates", "Tx_Count",          ["Mean"])
agg_total.setKeyedPropertyValue("aggregates", "Amount_Sum",        ["Mean"])
agg_total.setKeyedPropertyValue("aggregates", "Amount_Mean",       ["Mean"])
agg_total.setKeyedPropertyValue("aggregates", "Avg_Monthly_Spend", ["Mean"])
agg_total.setKeyedPropertyValue("aggregates", "Tenure_Months_Max", ["Mean"])
agg_total.setKeyedPropertyValue("aggregates", "DC_Ratio_Band",     ["Mean"])
agg_total.setKeyedPropertyValue("aggregates", "ItemNumber_Mean",   ["Mean"])
agg_total.setKeyedPropertyValue("aggregates", "Is_Weekend_Mean",   ["Mean"])

# NODE C — Append cluster profiles + total row
app_results = stream.createAt("append", "Append Results", 1250, 900)

# NODE D — Label total row
fil_app = stream.createAt("filler", "Label Total", 1350, 900)
fil_app.setPropertyValue("fields",       [km_field])
fil_app.setPropertyValue("replace_mode", "BlankAndNull")
fil_app.setPropertyValue("replace_with", "'Total'")

# NODE E — Segment results table
tbl_seg = stream.createAt("table", "Segment Results", 1500, 900)

# Links after nugget
stream.link(nugget,      agg_cluster)
stream.link(nugget,      agg_total)
stream.link(agg_cluster, app_results)
stream.link(agg_total,   app_results)
stream.link(app_results, fil_app)
stream.link(fil_app,     tbl_seg)

# Run final table
tbl_seg.run([])
