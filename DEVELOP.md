# Development Info

## Guidelines and Recommendations
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


