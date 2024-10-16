import {ComponentType} from 'react';
import 'primereact/resources/primereact.min.css';

import {IArticle, ICoverageMetadataPreviewProps} from 'interfaces';
import {gettext, isTouchDevice} from 'utils';

import {registerCoverageFieldComponent} from './agenda/components/preview';
import {Button} from './ui/components/Button';


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
    agenda: {
        registerCoverageFieldComponent(
            field: string,
            component: ComponentType<ICoverageMetadataPreviewProps>
        ): void;
    };
}

export const exposed: IExposedForExtensions = {
    ui: {
        Button,
    },
    locale: {
        gettext,
    },
    agenda: {
        registerCoverageFieldComponent,
    },
};

import 'app';

// navigation scripts
if (isTouchDevice()) {
    document.documentElement.classList.add('no-touch');
}

const navigation = document.getElementById('nav');
const pinButton = document.getElementById('pin-btn');

if (pinButton != null) {
    pinButton.addEventListener('click', () => {
        handleNavToggle();
    });
}

if (sessionStorage.getItem('navigation-pinned')) {
    handleNavToggle();
}

function handleNavToggle() {
    if (navigation == null || pinButton == null) {
        return null;
    }

    if (navigation.classList.contains('nav-block--pinned')) {
        sessionStorage.removeItem('navigation-pinned');
        navigation.classList.remove('nav-block--pinned');
        pinButton.setAttribute('title', gettext('Expand'));
    } else {
        sessionStorage.setItem('navigation-pinned', 'true');
        navigation.classList.add('nav-block--pinned');
        pinButton.setAttribute('title', gettext('Collapse'));
    }
}
