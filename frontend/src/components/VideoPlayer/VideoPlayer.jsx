import { useEffect, useRef, useState } from 'react';
import styles from './VideoPlayer.module.css';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function VideoPlayer({ channel }) {
  const playerRef = useRef(null);
  const clapprRef = useRef(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!channel?.slug) {
      if (clapprRef.current) {
        try { clapprRef.current.destroy(); } catch (e) {}
        clapprRef.current = null;
      }
      const el = document.getElementById('video-player');
      if (el) el.innerHTML = '';
      setError(null);
      return;
    }

    if (clapprRef.current) {
      try { clapprRef.current.destroy(); } catch (e) {}
      clapprRef.current = null;
    }
    const el = document.getElementById('video-player');
    if (el) el.innerHTML = '';

    setLoading(true);
    setError(null);

    const streamUrl = `${BASE_URL}/api/streams/${channel.slug}/playlist.m3u8`;

    if (window.Clappr) {
      clapprRef.current = new window.Clappr.Player({
        source: streamUrl,
        parentId: '#video-player',
        width: '100%',
        height: '100%',
        autoPlay: true,
        poster: channel.logo_url || '',
      });
      setLoading(false);
    } else {
      setError('Player no disponible');
      setLoading(false);
    }

    return () => {
      if (clapprRef.current) {
        try { clapprRef.current.destroy(); } catch (e) {}
        clapprRef.current = null;
      }
      const el = document.getElementById('video-player');
      if (el) el.innerHTML = '';
    };
  }, [channel?.slug]);

  return (
    <div className={styles.playerWrapper}>
      <div id="video-player" ref={playerRef} className={styles.player} />
      {!channel && (
        <div className={styles.placeholder}>
          <p>Selecciona un canal para ver el stream</p>
        </div>
      )}
      {loading && (
        <div className={styles.overlay}><p>Cargando stream...</p></div>
      )}
      {error && (
        <div className={styles.error}><p>{error}</p></div>
      )}
    </div>
  );
}
