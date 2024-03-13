import {isTouchDevice, gettext} from 'utils';
import 'primereact/resources/primereact.min.css';

if (isTouchDevice()) {
    document.documentElement.classList.add('no-touch');
}

const element = document.getElementById('nav');
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
    if (element == null || pinButton == null) {
        return null;
    }

    if (element.classList.contains('nav-block--pinned')) {
        sessionStorage.removeItem('navigation-pinned');
        element.classList.remove('nav-block--pinned');
        pinButton.setAttribute('title', gettext('Expand'));
    } else {
        sessionStorage.setItem('navigation-pinned', 'true');
        element.classList.add('nav-block--pinned');
        pinButton.setAttribute('title', gettext('Collapse'));
    }
}
