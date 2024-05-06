import {ComponentType} from 'react';
import 'primereact/resources/primereact.min.css';

import {IArticle, ICoverageMetadataPreviewProps} from 'interfaces';
import {gettext, isTouchDevice} from 'utils';

import {registerCoverageFieldComponent} from './agenda/components/preview';
import {Button} from './ui/components/Button';

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
