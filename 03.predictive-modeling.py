# STREAM 03 — Mobile Churn Prediction
# Source:  ODBC — TELECOM_DB / PREDICTA\plagios.DATA_TELCO
# Product: MOBILE
# Target:  CHURN_FLAG (Active | Churn)
# Method:  Two-window approach:
#          Observation : DATE = 2024-09-01  (active customers — Branch A)
#          Churn label : DATE = 2024-11-01 or 2024-12-01 — Branch B
#          Merge on asset_id → labelled training set
# Models:  CHAID → CHAID nugget → Evaluation (gains chart)
#
# Canvas layout:
#   y=200  Branch A (observation month)
#   y=300  Main pipeline (merge → type → partition → training → balance → CHAID)
#   y=400  Branch B (churn window)
#   y=500  Evaluation path (test partition → nugget → gains chart)
#
# FIXES APPLIED vs previous versions:
#   FIX 1 — merge property key_fields verified (consistent with 01/02)
#   FIX 2 — merge join set to "partialOuter"; Branch A linked first = primary
#   FIX 3 — CHAID nugget found via getTypeName() loop (not getLabel)
#   FIX 4 — Partition node explicitly configured: training=70 / testing=30 / validation=0
#            Previously created with no properties — Modeler silently defaulted to 50/50
#   FIX 5 — Evaluation path: create ev AFTER builder runs and nugget is found,
#            then link nugget → ev and run ev. Same pattern as 02 segmentation
#            (nugget → agg nodes created post-run). Pre-creating ev fails silently.
#
# *** BEFORE RUNNING: verify DSN name and table name match your environment ***

import modeler.api

stream = modeler.script.stream()

for node in list(stream.getNodes()):
    node.delete()

# Stream parameters — update dates per modeling run
stream.setParameterValue("obs_date",    "2024-09-01")
stream.setParameterValue("churn_date1", "2024-11-01")
stream.setParameterValue("churn_date2", "2024-12-01")

# BRANCH A — OBSERVATION MONTH (y=200)
# All active customers at obs_date — this is the PRIMARY input to the merge
src_a = stream.createAt("database", "DATA_TELCO Sep", 100, 200)
src_a.setPropertyValue("datasource", "TELECOM_DB")
src_a.setPropertyValue("mode",       "Table")
src_a.setPropertyValue("tablename",  "PREDICTA\\plagios.DATA_TELCO")

sel_obs = stream.createAt("select", "Period", 200, 200)
sel_obs.setPropertyValue("mode",      "Include")
sel_obs.setPropertyValue("condition", "DATE = to_date('$P-obs_date')")

sel_mob_a = stream.createAt("select", "Mobile", 300, 200)
sel_mob_a.setPropertyValue("mode",      "Include")
sel_mob_a.setPropertyValue("condition", 'descr_pr = "MOBILE"')

sel_active = stream.createAt("select", "Active", 400, 200)
sel_active.setPropertyValue("mode",      "Include")
sel_active.setPropertyValue("condition", 'CHURN_FLAG = "Active"')

# Drop CHURN_FLAG from Branch A before merge.
# Branch B provides the definitive CHURN_FLAG label after the join.
# Non-churners will have null CHURN_FLAG post-merge — filled with "Active" by filler node.
flt_drop_churn = stream.createAt("filter", "Drop Churn Flag", 500, 200)
flt_drop_churn.setKeyedPropertyValue("include", "CHURN_FLAG", False)

# BRANCH B — CHURN WINDOW (y=400)
# Only confirmed churners from the 2-month churn window — this is the SECONDARY input
src_b = stream.createAt("database", "DATA_TELCO NovDec", 100, 400)
src_b.setPropertyValue("datasource", "TELECOM_DB")
src_b.setPropertyValue("mode",       "Table")
src_b.setPropertyValue("tablename",  "PREDICTA\\plagios.DATA_TELCO")

sel_churn_period = stream.createAt("select", "2M Period", 200, 400)
sel_churn_period.setPropertyValue("mode",      "Include")
sel_churn_period.setPropertyValue("condition",
    "DATE = to_date('$P-churn_date1') or DATE = to_date('$P-churn_date2')")

