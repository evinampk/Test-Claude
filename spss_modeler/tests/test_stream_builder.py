"""
Unit tests for stream_builder.py using a mock modeler.api.

These run without a live SPSS Modeler installation.
"""

import sys
import types
import unittest
from unittest.mock import MagicMock, call, patch


# ---------------------------------------------------------------------------
# Build a minimal modeler.api stub so import works outside Modeler runtime
# ---------------------------------------------------------------------------

def _make_modeler_stub():
    modeler_mod   = types.ModuleType("modeler")
    modeler_api   = types.ModuleType("modeler.api")
    modeler_script = MagicMock()

    # Each stream.createAt() returns a fresh mock node
    def _create_at(node_type, name, x, y):
        node = MagicMock()
        node.getName.return_value = name
        node._type = node_type
        return node

    stream_mock = MagicMock()
    stream_mock.createAt.side_effect = _create_at
    stream_mock.findByType.return_value = MagicMock()
    stream_mock.findByType.return_value.getName.return_value = "RF Model"

    modeler_script.stream.return_value = stream_mock
    modeler_api.script = modeler_script

    modeler_mod.api = modeler_api
    sys.modules["modeler"] = modeler_mod
    sys.modules["modeler.api"] = modeler_api

    return stream_mock


_stream_mock = _make_modeler_stub()

# Now the real import will succeed
import importlib
import stream_builder as sb
importlib.reload(sb)      # reload so it picks up the stub


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestPartitionNode(unittest.TestCase):
    """Verify the 70/30 partition fix is applied correctly."""

    def setUp(self):
        _stream_mock.reset_mock()
        _stream_mock.createAt.side_effect = lambda t, n, x, y: MagicMock(getName=MagicMock(return_value=n))

    def test_partition_properties_70_30(self):
        node = MagicMock()
        _stream_mock.createAt.side_effect = lambda t, n, x, y: node

        result = sb._configure_partition_node(_stream_mock)

        calls = node.setPropertyValue.call_args_list
        props = {c.args[0]: c.args[1] for c in calls}

        self.assertEqual(props.get("training_partition"), 70,
                         "training_partition must be 70")
        self.assertEqual(props.get("testing_partition"), 30,
                         "testing_partition must be 30")
        self.assertEqual(props.get("validation_partition"), 0,
                         "validation_partition must be 0 (no validation slice)")

    def test_partition_uses_random_sampling(self):
        node = MagicMock()
        _stream_mock.createAt.side_effect = lambda t, n, x, y: node

        sb._configure_partition_node(_stream_mock)

        calls = node.setPropertyValue.call_args_list
        props = {c.args[0]: c.args[1] for c in calls}

        self.assertEqual(props.get("sampling_method"), "Random")
        self.assertTrue(props.get("set_seed"), "set_seed should be True for reproducibility")


class TestSourceNode(unittest.TestCase):
    """Verify the correct source node type is chosen per file extension."""

    def _get_created_type(self, path):
        created = []
        _stream_mock.createAt.side_effect = lambda t, n, x, y: created.append(t) or MagicMock()
        sb._create_source_node(_stream_mock, path)
        return created[0]

    def test_csv_uses_variablefile(self):
        self.assertEqual(self._get_created_type("data.csv"), "variablefile")

    def test_sav_uses_statisticsfile(self):
        self.assertEqual(self._get_created_type("data.sav"), "statisticsfile")

    def test_xlsx_uses_excel(self):
        self.assertEqual(self._get_created_type("data.xlsx"), "excel")


class TestModelNode(unittest.TestCase):
    """Verify model node is configured with partitioned data flag."""

    def test_use_partitioned_data_is_true(self):
        node = MagicMock()
        _stream_mock.createAt.side_effect = lambda t, n, x, y: node

        sb._configure_model_node(_stream_mock, "Churn", "cartree")

        calls = node.setPropertyValue.call_args_list
        props = {c.args[0]: c.args[1] for c in calls}

        self.assertEqual(props.get("target_field"), "Churn")
        self.assertTrue(props.get("use_partitioned_data"),
                        "model must train only on the Training partition")


class TestRunStreamArgs(unittest.TestCase):
    """Verify CLI argument parsing."""

    def test_required_args(self):
        import run_stream
        args = run_stream.parse_args(["--data", "d.csv", "--target", "T"])
        self.assertEqual(args.data, "d.csv")
        self.assertEqual(args.target, "T")
        self.assertEqual(args.model, "cartree")   # default
        self.assertIsNone(args.save)

    def test_model_override(self):
        import run_stream
        args = run_stream.parse_args(["--data", "d.csv", "--target", "T",
                                      "--model", "randomforest"])
        self.assertEqual(args.model, "randomforest")

    def test_invalid_model_exits(self):
        import run_stream
        with self.assertRaises(SystemExit):
            run_stream.parse_args(["--data", "d.csv", "--target", "T",
                                   "--model", "unknownalgo"])


if __name__ == "__main__":
    unittest.main()
