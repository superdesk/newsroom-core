import {gettext, isTouchDevice} from 'utils';
import 'primereact/resources/primereact.min.css';
import {Button} from './ui/components/Button';
import {IArticle} from 'interfaces';

if (isTouchDevice()) {
    document.documentElement.classList.add('no-touch');
}

interface IExtensions {
    prepareWirePreview?(content: HTMLElement, item: IArticle): HTMLElement;
}

export const extensions: IExtensions = {};

export function registerExtensions(extensionsToRegister: IExtensions) {
    Object.assign(extensions, extensionsToRegister);
}

interface IExposedForExtensions {
    ui: {
        Button: typeof Button,
    };
    locale: {
        gettext: typeof gettext,
    };
}

export const exposed: IExposedForExtensions = {
    ui: {
        Button,
    },
    locale: {
        gettext,
    },
};

import 'app';