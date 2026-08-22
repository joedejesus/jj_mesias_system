from __future__ import annotations
from src.training.entrenamiento import EntrenamientoConfig, train_lora_from_jsonl
from src.training.preparacion_datos import load_jsonl_examples, prepare_sft_dataset

"""Implementacion auxiliar del entrenamiento LoRA prudente de Mesias para terminal."""

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


DEFAULT_DATASET_PATH = PROJECT_ROOT / "data" / \
    "dataset_entrenamiento_docente.jsonl"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / \
    "checkpoints" / "mesias-qwen25-lora-safe"


def build_parser() -> argparse.ArgumentParser:
    """Construye el parser CLI del entrenamiento seguro de Mesias."""
    parser = argparse.ArgumentParser(
        description="Entrenamiento LoRA seguro para Mesias con defaults prudentes en CPU.",
    )
    parser.add_argument("--dataset", default=str(DEFAULT_DATASET_PATH))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--model-path", default=None)
    parser.add_argument("--epochs", type=float, default=1.0)
    parser.add_argument("--train-batch-size", type=int, default=1)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=8)
    parser.add_argument("--dataloader-num-workers", type=int, default=0)
    parser.add_argument("--cpu-threads", type=int, default=4)
    parser.add_argument("--max-length", type=int, default=1024)
    parser.add_argument("--learning-rate", type=float, default=2e-4)
    parser.add_argument("--logging-steps", type=int, default=10)
    parser.add_argument("--save-steps", type=int, default=100)
    parser.add_argument(
        "--prepare-only",
        action="store_true",
        help="Solo valida y tokeniza el dataset sin arrancar el entrenamiento.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Valida el dataset y, si procede, lanza el entrenamiento LoRA de Mesias."""
    parser = build_parser()
    args = parser.parse_args(argv)

    dataset_path = Path(args.dataset).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    if not dataset_path.exists():
        parser.error(f"No existe el dataset: {dataset_path}")

    config = EntrenamientoConfig(
        output_dir=output_dir,
        epochs=args.epochs,
        train_batch_size=args.train_batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        dataloader_num_workers=args.dataloader_num_workers,
        cpu_threads=args.cpu_threads,
        max_length=args.max_length,
        learning_rate=args.learning_rate,
        logging_steps=args.logging_steps,
        save_steps=args.save_steps,
    )

    examples = load_jsonl_examples(dataset_path)
    prepared_rows = prepare_sft_dataset(
        examples,
        model_path=args.model_path,
        max_length=config.max_length,
    )

    print(json.dumps(
        {
            "dataset_path": str(dataset_path),
            "output_dir": str(output_dir),
            "examples": len(examples),
            "prepared_rows": len(prepared_rows),
            "epochs": config.epochs,
            "train_batch_size": config.train_batch_size,
            "gradient_accumulation_steps": config.gradient_accumulation_steps,
            "dataloader_num_workers": config.dataloader_num_workers,
            "cpu_threads": config.cpu_threads,
            "max_length": config.max_length,
            "prepare_only": args.prepare_only,
        },
        ensure_ascii=False,
        indent=2,
    ))

    if args.prepare_only:
        return 0

    trainer = train_lora_from_jsonl(
        dataset_path,
        config=config,
        model_path=args.model_path,
    )
    print(f"Entrenamiento completado. Checkpoint guardado en: {output_dir}")
    print(type(trainer).__name__)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
