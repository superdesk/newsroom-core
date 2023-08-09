import React from 'react';
import PropTypes from 'prop-types';
import {gettext, isDisplayed} from 'utils';

export default function ArticleAuthor({item, displayConfig}: any) {
    return (
        (item.byline || item.located || item.versioncreated) && (
            <p className='wire-column__preview__author'>
                {isDisplayed('byline', displayConfig) && item.byline && (
                    <span>{gettext('By')}{' '}<b>
                        {item.byline.toLowerCase().startsWith('by ') ? item.byline.substring(3) : item.byline}</b>{' '}
                    </span>
                )}
                {isDisplayed('located', displayConfig) && item.located && (
                    <span>{item.byline ? gettext('in {{located}}', {located: item.located}) : item.located}</span>
                )}
            </p>
        ) || null
    );
}

ArticleAuthor.propTypes = {
    item: PropTypes.object.isRequired,
    displayConfig: PropTypes.object,
};
