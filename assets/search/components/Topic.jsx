import React from 'react';
import PropTypes from 'prop-types';

import classNames from 'classnames';

import {gettext, formatDate, formatTime} from 'utils';
import ActionButton from 'components/ActionButton';
import {ToolTip} from '../../ui/components/ToolTip';
import AuditInformation from 'components/AuditInformation';

export function Topic({topic, actions, users, selected}) {
    const getActionButtons = (topic) => actions.filter((action) => action.if == null || action.if(topic)).map(
        (action) => (
            <ActionButton
                key={action.name}
                item={topic}
                className='icon-button icon-button--primary'
                displayName={false}
                action={action}
                disabled={action.when != null && !action.when(topic)}
            />
        )
    );

    return (
        <div key={topic._id} className=''>
            <div
                className={classNames(
                    'simple-card',
                    'simple-card--draggable',
                    {'simple-card--selected': selected}
                )}
                draggable={true}
                onDragStart={(event) => {
                    event.dataTransfer.setData('topic', topic._id);
                    event.dataTransfer.dropEffect = 'move';
                }}
            >
                <div className="simple-card__header simple-card__header-with-icons">
                    <ToolTip>
                        <h6
                            className="simple-card__headline"
                            title={topic.label || topic.name}
                        >
                            {topic.label || topic.name}
                        </h6>
                    </ToolTip>
                    <div className='simple-card__icons'>
                        {getActionButtons(topic)}
                    </div>
                </div>
                <p className='simple-card__description'>{topic.description || ' '}</p>
                <div className="simple-card__row simple-card__row--space-between">
                    <div className="simple-card__column simple-card__column--align-start">
                        <span className="simple-card__date">Created on 29.05.2023 @ 12:38</span>
                        <span className="simple-card__date">Updated on 31.05.2023 @ 14:02</span>
                    </div>
                </div>

                {topic.is_global ? (
                    <span className="simple-card__date">
                        <AuditInformation
                            item={topic}
                            users={users}
                            className="p-0"
                            noPadding={true}
                        />
                    </span>
                ) : (
                    <span className="simple-card__date">
                        {gettext('Created on {{ date }} at {{ time }}', {
                            date: formatDate(topic._created),
                            time: formatTime(topic._created),
                        })}
                    </span>
                )}
            </div>
        </div>
    );
}

Topic.propTypes = {
    topic: PropTypes.shape({
        _id: PropTypes.string,
        name: PropTypes.string,
        label: PropTypes.string,
        description: PropTypes.string,
        is_global: PropTypes.bool,
        _created: PropTypes.string,
    }),
    actions: PropTypes.arrayOf(PropTypes.shape({
        name: PropTypes.string,
        icon: PropTypes.string,
        action: PropTypes.func,
        if: PropTypes.func,
    })),
    selected: PropTypes.bool,
    users: PropTypes.array,
};