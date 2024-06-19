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

### Content Disposition

```python
from fast_header import ContentDisposition
cd = ContentDisposition.parse('attachment; filename="=?ISO-8859-1?Q?foo-=E4.html?="')
assert cd.type == 'attachment'
assert cd.parameters == { 'filename': '=?ISO-8859-1?Q?foo-=E4.html?=' }
```

### Content Type

```python
from fast_header import ContentType
cd = ContentType.parse('text/html; charset=utf-8; foo=bar')
assert cd.type == 'text/html'
assert cd.parameters == { 'charset': 'utf-8', 'foo': 'bar' }
```

### Content Range

from fast_header import ContentRange

```python
from fast_header import ContentRange
cr = ContentRange.parse("bytes 0-20/30")
assert cr.unit == "bytes"
assert cr.range is not None
assert cr.range.start == 0
assert cr.range.stop == 20
assert cr.size == 30
```