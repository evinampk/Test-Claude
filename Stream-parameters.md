# Stream Parameters — SPSS Modeler 18.5
# How to define, set, and use stream parameters in scripts and CLEM expressions.
# All entries marked VERIFIED or UNVERIFIED based on live testing.

---

## WHAT ARE STREAM PARAMETERS?

Stream parameters are named variables stored at the stream level.
They can be:
- Set via script before running
- Referenced inside CLEM expressions using $P-parametername
- Used across multiple nodes without hardcoding values
- Defined with a type: timestamp, integer, string

Common use case: date windows for filtering transactions
  start_date = '2024-12-01'
  end_date   = '2025-01-01'
  month_1    = 202412
  month_3    = 202410
  month_6    = 202407

---

## DEFINING PARAMETERS VIA SCRIPT — VERIFIED ✅

```python
# CORRECT — confirmed working in 18.5
stream.setParameterValue("start_date", "2024-12-01")
stream.setParameterValue("end_date",   "2025-01-01")
stream.setParameterValue("month_1",    202412)
stream.setParameterValue("month_3",    202410)
stream.setParameterValue("month_6",    202407)
```

> Parameters appear immediately in stream's Parameters tab with correct values.
> Storage type shows "Unknown" when set this way — type declaration via script UNVERIFIED.

---

## READING PARAMETERS VIA SCRIPT — UNVERIFIED ⚠️

```python
# NOT YET TESTED — verify before using
val = stream.getParameterValue("start_date")  # ? unverified
```

> TODO: Test getParameterValue() in live Modeler session

---

## USING PARAMETERS IN CLEM EXPRESSIONS — VERIFIED SYNTAX ✅

Once a parameter is defined, reference it in CLEM with $P- prefix:

```clem
# In a select condition:
TimeStamp >= $P-start_date and TimeStamp < $P-end_date

# In a derive formula:
if datetime_month(TimeStamp) = $P-month_1 then 1 else 0 endif

# In a filter condition:
PMonth = $P-month_1
```

```python
# Example: select node using date parameter
sel = stream.createAt("select", "Date Window", 250, 200)
sel.setPropertyValue("mode", "Include")
sel.setPropertyValue("condition",
    "TimeStamp >= $P-start_date and TimeStamp < $P-end_date")

# Example: derive node using month parameter
drv = stream.createAt("derive", "Flag Month 1", 400, 200)
drv.setPropertyValue("new_name", "Flag_Month1")
drv.setPropertyValue("formula_expr",
    "if datetime_month(TimeStamp) = $P-month_1 then 1 else 0 endif")
```

---

## PARAMETER TYPES

| Type | Modeler Storage | Example Value |
|------|----------------|---------------|
| Date/Timestamp | `timestamp` | `"2024-12-01"` |
| Integer | `integer` | `202412` |
| String | `string` | `"Active"` |
| Real | `real` | `1.5` |

---

## VERIFIED WORKING ✅
- $P-parametername syntax in CLEM expressions ✅
- Parameters survive stream save/reload ✅

## UNVERIFIED ⚠️
- setParameterValue() method name — test before use
- getParameterValue() method name — test before use
- Parameter type declaration via script — test before use
