import {isEmpty} from 'lodash';
import classNames from 'classnames';
import videojs from 'video.js';

type VjsPlayer = ReturnType<typeof videojs>;
const isNotEmpty = (x: any) => !isEmpty(x);

/**
 * Get bem classes
 *
 * @param {String} block 
 * @param {String} element 
 * @param {Object} modifier 
 * @return {String}
 */
export function bem(block: any, element: any, modifier: any) {
    const main = [block, element].filter(isNotEmpty).join('__');
    const classes = [main];

    if (!isEmpty(modifier)) {
        const modifiers = classNames(modifier).split(' ');

        modifiers.forEach((suffix: any) => {
            classes.push(main + '--' + suffix);
        });
    }

    return classes.join(' ');
}

function initPlayer(
    el: HTMLElement,
    retries = 3,
    delay = 100,
    onReady: (player: VjsPlayer | null) => void
): () => void {
    let cancelled = false;
    let timeoutId: ReturnType<typeof setTimeout> | null = null;

    function attempt(remainingTries: number): void {
        if (cancelled) return;
        if (!document.body.contains(el)) { onReady(null); return; }

        if (typeof videojs === 'function') {
            try {
                const player = videojs(el, {
                    controls: true,
                    preload: 'auto',
                    fluid: true,
                });
                el.setAttribute('data-vjs-initialized', 'true');
                onReady(player);
                return;
            } catch (err) {
                console.warn('video.js init failed, retrying...', err);
            }
        }

        if (remainingTries > 0) {
            timeoutId = setTimeout(() => attempt(remainingTries - 1), delay);
        } else {
            console.warn('video.js not ready after retries for', el);
            onReady(null);
        }
    }

    attempt(retries);

    // Return cancel function for any pending timeouts in cases of unmounts and such
    return () => {
        cancelled = true;
        if (timeoutId) clearTimeout(timeoutId);
    };
}

export function setupMediaPlayers(root: HTMLElement) {
    const players: Array<VjsPlayer> = [];
    const timeoutCancels: Array<() => void> = [];
    const elements = root.querySelectorAll<HTMLVideoElement | HTMLAudioElement>('video, audio');

    elements.forEach((element) => {
        if (element.getAttribute('data-vjs-initialized')) return;

        const disable = element.getAttribute('data-disable-download') === 'true';

        if (disable) {
            // Remove native controls everywhere on all major browsers
            element.removeAttribute('controls');
            // Additional override for browsers that support controlsList
            element.setAttribute('controlsList', 'nodownload');
            // Disable right-click context menu on all browsers
            element.addEventListener('contextmenu', (e) => e.preventDefault());

            if (element instanceof HTMLVideoElement) {
                element.classList.add('video-js', 'vjs-big-play-centered');
            } else if (element instanceof HTMLAudioElement) {
                element.classList.add('video-js');
            }

            const cancel = initPlayer(element, 3, 100, (player: VjsPlayer | null) => {
                if (player) players.push(player);
            });
            timeoutCancels.push(cancel);
        } else {
            // Enable all native controls
            element.setAttribute('controls', '');
        }
    });

    return () => {
        timeoutCancels.forEach((c) => c());
        players.forEach((p) => p?.dispose?.());
    };
}
