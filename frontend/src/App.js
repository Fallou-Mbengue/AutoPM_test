import React, { useState, useEffect, useRef } from "react";

/**
 * Komkom News Listening Experience — App.js
 *
 * To override the backend base URL for API requests, set the env variable:
 * REACT_APP_API_BASE_URL. Default: http://127.0.0.1:8000/api/v1
 */
const API_BASE_URL =
  process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:8000/api/v1";

function formatTime(seconds) {
  const mm = Math.floor(seconds / 60)
    .toString()
    .padStart(2, "0");
  const ss = Math.floor(seconds % 60)
    .toString()
    .padStart(2, "0");
  return `${mm}:${ss}`;
}

export default function App() {
  const [loading, setLoading] = useState(true);
  const [episode, setEpisode] = useState(null);
  const [chapters, setChapters] = useState([]);
  const [error, setError] = useState(null);
  const [notFound, setNotFound] = useState(false);
  const audioRef = useRef(null);

  // Fetch latest Komkom News episode for the test user
  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    setError(null);
    setNotFound(false);
    setEpisode(null);
    setChapters([]);

    fetch(`${API_BASE_URL}/users/test_user_id_123/latest-komkom-news`)
      .then(async (res) => {
        if (res.status === 404) {
          if (isMounted) {
            setNotFound(true);
            setLoading(false);
          }
          return null;
        }
        if (!res.ok) {
          throw new Error("Failed to fetch episode data.");
        }
        return res.json();
      })
      .then((data) => {
        if (!data) return;
        if (isMounted) {
          setEpisode(data);
          // Fetch chapters for the episode
          fetch(
            `${API_BASE_URL}/episodes/${encodeURIComponent(data.id)}/chapters`
          )
            .then((res) => {
              if (!res.ok)
                throw new Error("Failed to fetch chapters for episode.");
              return res.json();
            })
            .then((chaptersData) => {
              if (isMounted) {
                setChapters(
                  Array.isArray(chaptersData)
                    ? chaptersData
                    : chaptersData.chapters || []
                );
                setLoading(false);
              }
            })
            .catch((err) => {
              if (isMounted) {
                setError("Could not load chapters.");
                setLoading(false);
              }
            });
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError("Could not load episode data.");
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  // Handle chapter click
  const handleChapterClick = (startTime) => {
    if (audioRef.current) {
      audioRef.current.currentTime = startTime;
      if (audioRef.current.paused) {
        audioRef.current.play();
      }
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <div className="max-w-xl mx-auto w-full p-4 flex flex-col gap-6">
        <h1 className="text-3xl font-bold text-center text-green-700 mb-2">
          Komkom News
        </h1>
        <p className="text-center text-gray-600 mb-4">
          Welcome! Listen to the latest Komkom News episode and explore opportunities.
        </p>

        {loading && (
          <div className="flex flex-col items-center justify-center py-16">
            <div className="w-12 h-12 border-4 border-green-400 border-t-transparent rounded-full animate-spin mb-2"></div>
            <span className="text-gray-600 mt-2">Loading...</span>
          </div>
        )}

        {error && (
          <div className="bg-red-100 border border-red-300 text-red-700 p-4 rounded text-center">
            {error}
          </div>
        )}

        {notFound && (
          <div className="bg-yellow-100 border border-yellow-300 text-yellow-800 p-4 rounded text-center">
            No Komkom News episode found for this user.
          </div>
        )}

        {!loading && !error && episode && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold text-green-800">
                {episode.title || "Komkom News Episode"}
              </h2>
              <p className="text-sm text-gray-500">
                Published:{" "}
                {episode.publication_date
                  ? new Date(episode.publication_date).toLocaleString()
                  : "Unknown"}
              </p>
            </div>
            <div>
              <audio
                controls
                ref={audioRef}
                src={`${API_BASE_URL}/episodes/${encodeURIComponent(
                  episode.id
                )}/audio.mp3`}
                className="w-full"
                preload="auto"
              >
                Your browser does not support the audio element.
              </audio>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-2 text-green-700">
                Chapters
              </h3>
              {chapters.length === 0 ? (
                <p className="text-gray-500 text-sm">
                  No chapters available for this episode.
                </p>
              ) : (
                <ul className="divide-y divide-gray-200 border rounded-lg bg-white overflow-hidden">
                  {chapters.map((chapter, idx) => (
                    <li
                      key={chapter.opportunity_id || idx}
                      className="flex items-center justify-between px-4 py-3 hover:bg-green-50 cursor-pointer transition"
                      onClick={() =>
                        handleChapterClick(chapter.start_time || 0)
                      }
                      tabIndex={0}
                      onKeyDown={(e) => {
                        if (e.key === "Enter" || e.key === " ") {
                          handleChapterClick(chapter.start_time || 0);
                        }
                      }}
                      aria-label={`Jump to chapter ${idx + 1}`}
                    >
                      <span className="font-mono text-green-800 font-semibold">
                        {formatTime(chapter.start_time || 0)}
                      </span>
                      <span className="text-gray-700 ml-2 flex-1">
                        Chapitre {idx + 1}
                      </span>
                      {/* Maybe display opportunity_id for debugging */}
                    </li>
                  ))}
                </ul>
              )}
            </div>
            <div className="flex justify-center mt-6">
              <button
                className="px-5 py-2 bg-green-600 text-white font-bold rounded shadow hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-400"
                onClick={() => alert("Feature coming soon!")}
                type="button"
              >
                Explore Opportunities
              </button>
            </div>
          </div>
        )}

        <footer className="text-xs text-gray-400 text-center mt-8">
          &copy; {new Date().getFullYear()} Komkom News. All rights reserved.
        </footer>
      </div>
    </div>
  );
}