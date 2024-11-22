#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Standard Library Imports
import csv
import logging
from pathlib import Path
from tqdm import tqdm
import regex as re

# Local imports
from . import dictionary


def save_vocab_to_csv(vocab: set, output_file: Path):
    with open(output_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["word"])
        for word in vocab:
            writer.writerow([word])


def process_vocab_file(vocab_file: Path, add_english: bool, add_furigana: bool):
    line_count = count_lines(vocab_file)

    updated_rows = []
    with open(vocab_file, "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        headers = next(reader)
        if add_english:
            headers.append("definition")
        updated_rows.append(headers)

        for row in tqdm(
            reader,
            desc="Processing vocab file:",
            total=line_count - 1,
        ):
            word = row[0]
            word_info = dictionary.get_word_info(word)

            # I currently decided one-letter kana words are not worth keeping in
            # because the definitions fetched for them are absolutely useless. This could
            # and should definitely be changed but I'm not really sure how to do it.
            one_letter_kana = re.match(r"^\p{Hiragana}$|^\p{Katakana}$", word)
            if not word_info["is_real"] or (one_letter_kana and add_english):
                logging.debug(f"Removing {word}")
                continue

            # Add English definition
            if add_english:
                row.append(word_info["definition"])

            # Add furigana
            if add_furigana and re.search(r"\p{Han}", word):
                row[0] = f"{word} ({word_info['kana']})"

            updated_rows.append(row)

    with open(vocab_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(updated_rows)


def count_lines(vocab_file: Path):
    with open(vocab_file, "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        line_count = sum(1 for row in reader)
    return line_count
