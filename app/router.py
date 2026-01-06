# app/router.py
from fastapi import APIRouter, HTTPException
from langchain_core.messages import HumanMessage
from app.schemas import ChatRequest, ChatResponse
from app.agent import graph_runnable

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    # Setup Config (Session ID)
    config = {"configurable": {"thread_id": payload.thread_id}}
    
    # Siapkan Input
    inputs = {"messages": [HumanMessage(content=payload.message)]}
    
    try:
        # Panggil Agent
        result = graph_runnable.invoke(inputs, config=config)
        
        # Ambil jawaban terakhir
        last_response = result['messages'][-1].content
        
        return ChatResponse(
            response=last_response,
            thread_id=payload.thread_id
        )
        
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")