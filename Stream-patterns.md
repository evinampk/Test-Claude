# Stream Patterns — SPSS Modeler 18.5
# Verified patterns based on real production streams — Predicta SA / Telecom
# ✅ = tested and working in 18.5

---

## CORE DATA MODELING RULE — READ FIRST

Before building any stream, always answer:

| Question | Answer determines |
|----------|------------------|
| What is the unique key of the source? | The grain — never break it accidentally |
| What level do I need the output? | Whether aggregation is needed |
| Are there multiple rows per customer? | Yes → aggregate to get one row per customer |

### The 3-Stage Preparation Pattern ✅
```
STAGE 1 — Source grain (e.g. one row per TransactionID)
  Source → Filler → Select → Derive (enrich each transaction row)

STAGE 2 — Aggregate to target grain (e.g. one row per CustomerID)
  Aggregate (key = CustomerID) → one row per customer

STAGE 3 — Target grain derives
  Derive new KPIs from aggregated values
  (Tenure, Averages, Ratios, Segments, Bands)
```

---

## PATTERN A — Full Transaction Preparation → Customer Level ✅
### Verified working in Modeler 18.5 — production run confirmed (01.transactions.py)
### Also confirms: merge "key_fields" property name ✅ | distinct properties ✅ | filter properties ✅

Use when: raw transaction file → customer-level KPI table
Source grain: TransactionID
Output grain: CardID (one row per customer)

