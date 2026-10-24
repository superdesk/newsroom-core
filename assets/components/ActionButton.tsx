import React from 'react';
import {gettext} from 'utils';
import {IconButton, IPropsSize, IPropsVariant} from './IconButton';

interface IProps {
    ['data-test-id']?: string,
    item: any,
    action: any,
    group?: string,
    plan?: string | any,
    disabled?: boolean,
    variant?: IPropsVariant;
    size?: IPropsSize;
    border?: boolean;
}

class ActionButton extends React.Component<IProps> {
    render() {
        const {item, group, plan, action, disabled} = this.props;
        const tooltip = this.props.action.tooltip ?? this.props.action.name;
        const ariaLabel = item?.headline ?
            gettext('{{action}}: {{headline}}', {action: tooltip, headline: item.headline}) :
            tooltip;

        return (
            <IconButton
                icon={this.props.action.icon}
                variant={this.props.variant}
                size={this.props.size}
                border={this.props.border}
                data-test-id={this.props['data-test-id']}
                disabled={disabled}
                onClick={
                    () => {
                        if (action.multi) {
                            return action.action([item._id]);
                        } else {
                            return action.action(item, group, plan);
                        }
                    }
                }
                tooltip={tooltip}
                ariaLabel={ariaLabel}
            />
        );
    }
}

export default ActionButton;
