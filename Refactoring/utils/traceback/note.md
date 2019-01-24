##### traceback

traceback 信息来源于 traceback objecct <---- sys.exc_info()

```python
    exc_type, exc_value, exc_traceback_obj = sys.exc_info()
```

- traceback.print_tb(tb[, limit[, file]])
    print up to 'limit' stack trace entries from the tracebakc 'tb'
    - tb, traceback obj
    - limit,  If limit is omitted or None, all entries are printed.
    - file, If 'file' omitted or None, the output goes to sys.stderr; otherwise 'file' should be an open file or file-like obj with a write() method.