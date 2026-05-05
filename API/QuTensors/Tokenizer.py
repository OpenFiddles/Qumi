import os
import json
import re

class Tokenizer:
    def __init__(self, folder="QumiData"):
        self.vocab_path = os.path.join(folder, "vocab.json")
        self.word_to_id = {"<UNK>": 0}
        self.id_to_word = {0: "<UNK>"}
        
        # Ensure the directory exists
        if not os.path.exists(folder):
            os.makedirs(folder)
            
        self._load_vocab()

    def _load_vocab(self):
        """Reads the known symbols/words from disk."""
        if os.path.exists(self.vocab_path):
            try:
                with open(self.vocab_path, 'r') as f:
                    self.word_to_id = json.load(f)
                    self.id_to_word = {int(v): k for k, v in self.word_to_id.items()}
            except:
                pass

    def tokenize(self, text):
        """Converts text + symbols into a list of numeric IDs."""
        # Split by whitespace to preserve attached symbols (e.g. 'hello!')
        raw_tokens = text.lower().split()
        ids = []
        
        for token in raw_tokens:
            if token not in self.word_to_id:
                new_id = len(self.word_to_id)
                self.word_to_id[token] = new_id
                self.id_to_word[new_id] = token
            ids.append(self.word_to_id[token])
        
        # Immediate persistence for the vocabulary
        self._save_vocab()
        return ids, raw_tokens

    def _save_vocab(self):
        """Saves the symbol mapping to QumiData/vocab.json."""
        try:
            with open(self.vocab_path, 'w') as f:
                json.dump(self.word_to_id, f)
        except:
            pass

    def decode(self, ids):
        """Turns IDs back into a readable string with symbols."""
        return " ".join([self.id_to_word.get(i, "<UNK>") for i in ids])
