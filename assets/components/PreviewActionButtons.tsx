import React from 'react';
import PropTypes from 'prop-types';
import ActionButton from './ActionButton';
import types from 'wire/types';


function PreviewActionButtons({item, user, actions, plan, group}: any) {
    const actionButtons = actions.map((action) =>
        <ActionButton
            key={action.name}
            item={item}
            className='icon-button icon-button--primary'
            isVisited={action.visited && action.visited(user, item)}
            displayName={false}
            action={action}
            plan={plan}
            group={group}
        />
    );

    return (
        <div className='wire-column__preview__buttons'>
            {actionButtons}
        </div>
    );
}

PreviewActionButtons.propTypes = {
    item: types.item,
    user: types.user,
    actions: types.actions,
    plan: PropTypes.string,
    group: PropTypes.string,
};

export default PreviewActionButtons;
