import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import {get} from 'lodash';

import {gettext} from 'utils';
import {STATUS_CANCELED, STATUS_POSTPONED, STATUS_RESCHEDULED} from '../utils';

export default function AgendaEdNote({item, plan, secondaryNoteField, noMargin}: any) {
    const planEdnote = get(plan, 'ednote');

    // We display Secondary Note only from 'item' for now
    const displaySecondaryNote = secondaryNoteField && get(item, secondaryNoteField);

    if (!item.ednote && !planEdnote && !displaySecondaryNote) {
        return null;
    }

    const tooltip = !item.ednote && !planEdnote ? gettext('Reason') : gettext('Editorial Note');
    const fixText = (text: any) => {
        // remove prefixes added by planning
        // which are always in english
        const POSTPONED = 0;
        const RESCHEDULED = 1;
        const CANCELLED = 2;
        const prefixes = [];

        prefixes[POSTPONED] = 'Event Postponed: ';
        prefixes[RESCHEDULED] = 'Event Rescheduled: ';
        prefixes[CANCELLED] = 'Event Cancelled: ';

        const index = prefixes.findIndex((_prefix) => text.startsWith(_prefix));

        if (index !== -1) {
            const reason = text.substr(prefixes[index].length);

            switch (index) {
            case POSTPONED:
                return gettext('Event Postponed: {{reason}}', {reason});
            case RESCHEDULED:
                return gettext('Event Rescheduled: {{reason}}', {reason});
            case CANCELLED:
                return gettext('Event Cancelled: {{reason}}', {reason});
            }
        }

        const reason = text;

        switch (item.state) {
        case STATUS_POSTPONED:
            return gettext('Event Postponed: {{reason}}', {reason});
        case STATUS_RESCHEDULED:
            return gettext('Event Rescheduled: {{reason}}', {reason});
        case STATUS_CANCELED:
            return gettext('Event Cancelled: {{reason}}', {reason});
        }

        return text;
    };

    const getMultiLineNote = (note) => (note && fixText(note).split('\n').map((t, key) =>
        <span key={key}>{t}<br/></span>)
    );

    const getNoteFields = () => {
        if (!item.ednote && !planEdnote) {
            // Display only Secondary Note
            return (<span className='ms-1'>{getMultiLineNote(item[secondaryNoteField])}</span>);
        }

        // Display both Ed & Secondary Note
        return (
            <span className='ms-1'>{getMultiLineNote(planEdnote || item.ednote)}
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
