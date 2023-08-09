import React from 'react';
import PropTypes from 'prop-types';
import classNames from  'classnames';

import {getName, getHighlightedName} from '../utils';

export default function AgendaName({item, noMargin, small}: any) {
    return (
        <h2 className={classNames({'wire-column__preview__headline': !small},
            {'wire-articles__item__text wire-column__preview__versions__box-headline': small},
            {'mt-4': !noMargin})}>{item.es_highlight ? (
                <span dangerouslySetInnerHTML={{__html: getHighlightedName(item)}} /> ) : getName(item)}</h2>
    );
}

AgendaName.propTypes = {
    item: PropTypes.object.isRequired,
    noMargin: PropTypes.bool,
    small: PropTypes.bool,
};