# DFAT Documents

Code to harvest DFAT's collection of Historical Documents and extract a bit of metadata. It was developed as a quick demonstration only, so it could be improved and extended in many ways.

Content on the DFAT website is made available under a [CC-BY licence](http://dfat.gov.au/about-us/about-this-website/Pages/copyright.aspx).

The documents are scraped from the DFAT website and converted to Markdown. You can find the results in the [`volumes`](volumes/) directory. Metadata is saved to the [`documents.csv`](documents.csv) file. I've also published the harvested files to a [new experimental website](https://wragge.github.io/dfat-documents-web/) using Jekyll.

Dates are extracted from the documents using simple pattern matching. The date is then saved to the front matter of the Markdown document. I've created a plot of the [distribution of documents by month](https://plot.ly/~wragge/469.embed), as well as one by [month and volume](https://plot.ly/~wragge/471.embed). On the Jekyll site you'll find [a date index](https://wragge.github.io/dfat-documents-web/dates/) that lists all the documents by month. At the bottom of this page you'll find a list of documents that I couldn't find a date in -- if you browse these you'll see various ways my pattern matching could be improved to cope with variations in punctuation, missing numbers etc.

I've also attempted to find references to files in the National Archives of Australia. I've then used my [RecordSearch-tools](https://github.com/wragge/recordsearch_tools) code to search for these references in RecordSearch -- if found, they're added as links in the Markdown. I created a [list of the references](unmatched_references.txt) I couldn't find in RecordSearch -- once again a few patterns are obvious, and it's pretty easy to work out how my code my be improved to find more links. You can also [browse a list](https://wragge.github.io/dfat-documents-web/references/) of the linked files.


