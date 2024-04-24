from typing import FrozenSet

from nltk import word_tokenize
from nltk.stem.snowball import RussianStemmer, EnglishStemmer
from string import ascii_letters

es = EnglishStemmer()
rs = RussianStemmer()


def tokenize(text: str) -> FrozenSet[str]:
    return frozenset(es.stem(i) if i[0] in ascii_letters else rs.stem(i)
                     for i in word_tokenize(text) if i.isalnum())
