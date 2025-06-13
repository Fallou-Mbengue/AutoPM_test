import os
from jinja2 import Environment, FileSystemLoader
from pydub import AudioSegment, effects
from datetime import datetime
from deep_research.db.database import get_session
from db.models import Episode, EpisodeItem
from .utils import normalize_audio, overlay_background, upload_to_s3

# Placeholder for actual TTS and opportunity fetching
def fetch_opportunities(user_id, opportunity_list=None):
    # For now, just return the given list for tests
    return opportunity_list if opportunity_list is not None else []

def build_episode(
    user_id,
    lang,
    opportunity_list,
    work_dir,
    title,
    date,
    background_music_path=None,
    DummyTTS=None,
):
    session = get_session()
    # Fetch opportunities (for now: pass-through for tests)
    opportunities = fetch_opportunities(user_id, opportunity_list=opportunity_list)

    # Load templates
    env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
    intro_template = env.get_template('intro.j2')
    outro_template = env.get_template('outro.j2')
    news_template = env.get_template('news_item.j2')

    # Render templates
    intro_text = intro_template.render(lang=lang, title=title, date=date)
    outro_text = outro_template.render(lang=lang)
    news_texts = [news_template.render(opportunity=opp) for opp in opportunities]

    # Generate audio segments (using DummyTTS or real TTS)
    tts = DummyTTS() if DummyTTS else None
    intro_audio = tts.synthesize(intro_text)
    news_audios = [tts.synthesize(text) for text in news_texts]
    outro_audio = tts.synthesize(outro_text)

    # Normalize all audio segments
    intro_audio = normalize_audio(intro_audio)
    news_audios = [normalize_audio(a) for a in news_audios]
    outro_audio = normalize_audio(outro_audio)

    # Concatenate all audio segments, track start times for episode items
    start_times = []
    position = 0
    current_time = 0
    combined = intro_audio
    if news_audios:
        for i, news_audio in enumerate(news_audios):
            start_times.append((opportunities[i]['id'], current_time, position))
            combined += news_audio
            current_time += int(news_audio.duration_seconds)
            position += 1
    combined += outro_audio
    total_duration = int(combined.duration_seconds)

    # Overlay background music if provided
    if background_music_path:
        bg_audio = AudioSegment.from_file(background_music_path)
        combined = overlay_background(combined, bg_audio)

    # Export to MP3
    mp3_path = os.path.join(work_dir, 'episode.mp3')
    combined.export(mp3_path, format="mp3")

    # Export to HLS (placeholder for now)
    hls_dir = os.path.join(work_dir, 'hls')
    os.makedirs(hls_dir, exist_ok=True)
    m3u8_path = os.path.join(hls_dir, 'playlist.m3u8')
    # Placeholder: just create a dummy manifest and one MP3 segment
    segment_path = os.path.join(hls_dir, 'segment0.mp3')
    combined.export(segment_path, format="mp3")
    with open(m3u8_path, "w") as f:
        f.write("#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-TARGETDURATION:60\n#EXTINF:{},\nsegment0.mp3\n#EXT-X-ENDLIST\n".format(total_duration))

    # Upload to S3 (using placeholder)
    mp3_url = upload_to_s3(mp3_path, f"episodes/{user_id}/{os.path.basename(mp3_path)}")
    hls_url = upload_to_s3(m3u8_path, f"episodes/{user_id}/{os.path.basename(m3u8_path)}")

    # Insert Episode and EpisodeItems into DB
    episode = Episode(
        user_id=user_id,
        language=lang,
        title=title,
        date=date,
        audio_url=mp3_url,
        duration=total_duration,
    )
    session.add(episode)
    session.commit()  # To get episode.id

    for (opp_id, start_time, pos) in start_times:
        item = EpisodeItem(
            episode_id=episode.id,
            opportunity_id=opp_id,
            start_time=start_time,
            position=pos,
        )
        session.add(item)
    session.commit()

    return {
        "mp3_url": mp3_url,
        "hls_url": hls_url,
        "episode_id": episode.id,
        "duration": total_duration,
    }