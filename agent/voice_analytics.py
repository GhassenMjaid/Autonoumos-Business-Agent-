"""
Voice-Activated Business Analytics
Speak to your data, get instant insights
"""

from business_agent import BusinessAgent
import speech_recognition as sr
from groq import Groq
import io
import wave
import numpy as np
import whisper
import os

import io
import os
import wave
import numpy as np
import whisper
import speech_recognition as sr
from business_agent import BusinessAgent
from groq import Groq




class VoiceAnalytics:
    """Voice-activated business intelligence"""
    
    def __init__(self, api_key):
        print("\nInitializing Voice Analytics...")
        self.agent = BusinessAgent(api_key=api_key)
        self.groq_client = Groq(api_key=api_key)
        self.recognizer = sr.Recognizer()

        # Load Whisper model
        model_name = "medium"  # or "small", "base", "large"
        print(f"   [Loading Whisper {model_name}...]")
        self.whisper_model = whisper.load_model(model_name)
        print("   Whisper ready!\n")
        
        print("Voice Analytics ready!\n")

    def listen(self):
        print("Listening... (speak your question)")
        print("   [Calibrating... speak a few words now]")
    
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2.0)
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.dynamic_energy_adjustment_damping = 0.15
            self.recognizer.dynamic_energy_ratio = 1.5
        
            print(f"   [Threshold: {int(self.recognizer.energy_threshold)}] Speak now...")
        
            try:
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=15)
                return audio
            except sr.WaitTimeoutError:
                print("   No speech detected.")
                return None
    def transcribe(self, audio):
        """Transcribe with clean audio + normalization"""
        temp_wav = "temp_clean.wav"
        try:
            # Extract raw PCM
            wav_bytes = audio.get_wav_data()
            with io.BytesIO(wav_bytes) as wav_io:
                with wave.open(wav_io, 'rb') as wf:
                    sample_rate = wf.getframerate()
                    pcm_data = wf.readframes(wf.getnframes())
                    audio_np = np.frombuffer(pcm_data, dtype=np.int16).astype(np.float32)

            # Normalize
            if audio_np.max() > 0:
                audio_np = audio_np / np.max(np.abs(audio_np))

            # Write clean WAV
            with wave.open(temp_wav, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(16000)
                wf.writeframes((audio_np * 32767).astype(np.int16).tobytes())

            # Transcribe
            result = self.whisper_model.transcribe(
                temp_wav,
                language="en",
                fp16=False,
                temperature=0.0,
                beam_size=5
            )
            return result["text"].strip()

        except Exception as e:
            print(f"   Transcription error: {e}")
            return None
        finally:
            if os.path.exists(temp_wav):
                os.remove(temp_wav)

    # ADD THIS METHOD — YOU WERE MISSING IT!
    def run(self):
        """Main interaction loop"""
        print("="*70)
        print("VOICE-ACTIVATED ANALYTICS")
        print("="*70)
        print("\nHow to use:")
        print("  1. Press ENTER to start recording")
        print("  2. Speak your question clearly")
        print("  3. Wait for answer")
        print("  4. Type 'quit' to exit\n")
        print("Example questions:")
        print("  • Who are my top customers?")
        print("  • Show me monthly revenue trends")
        print("="*70)
        
        while True:
            try:
                user_input = input("\nPress ENTER to speak (or type 'quit'): ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye!")
                    break
                
                if user_input:
                    print(f"\nText mode: {user_input}")
                    answer = self.agent.ask(user_input)
                    print(answer)
                    continue
                
                print()
                audio = self.listen()
                if not audio:
                    continue
                
                text = self.transcribe(audio)
                if not text:
                    print("   Couldn't understand. Try again.")
                    continue
                
                print(f"\nYou said: \"{text}\"")
                answer = self.agent.ask(text)
                print(answer)
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("VOICE-ACTIVATED BUSINESS ANALYTICS")
    print("   Talk to Your Data")
    print("="*70)
    
    api_key = input("\nEnter your Groq API key: ").strip()
    if not api_key:
        print("API key required!")
        exit()
    
    try:
        voice_system = VoiceAnalytics(api_key=api_key)
        voice_system.run()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
    except Exception as e:
        print(f"\nError: {e}")
    # Get API key
    api_key = input("\n🔑 Enter your Groq API key: ").strip()
    
    if not api_key:
        print("❌ API key required!")
        exit()
    
    try:
        # Initialize and run
        voice_system = VoiceAnalytics(api_key=api_key)
        voice_system.run()
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")