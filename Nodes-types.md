# Node Types & Verified Rules — SPSS Modeler 18.5
# Merged from node-types.md + verified-bugs.md
# ✅ = confirmed working  ❌ = confirmed broken  ⚠️ = unverified

---

## MANDATORY SCRIPT TEMPLATE

```python
import modeler.api

stream = modeler.script.stream()   # ONCE only — never call again

# -- CLEAR CANVAS (always first)
for node in list(stream.getNodes()):
    node.delete()

# -- CREATE ALL NODES FIRST
# ... nodes here ...

# -- ALL LINKS LAST (always upstream → downstream)
stream.link(nodeA, nodeB)
stream.link(nodeB, nodeC)

# -- RUN
stream.runAll([])
```

---

## CORE RULES — NEVER BREAK THESE

| # | Rule | Detail |
|---|------|--------|
| R1 | `stream = modeler.script.stream()` once only | Calling again = state corruption |
| R2 | Clear canvas first | `for node in list(stream.getNodes()): node.delete()` |
| R3 | Create all nodes before any links | NullPointerException if linked too early |
| R4 | Links always upstream → downstream | `stream.link(A,B)` means A feeds into B |
| R5 | Run command | `stream.runAll([])` — nothing else works |
| R6 | File paths use `/` or `\\` | Never single backslash |
| R7 | CLEM if/elseif on ONE line | ClemParseException if multiline |
| R8 | aggregate keys = Python list | `["Field"]` not `"Field"` |
| R9 | Never set result_type on derive | Property does not exist in 18.5 |
| R10 | Nuggets only exist after runAll([]) | Never search before running |
| R11 | Never use findByName() | AttributeError — use getNodes() loop |
| R12 | Never use findByType(x, None) | NullPointerException |
| R13 | Never use ===== divider comments | Parser crash |

---

## SAFE NODE SEARCH PATTERN

```python
# Find any node by name
target = None
for node in stream.getNodes():
    if node.getName() == "My Node Label":
        target = node
        break

# Find a nugget by type
nugget = None
for node in stream.getNodes():
    if node.getTypeName() == "kmeansmodel":
        nugget = node
        break
```

---

## VERIFIED NODE TYPE STRINGS ✅

| Category | Node | Type String |
|----------|------|-------------|
| Source | Variable File | `"variablefile"` |
| Source | Database | `"database"` |
| Record Ops | Select | `"select"` |
| Record Ops | Merge | `"merge"` |
| Record Ops | Aggregate | `"aggregate"` |
| Record Ops | Sort | `"sort"` |
| Record Ops | Append | `"append"` |
| Field Ops | Type | `"type"` |
| Field Ops | Derive | `"derive"` |
| Field Ops | Filter | `"filter"` |
| Field Ops | Filler | `"filler"` |
| Field Ops | Distinct | `"distinct"` |
| Field Ops | Partition | `"partition"` |
| Modeling | K-Means | `"kmeans"` |
| Modeling | TwoStep | `"twostep"` |
| Modeling | CHAID | `"chaid"` |
| Modeling | C5.0 | `"c50"` |
| Modeling nugget | CHAID nugget | `"chaidmodel"` |
| Modeling nugget | K-Means nugget | `"kmeansmodel"` |
| Output | Table | `"table"` |
| Output | Evaluation | `"evaluation"` |
| Record Ops | Balance | `"balance"` |

## WRONG NODE TYPE STRINGS ❌ — Common Mistakes

| Wrong | Correct | Error |
|-------|---------|-------|
| `"typenode"` | `"type"` | unknown node type |
| `"tableoutput"` | `"table"` | unknown node type |
| `"databasesource"` | `"database"` | unknown node type |

## UNVERIFIED NODE TYPE STRINGS ⚠️

| Node | Likely String | Status |
|------|--------------|--------|
| Reclassify | `"reclassify"` | Not tested |
| Binning | `"binning"` | Not tested |
| PCA/Factor | `"pca"` or `"factor"` | Not tested |
| Analysis | `"analysis"` | Not tested (different from Evaluation) |

---

## NODE PROPERTIES

### variablefile — Flat file / CSV source ✅
```python
src = stream.createAt("variablefile", "Source", 100, 200)
src.setPropertyValue("full_filename", "C:/data/file.txt")
src.setPropertyValue("read_field_names", True)
src.setPropertyValue("delimit_comma", True)
```

### database — ODBC Database source ✅
```python
db = stream.createAt("database", "DB Source", 100, 200)
db.setPropertyValue("datasource", "TELECOM_DB")  # ✅ DSN name
db.setPropertyValue("mode",       "Table")        # ✅ verified
db.setPropertyValue("tablename",  "dbo.customers") # ✅ verified

# Table name format: "dbo.tablename" or "schema.tablename"
# mode options: "Table" ✅ verified
# ⚠️ SQL Query mode value for "mode" property still unverified
```

