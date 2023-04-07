
export function setElementStyle(selector, field, value) {
    const ele = document.querySelector(selector);

    if (ele) {
        ele.style[field] = value;
    }
}

export function elementHasClass(selector, className) {
    const ele = document.querySelector(selector);

    return ele && ele.classList.contains(className);
}

export function replaceElementClasses(selector, classNames) {
    const ele = document.querySelector(selector);

    if (ele) {
        ele.classList = classNames;
    }
}

export function removeElementClass(selector, className) {
    const ele = document.querySelector(selector);

    if (ele) {
        ele.classList.remove(className);
    }
}

export function onElementClicked(selector, callback) {
    const ele = document.querySelector(selector);

    if (ele) {
        ele.addEventListener('click', callback);
    }
}
