Scripts :-

Step 1- wiki_indexer.py -- will create intermediate index files with the help of parsedata by parsing and creating index for 50000 documents in each intermediate file.
parsedata.py -- contains class for parsing data in xml files.

Step 2 - merger.py -- will create primary index files by merging intermediate files formed in step 1. Each primary index file contains 150000 words. Secondary index has also been created keeping a record of all primary files.

Step3 - search.py -- will take query.txt as input and secondary and primary index files to get relevant document as per the query.

Processing details:
Processed all 34 xml files 
Intermediate files - 222 each file containing 50000 documents
Final Inverted Index files - 111 primary index files and one secondary index file.
Total tokens in Inverted Index - 16618555
