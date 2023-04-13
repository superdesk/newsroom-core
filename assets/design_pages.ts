import 'babel-polyfill';
import 'url-search-params-polyfill';
import 'whatwg-fetch';
import {Tooltip, Dropdown} from 'bootstrap';
import {isTouchDevice} from './utils';
import {
    elementHasClass,
    replaceElementClasses,
    setElementStyle,
    onElementClicked,
    removeElementClass
} from './domUtils';

if (!isTouchDevice()) {
    document.documentElement.classList.add('no-touch');
}

let filterOpen = false;
let previewOpen = false;

function isGrid(): any {
    return elementHasClass('.wire-articles__item', 'wire-articles__item--grid');
}

// Function for responsive wire item
function responsiveWireItem(): any {
    if (filterOpen && !previewOpen) {
        document.getElementsByClassName('wire-column__main')[0].classList.add('wire-articles__one-side-pane');
        document.getElementsByClassName('wire-column__main')[0].classList.remove('wire-articles__two-side-panes');
        if (isGrid()) {
            replaceElementClasses('.wire-articles__item-wrap', [
                'wire-articles__item-wrap',
                'col-sm-12',
                'col-md-6',
                'col-xl-4',
                'col-xxl-3'
            ]);
        }
    } else if (filterOpen && previewOpen) {
        document.getElementsByClassName('wire-column__main')[0].classList.remove('wire-articles__one-side-pane');
        document.getElementsByClassName('wire-column__main')[0].classList.add('wire-articles__two-side-panes');
        if (isGrid()) {
            replaceElementClasses('.wire-articles__item-wrap', [
                'wire-articles__item-wrap',
                'col-sm-12',
                'col-md-12',
                'col-xl-6',
                'col-xxl-4',
            ]);
        }
    } else if (!filterOpen && previewOpen) {
        document.getElementsByClassName('wire-column__main')[0].classList.remove('wire-articles__two-side-panes');
        document.getElementsByClassName('wire-column__main')[0].classList.add('wire-articles__one-side-pane');
        if (isGrid()) {
            replaceElementClasses('.wire-articles__item-wrap', [
                'wire-articles__item-wrap',
                'col-sm-12',
                'col-md-6',
                'col-xl-4',
                'col-xxl-3',
            ]);
        }
    } else {
        document.getElementsByClassName('wire-column__main')[0].classList.remove('wire-articles__one-side-pane');
        document.getElementsByClassName('wire-column__main')[0].classList.remove('wire-articles__two-side-panes');
        if (isGrid()) {
            replaceElementClasses('.wire-articles__item-wrap', [
                'wire-articles__item-wrap',
                'col-sm-6',
                'col-md-4',
                'col-xl-3',
                'col-xxl-2',
            ]);
        }
    }
}

function setupCarouselCaptionParallax(): any {
    // Carousel caption parallax
    const contentMain = document.querySelector('.content-main');

    if (contentMain) {
        contentMain.addEventListener('scroll', () => {
            const scrollTop = contentMain.scrollTop;
            const imgPos = (scrollTop / 2) + 'px';

            setElementStyle('.carousel-item', 'backgroundPosition', '50% ' + imgPos);
            setElementStyle('.carousel-caption', 'opacity', 1 - scrollTop / 400);
        });
    }
}

function setupContentNavbarScroll(): any {
    // Content navbar scroll
    const wireArticlesList = document.querySelector('.wire-articles--list');

    if (wireArticlesList) {
        wireArticlesList.addEventListener('scroll', () => {
            const scrollTop = wireArticlesList.scrollTop;
            const mainHeader = document.querySelector('.wire-column__main-header');

            if (mainHeader) {
                if (scrollTop > 10) {
                    mainHeader.classList.add('wire-column__main-header--small');
                } else {
                    mainHeader.classList.remove('wire-column__main-header--small');
                }
            }
        });
    }
}

function setupTogglingLeftBarNavigation(): any {
    // Toggle left bar navigation
    if (document.getElementsByClassName('content-bar__menu--nav')[0]) {
        document.getElementsByClassName('content-bar__menu--nav')[0].onclick = function(){
            document.getElementsByClassName('wire-column__nav')[0].classList.toggle('wire-column__nav--open');
            document.getElementsByClassName('content-bar__menu--nav')[0].classList.toggle('content-bar__menu--nav--open');

            // responsive wire item
            filterOpen = !filterOpen;
            responsiveWireItem();
        };
    }
}

function setupOpenArticleFromWireList(): any {
    // Open article from wire list
    const listItem = document.getElementsByClassName('wire-articles__item');

    let currentItem;
    for(let i = 0; i < listItem.length; i++) {
        listItem[i].onclick = function(event) {
            document.getElementsByClassName('wire-articles__item')[0].classList.toggle('wire-articles__item--open');

            // responsive wire item
            previewOpen = !previewOpen;
            responsiveWireItem();

            if (event.target.classList[0] === 'no-bindable') {
                document.getElementsByClassName('wire-articles__versions')[0].classList.toggle('wire-articles__versions--open');
                return false;
            }

            if (currentItem !== this) {
                document.getElementsByClassName('wire-column__preview')[0].classList.add('wire-column__preview--open');
                // eslint-disable-next-line @typescript-eslint/no-this-alias
                return currentItem = this;
            } else {
                document.getElementsByClassName('wire-column__preview')[0].classList.remove('wire-column__preview--open');
                return currentItem = null;
            }
        };
    }
}

function setupTopBarSearchFocus(): any {
    // Top bar search items
    // TODO: Use CSS to achieve the same goal here
    const searchForm = document.getElementsByClassName('search__form')[0];
    const searchInput = document.getElementsByClassName('search__input')[0];
    if (searchInput) {
        searchInput.onfocus = function() {
            searchForm.classList.add('searchForm--active');
        };
    }
}

function setupClosePreviewOnMobile(): any {
    // close preview on mobile
    if (isTouchDevice()) {
        onElementClicked('.wire-column__preview__mobile-bar button', () => {
            removeElementClass('.wire-column__preview', 'wire-column__preview--open');

            previewOpen = !previewOpen;
            responsiveWireItem();
        });
    }
}

function setupBootstrapElementsFromServerTemplates(): any {
    if (!isTouchDevice()) {
        document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach((ele) => {
            new Tooltip(ele);
        });
    }

    // design view dropdown fix
    document.querySelectorAll('[data-bs-toggle="dropdown"]').forEach((ele) => {
        new Dropdown(ele);
    });
}

setupBootstrapElementsFromServerTemplates();

setupCarouselCaptionParallax();
setupContentNavbarScroll();
setupTogglingLeftBarNavigation();
setupOpenArticleFromWireList();
setupTopBarSearchFocus();
setupClosePreviewOnMobile();
