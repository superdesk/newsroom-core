import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import {gettext, getPlainTextMemoized} from 'utils';

export default function AgendaInternalNote({internalNote, onlyIcon, noMargin, mt2, alignCenter, marginRightAuto, borderRight, noPaddingRight}) {
    const note = getPlainTextMemoized(internalNote);

    if (!note) {
        return null;
    }

    const labelText = gettext('Internal Note');
    if (onlyIcon) {
        const className = classNames(
            'wire-column__preview_article-note',
            {
                'align-self-center': alignCenter,
                'm-0': noMargin,
                'me-auto': marginRightAuto,
                'mt-2': mt2,
                'border-right': borderRight,
                'pe-0': noPaddingRight,
            }
        );

        return (
            <div title={`${labelText}:\n${note}`}
                data-bs-toggle="tooltip"
                data-bs-placement="right"
                className={className}
            >
                <i className="icon--info icon--red icon--info--smaller"/>
            </div>
        );
    } else {
        return (
            <div className={classNames('wire-column__preview_article-note', {'m-0': noMargin}, {'mt-2': mt2})}>
                <i className="icon--info icon--red icon--info--smaller" title={labelText}/>
                <span className='ms-1'>
                    {internalNote[0] !== '<' ?
                        internalNote.split('\n').map((item, key) => (
                            <p key={key}>{item}</p>
                        ))
                        : (
                            <div dangerouslySetInnerHTML={{__html: internalNote}} />
                        )
                    }
                </span>
            </div>
        );
    }
}

AgendaInternalNote.propTypes = {
    internalNote: PropTypes.string,
    onlyIcon: PropTypes.bool,
    noMargin: PropTypes.bool,
    mt2: PropTypes.bool,
    alignCenter: PropTypes.bool,
    marginRightAuto: PropTypes.bool,
    borderRight: PropTypes.bool,
    noPaddingRight: PropTypes.bool,
};

AgendaInternalNote.defaultProps = {
    alignCenter: false,
    marginRightAuto: false,
    borderRight: false,
    noPaddingRight: false,
};
