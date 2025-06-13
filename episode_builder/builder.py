import json
import os
from jinja2 import Template
from episode_builder.utils import concatenate_audios, export_silence
from pydub import AudioSegment

class EpisodeBuilder:
    # Hardcoded templates for now
    TEMPLATES = {
        'intro_fr': Template("Bienvenue à notre épisode: {{ episode_title }}"),
        'intro_wo': Template("Jamm rekk ci wetu: {{ episode_title }}"),
        'outro_fr': Template("Merci d'avoir écouté cet épisode."),
        'outro_wo': Template("Jërëjëf ci yoon wi. Ba beneen yoon.")
    }

    def __init__(self, tts_generator, work_dir="episode_output"):
        self.tts_generator = tts_generator
        self.work_dir = work_dir
        os.makedirs(self.work_dir, exist_ok=True)

    def build_episode(self, episode_title, chapters):
        """
        chapters: List of dicts with 'title', 'text', and 'lang' keys.
        """
        audio_segments = []

        # Render and synthesize intro
        intro_fr_text = self.TEMPLATES['intro_fr'].render(episode_title=episode_title)
        intro_wo_text = self.TEMPLATES['intro_wo'].render(episode_title=episode_title)
        intro_fr_mp3 = self.tts_generator.synthesize(intro_fr_text, lang="fr")
        intro_wo_mp3 = self.tts_generator.synthesize(intro_wo_text, lang="wo")
        audio_segments.append(AudioSegment.from_mp3(intro_fr_mp3))
        audio_segments.append(export_silence(duration_ms=500))
        audio_segments.append(AudioSegment.from_mp3(intro_wo_mp3))
        audio_segments.append(export_silence(duration_ms=1000))

        chapter_json = []
        # Render and synthesize chapters
        for i, chapter in enumerate(chapters, 1):
            mp3_path = self.tts_generator.synthesize(chapter['text'], lang=chapter['lang'])
            audio = AudioSegment.from_mp3(mp3_path)
            audio_segments.append(audio)
            audio_segments.append(export_silence(duration_ms=1000))
            chapter_json.append({
                "number": i,
                "title": chapter['title'],
                "lang": chapter['lang'],
                "text": chapter['text'],
                "audio_path": mp3_path
            })

        # Render and synthesize outros
        outro_fr_text = self.TEMPLATES['outro_fr'].render()
        outro_wo_text = self.TEMPLATES['outro_wo'].render()
        outro_fr_mp3 = self.tts_generator.synthesize(outro_fr_text, lang="fr")
        outro_wo_mp3 = self.tts_generator.synthesize(outro_wo_text, lang="wo")
        audio_segments.append(export_silence(duration_ms=500))
        audio_segments.append(AudioSegment.from_mp3(outro_fr_mp3))
        audio_segments.append(export_silence(duration_ms=500))
        audio_segments.append(AudioSegment.from_mp3(outro_wo_mp3))

        # Assemble episode audio
        episode_audio = concatenate_audios(audio_segments)
        episode_mp3_path = os.path.join(self.work_dir, "episode.mp3")
        episode_audio.export(episode_mp3_path, format="mp3")

        # Save chapter JSON
        chapter_json_path = os.path.join(self.work_dir, "chapters.json")
        with open(chapter_json_path, "w", encoding="utf-8") as f:
            json.dump(chapter_json, f, ensure_ascii=False, indent=2)

        return chapter_json_path  # Return path to JSON file