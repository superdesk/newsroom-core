import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import {get} from 'lodash';
import {isPostponed, isRescheduled, isCanceled} from '../utils';

function AgendaListItemLabels({item, right}) {
    const getLabel = () => {
        let labelText;
        let labelColor;
        if (isPostponed(item)) {
            labelText = gettext('postponed');
            labelColor = 'label--blue';
        }

        if (isCanceled(item)) {
            labelText = gettext('cancelled');
            labelColor = 'label--red';
        }

        if (isRescheduled(item)) {
            labelText = gettext('rescheduled');
            labelColor = 'label--orange';
        }

        if (get(item, 'event.completed')) {
            labelText = gettext('event completed');
            labelColor = 'label--green';
        }

        if (!labelText) {
            return null;
        }

        return (<div><span className={classNames('label', labelColor, {'pull-right': right})}>{labelText}</span></div>);

    };

    return getLabel();
}

AgendaListItemLabels.propTypes = {
    item: PropTypes.object,
    right: PropTypes.bool,
};

export default AgendaListItemLabels;
