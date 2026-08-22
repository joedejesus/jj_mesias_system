from __future__ import annotations

import unittest
from pathlib import Path

from src.training.preparacion_datos import load_jsonl_examples, normalize_example


class TrainingDataTestCase(unittest.TestCase):
    def test_example_training_dataset_is_present_and_readable(self) -> None:
        dataset_path = Path("data") / "ejemplo_entrenamiento.jsonl"
        examples = load_jsonl_examples(dataset_path)
        self.assertGreaterEqual(len(examples), 8)

    def test_example_training_dataset_normalizes_all_rows(self) -> None:
        dataset_path = Path("data") / "ejemplo_entrenamiento.jsonl"
        examples = load_jsonl_examples(dataset_path)
        normalized = [normalize_example(example) for example in examples]
        self.assertTrue(all(example.messages for example in normalized))


if __name__ == "__main__":
    unittest.main()
