import {isEmpty} from 'lodash';
import classNames from 'classnames';

const isNotEmpty = (x: any) => !isEmpty(x);

/**
 * Get bem classes
 *
 * @param {String} block 
 * @param {String} element 
 * @param {Object} modifier 
 * @return {String}
 */
export function bem(block: any, element: any, modifier: any) {
    const main = [block, element].filter(isNotEmpty).join('__');
    const classes = [main];

    if (!isEmpty(modifier)) {
        const modifiers = classNames(modifier).split(' ');

        modifiers.forEach((suffix: any) => {
            classes.push(main + '--' + suffix);
        });
    }

    return classes.join(' ');
}