sel_mob_b = stream.createAt("select", "Mobile", 300, 400)
sel_mob_b.setPropertyValue("mode",      "Include")
sel_mob_b.setPropertyValue("condition", 'descr_pr = "MOBILE"')

# Discard Active — keep only confirmed churners in Branch B
sel_churn = stream.createAt("select", "Churn", 400, 400)
sel_churn.setPropertyValue("mode",      "Discard")
sel_churn.setPropertyValue("condition", 'CHURN_FLAG = "Active"')

# Keep only asset_id + CHURN_FLAG from churn branch — the label we are joining in
flt_b = stream.createAt("filter", "Churn Label Only", 500, 400)
flt_b.setPropertyValue("default_include", False)
flt_b.setKeyedPropertyValue("include", "asset_id",   True)
flt_b.setKeyedPropertyValue("include", "CHURN_FLAG", True)

# MERGE — partial outer join on asset_id
# join_type = "partialOuter":
#   Branch A (primary, linked first) — ALL active customers are kept
#   Branch B (secondary, linked second) — CHURN_FLAG joined where asset_id matches
#   Customers not in Branch B (non-churners) get null CHURN_FLAG → filled downstream
# Use inner join only when both inputs are expected to have full overlap.
# Use partialOuter when the secondary is a subset (e.g. event table, churn window).
merge_label = stream.createAt("merge", "Add Churn Label", 600, 300)
merge_label.setPropertyValue("method",    "Keys")
merge_label.setPropertyValue("key_fields",      ["asset_id"])
merge_label.setPropertyValue("join", "partialOuter")

# FILLER — fill null CHURN_FLAG (non-churners have null after merge) with "Active"
fil = stream.createAt("filler", "Fill Churn Nulls", 750, 300)
fil.setPropertyValue("fields",       ["CHURN_FLAG"])
fil.setPropertyValue("replace_mode", "BlankAndNull")
fil.setPropertyValue("replace_with", "'Active'")

# FILTER — select model input fields
flt_fields = stream.createAt("filter", "Model Fields", 900, 300)
flt_fields.setPropertyValue("default_include", False)
flt_fields.setKeyedPropertyValue("include", "CHURN_FLAG",             True)
flt_fields.setKeyedPropertyValue("include", "AGE",                    True)
flt_fields.setKeyedPropertyValue("include", "gender",                 True)
flt_fields.setKeyedPropertyValue("include", "region_id",              True)
flt_fields.setKeyedPropertyValue("include", "TENURE",                 True)
flt_fields.setKeyedPropertyValue("include", "CONTRACT_TENURE",        True)
flt_fields.setKeyedPropertyValue("include", "MONTHS_CONTRACT_ENDS",   True)
flt_fields.setKeyedPropertyValue("include", "CONTRACT_GROUP",         True)
flt_fields.setKeyedPropertyValue("include", "CUSTOMER_PRODUCTS",      True)
flt_fields.setKeyedPropertyValue("include", "AVG_OUT_MIN",            True)
flt_fields.setKeyedPropertyValue("include", "AVG_OUT_CALL",           True)
flt_fields.setKeyedPropertyValue("include", "AVG_Data Usage",         True)
flt_fields.setKeyedPropertyValue("include", "AVG_SMS",                True)
flt_fields.setKeyedPropertyValue("include", "AVG_International_min",  True)
flt_fields.setKeyedPropertyValue("include", "AVG_Roaming_min",        True)
flt_fields.setKeyedPropertyValue("include", "AVG_OUT_MIN_3M",         True)
flt_fields.setKeyedPropertyValue("include", "AVG_OUT_CALL_3M",        True)
flt_fields.setKeyedPropertyValue("include", "AVG_Data Usage_3M",      True)
flt_fields.setKeyedPropertyValue("include", "AVG_SMS_3M",             True)
flt_fields.setKeyedPropertyValue("include", "Months_Usage_3M",        True)
flt_fields.setKeyedPropertyValue("include", "DIFF_MIN",               True)
flt_fields.setKeyedPropertyValue("include", "DIFF_CALL",              True)
flt_fields.setKeyedPropertyValue("include", "DIFF_IN_MIN",            True)
flt_fields.setKeyedPropertyValue("include", "DIFF_DATA_USAGE",        True)
flt_fields.setKeyedPropertyValue("include", "DIFF_SMS",               True)
flt_fields.setKeyedPropertyValue("include", "TOTAL_PROBLEMS",         True)
flt_fields.setKeyedPropertyValue("include", "AVG_TOTAL_PROBLEMS",     True)
flt_fields.setKeyedPropertyValue("include", "Months_Problems",        True)
flt_fields.setKeyedPropertyValue("include", "MOVEMENT_FLAG",          True)
flt_fields.setKeyedPropertyValue("include", "Downgrade",              True)
flt_fields.setKeyedPropertyValue("include", "port_in",                True)

