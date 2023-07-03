import {isTouchDevice} from 'utils';
import 'primereact/resources/primereact.min.css';

if (isTouchDevice()) {
    document.documentElement.classList.add('no-touch');
}


window.sectionNames = {
    home: 'Home',
    wire: 'Wire',
    agenda: 'Agenda',
    monitoring: 'Monitoring',
    saved: 'Saved / Watched',
};