import {gettext, isTouchDevice} from 'utils';

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
