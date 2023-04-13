import * as React from 'react';
import PropTypes from 'prop-types';


export function PreviewText({text}: any) {
    if (text == null || !text.length) {
        return null;
    }

    return text[0] !== '<' ? (
        <p className="wire-column__preview__text wire-column__preview__text--pre">
            {text}
        </p>
    ) : (
        <div dangerouslySetInnerHTML={{__html: text}} />
    );
}

PreviewText.propTypes = {
    text: PropTypes.string.isRequired,
};
