#-------------------------------------------------------------------------
# AUTHOR: Josiah Degeneffe
# FILENAME: inverted_index.py
# SPECIFICATION: uses MongoClient to create and manage a database of
#                documents and corresponding term-frequency lists
# FOR: CS 4250 - Assignment #3
# TIME SPENT: 1 hr
#-------------------------------------------------------------------------

# Importing Python libraries
from pymongo import MongoClient

# Connecting to MongoDB
client = MongoClient("mongodb://localhost:27017/")

# Accessing the database and collections
db = client["assignment3"]
documents = db["documents"]
inverted_index = db["inverted_index"]

# reset database to avoid errors when rerunning the code 
documents.delete_many({})
inverted_index.delete_many({})


#-------------------------------------------------------------------------
# FUNCTION: getTermFrequencies
# SPECIFICATION: receives a text and returns the frequency of each term
#-------------------------------------------------------------------------
def getTermFrequencies(text):

    # Converting text to lowercase
    # --> add your Python code here
    text = text.lower()

    # Removing punctuation
    # --> add your Python code here
    text = text.replace('.', '')

    # Splitting the text into terms
    # --> add your Python code here
    terms = text.split()

    # Returning the term frequencies
    # --> add your Python code here
    freq = dict.fromkeys(terms, 0)
    for term in terms:
        freq.update({term: freq[term]+1})
    return freq


#-------------------------------------------------------------------------
# FUNCTION: addPosting
# SPECIFICATION: adds a posting to an existing term or creates a new term
#-------------------------------------------------------------------------
def addPosting(term, docId, tf):

    # Searching for the term in the inverted index
    # --> add your Python code here
    entry = inverted_index.find_one({"term":term})

    # Creating a new term if it does not exist
    # --> add your Python code here
    if entry == None:
        new_term = {
            "term": term,
            "postings": [
                {
                    "docId": docId,
                    "tf": tf,
                }
            ]
        }
        inverted_index.insert_one(new_term)

    # Adding a posting if the term already exists
    # --> add your Python code here
    else:
        inverted_index.update_one(
            {"term": term},
            {"$push": {
                    "postings": {
                        "docId": docId,
                        "tf": tf,
                    }
                }
            }
        )

#-------------------------------------------------------------------------
# FUNCTION: removePosting
# SPECIFICATION: removes a document posting from a term and deletes the
#                term if its postings list becomes empty
#-------------------------------------------------------------------------
def removePosting(term, docId):

    # Removing the posting from the term
    # --> add your Python code here
    inverted_index.update_one(
        {"term": term},
        {"$pull": {
                "postings": {
                    "docId": docId
                }
            }
        }
    )

    # Retrieving the term after removing the posting
    # --> add your Python code here
    term_entry = inverted_index.find_one({"term": term})

    # Deleting the term if its postings list is empty
    # --> add your Python code here
    if len(term_entry["postings"]) == 0:
        inverted_index.delete_one({"term": term})


#-------------------------------------------------------------------------
# FUNCTION: insertDocument
# SPECIFICATION: inserts a document and updates the inverted index
#-------------------------------------------------------------------------
def insertDocument(document):

    # Inserting the document into the documents collection
    # --> add your Python code here
    documents.insert_one(document)

    # Obtaining the term frequencies
    # --> add your Python code here
    text = document["text"]
    freq = getTermFrequencies(text)

    # Updating the inverted index
    # --> add your Python code here
    for term, tf in freq.items():
        addPosting(term, document["_id"], tf)


#-------------------------------------------------------------------------
# FUNCTION: updateDocument
# SPECIFICATION: updates a document and makes the corresponding changes
#                to the inverted index
#-------------------------------------------------------------------------
def updateDocument(docId, newText):

    # Retrieving the current document
    # --> add your Python code here
    cur_doc = documents.find_one({"_id": docId})

    # Obtaining the old and new term frequencies
    # --> add your Python code here
    freq_old = getTermFrequencies(cur_doc["text"])
    freq_new = getTermFrequencies(newText)

    # Processing terms that existed in the old document
    # --> add your Python code here
    for term in freq_old:
        removePosting(term, docId)

    # Processing terms that occur only in the new document
    # --> add your Python code here
    for term in freq_new:
        addPosting(term, docId, freq_new[term])

    # Updating the document text
    # --> add your Python code here
    documents.update_one(
        {"_id": docId},
        {"$set": {"text": newText}}
    )


#-------------------------------------------------------------------------
# FUNCTION: deleteDocument
# SPECIFICATION: deletes a document and removes all of its postings from
#                the inverted index
#-------------------------------------------------------------------------
def deleteDocument(docId):

    # Retrieving the document before deleting it
    # --> add your Python code here
    doc = documents.find_one({"_id": docId})

    # Obtaining the terms contained in the document
    # --> add your Python code here
    freq = getTermFrequencies(doc["text"])

    # Removing the document from every corresponding posting list
    # --> add your Python code here
    for term in freq:
        removePosting(term, docId)

    # Deleting the document
    # --> add your Python code here
    documents.delete_one({"_id": docId})


#-------------------------------------------------------------------------
# Executing the sequence of operations
#-------------------------------------------------------------------------

# Operation 1: document 1 is obtained
document1 = {
    "_id": 1,
    "text": "Summer rain is common in Florida."
}

insertDocument(document1)


# Operation 2: document 2 is obtained
document2 = {
    "_id": 2,
    "text": "Summer is hot in Arizona."
}

insertDocument(document2)


# Operation 3: document 1 is updated
updateDocument(
    1,
    "Summer rain is hot rain in Florida."
)


# Operation 4: document 3 is obtained
document3 = {
    "_id": 3,
    "text": "Hot summer rain in California."
}

insertDocument(document3)


# Operation 5: document 2 is deleted
deleteDocument(2)

# Operation 6: print the content of the documents and inverted_index collections
# --> add your Python code here
print("\nDocuments\n=========\n")
for doc in documents.find():
    print(doc)

print("\nInverted Index\n==============\n")
for term in inverted_index.find():
    print(term)