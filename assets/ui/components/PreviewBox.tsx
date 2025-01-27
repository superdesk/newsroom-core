import React from 'react';
import PropTypes from 'prop-types';

export default function PreviewBox(props: any) {
    return (
        <div className='preview__content-block'>
            <div className={props.labelClass || 'preview__content-block-title'}>{props.label}</div>
            {props.children}
        </div>
    );
}

PreviewBox.propTypes = {
    label: PropTypes.string,
    labelClass: PropTypes.string,
    children: PropTypes.node,
};
