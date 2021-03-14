from python_translators.query_processors.query_processor import QueryProcessor
from python_translators.translation_query import TranslationQuery
import nltk.data
from python_translators.utils import code_to_full_language
import os.path
import copy


NLTK_DATA_PATH = "~/nltk_data/tokenizers/punkt/%(language)s.pickle"
# on  windows it seems default install of NLTK is in AppData/roaming under current user.
NLTK_WINDOWS_DATA_PATH = (
    "~/AppData/Roaming/nltk_data/tokenizers/punkt/%(language)s.pickle"
)


class RemoveUnnecessarySentences(QueryProcessor):
    # Global storage of tokenizers indexed by language code to prevent reloading of tokenizers
    tokenizers = {}

    def __init__(self, language_code):
        super(RemoveUnnecessarySentences, self).__init__(
            name="remove_unnecessary_sentences"
        )

        # if a tokenizer was already in our global storage
        if language_code in RemoveUnnecessarySentences.tokenizers:
            self.tokenizer = RemoveUnnecessarySentences.tokenizers[language_code]

        else:
            self.tokenizer = RemoveUnnecessarySentences._load_tokenizer(language_code)
            RemoveUnnecessarySentences.tokenizers[language_code] = self.tokenizer

    @classmethod
    def _load_tokenizer(cls, language_code):
        on_windows = os.name == "nt"  # nt is the value for windows,
        if on_windows:
            resource_url = NLTK_WINDOWS_DATA_PATH % {
                "language": code_to_full_language(language_code)
            }
        else:
            resource_url = NLTK_DATA_PATH % {
                "language": code_to_full_language(language_code)
            }

        print(f"about to expand: {resource_url} ")
        resource_url = os.path.expanduser(resource_url)

        if on_windows:
            resource_url = "file://" + resource_url.replace("\\", "/")

        # try/catch trying to address: https://github.com/zeeguu-ecosystem/Python-Translators/issues/58#issue-831132909
        try:
            nltk.data.find(resource_url)
        except LookupError:
            print("installing punkt at " + resource_url)
            nltk.download("punkt")

        print(f"about to load: {resource_url}")
        tokenizer = nltk.data.load(resource_url)
        return tokenizer

    def _process_context(self, context: str, token_index: -1):
        tokenized_context = self.tokenizer.tokenize(context)

        try:
            return tokenized_context[token_index]
        except IndexError:
            return context

    def process_query(self, query: TranslationQuery) -> TranslationQuery:
        new_query = copy.copy(query)
        new_query.before_context = self._process_context(
            query.before_context, -1
        )  # last token
        new_query.after_context = self._process_context(
            query.after_context, 0
        )  # first token

        return new_query
