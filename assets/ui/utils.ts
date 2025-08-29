import {isEmpty} from 'lodash';
import classNames from 'classnames';
import videojs from 'video.js';

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
    const players: any[] = [];

    root.querySelectorAll('video, audio').forEach((element) => {
        if (element.getAttribute('data-vjs-initialized')) return;
        const disable = element.getAttribute('data-disable-download') === 'true';

        element.setAttribute('data-vjs-initialized', 'true');

        if (disable) {
            element.setAttribute('controlsList', 'nodownload');
            element.addEventListener('contextmenu', (e) => e.preventDefault());
            element.removeAttribute('controls');

            if (element instanceof HTMLVideoElement) {
                element.classList.add('video-js', 'vjs-big-play-centered');
            } else if (element instanceof HTMLAudioElement) {
                element.classList.add('video-js');
            }

            const player = videojs(element, {
                controls: true,
                preload: 'auto',
                fluid: true,
            });
            players.push(player);
        } else {
            element.setAttribute('controls', '');
            players.push(null);
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
