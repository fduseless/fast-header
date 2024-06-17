# Fast Header

HTTP Header Encoder & Decoder for Python

## Install

```bash
pip install fast-header
```

## Usage

### cache control

```python
from fast_header import CacheControl

cc = CacheControl(max_stale=True)
assert cc.max_stale
assert str(cc) == "max_stable"
cc = CacheControl.parse("max_stable")
```

### etag

```python
from fast_header import ETag
setag = ETag(value="a") # strong etag
wetag = ETag(value="a", weak=True) # weak etag
```

