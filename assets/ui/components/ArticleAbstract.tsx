import React from 'react';
import PropTypes from 'prop-types';

interface IProps {
    item: {
        description_text?: string;
    };
    displayAbstract?: boolean;
}

export default function ArticleAbstract({item, displayAbstract}: IProps) {
    return (
        (item.description_text && displayAbstract) &&
            <p className='wire-column__preview__lead'>{item.description_text}</p> || null
    );
}

ArticleAbstract.propTypes = {
    item: PropTypes.object.isRequired,
    displayAbstract: PropTypes.bool,
};