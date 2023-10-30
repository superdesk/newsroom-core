import {isTouchDevice} from 'utils';
import {newshubApi, INewshubApi} from './api';

if (isTouchDevice()) {
    document.documentElement.classList.add('no-touch');
}

let started = false;

export function startApp(): Promise<INewshubApi> {
    if (started === true) {
        return Promise.resolve(newshubApi);
    }

    started = true;
    return Promise.resolve(newshubApi);
}

setTimeout(() => {
    if (started !== true) {
        startApp();
    }
}, 500);
