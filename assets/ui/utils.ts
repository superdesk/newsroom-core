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

function tryInitPlayer(el: HTMLElement, retries = 3, delay = 100): VjsPlayer | null {
    if (!document.body.contains(el)) return null;

    if (typeof videojs !== 'function') {
        if (retries > 0) {
            setTimeout(() => tryInitPlayer(el, retries - 1, delay), delay);
        } else {
            console.warn('video.js not ready after retries for', el);
        }
        return null;
    }

    try {
        const player = videojs(el, {
            controls: true,
            preload: 'auto',
            fluid: true,
        });
        // Mark element initialized only after success
        el.setAttribute('data-vjs-initialized', 'true');
        return player;
    } catch (err) {
        console.warn('video.js init failed, retrying...', err);
        if (retries > 0) {
            setTimeout(() => tryInitPlayer(el, retries - 1, delay), delay);
        }
        return null;
    }
}

export function setupMediaPlayers(root: HTMLElement) {
    const players: Array<VjsPlayer> = [];
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

            const player = tryInitPlayer(element);
            if (player) players.push(player);
        } else {
            // Enable all native controls
            element.setAttribute('controls', '');
        }
    });

    return () => {
        players.forEach((player) => {
            if (player && typeof player.dispose === 'function') {
                player.dispose();
            }
        });
    };
}
