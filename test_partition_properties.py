# TEST — Discover Partition node property names in Modeler 18.5
#
# PURPOSE:
#   Find the correct property names for setting the training/testing split %
#   on the Partition node via Python scripting.
#
# HOW TO RUN:
#   1. Open a NEW empty stream in Modeler (or run on the current one — the
#      test node is deleted at the end)
#   2. Run this script from the Scripting console
#   3. Check the Messages tab for the results
#   4. Report which lines show OK and what value they return
#
# WHAT IT DOES:
#   - Creates a fresh Partition node
#   - Attempts getPropertyValue() for each candidate name
#   - Prints OK + value for properties that exist
#   - Prints FAIL for properties that do not exist
#   - Deletes the test node when done
#
# NOTE — Jython exception handling:
#   Modeler raises Java exceptions (AEQMJ0100E) for unknown properties.
#   Java exceptions are NOT caught by "except Exception" in Jython.
#   Must use bare "except:" to catch them.

import modeler.api

stream = modeler.script.stream()

# Create a clean test partition node
part = stream.createAt("partition", "TEST_PARTITION", 50, 50)

# ── Candidate property names to probe ────────────────────────────────────────
# Grouped by naming convention so patterns are easy to spot in the results.

candidates = [
    # Confirmed WRONG
    "training_partition",       # ❌ AEQMJ0100E confirmed
    "testing_partition",        # ❌ AEQMJ0100E confirmed
    "validation_partition",     # ❌ AEQMJ0100E confirmed

    # Convention: _size suffix
    "training_size",
    "testing_size",
    "validation_size",

    # Convention: numbered slots
    "size_1",
    "size_2",
    "size_3",

    # Convention: _percent suffix
    "train_percent",
    "test_percent",
    "validation_percent",
    "training_percent",
    "testing_percent",

    # Convention: plain names
    "training",
    "testing",
    "validation",

    # Convention: partition_ prefix
    "partition_training_size",
    "partition_testing_size",
    "partition_validation_size",

    # Convention: _fraction suffix
    "training_fraction",
    "testing_fraction",

    # Sampling / seed properties (likely to exist)
    "sampling_method",
    "method",
    "set_seed",
    "seed",
    "random_seed",
]

# ── Probe each candidate ──────────────────────────────────────────────────────
print("=" * 55)
print("Partition node property discovery")
print("=" * 55)

for prop in candidates:
    try:
        val = part.getPropertyValue(prop)
        print("OK   " + prop + " = " + str(val))
    except:
        print("FAIL " + prop)

print("=" * 55)
print("Done. Copy these results and report back.")
print("=" * 55)

# Clean up test node
part.delete()
