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
# ⚠️ UNVERIFIED: "key_fields" property name — report result
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

# NODE 21 — Table output
tbl = stream.createAt("table", "Customer KPIs", 900, 600)

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
