import os
import re
import joblib
import pandas as pd
import numpy as np
import logging

try:
    import emoji
except ImportError:
    # simple fallback if emoji is not installed, though we added it to requirements
    class EmojiFallback:
        def demojize(self, text, delimiters):
            return text
    emoji = EmojiFallback()

try:
    from deep_translator import GoogleTranslator
except ImportError:
    GoogleTranslator = None

logger = logging.getLogger("nlp_service")
logging.basicConfig(level=logging.INFO)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NLP_DIR = os.path.join(BASE_DIR, "models", "nlp")

SLANG_ID = {
    'gk': 'tidak', 'gak': 'tidak', 'ga': 'tidak', 'nggak': 'tidak',
    'bgt': 'sangat', 'bngt': 'sangat',
    'udh': 'sudah', 'udah': 'sudah',
    'blm': 'belum', 'belom': 'belum',
    'yg': 'yang', 'krn': 'karena', 'karna': 'karena',
    'dgn': 'dengan', 'tp': 'tapi', 'tpi': 'tapi',
    'utk': 'untuk', 'buat': 'untuk',
    'jg': 'juga', 'lg': 'lagi', 'jd': 'jadi',
    'klo': 'kalau', 'kalo': 'kalau',
    'aja': 'saja', 'doang': 'saja',
    'gue': 'saya', 'gw': 'saya',
    'lo': 'kamu', 'lu': 'kamu',
    'skrg': 'sekarang', 'kmrn': 'kemarin',
    'makasih': 'terima kasih', 'mksh': 'terima kasih',
    'kyk': 'seperti', 'kayak': 'seperti',
    'gimana': 'bagaimana', 'gmn': 'bagaimana',
    'nyebelin': 'menjengkelkan', 'kesel': 'kesal',
    'parah': 'parah', 'males': 'malas',
    'buffering': 'buffering', 'lag': 'lemot',
}

NEGATIONS_EN = {'not', "n't", 'no', 'never', "won't", "can't",
                "couldn't", "doesn't", "isn't", "wasn't"}
NEGATIONS_ID = {'tidak', 'tak', 'bukan', 'belum', 'jangan', 'tanpa'}

def normalize_slang(text: str, lang: str) -> str:
    """Ganti slang Indonesia dengan kata baku."""
    if lang != 'id':
        return text
    tokens = text.split()
    return ' '.join([SLANG_ID.get(t.lower(), t) for t in tokens])

def mark_negation(text: str, lang: str) -> str:
    neg_words = NEGATIONS_EN if lang == 'en' else (NEGATIONS_EN | NEGATIONS_ID)
    tokens = text.split()
    result, negate, window = [], False, 0
    for tok in tokens:
        tok_clean = tok.lower().rstrip('.,!?')
        if tok_clean in neg_words:
            result.append(tok)
            negate, window = True, 0
        elif negate:
            result.append('NOT_' + tok)
            window += 1
            if window >= 3:
                negate, window = False, 0
        else:
            result.append(tok)
    return ' '.join(result)

