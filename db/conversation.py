import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from pymongo import DESCENDING
from db.mongo import get_collection

# connecting to Conversation collection
conversations = get_collection("Conversation")

# creating index to find the recent interaction
conversations.create_index([("last_interacted", DESCENDING)])

# get the current time for timestamping
def now_utc():
    return datetime.now(timezone.utc)

# to create new unique conv id
def create_new_conversation_id() -> str:
    return str(uuid.uuid4())

# create conv id and timestamp only if role and content are given
def create_new_conversation(title: Optional[str] = None, role: Optional[str] = None, content: Optional[str] = None) -> str:
    conv_id = create_new_conversation_id()
    ts = now_utc()

    doc = {
        "_id" : conv_id,
        "title" : title or "Untitled Conversation",
        "messages" : [],
        "last_interacted" : ts,
    }

    if role and content:
        doc["messages"].append({"role": role, "content": content, "ts" : ts})
    conversations.insert_one(doc)
    return conv_id

# to add message by getting a id
def add_message(conv_id: str, role: str, content: str) -> bool:
    ts = now_utc()
    res = conversations.update_one(
        {"_id": conv_id},
        {
            # to add new item to list like append
            "$push": {"messages": {"role": role, "content": content, "ts": ts}},
            # to update the last interaction
            "$set": {"last_interacted": ts},
        },
    )
    return res.matched_count == 1

# find conv by conv_id and update the last interacted and return entire conv
def get_conversation(conv_id: str) -> Optional[Dict[str, Any]]:
    ts = now_utc()
    doc = conversations.find_one_and_update(
        {"_id": conv_id},
        {"$set": {"last_interacted": ts}},
        return_document= True
    )
    return doc

# get all conv by title and sort on last interacted
def get_all_conversation() -> Dict[str, str]:
    cursor = conversations.find({}, {"title": 1}).sort("last_interacted", DESCENDING)
    return {doc["_id"] : doc["title"] for doc in cursor}
