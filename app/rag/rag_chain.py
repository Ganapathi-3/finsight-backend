from langchain.chains import RetrievalQA
from langchain.llms.fake import FakeListLLM
from app.rag.vector_store import get_vector_store

def get_rag_response(role: str, query: str):

    vectorstore = get_vector_store(role)
    retriever = vectorstore.as_retriever()

    llm = FakeListLLM(
        responses=["This is a simulated AI response for your department."]
    )

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever
    )

    return qa.run(query)