def preprocess_text(text: str, lang: str = 'en') -> str:
    if not isinstance(text, str) or text.strip() == '':
        return ''

    # Emoji to text
    text = emoji.demojize(text, delimiters=(' ', ' '))

    text = text.lower()

    # Hapus URL, mention, tag HTML
    text = re.sub(r'http\S+|www\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'<[^>]+>', '', text)

    # Normalisasi karakter berulang
    text = re.sub(r'(.)\1{2,}', r'\1\1', text)

    # Normalisasi slang
    text = normalize_slang(text, lang)

    # Hapus karakter non-standar
    text = re.sub(r"[^a-zA-Z0-9\s.,!?'\"-]", ' ', text)

    # Marking negasi
    text = mark_negation(text, lang)

    # Rapikan spasi
    text = re.sub(r'\s+', ' ', text).strip()

    return text

class NLPPredictionService:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.label_encoder = None
        self._translation_cache = {}
        
        self.load_artifacts()

    def load_artifacts(self):
        model_path = os.path.join(NLP_DIR, "lgb_sentiment_model.pkl")
        vectorizer_path = os.path.join(NLP_DIR, "tfidf_vectorizer.pkl")
        le_path = os.path.join(NLP_DIR, "label_encoder.pkl")
        
        try:
            if os.path.exists(model_path):
                self.model = joblib.load(model_path)
                logger.info(f"Loaded NLP model from {model_path}")
            else:
                logger.warning(f"NLP model not found at {model_path}")
                
            if os.path.exists(vectorizer_path):
                self.vectorizer = joblib.load(vectorizer_path)
                logger.info(f"Loaded TF-IDF vectorizer from {vectorizer_path}")
            else:
                logger.warning(f"Vectorizer not found at {vectorizer_path}")
                
            if os.path.exists(le_path):
                self.label_encoder = joblib.load(le_path)
                logger.info(f"Loaded label encoder from {le_path}")
            else:
                logger.warning(f"Label encoder not found at {le_path}")
        except Exception as e:
            logger.error(f"Error loading NLP artifacts: {e}")

    def translate_to_en(self, text: str) -> str:
        if not text or not GoogleTranslator:
            return text
            
        try:
            # Quick clean before translation to improve accuracy
            clean = re.sub(r'http\S+|www\S+', '', text)
            clean = re.sub(r'@\w+', '', clean)
            clean = normalize_slang(clean, 'id')
            
            # Check translation cache first
            if clean in self._translation_cache:
                return self._translation_cache[clean]
                
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                translator = GoogleTranslator(source='id', target='en')
                future = executor.submit(translator.translate, clean)
                try:
                    translated = future.result(timeout=2.0)
                    val = translated if translated else text
                    self._translation_cache[clean] = val
                    return val
                except concurrent.futures.TimeoutError:
                    logger.warning("Translation timed out (2.0s limit). Falling back to original text.")
                    return text
        except Exception as e:
            logger.warning(f"Translation failed: {e}. Falling back to original text.")
            return text

    def translate_batch_to_en(self, texts: list) -> list:
        if not texts or not GoogleTranslator:
            return texts
            
        # Clean and count frequencies to prioritize translating most frequent texts
        clean_to_orig = {}
        frequencies = {}
        for t in texts:
            clean = re.sub(r'http\S+|www\S+', '', t)
            clean = re.sub(r'@\w+', '', clean)
            clean = normalize_slang(clean, 'id')
            if clean not in clean_to_orig:
                clean_to_orig[clean] = []
            clean_to_orig[clean].append(t)
            frequencies[clean] = frequencies.get(clean, 0) + 1
            
        unique_cleans = list(clean_to_orig.keys())
        
        # Check cache first for what we already translated
        needed_translation = []
        translated_map = {}
        
        for uc in unique_cleans:
            if uc in self._translation_cache:
                translated_map[uc] = self._translation_cache[uc]
            else:
                needed_translation.append(uc)
                
        # If we have texts that actually need translation
        if needed_translation:
            # Sort by frequency to translate the most common sentences first
            needed_translation.sort(key=lambda x: frequencies.get(x, 0), reverse=True)
            
            # Limit online translations to max 250 unique strings to prevent rate limits
            # and maintain fast API responses.
            MAX_TRANSLATIONS = 250
            to_translate = needed_translation[:MAX_TRANSLATIONS]
            to_bypass = needed_translation[MAX_TRANSLATIONS:]
            
            # For bypassed, keep them as original (no translation)
            for tb in to_bypass:
                translated_map[tb] = tb
                
            if to_translate:
                # Use translate_batch in chunks of 50 to optimize HTTP calls
                chunk_size = 50
                chunks = [to_translate[i:i + chunk_size] for i in range(0, len(to_translate), chunk_size)]
                
                import concurrent.futures
                
                def translate_chunk(chunk):
                    try:
                        translator = GoogleTranslator(source='id', target='en')
                        translated_chunk = translator.translate_batch(chunk)
                        return dict(zip(chunk, translated_chunk))
                    except Exception as ex:
                        logger.warning(f"Batch chunk translation failed: {ex}")
                        return {item: item for item in chunk}
                
                # Execute chunk translations with a timeout
                with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                    future_to_chunk = {executor.submit(translate_chunk, chunk): chunk for chunk in chunks}
                    for future in concurrent.futures.as_completed(future_to_chunk):
                        try:
                            # 6 seconds limit per chunk translation
                            res = future.result(timeout=6.0)
                            for k, v in res.items():
                                val = v if v else k
                                translated_map[k] = val
                                self._translation_cache[k] = val
                        except Exception as ex:
                            chunk = future_to_chunk[future]
                            logger.error(f"Chunk translation timed out or failed: {ex}")
                            for k in chunk:
                                if k not in translated_map:
                                    translated_map[k] = k
                                    
        # Reconstruct the original list in original order
        translated_results = []
        for t in texts:
            clean = re.sub(r'http\S+|www\S+', '', t)
            clean = re.sub(r'@\w+', '', clean)
            clean = normalize_slang(clean, 'id')
            translated_results.append(translated_map.get(clean, t))
            
        return translated_results

    def predict_single(self, text: str, lang: str = 'id') -> dict:
        # Translate to English if the model is trained only on English
        processed_lang = lang
        processed_text = text
        if lang == 'id':
            logger.info(f"Translating Indonesian text to English...")
            processed_text = self.translate_to_en(text)
            processed_lang = 'en' # Process as English from here on
            
        clean_text = preprocess_text(processed_text, lang=processed_lang)
        
        if not self.model or not self.vectorizer or not self.label_encoder:
            logger.warning("Mocking NLP prediction due to missing artifacts.")
            return {
                "text": text,
                "sentiment": "Neutral",
                "confidence": 0.5
            }
            
        try:
            vec = self.vectorizer.transform([clean_text])
            probs = self.model.predict_proba(vec)[0]
            pred_idx = np.argmax(probs)
            confidence = float(probs[pred_idx])
            
            # Use label encoder to get the original label name
            sentiment_label = self.label_encoder.inverse_transform([pred_idx])[0]
            
            return {
                "text": text,
                "sentiment": str(sentiment_label),
                "confidence": round(confidence, 4)
            }
        except Exception as e:
            logger.error(f"NLP Prediction failed: {e}")
            raise e

    def predict_batch(self, texts: list, lang: str = 'id') -> list:
        processed_texts = texts
        processed_lang = lang
        
        if lang == 'id':
            logger.info(f"Translating {len(texts)} Indonesian texts to English in parallel...")
            processed_texts = self.translate_batch_to_en(texts)
            processed_lang = 'en'
            
        clean_texts = [preprocess_text(t, lang=processed_lang) for t in processed_texts]
        
        if not self.model or not self.vectorizer or not self.label_encoder:
            return [{"text": t, "sentiment": "Neutral", "confidence": 0.5} for t in texts]
            
        try:
            vecs = self.vectorizer.transform(clean_texts)
            probs = self.model.predict_proba(vecs)
            
            results = []
            for i, p in enumerate(probs):
                pred_idx = np.argmax(p)
                conf = float(p[pred_idx])
                label = self.label_encoder.inverse_transform([pred_idx])[0]
                results.append({
                    "text": texts[i],
                    "sentiment": str(label),
                    "confidence": round(conf, 4)
                })
            return results
        except Exception as e:
            logger.error(f"NLP Batch prediction failed: {e}")
            raise e

# Global single instance
nlp_service = NLPPredictionService()
