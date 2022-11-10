import React from 'react';
import PropTypes from 'prop-types';
import {get} from 'lodash';
import classNames from 'classnames';

import {gettext} from 'utils';

export default function AgendaEdNote({item, plan, secondaryNoteField, noMargin}) {
    const planEdnote = get(plan, 'ednote');

    // We display Secondary Note only from 'item' for now
    const displaySecondaryNote = secondaryNoteField && get(item, secondaryNoteField);

    if (!item.ednote && !planEdnote && !displaySecondaryNote) {
        return null;
    }

    const tooltip = !item.ednote && !plan.ednote ? gettext('Reason') : gettext('Editorial Note');
    const fixText = (text) => {
        // remove prefixes added by planning
        // which are always in english
        const POSTPONED = 0;
        const RESCHEDULED = 1;
        const CANCELLED = 2;
        const prefixes = [];

        prefixes[POSTPONED] = 'Event Postponed: ';
        prefixes[RESCHEDULED] = 'Event Rescheduled: ';
        prefixes[CANCELLED] = 'Event Cancelled: ';

        return prefixes.reduce((_text, prefix, index) => {
            if (_text.startsWith(prefix)) {
                let reason = _text.substr(prefix.length);

                switch (index) {
                case POSTPONED:
                    return gettext('Event Postponed: {{reason}}', {reason});
                case RESCHEDULED:
                    return gettext('Event Rescheduled: {{reason}}', {reason});
                case CANCELLED:
                    return gettext('Event Cancelled: {{reason}}', {reason});
                }
            }

            return _text;
        }, text.trim());
    };

    const getMultiLineNote = (note) => (note && fixText(note).split('\n').map((t, key) =>
        <span key={key}>{t}<br/></span>)
    );

    const getNoteFields = () => {
        if (!item.ednote && !planEdnote) {
            // Display only Secondary Note
            return (<span className='ml-1'>{getMultiLineNote(item[secondaryNoteField])}</span>);
        }

        // Display both Ed & Secondary Note
        return (
            <span className='ml-1'>{getMultiLineNote(planEdnote || item.ednote)}
                <span className="secondary-note">
                    {getMultiLineNote(item[secondaryNoteField])}
                </span>
            </span>
        );
    };

    return (
        <div className={classNames('wire-column__preview_article-note', {'m-0': noMargin})}>
            <i className="icon--info icon--info--smaller" title={tooltip}/>
            {getNoteFields()}
        </div>
    );
}

AgendaEdNote.propTypes = {
    item: PropTypes.object.isRequired,
    plan: PropTypes.object,
    secondaryNoteField: PropTypes.string,
    noMargin: PropTypes.bool,
};
