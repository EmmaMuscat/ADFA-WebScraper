# A Text Analysis solution for html pages of ADFA's Supply Chain Manual

* Webscraper.py will extract and store the relevant content in correspondingly chapter titled JSON files (format seen in htm.format)

* Semantic_Similarity.py uses the JSON data to perform specific semantic comparisions (tfid cosine similarity) requested by the ADFA research team and outputs the results in csv format for future graphing and insight analysis.

* hyperlink_analysis.py will extract and store hyperlinks from given supply chain manual htm pages and store the necessaery components in JSON (format specified in hyperlink_format.json) and analyse these results using natural language processing to determine the purpose/nature of said hyperlinks.
