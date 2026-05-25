# CLEM Expressions Reference — SPSS Modeler 18.5
# Based on real usage in telecom preparation and segmentation streams.
# VERIFIED = confirmed working. UNVERIFIED = not yet tested.

---

## CRITICAL SYNTAX RULES — READ FIRST

| Rule | Wrong | Correct |
|------|-------|---------|
| if/elseif must be ONE line | multiline string | `"if X then A elseif Y then B else C endif"` |
| Not equal | `!=` | `/=` |
| String values | `"Active"` | `'Active'` |
| Null check | `Field == null` | `@NULL(Field)` |
| Blank check | `Field == ""` | `@BLANK(Field)` |
| String concat | `+` | `><` |
| Parameters | `start_date` | `$P-start_date` |

---

## FILLER NODE — VERIFIED PATTERN ✅

### Replace blanks and nulls with 0 (most common usage)
```python
fil = stream.createAt("filler", "Fill Nulls", 400, 200)
fil.setPropertyValue("fields",        ["PRC_International_min",
                                       "PRC_Off_Net_min",
                                       "PRC_On_Net_min",
                                       "PRC_Roaming_min"])
fil.setPropertyValue("replace_mode",  "BlankAndNull")
fil.setPropertyValue("replace_with",  "0")
```

### replace_mode options (all verified)
```python
fil.setPropertyValue("replace_mode", "BlankAndNull")  # blanks AND nulls ✅
fil.setPropertyValue("replace_mode", "Blanks")        # blanks only
fil.setPropertyValue("replace_mode", "Nulls")         # nulls only
fil.setPropertyValue("replace_mode", "Always")        # always replace
fil.setPropertyValue("replace_mode", "Condition")     # based on condition
```

### replace_with options
```python
fil.setPropertyValue("replace_with", "0")             # replace with zero
fil.setPropertyValue("replace_with", "0.0")           # replace with 0.0
fil.setPropertyValue("replace_with", "'Unknown'")     # replace with string
fil.setPropertyValue("replace_with", "@GLOBAL_MEAN")  # replace with mean
fil.setPropertyValue("replace_with", "undef")         # replace with null
```

### When using Condition mode — add condition property
```python
fil.setPropertyValue("replace_mode",  "Condition")
fil.setPropertyValue("condition",     "@BLANK(@FIELD)")
fil.setPropertyValue("replace_with",  "0")
```

> @FIELD refers to the current field being processed — only valid inside filler nodes

---

## SELECT NODE — CONDITIONS ✅

### Date window using parameters
```python
sel.setPropertyValue("condition",
    "TimeStamp >= $P-start_date and TimeStamp < $P-end_date")
```

### Exclude inactive records
```python
sel.setPropertyValue("condition", "ACTIVE_FLAG /= 0")
# OR:
sel.setPropertyValue("condition", "ACTIVE_FLAG = 1")
```

### Remove nulls on key field
```python
sel.setPropertyValue("condition", "not @NULL(CustomerID)")
```

### Multiple conditions
```python
sel.setPropertyValue("condition",
    "not @NULL(CustomerID) and ACTIVE_FLAG = 1 and Age > 0")
```

### Telecom threshold filter
```python
sel.setPropertyValue("condition",
    "Out_Call_min_3m > 0 or SMS_AVG_6 > 0")
```

---

## DERIVE NODE — FORMULAS ✅

> WARNING: Never set result_type on derive — not supported in 18.5

### Age band (confirmed from preparation stream)
```python
drv.setPropertyValue("new_name", "Age_Band")
drv.setPropertyValue("formula_expr",
    "if Age < 30 then 'Under 30' elseif Age < 45 then '30-44' elseif Age < 60 then '45-59' else '60+' endif")
```

### Month flag using parameter
```python
drv.setPropertyValue("new_name", "Flag_Month1")
drv.setPropertyValue("formula_expr",
    "if datetime_month(TimeStamp) = $P-month_1 then 1 else 0 endif")
```

### Binary activity flag
```python
drv.setPropertyValue("new_name", "Has_OutCalls")
drv.setPropertyValue("formula_expr",
    "if Out_Call_min_3m > 0 then 1 else 0 endif")
```

### Gender label
```python
drv.setPropertyValue("new_name", "Gender_Label")
drv.setPropertyValue("formula_expr",
    "if Gender = 'MALE' then 'Male' elseif Gender = 'FEMALE' then 'Female' else 'Unknown' endif")
```

### Segment label from numeric code
```python
drv.setPropertyValue("new_name", "Segment_Label")
drv.setPropertyValue("formula_expr",
    "if Segment = 1 then 'High Value' elseif Segment = 2 then 'Mid Value' else 'Low Value' endif")
```

