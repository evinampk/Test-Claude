"""
SPSS Modeler Stream Builder
Builds a predictive model stream with a 70/30 partition,
trains a model, and wires it to an Analysis (evaluation) node.

Usage:
    python run_stream.py --data path/to/data.csv --target target_field
"""

import sys

try:
    import modeler.api as modeler
except ImportError:
    modeler = None  # allow unit-testing outside Modeler runtime


# ---------------------------------------------------------------------------
# Node layout constants (canvas coordinates)
# ---------------------------------------------------------------------------
_X = {
    "source":    50,
    "type":     200,
    "partition": 370,
    "builder":   540,
    "nugget":    710,
    "analysis":  880,
}
_Y = 150


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_source_node(stream, data_path: str):
    """Create the correct source node based on file extension."""
    ext = data_path.lower().rsplit(".", 1)[-1]

    if ext == "sav":
        node = stream.createAt("statisticsfile", "Source", _X["source"], _Y)
        node.setPropertyValue("full_filename", data_path)
    elif ext in ("xlsx", "xls"):
        node = stream.createAt("excel", "Source", _X["source"], _Y)
        node.setPropertyValue("full_filename", data_path)
    else:
        # Default: delimited text / CSV
        node = stream.createAt("variablefile", "Source", _X["source"], _Y)
        node.setPropertyValue("full_filename", data_path)
        node.setPropertyValue("field_names_on_first_line", True)
        node.setPropertyValue("delimiters", ",")

    return node


def _configure_partition_node(stream):
    """
    Create and configure a Partition node for a 70 / 30 train-test split.

    Fix applied: training_partition + testing_partition must sum to 100
    and validation_partition must be set explicitly to 0 so Modeler
    does not silently keep a previous non-zero value.
    """
    node = stream.createAt("partition", "Partition 70-30", _X["partition"], _Y)

    # --- THE FIX: explicit 70/30, no validation slice ---
    node.setPropertyValue("training_partition", 70)
    node.setPropertyValue("testing_partition",  30)
    node.setPropertyValue("validation_partition", 0)

    # Reproducible random split
    node.setPropertyValue("sampling_method", "Random")
    node.setPropertyValue("set_seed", True)
    node.setPropertyValue("seed", 12345)

    return node


def _configure_model_node(stream, target_field: str, model_type: str):
    """
    Create a modeling (builder) node.

    Supported model_type values:
        "cartree"      – C&RT (default, works for both classification & regression)
        "chaid"        – CHAID
        "logistic"     – Logistic Regression
        "randomforest" – Random Forest
        "neuralnet"    – Neural Network
    """
    node = stream.createAt(model_type, model_type.upper(), _X["builder"], _Y)
    node.setPropertyValue("target_field", target_field)

    # Always train only on the Training partition created above
    node.setPropertyValue("use_partitioned_data", True)

    return node


# ---------------------------------------------------------------------------
# Main builder
# ---------------------------------------------------------------------------

def build_and_run(
    data_path: str,
    target_field: str,
    model_type: str = "cartree",
    stream_save_path: str = None,
):
    """
    Build a full Modeler stream, run the model, and execute the Analysis node.

    Stream topology:
        Source → Type → Partition(70/30) → ModelBuilder
                                                 ↓  (run → nugget created)
                        Partition(70/30) → ModelNugget → Analysis

    Parameters
    ----------
    data_path       : Path to the input data file.
    target_field    : Name of the outcome/target field.
    model_type      : Modeler node type string for the algorithm.
    stream_save_path: Optional .str path to persist the stream.

    Returns
    -------
    stream object
    """
    if modeler is None:
        raise RuntimeError(
            "modeler.api not available – run this script inside SPSS Modeler."
        )

    stream = modeler.script.stream()

    # ── 1. Source ────────────────────────────────────────────────────────────
    source = _create_source_node(stream, data_path)
    print(f"[1/6] Source node created  ({data_path})")

    # ── 2. Type ──────────────────────────────────────────────────────────────
    type_node = stream.createAt("type", "Types", _X["type"], _Y)
    # Read field metadata from source; target role set after instantiation
    type_node.setPropertyValue("read_metadata", True)
    print("[2/6] Type node created")

    # ── 3. Partition (70/30) ─────────────────────────────────────────────────
    partition = _configure_partition_node(stream)
    print("[3/6] Partition node created  (train=70 %, test=30 %)")

    # ── 4. Model builder ─────────────────────────────────────────────────────
    builder = _configure_model_node(stream, target_field, model_type)
    print(f"[4/6] Model builder node created  ({model_type})")

    # ── 5. Wire source → type → partition → builder and run ──────────────────
    stream.link(source,    type_node)
    stream.link(type_node, partition)
    stream.link(partition, builder)

    print("[5/6] Running model builder …")
    builder.run([])

    # ── 6. Retrieve nugget and attach Analysis node ───────────────────────────
    # Modeler places the generated nugget on the canvas after a successful run.
    nugget_type = model_type + "model"          # e.g. "cartreemodel"
    nugget = stream.findByType(nugget_type, None)

    if nugget is None:
        # Fallback: search any newly added model nugget
        nugget = stream.findByType(None, None)
        raise RuntimeError(
            f"Model nugget of type '{nugget_type}' not found after training. "
            "Check that the model built successfully."
        )

    print(f"[6/6] Model nugget found: {nugget.getName()}")

    # Connect nugget back into the scored stream
    stream.link(partition, nugget)

    analysis = stream.createAt("analysis", "Analysis", _X["analysis"], _Y)
    analysis.setPropertyValue("mode", "auto")
    stream.link(nugget, analysis)

    print("      Running Analysis (evaluation) node …")
    analysis.run([])
    print("      Evaluation complete.")

    # ── 7. Optionally persist the stream ────────────────────────────────────
    if stream_save_path:
        stream.saveAs(stream_save_path)
        print(f"Stream saved → {stream_save_path}")

    return stream