```python
import modeler.api

stream = modeler.script.stream()

# -- CLEAR CANVAS
for node in list(stream.getNodes()):
    node.delete()

# -- PARAMETERS (adjust dates as needed)
stream.setParameterValue("start_date", "2001-01-01")
stream.setParameterValue("end_date",   "2001-06-01")

# -- SOURCE
src = stream.createAt("variablefile", "Transactions", 100, 200)
src.setPropertyValue("full_filename", "C:/path/to/TRANSACTIONS_FILE.TXT")
src.setPropertyValue("read_field_names", True)
src.setPropertyValue("delimit_comma", True)

# -- FILLER (replace nulls)
fil = stream.createAt("filler", "Fill Nulls", 250, 200)
fil.setPropertyValue("fields",       ["Amount"])
fil.setPropertyValue("replace_mode", "BlankAndNull")
fil.setPropertyValue("replace_with", "0")

# -- SELECT: date window
sel_date = stream.createAt("select", "Date Window", 400, 200)
sel_date.setPropertyValue("mode",      "Include")
sel_date.setPropertyValue("condition",
    "TimeStamp >= '$P-start_date' and TimeStamp < '$P-end_date'")

# -- SELECT: valid records
sel_valid = stream.createAt("select", "Valid Records", 550, 200)
sel_valid.setPropertyValue("mode",      "Include")
sel_valid.setPropertyValue("condition",
    "not(@NULL(TransactionID)) and Amount > 0")

# -- STAGE 1: TRANSACTION LEVEL DERIVES
drv_month = stream.createAt("derive", "PMonth", 700, 200)
drv_month.setPropertyValue("new_name",     "PMonth")
drv_month.setPropertyValue("formula_expr",
    "datetime_year(TimeStamp) * 100 + datetime_month(TimeStamp)")

drv_dc = stream.createAt("derive", "Is_DC", 850, 200)
drv_dc.setPropertyValue("new_name",     "Is_DC")
drv_dc.setPropertyValue("formula_expr",
    "if PaymentMethod = 'DC' then 1 else 0 endif")

drv_band = stream.createAt("derive", "Tx_Band", 1000, 200)
drv_band.setPropertyValue("new_name", "Tx_Band_Num")
drv_band.setPropertyValue("formula_expr",
    "if Amount < 20 then 1 elseif Amount < 100 then 2 else 3 endif")

# Monthly active flags (one per month in window)
drv_m1 = stream.createAt("derive", "Flag_M1", 1150, 200)
drv_m1.setPropertyValue("new_name",     "Flag_M1")
drv_m1.setPropertyValue("formula_expr",
    "if datetime_month(TimeStamp) = 1 then 1 else 0 endif")

drv_m2 = stream.createAt("derive", "Flag_M2", 1300, 200)
drv_m2.setPropertyValue("new_name",     "Flag_M2")
drv_m2.setPropertyValue("formula_expr",
    "if datetime_month(TimeStamp) = 2 then 1 else 0 endif")

drv_m3 = stream.createAt("derive", "Flag_M3", 1450, 200)
drv_m3.setPropertyValue("new_name",     "Flag_M3")
drv_m3.setPropertyValue("formula_expr",
    "if datetime_month(TimeStamp) = 3 then 1 else 0 endif")

drv_m4 = stream.createAt("derive", "Flag_M4", 1600, 200)
drv_m4.setPropertyValue("new_name",     "Flag_M4")
drv_m4.setPropertyValue("formula_expr",
    "if datetime_month(TimeStamp) = 4 then 1 else 0 endif")

drv_m5 = stream.createAt("derive", "Flag_M5", 1750, 200)
drv_m5.setPropertyValue("new_name",     "Flag_M5")
drv_m5.setPropertyValue("formula_expr",
    "if datetime_month(TimeStamp) = 5 then 1 else 0 endif")

# -- STAGE 2: AGGREGATE TO CUSTOMER LEVEL
agg = stream.createAt("aggregate", "Customer Level", 1900, 200)
agg.setPropertyValue("keys",             ["CardID"])
agg.setPropertyValue("inc_record_count", True)
agg.setPropertyValue("count_field",      "Tx_Count")
agg.setKeyedPropertyValue("aggregates", "Amount",      ["Sum"])
agg.setKeyedPropertyValue("aggregates", "Amount",      ["Mean"])
agg.setKeyedPropertyValue("aggregates", "Amount",      ["Max"])
agg.setKeyedPropertyValue("aggregates", "Amount",      ["Min"])
agg.setKeyedPropertyValue("aggregates", "Is_DC",       ["Sum"])
agg.setKeyedPropertyValue("aggregates", "Is_DC",       ["Mean"])
agg.setKeyedPropertyValue("aggregates", "Tx_Band_Num", ["Mean"])
agg.setKeyedPropertyValue("aggregates", "Tx_Band_Num", ["Max"])
agg.setKeyedPropertyValue("aggregates", "Flag_M1",     ["Max"])
agg.setKeyedPropertyValue("aggregates", "Flag_M2",     ["Max"])
agg.setKeyedPropertyValue("aggregates", "Flag_M3",     ["Max"])
agg.setKeyedPropertyValue("aggregates", "Flag_M4",     ["Max"])
agg.setKeyedPropertyValue("aggregates", "Flag_M5",     ["Max"])
agg.setKeyedPropertyValue("aggregates", "ItemNumber",  ["Sum"])
agg.setKeyedPropertyValue("aggregates", "ItemNumber",  ["Max"])

# -- STAGE 3: CUSTOMER LEVEL DERIVES
drv_tenure = stream.createAt("derive", "Tenure", 2050, 200)
drv_tenure.setPropertyValue("new_name", "Tenure_Months")
drv_tenure.setPropertyValue("formula_expr",
    "Flag_M1_Max + Flag_M2_Max + Flag_M3_Max + Flag_M4_Max + Flag_M5_Max")

drv_avg = stream.createAt("derive", "Avg Monthly Spend", 2200, 200)
drv_avg.setPropertyValue("new_name", "Avg_Monthly_Spend")
drv_avg.setPropertyValue("formula_expr",
    "if Tenure_Months > 0 then Amount_Sum / Tenure_Months else 0 endif")

drv_dc_band = stream.createAt("derive", "DC Band", 2350, 200)
drv_dc_band.setPropertyValue("new_name", "DC_Ratio_Band")
drv_dc_band.setPropertyValue("formula_expr",
    "if Is_DC_Mean >= 0.8 then 'High DC' elseif Is_DC_Mean >= 0.4 then 'Mixed' else 'Low DC' endif")

drv_seg = stream.createAt("derive", "Spending Segment", 2500, 200)
drv_seg.setPropertyValue("new_name", "Spending_Segment")
drv_seg.setPropertyValue("formula_expr",
    "if Amount_Sum < 100 then 'Low' elseif Amount_Sum < 500 then 'Mid' else 'High' endif")

# -- SORT
srt = stream.createAt("sort", "Top Customers", 2650, 200)
srt.setPropertyValue("keys", [["Amount_Sum", "Descending"]])

# -- OUTPUT
tbl = stream.createAt("table", "Customer KPIs", 2800, 200)

# -- LINKS STAGE 1
stream.link(src,       fil)
stream.link(fil,       sel_date)
stream.link(sel_date,  sel_valid)
stream.link(sel_valid, drv_month)
stream.link(drv_month, drv_dc)
stream.link(drv_dc,    drv_band)
stream.link(drv_band,  drv_m1)
stream.link(drv_m1,    drv_m2)
stream.link(drv_m2,    drv_m3)
stream.link(drv_m3,    drv_m4)
stream.link(drv_m4,    drv_m5)

# -- LINKS STAGE 2 + 3
stream.link(drv_m5,        agg)
stream.link(agg,           drv_tenure)
stream.link(drv_tenure,    drv_avg)
stream.link(drv_avg,       drv_dc_band)
stream.link(drv_dc_band,   drv_seg)
stream.link(drv_seg,       srt)
stream.link(srt,           tbl)
```

