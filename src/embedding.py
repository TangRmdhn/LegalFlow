# !pip install langchain-core pandas

import os
import re
import pandas as pd
from typing import List, Dict
from langchain_core.documents import Document

# Set path folder data lu (sesuaikan kalau beda folder)
DATA_FOLDER = "../data"

# Config: Mapping nama file ke Metadata (Judul & Topik)
LAW_CONFIG = {
    "Nomor_5_Tahun_2020.pdf.txt": {
        "name": "Permenkominfo No 5 Tahun 2020",
        "tentang": "Penyelenggara Sistem Elektronik Lingkup Privat"
    },
    "PP_Nomor_71_Tahun_2019.pdf.txt": {
        "name": "PP No 71 Tahun 2019",
        "tentang": "Penyelenggaraan Sistem dan Transaksi Elektronik (PSTE)"
    },
    "PP_Nomor_80_Tahun_2019.pdf.txt": {
        "name": "PP No 80 Tahun 2019",
        "tentang": "Perdagangan Melalui Sistem Elektronik (PMSE)"
    },
    "UU_Nomor_1_Tahun_2024.pdf.txt": {
        "name": "UU No 1 Tahun 2024",
        "tentang": "Perubahan Kedua Atas UU ITE (Informasi & Transaksi Elektronik)"
    },
    "UU_Nomor_11_Tahun_2008.pdf.txt": {
        "name": "UU No 11 Tahun 2008",
        "tentang": "Informasi dan Transaksi Elektronik (UU ITE Original)"
    },
    "UU_Nomor_19_Tahun_2016.pdf.txt": {
        "name": "UU No 19 Tahun 2016",
        "tentang": "Perubahan Pertama Atas UU ITE"
    },
    "UU_Nomor_27_Tahun_2022.pdf.txt": {
        "name": "UU No 27 Tahun 2022",
        "tentang": "Pelindungan Data Pribadi (PDP)"
    },
    "UU_Nomor_28_Tahun_2014.pdf.txt": {
        "name": "UU No 28 Tahun 2014",
        "tentang": "Hak Cipta"
    }
}

class IndonesianLegalSplitter:
    def __init__(self, doc_name: str, doc_tentang: str):
        self.doc_name = doc_name
        self.doc_tentang = doc_tentang

    def clean_noise(self, text: str) -> str:
        # Bersihin header halaman, footer url, dll
        text = re.sub(r'--- HALAMAN \d+ ---', '', text)
        text = re.sub(r'\n\s*-\d+-\s*\n', '\n', text)
        text = re.sub(r'www\.peraturan\.go\.id', '', text)
        text = re.sub(r'\d+, No\.\d+', '', text) 
        text = re.sub(r'\n\s*\n', '\n', text)
        return text

    def split_text(self, raw_text: str) -> List[Document]:
        clean_content = self.clean_noise(raw_text)
        lines = clean_content.split('\n')
        chunks = []
        
        # State Variables
        current_bab = "Pembukaan"
        current_pasal_title = "Umum"
        current_pasal_num = 0 # Counter buat tracking urutan pasal
        buffer_text = []
        
        # Regex (Start of Line only)
        bab_pattern = re.compile(r'^\s*(BAB\s+[IVXLCDM]+)', re.IGNORECASE)
        pasal_pattern = re.compile(r'^\s*(Pasal\s+(\d+))', re.IGNORECASE)

        for line in lines:
            line = line.strip()
            if not line: continue

            # 1. Deteksi BAB
            match_bab = bab_pattern.match(line)
            if match_bab:
                current_bab = match_bab.group(1).upper()
                buffer_text.append(line)
                continue

            # 2. Deteksi Pasal (Pake Logic Urutan N+1)
            match_pasal = pasal_pattern.match(line)
            if match_pasal:
                found_full_title = match_pasal.group(1)
                found_num = int(match_pasal.group(2))
                
                # Logic: Hanya anggap pasal baru JIKA urut (angka sekarang + 1)
                if found_num == current_pasal_num + 1:
                    # Save pasal sebelumnya ke list chunks
                    if buffer_text:
                        full_content = "\n".join(buffer_text)
                        if len(full_content) > 20: 
                            # Context Injection: Masukin Judul UU ke dalam teks chunk
                            header = f"{self.doc_name} ({self.doc_tentang})"
                            content_display = f"{header}\n{current_bab} > {current_pasal_title}:\n{full_content}"
                            
                            chunks.append(Document(
                                page_content=content_display,
                                metadata={
                                    "source": self.doc_name,
                                    "tentang": self.doc_tentang,
                                    "bab": current_bab,
                                    "pasal": current_pasal_title,
                                    "pasal_num": current_pasal_num
                                }
                            ))
                    
                    # Reset state untuk pasal baru ini
                    current_pasal_title = found_full_title.title()
                    current_pasal_num = found_num
                    buffer_text = [line]
                else:
                    # Kalau gak urut (misal di bagian Mengingat), anggap teks biasa
                    buffer_text.append(line)
            else:
                # Konten biasa
                buffer_text.append(line)

        # Flush sisa buffer terakhir
        if buffer_text:
            full_content = "\n".join(buffer_text)
            header = f"{self.doc_name} ({self.doc_tentang})"
            chunks.append(Document(
                page_content=f"{header}\n{current_bab} > {current_pasal_title}:\n{full_content}",
                metadata={
                    "source": self.doc_name,
                    "tentang": self.doc_tentang,
                    "bab": current_bab,
                    "pasal": current_pasal_title
                }
            ))

        return chunks

def load_documents(folder_path):
    all_documents = []
    
    # Cek file yang ada di folder
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' tidak ditemukan.")
        return []

    files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]
    print(f"🔍 Ditemukan {len(files)} file .txt di folder '{folder_path}'\n")

    for filename in files:
        if filename in LAW_CONFIG:
            config = LAW_CONFIG[filename]
            file_path = os.path.join(folder_path, filename)
            
            print(f"🚀 Processing: {config['name']}...")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    raw_text = f.read()
                
                splitter = IndonesianLegalSplitter(
                    doc_name=config['name'],
                    doc_tentang=config['tentang']
                )
                
                file_chunks = splitter.split_text(raw_text)
                all_documents.extend(file_chunks)
                print(f"   ✅ OK. Generated {len(file_chunks)} chunks.")
                
            except Exception as e:
                print(f"   ❌ ERROR: {e}")
        else:
            print(f"⚠️  Skipping: {filename} (Tidak terdaftar di Config)")
            
    return all_documents

final_docs = load_documents(DATA_FOLDER)


from dotenv import load_dotenv
load_dotenv(override=True)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

vector_store = Chroma(
    collection_name="example_collection",
    embedding_function=embeddings,
    persist_directory="../db",  # Where to save data locally, remove if not necessary
)

vector_store.add_documents(final_docs)