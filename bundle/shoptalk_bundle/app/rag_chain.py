from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import HuggingFacePipeline
from langchain import PromptTemplate, LLMChain
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from .config import CHROMA_DIR, LLM_MODEL, EMBED_MODEL, LORA_OUTPUT


def get_retriever(k=8):
    embeddings = SentenceTransformerEmbeddings(model_name=str(LORA_OUTPUT if LORA_OUTPUT.exists() else EMBED_MODEL))
    store = Chroma(collection_name="products", persist_directory=str(CHROMA_DIR), embedding_function=embeddings)
    return store.as_retriever(search_kwargs={"k": k})


def get_llm():
    tok = AutoTokenizer.from_pretrained(LLM_MODEL)
    model = AutoModelForCausalLM.from_pretrained(LLM_MODEL, device_map='auto', torch_dtype='auto')
    gen = pipeline('text-generation', model=model, tokenizer=tok, max_length=512)
    return HuggingFacePipeline(pipeline=gen)


template = PromptTemplate(
    input_variables=['context', 'question'],
    template="""You are ShopTalk, an expert shopping assistant.
Context:
{context}

User query: {question}
Answer with the best matching products, each on a new line as:
- <Title> – URL: <url>
"""
)


def build_chain():
    return get_retriever(), LLMChain(llm=get_llm(), prompt=template)
