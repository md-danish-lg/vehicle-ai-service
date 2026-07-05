from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from groq import Groq
from dotenv import load_dotenv
import chromadb

load_dotenv()


app = FastAPI()
llm_client = Groq()
chroma_client = chromadb.PersistentClient(path="./chroma_data")
collection = chroma_client.get_or_create_collection("vehicle_collection")




class RepairHistory(BaseModel):
    id: str = Field(min_length=1)
    text: str = Field(min_length=1)


class RepairHistoryQuery(BaseModel):
    text: str = Field(min_length=1)
    result_length: int = 3

@app.get("/")
async def hello_world():
    return {"text":"hello world"}


@app.get("/health")
async def app_status():
    return {"status" : "ok"}


@app.post("/repair-history/add")
async def add_repair_history(repair: RepairHistory):
    collection.add(
        documents=[repair.text], 
        ids=[repair.id]
    )
    return {"status": "record created successfully"}


@app.post("/repair-history/search")
async def search_repair_history(repair: RepairHistoryQuery):    
    result = collection.query(query_texts=[repair.text], n_results=repair.result_length)


    documents = result['documents'][0]
    if not documents:
        return {"result": [], "message": "No matching records found"}



    return {"result": documents}



@app.post("/repair-history/summarize")
async def summarize_repair_history(query: RepairHistoryQuery):
    try:
        result = collection.query(
            query_texts=[query.text],
            n_results=query.result_length
        )

        documents = result['documents'][0]

        if not documents:
            raise HTTPException(status_code=404, detail="Repair History Not Found")
        
        summary = llm_client.chat.completions.create(
            messages=[
                {
                        "role": "user",
                        "content": f"summarize the vehicle's repair history based on these records - {documents}",
                    }
                ],
                model="llama-3.3-70b-versatile"
        )

        return {
            "summary": summary.choices[0].message.content,
            "records_used": len(documents)
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM CALL FAILED - {str(e)}")
