# Merge & Append Nodes — SPSS Modeler 18.5
# Properties extracted from real production preparation.str
# ✅ = confirmed  ⚠️ = unverified

---

## MERGE NODE — Join two or more streams on a key

### Key concepts
- Merge requires at least 2 input streams linked to it
- Always create merge node AFTER all input nodes
- Links must go: input1 → merge, input2 → merge
- joinType controls what records are kept

### Basic inner join (most common)
```python
mrg = stream.createAt("merge", "Merge Data", 550, 200)
mrg.setPropertyValue("method",  "Keys")       # join by key fields
mrg.setPropertyValue("keys",    ["CustomerID"])  # must match in both inputs
# joinType default is inner — only matching records kept

# Link both inputs into merge:
stream.link(src1, mrg)
stream.link(src2, mrg)
```

### Join types — from preparation.str XML ✅
```python
# Inner join — only records matching in BOTH inputs
mrg.setPropertyValue("join_type", "inner")        # ✅ from XML

# Partial outer (left join) — all from primary + matches from secondary
mrg.setPropertyValue("join_type", "partialOuter") # ✅ from XML

# Full outer — all records from all inputs
mrg.setPropertyValue("join_type", "fullOuter")    # ⚠️ unverified
```

### Include incomplete records
```python
mrg.setPropertyValue("include_incomplete", True)   # ⚠️ unverified name
```

### Rename duplicate fields
```python
mrg.setPropertyValue("rename_duplicates", True)    # ⚠️ unverified name
```

### WARNING: merge node type string
```python
# ⚠️ "merge" type string NOT yet verified in live test
# Test before using in production
mrg = stream.createAt("merge", "Merge", 550, 200)
```

---

## APPEND NODE — Stack / union two streams ✅

### Verified working
```python
app = stream.createAt("append", "Append", 250, 350)
# Link multiple sources:
stream.link(src1, app)
stream.link(src2, app)
# No required properties for basic append
```

### Match by field name (default)
```python
app.setPropertyValue("match_type", "Name")     # ⚠️ unverified property name
```

### Match by position
```python
app.setPropertyValue("match_type", "Position") # ⚠️ unverified property name
```

---

## COMMON MERGE PATTERNS

### Pattern 1 — Enrich customer data (inner join)
```
customers table → 
                  → merge(CustomerID) → enriched output
transactions agg →
```
```python
# Source 1: customer master
db1 = stream.createAt("database", "Customers", 100, 200)
db1.setPropertyValue("datasource", "TELECOM_DB")
db1.setPropertyValue("mode", "Table")

# Source 2: aggregated transactions
db2 = stream.createAt("database", "Tx Summary", 100, 350)
db2.setPropertyValue("datasource", "TELECOM_DB")
db2.setPropertyValue("mode", "Table")

# Merge on customer key
mrg = stream.createAt("merge", "Enrich Customers", 400, 275)
mrg.setPropertyValue("method", "Keys")
mrg.setPropertyValue("keys",   ["CustomerID"])

stream.link(db1, mrg)
stream.link(db2, mrg)
```

### Pattern 2 — Stack two periods (append)
```
Period 1 data →
               → append → combined output
Period 2 data →
```
```python
src1 = stream.createAt("variablefile", "Period 1", 100, 200)
src1.setPropertyValue("full_filename", "C:/data/period1.txt")
src1.setPropertyValue("read_field_names", True)
src1.setPropertyValue("delimit_comma", True)

src2 = stream.createAt("variablefile", "Period 2", 100, 350)
src2.setPropertyValue("full_filename", "C:/data/period2.txt")
src2.setPropertyValue("read_field_names", True)
src2.setPropertyValue("delimit_comma", True)

app = stream.createAt("append", "Combined", 300, 275)

stream.link(src1, app)
stream.link(src2, app)
```

### Pattern 3 — Lookup join (partial outer / left join)
```
All customers (primary) →
                          → merge(partialOuter) → all customers + matches
Complains table →
```
```python
mrg = stream.createAt("merge", "Customer+Complaints", 550, 275)
mrg.setPropertyValue("method",    "Keys")
mrg.setPropertyValue("keys",      ["CustomerID"])
mrg.setPropertyValue("join_type", "partialOuter")

stream.link(customers, mrg)   # primary — all records kept
stream.link(complaints, mrg)  # secondary — only matching records joined
```

---

## LAYOUT FOR MULTI-INPUT NODES

```
src1  x=100, y=200  (upper branch)
src2  x=100, y=350  (lower branch)
merge x=400, y=275  (centre between branches)
next  x=550, y=275  (continues from merge)

For 3 inputs:
src1  y=100
src2  y=250
src3  y=400
merge y=250  (middle)
```

---

## UNVERIFIED — Must Test ⚠️

| Property | Status |
|----------|--------|
| `"merge"` type string | ⚠️ Not live tested yet |
| `join_type` property name | ⚠️ From XML — test in script |
| `include_incomplete` property name | ⚠️ Not tested |
| `rename_duplicates` property name | ⚠️ Not tested |
| `match_type` on append | ⚠️ Not tested |

---

## TEST SCRIPT — Run to verify merge node string

```python
import modeler.api
stream = modeler.script.stream()

for node in list(stream.getNodes()):
    node.delete()

src1 = stream.createAt("variablefile", "Source 1", 100, 200)
src1.setPropertyValue("full_filename", "C:/path/to/file.txt")
src1.setPropertyValue("read_field_names", True)
src1.setPropertyValue("delimit_comma", True)

src2 = stream.createAt("variablefile", "Source 2", 100, 350)
src2.setPropertyValue("full_filename", "C:/path/to/file.txt")
src2.setPropertyValue("read_field_names", True)
src2.setPropertyValue("delimit_comma", True)

mrg = stream.createAt("merge", "Test Merge", 300, 275)
mrg.setPropertyValue("method", "Keys")
mrg.setPropertyValue("keys",   ["CardID"])

tbl = stream.createAt("table", "Merged Output", 450, 275)

stream.link(src1, mrg)
stream.link(src2, mrg)
stream.link(mrg,  tbl)
```
