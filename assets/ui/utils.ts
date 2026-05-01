import {isEmpty} from 'lodash';
import classNames from 'classnames';
import videojs from 'video.js';
import server from '../server';
import {notify, gettext} from '../utils';

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
        if (!document.body.contains(el)) {
            onReady(null);
            return;
        }
        const isAudio = el instanceof HTMLAudioElement;

        if (typeof videojs === 'function') {
            try {
                const player = videojs(el, {
                    controls: true,
                    preload: 'auto',
                    fluid: true,
                    audioOnlyMode: isAudio,
                    controlBar: {
                        pictureInPictureToggle: false,
                        fullscreenToggle: false
                    },
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

        const disableDownload = element.getAttribute('data-disable-download') === 'true';

        element.classList.add('video-js');
        // Convince the player to show the ControlBar
        if (element instanceof HTMLVideoElement) {
            element.classList.add('vjs-has-started');
        }

        // Remove native controls everywhere on all major browsers
        element.removeAttribute('controls');
        // Additional override for browsers that support controlsList
        element.setAttribute('controlsList', 'nodownload');
        // Disable right-click context menu on all browsers
        element.addEventListener('contextmenu', (e) => e.preventDefault());

        const cancel = initPlayer(element, 3, 100, (player: VjsPlayer | null) => {
            if (!player) return;

            if (player) players.push(player);

            if (!disableDownload) {
                const VjsButton = videojs.getComponent('Button');
                const downloadBtn = new VjsButton(player, {
                    className: 'vjs-control vjs-download-button vjs-icon-file-download'
                });
                (downloadBtn as any).controlText('Download');

                (downloadBtn as any).handleClick = async () => {
                    const item_id = element.getAttribute('data-item-id') || '';
                    const altText = element.getAttribute('alt') || 'download';
                    const filename = sanitizeFilename(altText);

                    const source = player.currentSrc() + '/download';

                    const downloadUrl = new URL(source);
                    downloadUrl.searchParams.set('item_id', item_id);

                    try {
                        // Make a head request to ensure that the user has download rights
                        await server.head(downloadUrl.toString());

                        const link = document.createElement('a');
                        downloadUrl.searchParams.set('filename', filename);
                        link.href = downloadUrl.toString();
                        link.setAttribute('download', '');
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                    } catch (error: any) {
                        if (error.status === 403) {
                            notify.warning(gettext('Permission Denied'));
                        } else if (error.status === 404) {
                            notify.error(gettext('File not found.'));
                        } else {
                            notify.error(gettext('An error occurred while checking permissions.'));
                        }
                    }
                };
                const controlBar = player.getChild('ControlBar');
                if (controlBar) {
                    controlBar.addChild(downloadBtn);
                }
            }
        });

        timeoutCancels.push(cancel);
    });

    return () => {
        timeoutCancels.forEach((c) => c());
        players.forEach((p) => p?.dispose?.());
    };
}

function sanitizeFilename(name: string): string {
    if (!name) return 'download';

    return name
        // eslint-disable-next-line no-control-regex
        .replace(/[\x00-\x1f\x80-\x9f]/g, '')
        .replace(/[\\/:*?"<>|%]/g, '')
        .replace(/[\s_]+/g, '_')
        .replace(/[.\s]+$/, '')
        .substring(0, 255); // Max filename length for most OS
}
