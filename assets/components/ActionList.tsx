import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';

interface IProps {
    item: any,
    action: any,
    group?: string,
    plan?: string | any,
}

class ActionListItem extends React.Component<IProps> {
    render() {
        const classes = classNames(`icon--${this.props.action.icon}`);
        const {item, group, plan, action} = this.props;

        return (
            <button
                type='button'
                className='dropdown-item'
                onClick={
                    () => {
                        if (action.multi) {
                            return action.action([item._id]);
                        } else {
                            return action.action(item, group, plan);
                        }
                    }
                }
                aria-label={this.props.action.name}
            >
                <i className={classes} />
                {this.props.action.name}
            </button>
        );
    }
}

function ActionList({item, group, plan, actions, onMouseLeave, showShortcutActions}: any) {
    return (
        <div onMouseLeave={onMouseLeave}>
            {actions.map((action: any) => (showShortcutActions || !action.shortcut) &&
                <ActionListItem
                    key={action.name}
                    action={action}
                    item={item}
                    group={group}
                    plan={plan}
                />
            )}
        </div>
    );
}

export default ActionList;