### Output Fields — One Row Per CardID ✅
| Field | Description |
|-------|-------------|
| `CardID` | Unique customer key |
| `Tx_Count` | Total transactions in window |
| `Amount_Sum/Mean/Max/Min` | Spend KPIs |
| `Is_DC_Sum/Mean` | DC payment behaviour |
| `Tx_Band_Num_Mean/Max` | Typical transaction size |
| `Flag_M1-5_Max` | Active flag per month |
| `ItemNumber_Sum/Max` | Item behaviour |
| `Tenure_Months` | Months active (1-5) |
| `Avg_Monthly_Spend` | Spend ÷ tenure |
| `DC_Ratio_Band` | High DC / Mixed / Low DC |
| `Spending_Segment` | Low / Mid / High |

---

## PATTERN B — Simple ETL (Read → Clean → View) ✅

Use when: quick data exploration or first look at a file.

```python
import modeler.api

stream = modeler.script.stream()

for node in list(stream.getNodes()):
    node.delete()

src = stream.createAt("variablefile", "Source", 100, 200)
src.setPropertyValue("full_filename", "C:/path/to/file.txt")
src.setPropertyValue("read_field_names", True)
src.setPropertyValue("delimit_comma", True)

fil = stream.createAt("filler", "Fill Nulls", 250, 200)
fil.setPropertyValue("fields",       ["FieldName"])
fil.setPropertyValue("replace_mode", "BlankAndNull")
fil.setPropertyValue("replace_with", "0")

sel = stream.createAt("select", "Valid Records", 400, 200)
sel.setPropertyValue("mode",      "Include")
sel.setPropertyValue("condition", "not(@NULL(KeyField))")

tbl = stream.createAt("table", "View Data", 550, 200)

stream.link(src, fil)
stream.link(fil, sel)
stream.link(sel, tbl)
```

---

## PATTERN C — Database Source ✅ FULLY VERIFIED

Use when: reading from ODBC database instead of file.

```python
db = stream.createAt("database", "DB Source", 100, 200)
db.setPropertyValue("datasource", "TELECOM_DB")   # ✅ DSN name
db.setPropertyValue("mode",       "Table")         # ✅ verified
db.setPropertyValue("tablename",  "dbo.customers") # ✅ verified

# Table name format: "dbo.tablename"
# Continue with same preparation nodes as Pattern A
```

---

---

## PATTERN E — Predictive Model with 70/30 Partition + Evaluation ✅
### Verified working in Modeler 18.5

Use when: labelled dataset → train CHAID model → gains chart on test partition
Key rule: evaluation must use test records — never training records

