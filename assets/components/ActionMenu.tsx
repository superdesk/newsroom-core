import React from 'react';
import PropTypes from 'prop-types';
import ActionList from './ActionList';
import {Popover, PopoverBody} from 'reactstrap';

import {gettext} from 'utils';

class ActionMenu extends React.Component {
    constructor(props) {
        super(props);
        this.onMouseLeave = this.onMouseLeave.bind(this);
    }

    onMouseLeave(event) {
        if (this.props.showActions) {
            this.props.onActionList(event, this.props.item, this.props.group);
        }
    }

    render() {
        const {item, plan, user, actions, group, onActionList, showActions, showShortcutActions} = this.props;
        return (
            <div className='btn-group'>
                <button
                    ref={(elem: any) => this.referenceElem = elem}
                    onClick={(event: any) => onActionList(event, item, group, plan)}
                    className="icon-button icon-button--secondary"
                    aria-label={gettext('More Actions')}>
                    <i className='icon--more'></i>
                </button>
                {this.referenceElem && (
                    <Popover
                        placement="left-end"
                        isOpen={showActions}
                        target={this.referenceElem}
                        className="action-popover"
                        delay={0}
                        fade={false}
                    >
                        <PopoverBody>
                            <ActionList
                                item={item}
                                group={group}
                                plan={plan}
                                user={user}
                                actions={actions}
                                onMouseLeave={this.onMouseLeave}
                                showShortcutActions={showShortcutActions}
                            />
                        </PopoverBody>
                    </Popover>
                )}
            </div>
        );
    }
}

ActionMenu.propTypes = {
    item: PropTypes.object,
    user: PropTypes.string,
    plan: PropTypes.object,
    actions: PropTypes.arrayOf(PropTypes.shape({
        name: PropTypes.string.isRequired,
        icon: PropTypes.string.isRequired,
        action: PropTypes.func.isRequired,
    })),
    group: PropTypes.string,
    onActionList: PropTypes.func.isRequired,
    showActions: PropTypes.bool.isRequired,
    showShortcutActions: PropTypes.bool,
};

export default ActionMenu;