### Telecom usage band
```python
drv.setPropertyValue("new_name", "Usage_Band")
drv.setPropertyValue("formula_expr",
    "if Out_Call_min_3m <= 400 then 'Low' elseif Out_Call_min_3m <= 800 then 'Mid' else 'High' endif")
```

### Month period string
```python
drv.setPropertyValue("new_name", "PMonth")
drv.setPropertyValue("formula_expr",
    "datetime_year(TimeStamp) * 100 + datetime_month(TimeStamp)")
```

### Days since last activity
```python
drv.setPropertyValue("new_name", "Days_Since_Tx")
drv.setPropertyValue("formula_expr",
    "date_days_difference(LastTxDate, today())")
```

---

## DATE & TIME FUNCTIONS ✅

```python
# Extract parts from a date/timestamp field
datetime_year(DateField)        # 2024
datetime_month(DateField)       # 1-12
datetime_day(DateField)         # 1-31
datetime_hour(DateField)        # 0-23
datetime_minute(DateField)      # 0-59

# Date comparison
date_days_difference(Date1, Date2)   # integer days between
date_before(Date1, Date2)            # boolean
date_after(Date1, Date2)             # boolean

# Today
today()                              # current date
```

---

## NULL & BLANK FUNCTIONS ✅

```python
@NULL(Field)         # true if field is null
@BLANK(Field)        # true if field is blank or null
@FIELD               # current field (use inside filler only)
undef                # represents null/missing value
```

---

## ARITHMETIC & NUMERIC ✅

```python
Field * 2
Field / 12
Field1 + Field2
Field1 - Field2
abs(Field)           # absolute value
round(Field, 2)      # round to 2 decimals
int(Field)           # truncate to integer
sqrt(Field)          # square root
log(Field)           # natural log — field must be > 0
mod(Field, 100)      # modulo
```

---

## STRING FUNCTIONS ✅

```python
upcase(Field)                    # UPPERCASE
lowcase(Field)                   # lowercase
length(Field)                    # string length
trim(Field)                      # remove leading/trailing spaces
hassubstr(Field, 'text')         # true if contains substring
Field1 >< ' ' >< Field2          # concatenate strings with space
```

---

## LOGICAL OPERATORS ✅

```python
# AND / OR / NOT
Age > 18 and Income > 30000
Age < 18 or Status = 'Minor'
not @NULL(CustomerID)
not (ACTIVE_FLAG = 0)

# Comparisons
Field = 'Value'       # equals
Field /= 'Value'      # not equal (NOT !=)
Field > 100
Field >= 100
Field < 100
Field <= 100
```

---

## AGGREGATE FUNCTIONS (inside aggregate node) ✅

```python
# In setKeyedPropertyValue("aggregates", "FIELDNAME", [func])
["Sum"]      # total
["Mean"]     # average
["Min"]      # minimum
["Max"]      # maximum
["StdDev"]   # standard deviation
["Count"]    # count of non-null values
```

---

## PARAMETERS IN CLEM ✅

```python
# Reference stream parameters with $P- prefix
# IMPORTANT: wrap in single quotes inside conditions

# In select condition — quotes required ✅
sel.setPropertyValue("condition",
    "not(@NULL(CardID)) and Amount > '$P-min_amount'")

# In derive formula — quotes required ✅
drv.setPropertyValue("formula_expr",
    "if PMonth = '$P-month_1' then 1 else 0 endif")

# not() needs brackets in CLEM ✅
sel.setPropertyValue("condition", "not(@NULL(CardID))")

# Common parameter names used in telecom streams:
# $P-start_date   $P-end_date
# $P-month_1      $P-month_3      $P-month_6
# $P-min_amount
```

---

## COMMON PITFALLS ⚠️

| Mistake | Result | Fix |
|---------|--------|-----|
| `if X then\nY endif` | ClemParseException | One line only |
| `Field != 'x'` | Parse error | Use `Field /= 'x'` |
| `"string value"` | Parse error | Use `'string value'` |
| `Field = null` | Parse error | Use `@NULL(Field)` |
| `Field + ' text'` | Type error | Use `Field >< ' text'` |
| `log(0)` | Error | Guard: `if Field > 0 then log(Field) else 0 endif` |
| `result_type` on derive | Property error | Omit entirely |
| `not @NULL(Field)` | Wrong number of arguments | Use `not(@NULL(Field))` |
| `Amount > $P-min_amount` | CLEM parse error | Use `Amount > '$P-min_amount'` |