# TYPE — set CHURN_FLAG as Target
# ✅ VERIFIED API in 18.5: two separate keyed calls for "type" and "direction"
# ❌ "types" with a list does NOT exist in 18.5 (AEQMJ0100E on line 148)
type_node = stream.createAt("type", "Set Roles", 1050, 300)
type_node.setKeyedPropertyValue("type",      "CHURN_FLAG", "Flag")
type_node.setKeyedPropertyValue("direction", "CHURN_FLAG", "Target")

# PARTITION — 70% training / 30% testing / 0% validation
# ✅ VERIFIED property names (test_partition_properties.py):
#   training_size / testing_size / validation_size / random_seed
part = stream.createAt("partition", "Partition 70-30", 1200, 300)
part.setPropertyValue("training_size",   70)
part.setPropertyValue("testing_size",    30)
part.setPropertyValue("validation_size", 0)
part.setPropertyValue("random_seed",     12345)

sel_train = stream.createAt("select", "Training Only", 1350, 300)
sel_train.setPropertyValue("mode",      "Include")
sel_train.setPropertyValue("condition", 'Partition = "1_Training"')

bal = stream.createAt("balance", "Balance", 1500, 300)

# CHAID MODEL
chaid_node = stream.createAt("chaid", "CHAID Model", 1650, 300)

# LINKS
# ---------------------------------------------------------------
# Branch B: source → period filter → mobile → churn only → label filter
stream.link(src_b,            sel_churn_period)
stream.link(sel_churn_period, sel_mob_b)
stream.link(sel_mob_b,        sel_churn)
stream.link(sel_churn,        flt_b)

# Branch A: source → period → mobile → active → drop CHURN_FLAG → merge (PRIMARY input)
# Chain confirmed: sel_active → flt_drop_churn → merge_label
stream.link(src_a,          sel_obs)
stream.link(sel_obs,        sel_mob_a)
stream.link(sel_mob_a,      sel_active)
stream.link(sel_active,     flt_drop_churn)
stream.link(flt_drop_churn, merge_label)

# Branch B into merge AFTER Branch A — makes Branch A the primary in partialOuter join
stream.link(flt_b, merge_label)

# Main pipeline: merge → fill nulls → field filter → type → partition
stream.link(merge_label, fil)
stream.link(fil,         flt_fields)
stream.link(flt_fields,  type_node)
stream.link(type_node,   part)

# Training path: partition → training select → balance → CHAID builder
stream.link(part,      sel_train)
stream.link(sel_train, bal)
stream.link(bal,       chaid_node)

# RUN model builder — nugget is auto-created and auto-wired to bal (training upstream)
chaid_node.run([])

# FIND CHAID NUGGET — same pattern as 02 segmentation file: loop getNodes(), match typeName
chaid_nugget = None
for node in stream.getNodes():
    if node.getTypeName() == "chaidmodel":
        chaid_nugget = node
        break

if chaid_nugget is None:
    raise RuntimeError("chaidmodel nugget not found — check CHAID built successfully")

# Create output nodes AFTER nugget exists — same pattern as segmentation file
# (nugget → agg_cluster / agg_total). Pre-creating and linking later fails silently.
ev = stream.createAt("evaluation", "Gains Chart", 1800, 500)

chaid_nugget.setLocation(1650, 500)
stream.link(chaid_nugget, ev)
ev.run([])
