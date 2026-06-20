from fastapi import APIRouter, Depends, HTTPException
# Anggap saja kamu nanti mengimpor client supabase dari folder services/config kalian
# from api.services.supabase import supabase 

router = APIRouter(
    prefix="/history",
    tags=["History"]
)

# 1. Endpoint untuk mengambil semua riwayat prediksi milik tim marketing
@router.get("/")
async def get_prediction_history():
    try:
        # Contoh logika mengambil data dari tabel 'history' di Supabase
        # response = supabase.table("history").select("*").execute()
        # return response.data
        
        return {"status": "success", "message": "Ini adalah tempat untuk menampilkan riwayat prediksi tim marketing."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 2. Endpoint untuk menyimpan riwayat prediksi baru
@router.post("/save")
async def save_prediction_history(data: dict):
    try:
        # Contoh logika memasukkan data ke tabel 'history' di Supabase
        # response = supabase.table("history").insert(data).execute()
        
        return {"status": "success", "message": "Riwayat prediksi berhasil disimpan ke database!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))