### select — Filter rows ✅
```python
sel = stream.createAt("select", "Filter", 250, 200)
sel.setPropertyValue("mode", "Include")  # or "Exclude"
sel.setPropertyValue("condition", "not @NULL(CustomerID) and Age > 0")
# With parameters:
sel.setPropertyValue("condition",
    "TimeStamp >= $P-start_date and TimeStamp < $P-end_date")
```

### aggregate — Group and summarise ✅
```python
agg = stream.createAt("aggregate", "Aggregate", 250, 200)
agg.setPropertyValue("keys", ["CardID"])       # MUST be a list
agg.setPropertyValue("inc_record_count", True)
agg.setPropertyValue("count_field", "TxCount")
agg.setKeyedPropertyValue("aggregates", "Amount", ["Sum"])
agg.setKeyedPropertyValue("aggregates", "Amount", ["Mean"])
# Options: "Sum" "Mean" "Min" "Max" "StdDev" "Count"
```

### sort — Sort records ✅
```python
srt = stream.createAt("sort", "Sort", 400, 200)
srt.setPropertyValue("keys", [["Field1", "Descending"],
                               ["Field2", "Ascending"]])
```

### append — Union / stack records ✅
```python
app = stream.createAt("append", "Append", 250, 350)
stream.link(src1, app)
stream.link(src2, app)
```

### merge — Join two streams on key fields ✅
```python
mrg = stream.createAt("merge", "Merge", 500, 200)
mrg.setPropertyValue("method",     "Keys")        # ✅ verified
mrg.setPropertyValue("key_fields", ["CardID"])    # ✅ list, not string

# join options:
# "inner"        — only matching records from both inputs
# "fullOuter"    — all records from both inputs, nulls where no match
# "partialOuter" — ALL records from the PRIMARY (first-linked) input;
#                  only matched records from SECONDARY inputs
mrg.setPropertyValue("join", "partialOuter")

# Link order matters for "partialOuter":
#   stream.link(primary_node, mrg)    ← linked FIRST = primary (all records kept)
#   stream.link(secondary_node, mrg)  ← linked SECOND = secondary (matched only)
```

### type — Set field roles and measurement levels ✅
```python
types = stream.createAt("type", "Types", 250, 200)

# ✅ VERIFIED in 18.5: two separate keyed calls
# "type"      sets the measurement level
# "direction" sets the role
types.setKeyedPropertyValue("type",      "Age",   "continuous")
types.setKeyedPropertyValue("direction", "Age",   "Input")
types.setKeyedPropertyValue("type",      "Churn", "flag")
types.setKeyedPropertyValue("direction", "Churn", "Target")
types.setKeyedPropertyValue("type",      "ID",    "nominal")
types.setKeyedPropertyValue("direction", "ID",    "None")

# Measurement values: "continuous" "nominal" "ordinal" "flag" "typeless"
# Role values:        "Input" "Target" "Both" "None" "Partition" "Split"

# ❌ DOES NOT EXIST in 18.5 — causes AEQMJ0100E:
#   types.setKeyedPropertyValue("types", "Churn", ["flag", "Target"])
# Field names are case-sensitive — must match source exactly
```

### derive — Create new calculated field ✅
```python
drv = stream.createAt("derive", "New Field", 400, 200)
drv.setPropertyValue("new_name",     "OutputField")
drv.setPropertyValue("formula_expr", "Age * 2")
# ❌ NEVER set result_type — does not exist in 18.5
# if/elseif/endif MUST be one line:
drv.setPropertyValue("formula_expr",
    "if Age < 18 then 'Minor' elseif Age < 65 then 'Adult' else 'Senior' endif")
```

### filter — Rename or remove fields ✅
```python
flt = stream.createAt("filter", "Filter Fields", 400, 200)

# Whitelist mode: only named fields pass through
flt.setPropertyValue("default_include", False)
flt.setKeyedPropertyValue("include", "CardID",    True)
flt.setKeyedPropertyValue("include", "Amount",    True)

# Rename a field
flt.setKeyedPropertyValue("new_name", "TimeStamp", "First_Tx_Date")

# Blacklist mode: drop a specific field, keep everything else
flt.setKeyedPropertyValue("include", "CHURN_FLAG", False)
```

### filler — Replace missing values ✅
```python
fil = stream.createAt("filler", "Fill Nulls", 400, 200)
fil.setPropertyValue("fields",       ["Field1", "Field2", "Field3"])
fil.setPropertyValue("replace_mode", "BlankAndNull")  # ✅
fil.setPropertyValue("replace_with", "0")             # ✅
# replace_mode options: "BlankAndNull" "Blanks" "Nulls" "Always" "Condition"
# For condition mode:
# fil.setPropertyValue("replace_mode", "Condition")
# fil.setPropertyValue("condition",    "@BLANK(@FIELD)")
# fil.setPropertyValue("replace_with", "0")
```

### distinct — Remove duplicates / keep first per key ✅
```python
dis = stream.createAt("distinct", "First Tx Distinct", 300, 400)
dis.setPropertyValue("fields",    ["CardID"])                    # key field(s)
dis.setPropertyValue("sort_keys", [["TimeStamp", "Ascending"]])  # order before dedup
dis.setPropertyValue("mode",      "Include")                     # keep first record
# Pair with a filter node to rename the retained sort key field
```

