The goal is to ensure that this project does not use any custom error/exception classes.
There was originally a `tarot_oracle/exceptions.py` file which included around 20 custom error/exception classes.
That file has been removed, but references to these old classes may still exist within the code base.
Find every instance where such a class has been used and replace it with either a `TypeError` or a `ValueError`.

# Project Invariants

1. Under no circumstances can the files in tests/vectors/ be changed in any way.
2. No functionality changes can be made to the files in `tarot_oracle` other than replacing references to old error classes.
3. Ensure the `tests/test_oracle.py` file does not make external API calls to genai/ollama/openrouter before running it.

