# PyGDC

Python API for accessing Genomic Data Commons

### Basic API

#### Cases
```python
from pygdc import get_cases
from pygdc.filters import equals_filter


results = get_cases(
    filters=equals_filter('project.primary_site', 'Lung'), 
    fields='demographic.gender,project.disease_type', 
    max_results=50
)
```

### Cohorts Example

Using [cohorts](http://github.com/hammerlab/cohorts)

```python
import pygdc

pygdc.build_cohort(
    primary_site='Lung', 
    cohort_cache_dir='cache-dir')
```
