import {isTouchDevice} from 'utils';
import 'primereact/resources/primereact.min.css';

if (isTouchDevice()) {
    document.documentElement.classList.add('no-touch');
}

interface IExtensions {
    prepareWirePreview?(content: HTMLElement): HTMLElement;
}

export const extensions: IExtensions = {};

export function registerExtensions(extensionsToRegister: IExtensions) {
    Object.assign(extensions, extensionsToRegister);
}