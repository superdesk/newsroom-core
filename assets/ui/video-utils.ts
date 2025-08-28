import videojs from 'video.js';

export function setupVideoPlayers(root: HTMLElement) {
    const players: any[] = [];
    root.querySelectorAll('video').forEach((element) => {
        if (element.getAttribute('data-vjs-initialized')) return;
        const disable = element.getAttribute('data-disable-download') === 'true';

        if (disable) {
            element.setAttribute('controlsList', 'nodownload');
            element.addEventListener('contextmenu', (e) => e.preventDefault());
            element.removeAttribute('controls');
        } else {
            element.setAttribute('controls', '');
        }

        element.setAttribute('data-vjs-initialized', 'true');
        element.classList.add('video-js', 'vjs-big-play-centered');

        const player = videojs(element, {
            controls: true,
            preload: 'auto',
            fluid: true,
        });
        players.push(player);
    });

    return () => players.forEach((player) => player.dispose());
}