### partition — Split data into training / testing partitions ⚠️ PROPERTIES UNVERIFIED
```python
# Node type string "partition" is correct — node creates fine.
# Property names for setting the split % are UNVERIFIED in 18.5.
# Confirmed WRONG (AEQMJ0100E — property undefined):
#   ❌ part.setPropertyValue("training_partition", 70)

# Candidates still to test — try one at a time:
#   part.setPropertyValue("training_size",    70)   # ⚠️ try first
#   part.setPropertyValue("testing_size",     30)
#   part.setPropertyValue("validation_size",  0)
#
#   part.setPropertyValue("size_1",  70)            # ⚠️ try second
#   part.setPropertyValue("size_2",  30)
#   part.setPropertyValue("size_3",  0)
#
#   part.setPropertyValue("train_percent", 70)      # ⚠️ try third
#   part.setPropertyValue("test_percent",  30)

# ── VERIFIED WORKAROUND — derive-based 70/30 partition ✅ ──────────────────
# Uses verified Derive node. Produces identical field values to the real Partition node.
# mod(@INDEX + 9, 10) < 7  →  first 7 of every 10 records = "1_Training" (70%)
#                              last  3 of every 10 records = "2_Testing"  (30%)
# Deterministic: same split every run, no seed needed.
drv_part = stream.createAt("derive", "Partition", 1200, 300)
drv_part.setPropertyValue("new_name",     "Partition")
drv_part.setPropertyValue("formula_expr",
    "if mod(@INDEX + 9, 10) < 7 then '1_Training' else '2_Testing' endif")

# Downstream select nodes — same as with the real Partition node:
#   sel_train: condition = 'Partition = "1_Training"'
#   sel_test:  condition = 'Partition = "2_Testing"'
```

### balance — Oversample / undersample records ✅ (type string only)
```python
bal = stream.createAt("balance", "Balance", 1500, 300)
# Properties UNVERIFIED — default behaviour balances based on target field
# Place between sel_train and model builder; never apply to test partition
```

### kmeans — K-Means clustering ✅
```python
km = stream.createAt("kmeans", "KMeans", 500, 200)
km.setPropertyValue("num_clusters", 3)
# Nugget type string: "kmeansmodel"
# Find after run: loop getNodes(), check getTypeName() == "kmeansmodel"
```

### twostep — TwoStep clustering ✅ (type string only)
```python
ts = stream.createAt("twostep", "TwoStep", 500, 200)
# ⚠️ Properties UNVERIFIED — test before use
```

### chaid — CHAID decision tree ✅ (type string only)
```python
ch = stream.createAt("chaid", "CHAID", 500, 200)
# Nugget type string: "chaidmodel"
# Find after run: loop getNodes(), check getTypeName() == "chaidmodel"
# ⚠️ Builder properties (max depth, alpha etc.) UNVERIFIED — set in GUI
```

### c50 — C5.0 decision tree ✅ (type string only)
```python
c5 = stream.createAt("c50", "C5.0", 500, 200)
# ⚠️ Properties UNVERIFIED — test before use
```

### evaluation — Gains chart / lift chart output ✅
```python
ev = stream.createAt("evaluation", "Gains Chart", 1800, 500)
# No required properties for default gains chart
# IMPORTANT: connect nugget → evaluation, NOT builder → evaluation
# The nugget must have an upstream data source (scored records) before ev.run([])
# Correct topology:  part → sel_test → nugget → ev
# Wrong topology:    nugget → ev  (no upstream = nothing to score)
```

### table — Table output ✅
```python
tbl = stream.createAt("table", "View Data", 700, 200)
# No required properties for basic screen output
```

---

## STREAM PARAMETERS ✅

```python
# Set parameters (verified)
stream.setParameterValue("start_date", "2024-12-01")
stream.setParameterValue("end_date",   "2025-01-01")
stream.setParameterValue("month_1",    202412)
stream.setParameterValue("month_3",    202410)
stream.setParameterValue("month_6",    202407)

# Use in CLEM with $P- prefix — wrap in single quotes in conditions
sel.setPropertyValue("condition",
    "not(@NULL(CardID)) and Amount > '$P-min_amount'")

# ⚠️ getParameterValue() not yet tested
```

---

## ADDITIONAL VERIFIED RULES ✅

| Rule | Detail |
|------|--------|
| `db.setPropertyValue("tablename", "dbo.customers")` | ✅ Correct table property name |
| `db.setPropertyValue("tablename", "dbo.tablename")` | Format: schema.tablename |
| Close all node dialogs before running script | node.delete() fails if any dialog is open |
| `not(@NULL(Field))` | ✅ not() needs brackets in CLEM |
| `'$P-param_name'` in conditions | ✅ wrap parameter in single quotes |

---

## LAYOUT CONVENTION

```
x=100  Source
x=250  Step 1
x=400  Step 2
x=550  Step 3
x=700  Output

y=200  Main branch
y=100  Branch up
y=350  Branch down
```
Increment x by 150 per node.
