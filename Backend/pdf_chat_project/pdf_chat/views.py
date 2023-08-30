from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
import pickle
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks import get_openai_callback
from rest_framework.decorators import api_view
os.environ["OPENAI_API_KEY"] = "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"
@csrf_exempt
@api_view(['POST'])
def pdf_chat_backend(request):
    if request.method == 'POST':
        pdf_file = request.FILES.get('pdf')
        if pdf_file:
            pdf_reader = PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=20000,
                chunk_overlap=20000,
                length_function=len
            )
            chunks = text_splitter.split_text(text=text)

            store_name = pdf_file.name[:-4]

            if os.path.exists(f"{store_name}.pkl"):
                with open(f"{store_name}.pkl", "rb") as f:
                    VectorStore = pickle.load(f)
            else:
                embeddings = OpenAIEmbeddings(openai_api_key='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')
                VectorStore = FAISS.from_texts(chunks, embedding=embeddings)
                with open(f"{store_name}.pkl", "wb") as f:
                    pickle.dump(VectorStore, f)

            query = request.POST.get('query')
            if query:
                docs = VectorStore.similarity_search(query=query, k=3)
                llm = OpenAI()
                chain = load_qa_chain(llm=llm, chain_type="stuff")
                with get_openai_callback() as cb:
                    response = chain.run(input_documents=docs, question=query)
                return JsonResponse({'response': response})
    return JsonResponse({'response': 'Invalid request.'})
