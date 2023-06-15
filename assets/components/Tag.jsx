import * as React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';

export function Tag({text, keyValue, shade, readOnly, onClick, label, operator}) {
    let classes = classNames('tag-label', {
        [`tag-label--${shade}`]: shade && shade !== 'light',
        'tag-label--operator': operator,
    });

    return (
        <React.Fragment>
            {label
                ?
                <span className={classes} key={keyValue}>
                    <span className='tag-label--text-wrapper'>
                        <span className='tag-label--text-label'>
                            {label}:
                        </span>
                        <span className='tag-label--text'>
                            {text}
                        </span>
                    </span>
                    {!readOnly ? <button className='tag-label__remove' onClick={onClick}>
                        <i className="icon--close-thin" />
                    </button> : null}
                </span>
                :
                <span className={classes} key={keyValue}>
                    <span className='tag-label--text'>
                        {text}
                    </span>
                    {!readOnly ? <button className='tag-label__remove' onClick={onClick}>
                        <i className="icon--close-thin" />
                    </button> : null}
                </span>
            }
        </React.Fragment>
    );
}

Tag.propTypes = {
    text: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.number,
    ]).isRequired,
    label: PropTypes.string,
    keyValue: PropTypes.string,
    shade: PropTypes.oneOf([
        'light',
        'darker',
        'highlight',
        'highlight1',
        'highlight2',

        'inverse',
        'info',
        'success',
        'alert',
        'warning',
    ]),
    operator: PropTypes.bool,
    readOnly: PropTypes.bool,
    onClick: PropTypes.func,
};