```python
import modeler.api

stream = modeler.script.stream()

for node in list(stream.getNodes()):
    node.delete()

# -- SOURCE + PREPARATION (your existing preparation nodes here)
src = stream.createAt("variablefile", "Source", 100, 200)
src.setPropertyValue("full_filename", "C:/path/to/data.csv")
src.setPropertyValue("read_field_names", True)
src.setPropertyValue("delimit_comma", True)

# -- TYPE: set target field role
# ✅ VERIFIED in 18.5: two separate keyed calls ("type" + "direction")
# ❌ setKeyedPropertyValue("types", FIELD, [measurement, role]) → AEQMJ0100E
type_node = stream.createAt("type", "Set Roles", 250, 200)
type_node.setKeyedPropertyValue("type",      "TARGET_FIELD", "flag")
type_node.setKeyedPropertyValue("direction", "TARGET_FIELD", "Target")

# -- PARTITION: 70% train / 30% test — derive-based workaround ✅
# Partition node property names unverified in 18.5 (training_partition → AEQMJ0100E).
# Derive node produces identical field + values: "1_Training" / "2_Testing".
# mod(@INDEX + 9, 10) < 7 → 70% training, 30% testing, deterministic.
drv_part = stream.createAt("derive", "Partition", 400, 200)
drv_part.setPropertyValue("new_name",     "Partition")
drv_part.setPropertyValue("formula_expr",
    "if mod(@INDEX + 9, 10) < 7 then '1_Training' else '2_Testing' endif")

# -- TRAINING PATH: balance then build model
sel_train = stream.createAt("select", "Training Only", 550, 200)
sel_train.setPropertyValue("mode",      "Include")
sel_train.setPropertyValue("condition", 'Partition = "1_Training"')

bal = stream.createAt("balance", "Balance", 700, 200)

chaid = stream.createAt("chaid", "CHAID Model", 850, 200)

# -- EVALUATION PATH: test partition → nugget → gains chart
sel_test = stream.createAt("select", "Test Only", 550, 400)
sel_test.setPropertyValue("mode",      "Include")
sel_test.setPropertyValue("condition", 'Partition = "2_Testing"')

ev = stream.createAt("evaluation", "Gains Chart", 1000, 400)

# -- LINKS
stream.link(src,      type_node)
stream.link(type_node, drv_part)

# Training path
stream.link(drv_part,  sel_train)
stream.link(sel_train, bal)
stream.link(bal,       chaid)

# Evaluation path — fans out from derive-partition node
# sel_test → nugget link added AFTER builder runs (nugget doesn't exist yet)
stream.link(drv_part, sel_test)

# -- RUN MODEL
chaid.run([])

# -- FIND NUGGET (safe loop pattern — never findByType or findByName)
nugget = None
for node in stream.getNodes():
    if node.getTypeName() == "chaidmodel":
        nugget = node
        break

if nugget is None:
    raise RuntimeError("chaidmodel nugget not found — check CHAID built successfully")

nugget.setLocation(850, 400)

# -- WIRE EVALUATION PATH AND RUN
stream.link(sel_test, nugget)
stream.link(nugget,   ev)
ev.run([])
```

### Topology diagram
```
src → type → part ──────────────── sel_train → bal → chaid (builder)
               │                                           ↓ run
               └──────────────── sel_test → chaid_nugget → ev
```

### Key rules
| Rule | Detail |
|------|--------|
| Use derive for partition, not Partition node | Partition node properties undefined in 18.5 |
| type node: use `"type"` + `"direction"` separately | `"types"` with list → AEQMJ0100E |
| Balance only on training data | never apply balance to test partition |
| Nugget link done after builder runs | nugget node doesn't exist before run |
| Evaluation input = test partition | training data in evaluation = data leakage |

---

## PATTERNS STILL TO BUILD ⏳

| Pattern | Description |
|---------|-------------|
| Pattern D | Type node + KMeans segmentation on customer KPIs |
| Pattern F | Database source → full preparation → export back to DB |
