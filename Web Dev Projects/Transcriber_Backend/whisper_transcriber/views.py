import os
import torch
import whisper
import librosa
import numpy as np
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.storage import default_storage
from together import Together

# Access preloaded model
whisper_model = whisper.load_model("base")
client = Together(api_key="40e99ab44b369b3bf108d547d07ef7d88fcfe9dc894051d89d4efba30065b2df")

def home(request):
    """Render the index.html template."""
    return render(request, "index.html")

@csrf_exempt
def transcribe_audio(request):
    """Process uploaded audio file and return transcription."""
    if request.method == "POST" and request.FILES.get("audio_file"):
        audio_file = request.FILES["audio_file"]
        
        print("Hello Here I am")
        # Save temporarily and load
        file_path = default_storage.save("temp_audio.wav", audio_file)
        print("Hello Here I am 2")
        result = whisper_model.transcribe(file_path)
        print("Hello Here I am 3")
        result = result["text"]
        print("Result =>", result)
        return JsonResponse({"result": result})

    return JsonResponse({"error": "No valid audio received"}, status=400)


def index(request):
    if request.method == 'POST':
        audio_file = request.FILES.get('audio')
        input_lang = request.POST.get('input_lang')
        output_lang = request.POST.get('output_lang')

        file_url = None
        if audio_file:
            file_path = default_storage.save(f"uploads/{audio_file.name}", audio_file)
            file_url = os.path.join(settings.MEDIA_URL, file_path)

        file_path_final = default_storage.save(f"uploads/{audio_file.name}_temp_audio.wav", audio_file)
        file_path_final = os.path.join(settings.MEDIA_ROOT, "uploads", f"{audio_file.name}_temp_audio.wav")
        print(f"Absolute File Path: {file_path_final}")
        result = whisper_model.transcribe(file_path_final)
        result = result["text"]                       

        response = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3-8B-Instruct-Turbo",
            messages=[{"role": "user", "content": f"Split the following paragraph into individual sentences. Your response should not have any other sentence.:\n\n{result}\n\nSentences:"}],
        )

        print(response.choices[0].message.content)
                
        # 🪓 Try splitting by newline or numbered bullets
        sentences = [line.strip("1234567890. ").strip() for line in response.choices[0].message.content.strip().split("\n") if line.strip()]

        print(sentences)

        final_result = []
        for i in sentences:
            response = client.chat.completions.create(
                model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
                messages=[{"role": "user", "content": f"""Forget the last prompt. Translate the following sentence into spanish.
        For each sentence, return the output in the following format:

            [Original Sentence]
            [Translation of Sentence]

        Do not provide any word-by-word or phrase-level breakdowns.
        Do not add explanations or notes. Only return:

            [Original Sentence]
            [Translation of Sentence]

        Now translate this sentence:

        {i}"""}],
            )
            
            print(response.choices[0].message.content)
            
            lines = response.choices[0].message.content.strip().split('\n')
    
            # Check if the number of lines is even (to ensure every German sentence has a Spanish translation)
            if len(lines) % 2 != 0:
                print("Warning: The number of sentences is odd. One sentence may not have a translation.")
            
            # Split lines into two lists: one for the German sentences and one for the Spanish translations
            original_sentences = lines[::2]  # Get sentences at even indices (starting from 0)
            translated_sentences = lines[1::2]  # Get sentences at odd indices (starting from 1)
            
            print(original_sentences, translated_sentences)    

            final_result.append(translated_sentences[0])

        
        context = {
            'audio_name': audio_file.name if audio_file else 'No file',
            'audio_url': file_url,
            'input_lang': input_lang,
            'output_lang': output_lang,
            'final_result': ". ".join(final_result),
            'success': True,
        }

        default_storage.delete(file_path)
        default_storage.delete(file_path_final)

        return render(request, 'index.html', context)

    return render(request, 'index.html')