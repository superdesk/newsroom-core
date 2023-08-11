import {isTouchDevice} from 'utils';
import 'primereact/resources/primereact.min.css';

if (isTouchDevice()) {
    document.documentElement.classList.add('no-touch');
}
