# Development Info

## Overview

This project uses the [`typer`](https://typer.tiangolo.com) library to create a dynamically invoked command line tool
that can be easily extended and updated. For a more complete overview of typer, I recommend starting with the
tutorial [here](https://typer.tiangolo.com/tutorial/). In brief, the project is composed into multiple 'apps' that are
loaded by typer and arranged with their own command names and arguments.

Ex: `src/bangertools/ahf/app.py` is loaded by `main.py` and provides a common set of commands that can be accessed
using `banger ahf`. Functions within `ahf/app.py` are decorated with `@app_name.command` so they will be automatically
picked up and added to the tool.

### Guidelines and Recommendations

- Use descriptive names. Shorter names don't improve performance and just hinder readability for the next person.
- Not everyone has a fancy IDE. Try to keep lines < 120 characters long.
- Type hints are optional, but encouraged.

## Type Hints

Type hints are a way to indicate what kind of information a variable or parameter should be. They are optional and not
required, but are encouraged. Type hints can help to improve code readability, editor support, and static analysis.
Type hints help catch bugs early and make the codebase easier to understand and maintain.

### How To

Add type hints by specifying the expected type after each function parameter and after the `->` symbol for the return
value, for example: `def greet(name: str) -> str:`. Use built-in types such as `str`, `int`, `bool`, `list[str]`, and
`dict[str, int]` to describe the values your code expects. When modifying existing code, add type hints to new
functions first and then gradually update older code as you work on it.

### Example

```python
def get_user_name(user_id: int) -> str:
    return database.fetch_name(user_id)
```


