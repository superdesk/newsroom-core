import {isTouchDevice} from 'utils';

if (isTouchDevice()) {
    document.documentElement.classList.add('no-touch');
}
