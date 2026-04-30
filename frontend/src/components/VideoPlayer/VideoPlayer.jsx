import styles from './VideoPlayer.module.css';

export default function VideoPlayer({ channel }) {
  if (!channel) {
    return (
      <div className={styles.playerWrapper}>
        <div className={styles.placeholder}>
          <p>Selecciona un canal para ver el stream</p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.playerWrapper}>
      <iframe
        key={channel.slug}
        src={channel.stream_url}
        className={styles.player}
        allowFullScreen
        allow="autoplay; fullscreen; picture-in-picture"
        frameBorder="0"
        title={channel.name}
        scrolling="no"
        style={{ border: 'none' }}
      />
    </div>
  );
}
