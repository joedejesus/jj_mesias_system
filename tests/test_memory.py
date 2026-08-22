from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.memory.memoria import Memoria
from src.memory.memoria_chat import MemoriaChat


class MemoryTestCase(unittest.TestCase):
    def test_memoria_and_chat_bootstrap_missing_storage_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            memory_path = Path(temp_dir) / "memory.json"
            chat_path = Path(temp_dir) / "chat.json"

            memoria = Memoria(storage_path=memory_path)
            chat = MemoriaChat(memoria=memoria, storage_path=chat_path)

            self.assertTrue(memory_path.exists())
            self.assertTrue(chat_path.exists())
            self.assertEqual(memory_path.read_text(encoding="utf-8"), "[]")
            self.assertEqual(chat_path.read_text(encoding="utf-8"), "[]")
            self.assertEqual(memoria.list_all(), [])
            self.assertEqual(chat.history(), [])

    def test_memoria_can_recover_from_corrupt_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            memory_path = Path(temp_dir) / "broken_memory.json"
            memory_path.write_text("{not-json", encoding="utf-8")
            memoria = Memoria(storage_path=memory_path)
            self.assertEqual(memoria.list_all(), [])
            backup_files = list(Path(temp_dir).glob(
                "broken_memory.json.corrupt*"))
            self.assertTrue(backup_files)

    def test_memoria_chat_filters_and_clears_by_speaker(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            memory_path = Path(temp_dir) / "memory.json"
            chat_path = Path(temp_dir) / "chat.json"
            memoria = Memoria(storage_path=memory_path)
            local_chat = MemoriaChat(
                memoria=memoria, storage_path=chat_path, speaker_id="user-a")
            local_chat.add_user_message("hola")
            local_chat.remember("me gusta el cafe", metadata={
                                "speaker_id": "user-a"})
            self.assertEqual(len(local_chat.history()), 1)
            self.assertEqual(len(memoria.recent_for_speaker("user-a")), 1)
            memoria.clear_for_speaker("user-a")
            self.assertEqual(memoria.recent_for_speaker("user-a"), [])
            local_chat.clear()
            self.assertEqual(local_chat.history(), [])


if __name__ == "__main__":
    unittest.main()
