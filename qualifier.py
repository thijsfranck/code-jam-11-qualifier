from enum import auto, StrEnum
import warnings
import shlex

MAX_QUOTE_LENGTH = 50


# The two classes below are available for you to use
# You do not need to implement them
class VariantMode(StrEnum):
    NORMAL = auto()
    UWU = auto()
    PIGLATIN = auto()


class DuplicateError(Exception):
    """Error raised when there is an attempt to add a duplicate entry to a database"""


def transform_to_uwu(quote: str) -> str:
    """
    Transforms a quote to its uwu variant
    """
    base = (
        quote
        .replace("l", "w")
        .replace("L", "W")
        .replace("r", "w")
        .replace("R", "W")
    )

    result = " ".join(
        [
            f"{word[0]}-{word}" if word.startswith(("u", "U")) else word
            for word in base.split()
        ]
    )

    if len(result) > MAX_QUOTE_LENGTH:
        warnings.warn("Quote too long, only partially transformed")
        result = base

    if result == quote:
        raise ValueError("Quote was not modified")

    return result


def _word_to_piglatin(word: str) -> str:
    """
    Transforms a word to its piglatin variant
    """
    first_vowel_idx = next(
        (i for i, c in enumerate(word) if c in "aeiou"),
        None
    )

    if first_vowel_idx == 0:
        return word + "way"
    elif first_vowel_idx is not None:
        consonant_cluster = word[:first_vowel_idx]
        return word[first_vowel_idx:] + consonant_cluster + "ay"

    return word


def transform_to_piglatin(quote: str) -> str:
    """
    Transforms a quote to its piglatin variant
    """
    words = quote.lower().split()
    piglatin_words = [_word_to_piglatin(word) for word in words]
    result = " ".join(piglatin_words).capitalize()

    if len(result) > MAX_QUOTE_LENGTH:
        result = quote

    if result == quote:
        raise ValueError("Quote was not modified")

    return result


class Quote:

    transformers = {
        VariantMode.NORMAL: lambda quote: quote,
        VariantMode.UWU: transform_to_uwu,
        VariantMode.PIGLATIN: transform_to_piglatin,
    }

    def __init__(self, quote: str, mode: "VariantMode") -> None:
        self.quote = quote
        self.mode = mode

    def __str__(self) -> str:
        return self._create_variant()

    def _create_variant(self) -> str:
        """
        Transforms the quote to the appropriate variant indicated by `self.mode` and returns the result
        """
        return Quote.transformers[self.mode](self.quote)


def run_command(command: str) -> None:
    """
    Will be given a command from a user. The command will be parsed and executed appropriately.

    Current supported commands:
        - `quote` - creates and adds a new quote
        - `quote uwu` - uwu-ifys the new quote and then adds it
        - `quote piglatin` - piglatin-ifys the new quote and then adds it
        - `quote list` - print a formatted string that lists the current
           quotes to be displayed in discord flavored markdown
    """

    # Replace smart quotes with regular quotes
    command = command.replace("“", '"').replace("”", '"')

    name, *args = shlex.split(command)

    if name != "quote" or 1 < len(args) > 2:
        raise ValueError("Invalid command")

    operation = args[0]

    if operation == "list":
        list_items = [f"- {quote}" for quote in Database.get_quotes()]
        print("\n".join(list_items))
        return

    quote = args[-1]

    if len(quote) > MAX_QUOTE_LENGTH:
        raise ValueError("Quote is too long")

    if operation in VariantMode:
        mode = VariantMode(operation)
    elif operation == quote:
        mode = VariantMode.NORMAL
    else:
        raise ValueError("Invalid command")

    quote = Quote(quote, mode)

    try:
        Database.add_quote(quote)
    except DuplicateError:
        print("Quote has already been added previously")


# The code below is available for you to use
# You do not need to implement it, you can assume it will work as specified
class Database:
    quotes: list["Quote"] = []

    @classmethod
    def get_quotes(cls) -> list[str]:
        "Returns current quotes in a list"
        return [str(quote) for quote in cls.quotes]

    @classmethod
    def add_quote(cls, quote: "Quote") -> None:
        "Adds a quote. Will raise a `DuplicateError` if an error occurs."
        if str(quote) in [str(quote) for quote in cls.quotes]:
            raise DuplicateError
        cls.quotes.append(quote)
