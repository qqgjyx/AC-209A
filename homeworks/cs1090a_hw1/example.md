---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.19.5
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

```{code-cell} ipython3
import requests
from bs4 import BeautifulSoup
import wikipedia
```

```{code-cell} ipython3
# micromamba install wikipedia -c conda-forge -y
```

```{code-cell} ipython3
wikipedia.set_lang("en")
wikipedia.set_rate_limiting(True)  # Built-in rate limiting
```

```{code-cell} ipython3
html = wikipedia.page("The Last Emperor").html()
soup = BeautifulSoup(html)
```

```{code-cell} ipython3
for tag in soup.select("th"):
    if tag.text == "Budget":
        budget = tag.next_sibling.text
        print(budget)
```

```{code-cell} ipython3
# If you're concerned about the citation at the end of the str
budget.split("[")[0]
```

```{code-cell} ipython3
soup.find("th", string="Budget").next_sibling.text.split("[")[0]
```

```{code-cell} ipython3

```
