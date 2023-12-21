import * as React from 'react';
import classNames from 'classnames';
import {Icon} from './Icon';
import {Tooltip} from 'bootstrap';
import {isTouchDevice} from 'utils';

export type IPropsVariant = 'primary' | 'secondary' | 'tertiary';
export type IPropsSize = 'default' | 'small';

interface IProps {
    icon: string;
    variant?: IPropsVariant; // default secondary
    size?: IPropsSize;
    disabled?: boolean;
    border?: boolean;
    id?: string;
    className?: string;
    tooltip?: string;
    ariaLabel?: string;
    ariaHidden?: boolean;
    'data-test-id'?: string;
    'data-bs-toggle'?: string;
    'data-bs-dismiss'?: string;
    onClick(event: React.MouseEvent): void;
}

class IconButtonComponent extends React.PureComponent<IProps> {
    tooltip: any;
    elem: any;
    constructor(props: any) {
        super(props);

        this.tooltip = null;
    }

    componentDidMount() {
        if (!isTouchDevice() && this.elem && this.props.tooltip) {
            this.tooltip = new Tooltip(this.elem, {trigger: 'hover', title: this.props.tooltip});
        }
    }

    componentWillUnmount() {
        if (this.tooltip) {
            this.tooltip.dispose();
        }
    }

    render() {
        const classes = classNames('icon-button', {
            'icon-button--small': this.props.size === 'small',
            [`icon-button--${this.props.variant}`]: this.props.variant,
            'icon-button--secondary': !this.props.variant,
            'icon-button--bordered': this.props.border,
        }, this.props.className);

        return (
            <button
                ref={(elem: any) => this.elem = elem}
                id={this.props.id}
                className={classes}
                aria-label={this.props.ariaLabel}
                data-test-id={this.props['data-test-id']}
                data-bs-toggle={this.props['data-bs-toggle']}
                data-bs-dismiss={this.props['data-bs-dismiss']}
                tabIndex={0}
                disabled={this.props.disabled}
                onClick={this.props.onClick}
            >
                <Icon name={this.props.icon} aria-hidden={this.props.ariaHidden} />
            </button>
        );
    }
}

export class IconButton extends React.PureComponent<IProps> {
    render() {
        return (
            <IconButtonComponent {...this.props} key={this.props.tooltip} />
        );
    }
}
