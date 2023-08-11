
export function setElementStyle(selector: any, field: any, value: any) {
    const ele = document.querySelector(selector);

    if (ele) {
        ele.style[field] = value;
    }
}

export function elementHasClass(selector: any, className: any) {
    const ele = document.querySelector(selector);

    return ele && ele.classList.contains(className);
}

export function replaceElementClasses(selector: any, classNames: any) {
    const ele = document.querySelector(selector);

    if (ele) {
        ele.classList = classNames;
    }
}

export function removeElementClass(selector: any, className: any) {
    const ele = document.querySelector(selector);

    if (ele) {
        ele.classList.remove(className);
    }
}

export function onElementClicked(selector: any, callback: any) {
    const ele = document.querySelector(selector);

    if (ele) {
        ele.addEventListener('click', callback);
    }
}
