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

export function setupMediaPlayers(root: HTMLElement) {
    const players: Array<VjsPlayer> = [];

    root.querySelectorAll('video, audio').forEach((element) => {
        if (element.getAttribute('data-vjs-initialized')) return;

        try {
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

                // Guard to return early if import is not resolved
                if (typeof videojs !== 'function') {
                    console.warn('videojs not ready yet'); 
                    return;
                }

                const player = videojs(element, {
                    controls: true,
                    preload: 'auto',
                    fluid: true,
                });
                players.push(player);

                // Mark element as initialized only after successful initialization to allow for retrys
                element.setAttribute('data-vjs-initialized', 'true');
            } else {
                // Enable all native controls
                element.setAttribute('controls', '');
            }
        } catch (err) {
            console.error('Video.js init failed', err);
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
