+++
# Used both in bibtex generation, and for link creation - should be unique
bibkey = ""

# Raw bibtex
bibtex = ""

# Information about work that cites this
citation = []

title = "{{ replace .TranslationBaseName "-" " " | title }}"
date = {{ .Date }}
draft = false

# Authors. Comma separated list, e.g. `["Bob Smith", "David Jones"]`.
authors = [""]

# Publication type.
# Legend:
# 0 = Uncategorized
# 1 = Conference proceedings
# 2 = Journal
# 3 = Work in progress
# 4 = Technical report
# 5 = Book
# 6 = Book chapter
publication_types = ["0"]

# Publication name and optional abbreviated version.
publication = ""
publication_short = ""

# Abstract and optional shortened version.
abstract = ""
abstract_short = ""

# Additional bibliographic fields
address = ""
doi = ""
issue = ""
number = ""
pages = ""
publisher = ""
volume = ""

# Does this page contain LaTeX math? (true/false)
math = false

# Does this page require source code highlighting? (true/false)
highlight = true

# Featured image thumbnail (optional)
image_preview = ""

# Is this a selected publication? (true/false)
selected = false

# Links (optional)
url_pdf = ""
url_code = ""
url_dataset = ""
url_project = ""
url_poster = ""
url_slides = ""
url_slides_pdf = ""
url_video = ""

# Featured image
# Place your image in the `static/img/` folder and reference its filename below, e.g. `image = "example.jpg"`.
[header]
image = ""
caption = ""

+++
