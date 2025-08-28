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

export function setupVideoPlayers(root: HTMLElement) {
    const players: any[] = [];

    root.querySelectorAll('video').forEach((element) => {
        if (element.getAttribute('data-vjs-initialized')) return;
        const disable = element.getAttribute('data-disable-download') === 'true';

        if (disable) {
            element.setAttribute('controlsList', 'nodownload');
            element.addEventListener('contextmenu', e => e.preventDefault());
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
